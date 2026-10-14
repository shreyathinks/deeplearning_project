import os
import cv2
import numpy as np
from pathlib import Path
from torch.utils.data import Dataset

class SegFormerDataset(Dataset):
    def __init__(self, data_dir, split="train", transform=None, feature_extractor=None):
        self.data_dir = Path(data_dir) / split
        self.img_dir = self.data_dir / "images"
        self.mask_dir = self.data_dir / "masks"
        self.transform = transform
        self.feature_extractor = feature_extractor
        
        self.images = sorted([f for f in os.listdir(self.img_dir) if f.endswith('.png') or f.endswith('.jpg')])
        
    def __len__(self):
        return len(self.images)
        
    def __getitem__(self, idx):
        img_name = self.images[idx]
        img_path = self.img_dir / img_name
        mask_path = self.mask_dir / (Path(img_name).stem + '.png')
        
        image = cv2.imread(str(img_path))
        if image is None:
            raise FileNotFoundError(f"Failed to load image: {img_path}")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
        if mask is None:
            raise FileNotFoundError(f"Failed to load mask: {mask_path}")

        # Fix #11: verify that image and mask have matching spatial dimensions
        if image.shape[:2] != mask.shape[:2]:
            raise ValueError(
                f"Image and mask size mismatch for {img_name}: "
                f"image={image.shape[:2]}, mask={mask.shape[:2]}"
            )
        
        # Ensure mask is binary [0, 1]
        mask = (mask > 0).astype('int64')
        
        if self.transform is not None:
            # Assumes albumentations style transforms which take both image and mask
            augmented = self.transform(image=image, mask=mask)
            image = augmented['image']
            mask = augmented['mask']
            
        if self.feature_extractor is not None:
            # Huggingface feature extractor
            encoded = self.feature_extractor(image, segmentation_maps=mask, return_tensors="pt")
            # Remove batch dimension
            for k, v in encoded.items():
                encoded[k] = v.squeeze()
            return encoded
            
        return {"pixel_values": image, "labels": mask}
