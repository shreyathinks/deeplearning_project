import os
import json
import shutil
from pathlib import Path
import yaml

def convert_coco_to_yolo(coco_dir="data/CarDD_COCO", yolo_dir="data/yolo"):
    coco_dir = Path(coco_dir)
    yolo_dir = Path(yolo_dir)
    
    splits = {"train2017": "train", "val2017": "val", "test2017": "test"}
    
    # Create output directories
    for split in splits.values():
        (yolo_dir / "images" / split).mkdir(parents=True, exist_ok=True)
        (yolo_dir / "labels" / split).mkdir(parents=True, exist_ok=True)
        
    class_names = {}
    total_coco_anns = 0
    total_yolo_anns = 0
    
    for coco_split, yolo_split in splits.items():
        ann_file = coco_dir / "annotations" / f"instances_{coco_split}.json"
        img_dir = coco_dir / coco_split
        
        if not ann_file.exists():
            continue
            
        with open(ann_file, "r") as f:
            coco_data = json.load(f)
            
        # Extract categories
        if not class_names:
            for cat in coco_data["categories"]:
                # YOLO uses 0-indexed classes
                # Original CarDD COCO format typically starts at 1
                class_names[cat["id"] - 1] = cat["name"] 
                
        imgs_by_id = {img["id"]: img for img in coco_data["images"]}
        
        total_coco_anns += len(coco_data["annotations"])
        
        # Group annotations by image
        anns_by_img = {}
        for ann in coco_data["annotations"]:
            img_id = ann["image_id"]
            if img_id not in anns_by_img:
                anns_by_img[img_id] = []
            anns_by_img[img_id].append(ann)
            
        for img_id, img_info in imgs_by_id.items():
            file_name = img_info["file_name"]
            width = img_info["width"]
            height = img_info["height"]
            
            # Copy image (using symlink if possible to save space, else copy)
            src_img = img_dir / file_name
            dst_img = yolo_dir / "images" / yolo_split / file_name
            if src_img.exists() and not dst_img.exists():
                try:
                    os.symlink(src_img.absolute(), dst_img.absolute())
                except OSError:
                    shutil.copy2(src_img, dst_img)
                    
            # Write labels
            label_file = yolo_dir / "labels" / yolo_split / f"{Path(file_name).stem}.txt"
            anns = anns_by_img.get(img_id, [])
            
            with open(label_file, "w") as f:
                for ann in anns:
                    bbox = ann["bbox"] # [x, y, w, h]
                    x_center = (bbox[0] + bbox[2] / 2) / width
                    y_center = (bbox[1] + bbox[3] / 2) / height
                    w = bbox[2] / width
                    h = bbox[3] / height
                    
                    # Ensure coordinates are within [0, 1]
                    x_center = max(0, min(1, x_center))
                    y_center = max(0, min(1, y_center))
                    w = max(0, min(1, w))
                    h = max(0, min(1, h))
                    
                    # 0-indexed class ID
                    cls_id = ann["category_id"] - 1 
                    
                    f.write(f"{cls_id} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}\n")
                    total_yolo_anns += 1
                    
    # Create data.yaml
    yaml_data = {
        "path": str(yolo_dir.absolute()),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "names": {k: v for k, v in sorted(class_names.items())}
    }
    
    with open(yolo_dir / "data.yaml", "w") as f:
        yaml.dump(yaml_data, f, sort_keys=False)
        
    print(f"COCO annotations: {total_coco_anns}")
    print(f"YOLO annotations: {total_yolo_anns}")
    assert total_coco_anns == total_yolo_anns, "Mismatch in annotation counts!"
    print("Successfully converted dataset to YOLO format.")

if __name__ == "__main__":
    convert_coco_to_yolo()
