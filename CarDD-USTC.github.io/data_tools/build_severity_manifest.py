import os
import pandas as pd
import json
from pathlib import Path
import argparse

def build_severity_manifest(coco_dir="data/CarDD_COCO", manifest_path="data/manifests/cardd_manifest.csv", out_path="data/manifests/severity_manifest.csv"):
    """
    Builds a severity dataset combining image-level severity and out-of-fold/frozen features.
    For this initial phase, we will just prepare the structure and integrate the metadata.
    """
    manifest_df = pd.read_csv(manifest_path)
    
    # We expect features to be generated later and merged here, or computed dynamically.
    # We will initialize placeholder columns for features.
    
    feature_cols = [
        "num_detected_damages",
        "num_damage_types",
        "total_damage_area",
        "total_damage_area_ratio",
        "largest_damage_area",
        "largest_damage_area_ratio",
        "mean_damage_area",
        "max_detection_confidence",
        "mean_detection_confidence"
    ]
    
    for col in feature_cols:
        manifest_df[col] = 0.0
        
    manifest_df.to_csv(out_path, index=False)
    print(f"Created severity manifest at {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--coco_dir", type=str, default="data/CarDD_COCO")
    parser.add_argument("--manifest", type=str, default="data/manifests/cardd_manifest.csv")
    parser.add_argument("--out", type=str, default="data/manifests/severity_manifest.csv")
    args = parser.parse_args()
    
    build_severity_manifest(args.coco_dir, args.manifest, args.out)
