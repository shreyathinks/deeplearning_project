from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import subprocess
import json
import uuid
from pathlib import Path
import concurrent.futures

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

import glob

def find_checkpoint(pattern):
    matches = glob.glob(pattern, recursive=True)
    if matches:
        # Return the most recently modified matching file/dir
        return max(matches, key=os.path.getmtime)
    return None

YOLO_CKPT = os.environ.get("YOLO_CKPT") or find_checkpoint("runs/detect/**/weights/best.pt") or find_checkpoint("outputs/yolo/**/weights/best.pt") or "outputs/yolo/yolov8s_v1/weights/best.pt"
SEG_CKPT  = os.environ.get("SEG_CKPT") or find_checkpoint("outputs/segformer/**/best/best") or find_checkpoint("outputs/segformer/**/best") or "outputs/segformer/segformer_b0_v1/best"
SEV_CKPT  = os.environ.get("SEV_CKPT") or find_checkpoint("outputs/severity/**/best_severity.pt") or "outputs/severity/severity_resnet18_v1/best_severity.pt"


# Fix #5: set a generous but finite timeout so the server never hangs indefinitely
PIPELINE_TIMEOUT_SECONDS = 300

executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

app = Flask(__name__, template_folder='webapp/templates', static_folder='webapp/static')
UPLOAD_FOLDER = 'webapp/uploads'
OUTPUT_FOLDER = 'outputs/inference'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
        
    file = request.files['image']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file or file type not allowed'}), 400
        
    # Generate unique filename
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
    filename = f"{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    # Run pipeline
    base_name = Path(filename).stem
    cmd = [
        "python", "pipeline/final_pipeline.py",
        "--image", filepath,
        "--yolo-checkpoint", YOLO_CKPT,
        "--segformer-checkpoint", SEG_CKPT,
        "--severity-checkpoint", SEV_CKPT
    ]
    
    try:
        # Fix #5: submit with a finite timeout to avoid hanging the server forever
        future = executor.submit(
            subprocess.run, cmd,
            check=True, capture_output=True, text=True,
            timeout=PIPELINE_TIMEOUT_SECONDS
        )
        future.result(timeout=PIPELINE_TIMEOUT_SECONDS + 10)  # outer guard
        
        # Read JSON output
        json_path = os.path.join(OUTPUT_FOLDER, base_name, "prediction.json")
        with open(json_path, 'r') as f:
            prediction = json.load(f)
            
        # Calculate Repair Cost for Demo
        base_cost = 0
        if prediction.get('status') == 'damage_detected':
            sev_label = prediction.get('severity', {}).get('label', 'Low').split(' ')[0]
            sev_multiplier = {"High": 3.5, "Medium": 2.0, "Low": 1.0}.get(sev_label, 1.0)
            
            for dmg in prediction.get('damages', []):
                dtype = dmg['damage_type']
                cost_map = {"scratch": 150, "dent": 300, "crack": 450, "tire_flat": 200, "glass_shatter": 600}
                base_cost += cost_map.get(dtype, 200) * sev_multiplier
                
        prediction['repair_cost'] = f"${int(base_cost):,}"
            
        # Add output image URLs to the response (Fix #20: include gradcam URL)
        prediction['images'] = {
            'original':    f"/outputs/{base_name}/original.jpg",
            'detection':   f"/outputs/{base_name}/detection.jpg",
            'segmentation':f"/outputs/{base_name}/segmentation.jpg",
            'gradcam':     f"/outputs/{base_name}/gradcam.jpg",
            'final':       f"/outputs/{base_name}/final_visualization.jpg"
        }
        return jsonify(prediction)
        
    except concurrent.futures.TimeoutError:
        return jsonify({'error': 'Pipeline timed out after 5 minutes'}), 504
    except subprocess.CalledProcessError as e:
        print(f"Pipeline error: {e.stderr}")
        return jsonify({'error': 'Pipeline execution failed', 'details': e.stderr}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to serve the generated images
@app.route('/outputs/<folder>/<filename>')
def serve_output(folder, filename):
    folder_path = os.path.join(os.getcwd(), OUTPUT_FOLDER, folder)
    return send_from_directory(folder_path, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
