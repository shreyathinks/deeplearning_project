import os
import json
import numpy as np
import cv2
from pathlib import Path

def build_segformer_dataset(coco_dir="data/CarDD_COCO", out_dir="data/segformer", padding=0.1, target_size=(224, 224)):
    coco_dir = Path(coco_dir)
    out_dir = Path(out_dir)
    splits = {"train2017": "train", "val2017": "val", "test2017": "test"}
    
    for split in splits.values():
        (out_dir / split / "images").mkdir(parents=True, exist_ok=True)
        (out_dir / split / "masks").mkdir(parents=True, exist_ok=True)
        
    for coco_split, target_split in splits.items():
        ann_file = coco_dir / "annotations" / f"instances_{coco_split}.json"
        img_dir = coco_dir / coco_split
        
        if not ann_file.exists():
            continue
            
        print(f"Processing {coco_split} -> {target_split}")
        with open(ann_file, "r") as f:
            coco_data = json.load(f)
            
        imgs_by_id = {img["id"]: img for img in coco_data["images"]}
        
        for ann in coco_data["annotations"]:
            if "segmentation" not in ann or not ann["segmentation"]:
                continue
                
            img_id = ann["image_id"]
            img_info = imgs_by_id[img_id]
            file_name = img_info["file_name"]
            img_path = img_dir / file_name
            
            if not img_path.exists():
                continue
                
            img = cv2.imread(str(img_path))
            if img is None:
                continue
                
            h, w = img.shape[:2]
            
            # Create full binary mask for this instance
            mask = np.zeros((h, w), dtype=np.uint8)
            for poly in ann["segmentation"]:
                pts = np.array(poly, np.int32).reshape((-1, 1, 2))
                cv2.fillPoly(mask, [pts], 255)
                
            # Bounding box
            bx, by, bw, bh = ann["bbox"]
            bx, by, bw, bh = int(bx), int(by), int(bw), int(bh)
            
            # Add padding
            pad_x = int(bw * padding)
            pad_y = int(bh * padding)
            
            x1 = max(0, bx - pad_x)
            y1 = max(0, by - pad_y)
            x2 = min(w, bx + bw + pad_x)
            y2 = min(h, by + bh + pad_y)
            
            # Crop
            crop_img = img[y1:y2, x1:x2]
            crop_mask = mask[y1:y2, x1:x2]
            
            # Resize
            if crop_img.size == 0 or crop_mask.size == 0:
                continue
                
            crop_img = cv2.resize(crop_img, target_size, interpolation=cv2.INTER_LINEAR)
            crop_mask = cv2.resize(crop_mask, target_size, interpolation=cv2.INTER_NEAREST)
            
            # Save
            ann_id = ann["id"]
            base_name = Path(file_name).stem
            save_name = f"{base_name}_inst_{ann_id}.png"
            
            cv2.imwrite(str(out_dir / target_split / "images" / save_name), crop_img)
            cv2.imwrite(str(out_dir / target_split / "masks" / save_name), crop_mask)
            
    print("Finished building SegFormer dataset.")

if __name__ == "__main__":
    build_segformer_dataset()
