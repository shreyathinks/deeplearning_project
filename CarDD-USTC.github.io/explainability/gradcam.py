import os
import cv2
import numpy as np
import torch
import argparse
from pathlib import Path
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
import sys

# Ensure severity package is in path
sys.path.append(str(Path(__file__).parent.parent))
try:
    from severity.model import SeverityClassifier
except ImportError:
    pass

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, required=True, help="Path to input image")
    parser.add_argument("--mask", type=str, required=True, help="Path to input binary damage mask")
    parser.add_argument("--checkpoint", type=str, required=True, help="Path to best_severity.pt")
    parser.add_argument("--target_class", type=int, default=None,
                        help="Target class index for Grad-CAM. If None, uses top prediction.")
    parser.add_argument("--out", type=str, default="outputs/explainability", help="Output directory")
    return parser.parse_args()

class ModelWrapper(torch.nn.Module):
    def __init__(self, model, features):
        super().__init__()
        self.model = model
        self.features = features
        
    def forward(self, x):
        return self.model(x, self.features)

def main():
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Load model
    model = SeverityClassifier(num_classes=3, num_engineered_features=9)
    # Fix #22: weights_only=True to suppress FutureWarning
    model.load_state_dict(torch.load(args.checkpoint, map_location=device, weights_only=True))
    model.to(device)
    model.eval()
    
    # Load image and mask
    image_bgr = cv2.imread(args.image)
    if image_bgr is None:
        raise ValueError(f"Could not load image: {args.image}")
        
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    
    mask = cv2.imread(args.mask, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise ValueError(f"Could not load mask: {args.mask}")
        
    # Create damage focused image
    mask_bool = mask > 127
    focused_image = image_rgb * mask_bool[..., None]
    
    # Transform
    import albumentations as A
    from albumentations.pytorch import ToTensorV2
    transform = A.Compose([
        A.Resize(224, 224),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2(),
    ])
    
    input_tensor = transform(image=focused_image)["image"].unsqueeze(0).to(device)
    
    # Fix #19 (standalone): approximate features from mask rather than hardcoded dummy values.
    # Counts are estimated as 1 detection since we have one mask; confidence defaults to 1.0
    # since we don't have YOLO output here.  These are documented approximations.
    area = int(np.sum(mask_bool))
    h, w = image_rgb.shape[:2]
    area_ratio = area / (h * w) if h * w > 0 else 0
    approx_features = torch.tensor(
        [[
            1,            # num_detected_damages (estimated: 1 mask provided)
            1,            # num_damage_types (estimated: 1 mask provided)
            area,         # total_damage_area
            area_ratio,   # total_damage_area_ratio
            area,         # largest_damage_area
            area_ratio,   # largest_damage_area_ratio
            float(area),  # mean_damage_area
            1.0,          # max_detection_confidence (unknown without YOLO, use 1.0)
            1.0,          # mean_detection_confidence (unknown without YOLO, use 1.0)
        ]],
        dtype=torch.float32
    ).to(device)
    
    # We need a wrapper because our model takes two inputs, but GradCAM expects one tensor
    wrapper = ModelWrapper(model, approx_features)
    
    # Target layer for ResNet18 is the last residual block
    target_layers = [model.backbone.layer4[-1]]
    
    cam = GradCAM(model=wrapper, target_layers=target_layers)
    
    targets = None
    if args.target_class is not None:
        targets = [ClassifierOutputTarget(args.target_class)]
        
    grayscale_cam = cam(input_tensor=input_tensor, targets=targets)
    grayscale_cam = grayscale_cam[0, :]
    
    # Resize grayscale_cam back to original image size
    grayscale_cam_resized = cv2.resize(grayscale_cam, (image_rgb.shape[1], image_rgb.shape[0]))
    
    # Overlay
    image_float = np.float32(image_rgb) / 255
    cam_image = show_cam_on_image(image_float, grayscale_cam_resized, use_rgb=True)
    
    # Save outputs
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    base_name = Path(args.image).stem
    
    cv2.imwrite(str(out_dir / f"{base_name}_original.png"), cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR))
    cv2.imwrite(str(out_dir / f"{base_name}_damage_mask.png"), mask)
    
    # Save raw heatmap coloring
    heatmap = cv2.applyColorMap(np.uint8(255 * grayscale_cam_resized), cv2.COLORMAP_JET)
    cv2.imwrite(str(out_dir / f"{base_name}_gradcam.png"), heatmap)
    
    # Save overlay
    cv2.imwrite(str(out_dir / f"{base_name}_overlay.png"), cv2.cvtColor(cam_image, cv2.COLOR_RGB2BGR))
    
    print(f"Explainability results saved to {out_dir}")

if __name__ == "__main__":
    main()
