import os
import json
import pandas as pd
from pathlib import Path
from glob import glob

def inspect_dataset(data_dir="data/CarDD_COCO"):
    data_dir = Path(data_dir)
    splits = ["train2017", "val2017", "test2017"]
    
    manifest_data = []
    
    # Locate severity excel file if exists
    excel_files = list(data_dir.parent.glob("*.xlsx")) + list(data_dir.glob("*.xlsx"))
    severity_df = None
    if excel_files:
        excel_path = excel_files[0]
        print(f"Found metadata excel: {excel_path}")
        severity_df = pd.read_excel(excel_path)
        # TODO: map actual columns after inspecting the excel file
    else:
        print("No metadata excel file found yet.")
    
    for split in splits:
        ann_file = data_dir / "annotations" / f"instances_{split}.json"
        img_dir = data_dir / split
        
        if not ann_file.exists():
            print(f"Missing {ann_file}")
            continue
            
        with open(ann_file, "r") as f:
            coco_data = json.load(f)
            
        # Create lookups
        imgs_by_id = {img["id"]: img for img in coco_data["images"]}
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
            
            anns = anns_by_img.get(img_id, [])
            num_instances = len(anns)
            categories = set(ann["category_id"] for ann in anns)
            num_categories = len(categories)
            
            # Calculate synthetic severity based on bbox areas
            total_area = 0
            max_area = 0
            
            for ann in anns:
                bbox = ann["bbox"] # [x, y, w, h]
                area = bbox[2] * bbox[3]
                total_area += area
                if area > max_area:
                    max_area = area
                    
            img_area = width * height
            total_damage_ratio = total_area / img_area
            max_damage_ratio = max_area / img_area
            
            # Synthetic Labeling Heuristic
            severity_label = "Medium"
            if total_damage_ratio > 0.15 or max_damage_ratio > 0.10 or num_instances > 5:
                severity_label = "High"
            elif total_damage_ratio < 0.05 and max_damage_ratio < 0.02 and num_instances <= 2:
                severity_label = "Low"
                
            shooting_angle = None # Placeholder or read from excel if desired
                
            manifest_data.append({
                "image_id": img_id,
                "file_name": file_name,
                "split": split.replace("2017", ""),
                "width": width,
                "height": height,
                "num_instances": num_instances,
                "num_categories": num_categories,
                "severity_raw": severity_label, # Synthetic raw maps directly
                "severity_label": severity_label,
                "shooting_angle": shooting_angle
            })

    out_dir = Path("data/manifests")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "cardd_manifest.csv"
    
    df = pd.DataFrame(manifest_data)
    df.to_csv(out_file, index=False)
    print(f"Saved manifest to {out_file} with {len(df)} entries.")

if __name__ == "__main__":
    inspect_dataset()
