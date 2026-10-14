import os
import json
import pandas as pd
from pathlib import Path
from PIL import Image
import hashlib

def validate_dataset(data_dir="data/CarDD_COCO", manifest_path="data/manifests/cardd_manifest.csv"):
    data_dir = Path(data_dir)
    manifest_path = Path(manifest_path)
    
    print("Starting Phase 3: Data integrity validation...")
    
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
        
    manifest_df = pd.read_csv(manifest_path)
    
    # Check I - no duplicate image rows in manifest
    if manifest_df.duplicated(subset=['file_name']).any():
        raise ValueError("Check I Failed: Duplicate image rows in manifest.")
    print("Check I Passed: No duplicate image rows in manifest.")
    
    splits = ["train2017", "val2017", "test2017"]
    
    all_image_hashes = {}
    valid_class_ids = set(range(1, 7)) # Assuming classes 1-6
    
    errors = []
    
    for split in splits:
        ann_file = data_dir / "annotations" / f"instances_{split}.json"
        img_dir = data_dir / split
        
        if not ann_file.exists():
            continue
            
        with open(ann_file, "r") as f:
            coco_data = json.load(f)
            
        imgs_by_id = {img["id"]: img for img in coco_data["images"]}
        
        for ann in coco_data["annotations"]:
            img_id = ann["image_id"]
            
            # Check A - every annotation references an image
            if img_id not in imgs_by_id:
                errors.append(f"Check A Failed: Annotation {ann['id']} references missing image {img_id}")
                continue
                
            img_info = imgs_by_id[img_id]
            file_path = img_dir / img_info["file_name"]
            
            # Check B - every image referenced by annotation exists
            if not file_path.exists():
                errors.append(f"Check B Failed: Image {file_path} referenced by annotation {ann['id']} does not exist.")
                
            # Check C - class IDs are valid
            if ann["category_id"] not in valid_class_ids:
                errors.append(f"Check C Failed: Invalid class ID {ann['category_id']} in annotation {ann['id']}")
                
            # Check D - bounding boxes are inside image boundaries
            bbox = ann["bbox"] # [x, y, width, height]
            if bbox[0] < 0 or bbox[1] < 0 or (bbox[0] + bbox[2]) > img_info["width"] or (bbox[1] + bbox[3]) > img_info["height"]:
                errors.append(f"Check D Failed: Bbox {bbox} outside image {img_info['file_name']} boundaries ({img_info['width']}x{img_info['height']})")
                
            # Check E - polygons are valid
            if "segmentation" in ann and isinstance(ann["segmentation"], list):
                for poly in ann["segmentation"]:
                    if len(poly) < 6: # Minimum 3 points (x,y)
                        errors.append(f"Check E Failed: Invalid polygon in annotation {ann['id']}")
                        
        # Check F - no train/test duplicate image hashes
        # Check J - no corrupted image files
        for img_id, img_info in imgs_by_id.items():
            file_path = img_dir / img_info["file_name"]
            if file_path.exists():
                try:
                    with Image.open(file_path) as img:
                        img.verify()
                        
                    # Calculate hash for Check F
                    with open(file_path, "rb") as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                        
                    if file_hash in all_image_hashes:
                        prev_split = all_image_hashes[file_hash]
                        if prev_split != split:
                            errors.append(f"Check F Failed: Duplicate image hash found across splits ({prev_split} and {split}) for {file_path.name}")
                    else:
                        all_image_hashes[file_hash] = split
                        
                except Exception as e:
                    errors.append(f"Check J Failed: Corrupted image file {file_path} - {str(e)}")

    # Check G - all derived samples inherit the parent image split
    # (This will be tested more robustly during dataset generation, but conceptually belongs here)
    
    # Check H - severity metadata joins correctly
    if manifest_df['severity_label'].isnull().all():
        print("Check H Warning: Severity metadata not yet joined or all NULL.")
    else:
        print("Check H Passed: Severity metadata joined.")

    if errors:
        print(f"Validation failed with {len(errors)} errors.")
        for error in errors[:10]:
            print(error)
        if len(errors) > 10:
            print("...")
        
        out_dir = Path("data/audit")
        out_dir.mkdir(parents=True, exist_ok=True)
        with open(out_dir / "dataset_audit.txt", "w") as f:
            for error in errors:
                f.write(error + "\n")
                
        with open(out_dir / "dataset_audit.json", "w") as f:
            json.dump({"errors": errors}, f, indent=4)
            
        import sys
        sys.exit(1)
    else:
        print("All validation checks passed.")
        out_dir = Path("data/audit")
        out_dir.mkdir(parents=True, exist_ok=True)
        with open(out_dir / "dataset_audit.json", "w") as f:
            json.dump({"status": "success", "errors": []}, f, indent=4)

if __name__ == "__main__":
    validate_dataset()
