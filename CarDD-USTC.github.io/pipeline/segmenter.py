import torch
import cv2
import numpy as np
from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation
import torch.nn as nn

class DamageSegmenter:
    def __init__(self, checkpoint_path, target_size=(224, 224), padding=0.1):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.feature_extractor = SegformerImageProcessor.from_pretrained(checkpoint_path)
        self.model = SegformerForSemanticSegmentation.from_pretrained(checkpoint_path)
        self.model.to(self.device)
        self.model.eval()
        self.target_size = target_size
        self.padding = padding
        
    def segment_roi(self, image_rgb, bbox):
        """
        Extracts the ROI, runs SegFormer, and returns the binary mask in the original image coordinate space.
        bbox: [x1, y1, x2, y2]
        """
        h, w = image_rgb.shape[:2]
        x1, y1, x2, y2 = bbox
        
        bw = x2 - x1
        bh = y2 - y1
        
        pad_x = int(bw * self.padding)
        pad_y = int(bh * self.padding)
        
        cx1 = max(0, x1 - pad_x)
        cy1 = max(0, y1 - pad_y)
        cx2 = min(w, x2 + pad_x)
        cy2 = min(h, y2 + pad_y)
        
        crop_img = image_rgb[cy1:cy2, cx1:cx2]
        if crop_img.size == 0:
            return np.zeros((h, w), dtype=np.uint8)
            
        crop_resized = cv2.resize(crop_img, self.target_size, interpolation=cv2.INTER_LINEAR)
        
        inputs = self.feature_extractor(images=crop_resized, return_tensors="pt")
        pixel_values = inputs.pixel_values.to(self.device)
        
        with torch.no_grad():
            outputs = self.model(pixel_values=pixel_values)
            logits = outputs.logits
            
        upsampled_logits = nn.functional.interpolate(
            logits, size=self.target_size, mode="bilinear", align_corners=False
        )
        
        pred_mask_resized = upsampled_logits.argmax(dim=1).squeeze().cpu().numpy().astype(np.uint8)
        
        # Resize back to crop size
        crop_h, crop_w = crop_img.shape[:2]
        pred_mask_crop = cv2.resize(pred_mask_resized, (crop_w, crop_h), interpolation=cv2.INTER_NEAREST)
        
        # Place into full image mask
        full_mask = np.zeros((h, w), dtype=np.uint8)
        full_mask[cy1:cy2, cx1:cx2] = pred_mask_crop
        
        # Post-processing: keep only mask pixels that are actually inside the original bbox (optional, based on Phase 13)
        # We can also do morphological cleanup here.
        
        return full_mask
