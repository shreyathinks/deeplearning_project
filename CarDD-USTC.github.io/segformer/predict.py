import os
import torch
import cv2
import numpy as np
# Fix #4: SegformerFeatureExtractor is deprecated — use SegformerImageProcessor
from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation
import argparse
from pathlib import Path
import torch.nn as nn

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=str, required=True, help="Path to best model dir")
    parser.add_argument("--image", type=str, required=True, help="Path to input image")
    parser.add_argument("--out", type=str, default="outputs/segformer_predict", help="Output directory")
    return parser.parse_args()

def main():
    args = parse_args()
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Fix #4: use SegformerImageProcessor instead of deprecated SegformerFeatureExtractor
    feature_extractor = SegformerImageProcessor.from_pretrained(args.checkpoint)
    model = SegformerForSemanticSegmentation.from_pretrained(args.checkpoint)
    model.to(device)
    model.eval()
    
    image_bgr = cv2.imread(args.image)
    if image_bgr is None:
        print(f"Error loading {args.image}")
        return
        
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    
    inputs = feature_extractor(images=image_rgb, return_tensors="pt")
    pixel_values = inputs.pixel_values.to(device)
    
    with torch.no_grad():
        outputs = model(pixel_values=pixel_values)
        logits = outputs.logits
        
    upsampled_logits = nn.functional.interpolate(
        logits, size=image_rgb.shape[:2], mode="bilinear", align_corners=False
    )
    
    pred_mask = upsampled_logits.argmax(dim=1).squeeze().cpu().numpy().astype(np.uint8)
    
    # Save output
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    base_name = Path(args.image).name
    cv2.imwrite(str(out_dir / f"mask_{base_name}"), pred_mask * 255)
    print(f"Saved prediction to {out_dir / f'mask_{base_name}'}")

if __name__ == "__main__":
    main()
