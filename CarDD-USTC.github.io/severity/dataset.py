import os
import cv2
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset
from pathlib import Path

class SeverityDataset(Dataset):
    def __init__(self, manifest_path, img_dir, split="train", transform=None, labels_map=None):
        self.img_dir = Path(img_dir)
        self.transform = transform
        
        # Load manifest
        df = pd.read_csv(manifest_path)

        # Fix #10: allow split=None to load the full dataset for building the global labels_map
        if split is not None:
            df = df[df['split'] == split].copy()
        else:
            df = df.copy()
        
        # Filter out rows with NULL severity
        self.df = df.dropna(subset=['severity_label'])
        
        # Fix #10: accept an externally-provided labels_map so all splits share the same encoding.
        # If not provided, build from this subset (backwards compatible for standalone use).
        if labels_map is not None:
            self.labels_map = labels_map
        else:
            self.labels_map = {
                label: i for i, label in enumerate(sorted(self.df['severity_label'].unique()))
            }
        self.num_classes = len(self.labels_map)
        
        # Feature columns
        self.feature_cols = [
            "num_detected_damages", "num_damage_types", "total_damage_area",
            "total_damage_area_ratio", "largest_damage_area", "largest_damage_area_ratio",
            "mean_damage_area", "max_detection_confidence", "mean_detection_confidence"
        ]
        
    def get_class_weights(self):
        counts = self.df['severity_label'].value_counts().to_dict()
        total = sum(counts.values())
        # Fix: order weights by labels_map index (not alphabetical sort of counts.keys())
        # so that weight[i] correctly corresponds to class index i as encoded by labels_map
        idx_to_label = {v: k for k, v in self.labels_map.items()}
        weights = [total / counts[idx_to_label[i]] for i in range(len(self.labels_map))]
        weights = torch.FloatTensor(weights)
        weights = weights / weights.sum() * self.num_classes
        return weights

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        file_name = row['file_name']
        # split column may be 'train', 'val', or 'test' — use it for the sub-directory path.
        # When split=None was used for labels_map construction, __getitem__ should never be
        # called on that instance (it has no meaningful image paths), but guard anyway.
        split_name = row.get('split', '') if isinstance(row, dict) else row['split']
        img_path = self.img_dir / f"{split_name}2017" / file_name
        
        image = cv2.imread(str(img_path))
        if image is None:
            raise FileNotFoundError(f"Failed to read image at {img_path}")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Use damage-focused image if OOF masks are pre-generated, else fall back to full image
        mask_path = self.img_dir / "masks" / file_name
        if mask_path.exists():
            mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
            if mask is not None:
                mask_bool = mask > 127
                # Fix: cast to uint8 before multiply to avoid silent dtype promotion
                image = (image * mask_bool[..., None]).astype(np.uint8)
            
        if self.transform:
            image = self.transform(image=image)["image"]
        
        # Extract engineered features
        features = row[self.feature_cols].values.astype(np.float32)
        features = torch.tensor(features, dtype=torch.float32)
        
        # Label — guaranteed consistent across splits via shared labels_map
        label_str = row['severity_label']
        label = self.labels_map[label_str]
        
        return image, features, label
