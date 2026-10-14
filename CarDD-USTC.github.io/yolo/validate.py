import os
import sys
import json
import argparse
from pathlib import Path
from ultralytics import YOLO

def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate YOLOv8 on CarDD dataset")
    parser.add_argument("--checkpoint", type=str, required=True, help="Path to best.pt")
    parser.add_argument("--data", type=str, default="data/yolo/data.yaml", help="Path to data.yaml")
    parser.add_argument("--split", type=str, default="test", help="Split to evaluate on (test or val)")
    parser.add_argument("--name", type=str, default="yolov8s_eval", help="Experiment name")
    parser.add_argument("--project", type=str, default="outputs/yolo_eval", help="Project directory")
    return parser.parse_args()

def main():
    args = parse_args()
    print(f"Evaluating YOLOv8 checkpoint: {args.checkpoint}")
    
    if not Path(args.checkpoint).exists():
        print(f"Error: Checkpoint {args.checkpoint} not found.")
        sys.exit(1)
        
    model = YOLO(args.checkpoint)
    
    # 1. Evaluate on overall test set
    metrics = model.val(
        data=args.data,
        split=args.split,
        name=f"{args.name}_overall",
        project=args.project,
        save_json=True
    )
    
    save_dir = Path(args.project) / f"{args.name}_overall"
    # Fix #6: ensure output directory exists before writing JSON
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Extract metrics
    results = {
        "mAP50": float(metrics.box.map50),
        "mAP50-95": float(metrics.box.map),
        "precision": float(metrics.box.mp),
        "recall": float(metrics.box.mr),
        "f1": float(metrics.box.f1.mean()) if hasattr(metrics.box, 'f1') else 0, # Depending on ultralytics version
        "inference_speed_ms": metrics.speed.get("inference", 0),
        "fps": 1000.0 / metrics.speed.get("inference", 1) if metrics.speed.get("inference", 0) > 0 else 0
    }
    
    # Per-class AP
    per_class_ap = metrics.box.maps
    class_indices = metrics.box.ap_class_index
    
    results["per_class"] = {}
    for i, class_idx in enumerate(class_indices):
        class_name = model.names[class_idx]
        results["per_class"][class_name] = {
            "mAP50-95": float(per_class_ap[i])
        }
    
    with open(save_dir / "evaluation_metrics.json", "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"Overall evaluation completed. Metrics saved to {save_dir / 'evaluation_metrics.json'}")
    
    # TODO: Implement evaluate separately on small, medium, large damage instances
    # This requires parsing the ground truth and filtering instances by size before eval
    # or modifying the pycocotools evaluation parameters to match COCO area ranges.
    print("Note: Small/Medium/Large size bucket evaluation will be implemented using COCO-eval backend.")

if __name__ == "__main__":
    main()
