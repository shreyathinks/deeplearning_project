import os
import cv2
import numpy as np
import torch
import json
import argparse
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))      # Fix #1: allow bare imports from pipeline/
sys.path.append(str(Path(__file__).parent.parent))  # allow imports from project root

from detector import DamageDetector
from segmenter import DamageSegmenter
from severity.model import SeverityClassifier
from explainability.gradcam import ModelWrapper
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
import albumentations as A
from albumentations.pytorch import ToTensorV2

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, required=True, help="Path to input image")
    parser.add_argument("--yolo-checkpoint", type=str, required=True, help="Path to YOLO best.pt")
    parser.add_argument("--segformer-checkpoint", type=str, required=True, help="Path to SegFormer best model")
    parser.add_argument("--severity-checkpoint", type=str, required=True, help="Path to Severity best_severity.pt")
    parser.add_argument("--output-dir", type=str, default="outputs/inference/", help="Output directory")
    return parser.parse_args()

def calculate_features(detections, full_mask, image_shape):
    """
    Calculate engineered features.
    """
    h, w = image_shape[:2]
    total_area_pixels = np.sum(full_mask > 0)
    
    features = {
        "num_detected_damages": len(detections),
        "num_damage_types": len(set([d["class_id"] for d in detections])),
        "total_damage_area": total_area_pixels,
        "total_damage_area_ratio": total_area_pixels / (h * w),
        "largest_damage_area": max([d.get("area_pixels", 0) for d in detections]) if detections else 0,
        "largest_damage_area_ratio": max([d.get("area_ratio", 0) for d in detections]) if detections else 0,
        "mean_damage_area": np.mean([d.get("area_pixels", 0) for d in detections]) if detections else 0,
        "max_detection_confidence": max([d["confidence"] for d in detections]) if detections else 0,
        "mean_detection_confidence": np.mean([d["confidence"] for d in detections]) if detections else 0,
    }
    
    # Return as a 1x9 tensor for the model
    tensor_feat = torch.tensor([list(features.values())], dtype=torch.float32)
    return features, tensor_feat

def main():
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    img_name = Path(args.image).stem
    out_dir = Path(args.output_dir) / img_name
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load image
    image_bgr = cv2.imread(args.image)
    if image_bgr is None:
        raise FileNotFoundError(f"Failed to read image at {args.image}")
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    h, w = image_rgb.shape[:2]
    
    # 2. Initialize models
    detector = DamageDetector(args.yolo_checkpoint)
    segmenter = DamageSegmenter(args.segformer_checkpoint)
    
    severity_model = SeverityClassifier(num_classes=3, num_engineered_features=9)
    severity_model.load_state_dict(
        torch.load(args.severity_checkpoint, map_location=device, weights_only=True)
    )
    severity_model.to(device)
    severity_model.eval()
    
    # 3. YOLOv8 detection
    detections = detector.detect(image_bgr)
    
    # JSON structure setup
    report = {
        "image": Path(args.image).name,
        "status": "NO_DAMAGE_DETECTED" if not detections else "damage_detected",
        "severity": None,
        "damages": [],
        "explainability": None
    }
    
    # Visualization setup
    vis_detect = image_bgr.copy()
    vis_seg = image_bgr.copy()
    full_mask = np.zeros((h, w), dtype=np.uint8)
    
    if detections:
        # 4 & 5. Crop each detected ROI & SegFormer mask prediction
        for det in detections:
            bbox = det["bbox"]
            cls_name = det["damage_type"]
            conf = det["confidence"]
            
            # Draw bbox on detection vis
            cv2.rectangle(vis_detect, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
            cv2.putText(vis_detect, f"{cls_name} {conf:.2f}", (bbox[0], bbox[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Segment
            mask = segmenter.segment_roi(image_rgb, bbox)
            
            # 6. Map masks to original image
            full_mask = np.maximum(full_mask, mask)
            
            # Add mask visualization
            colored_mask = np.zeros_like(image_bgr)
            colored_mask[mask > 0] = (0, 0, 255)  # Red for damage
            vis_seg = cv2.addWeighted(vis_seg, 1.0, colored_mask, 0.5, 0)
            
            # Update detection info
            area_pixels = int(np.sum(mask > 0))
            det["area_pixels"] = area_pixels
            det["area_ratio"] = area_pixels / (h * w)
            det["mask_path"] = str(out_dir / f"mask_{len(report['damages'])}.png")
            
            cv2.imwrite(det["mask_path"], mask * 255)
            report["damages"].append(det)
            
        # 7. Calculate damage features
        feat_dict, tensor_feat = calculate_features(report["damages"], full_mask, image_rgb.shape)
        tensor_feat = tensor_feat.to(device)
        
        # 8. Create damage-focused image
        mask_bool = full_mask > 0
        focused_image = image_rgb * mask_bool[..., None]
        
        transform = A.Compose([
            A.Resize(224, 224),
            A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
            ToTensorV2(),
        ])
        
        input_tensor = transform(image=focused_image)["image"].unsqueeze(0).to(device)
        
        # 9. Severity prediction
        with torch.no_grad():
            logits = severity_model(input_tensor, tensor_feat)
            prob = torch.softmax(logits, dim=1)[0]
            pred_class = logits.argmax(dim=1).item()
            confidence = prob[pred_class].item()
            
        # Load dynamic labels map — Fix #7: warn loudly if not found instead of silently using wrong defaults
        labels_path = Path(args.severity_checkpoint).parent / "labels_map.json"
        if labels_path.exists():
            with open(labels_path, "r") as f:
                label_name_to_idx = json.load(f)
                severity_labels = {v: k for k, v in label_name_to_idx.items()}
        else:
            # Fallback: alphabetical order matches SeverityDataset's sorted() behaviour
            # i.e. High=0, Low=1, Medium=2. Warn the user so they know.
            print(
                f"[WARNING] labels_map.json not found at {labels_path}. "
                "Using alphabetical fallback {0:'High', 1:'Low', 2:'Medium'}. "
                "Retrain and ensure labels_map.json is saved alongside the checkpoint."
            )
            severity_labels = {0: "High", 1: "Low", 2: "Medium"}
        
        report["severity"] = {
            "label": severity_labels.get(pred_class, "Unknown"),
            "confidence": float(confidence)
        }
        
        # 10. Grad-CAM
        # Fix #13: overlay GradCAM on the clean original image, then composite with detection boxes
        wrapper = ModelWrapper(severity_model, tensor_feat)
        target_layers = [severity_model.backbone.layer4[-1]]
        cam = GradCAM(model=wrapper, target_layers=target_layers)
        
        grayscale_cam = cam(input_tensor=input_tensor, targets=None)[0, :]
        grayscale_cam_resized = cv2.resize(grayscale_cam, (w, h))
        
        image_float = np.float32(image_rgb) / 255
        cam_image = show_cam_on_image(image_float, grayscale_cam_resized, use_rgb=True)
        cam_bgr = cv2.cvtColor(cam_image, cv2.COLOR_RGB2BGR)
        
        gradcam_path = str(out_dir / "gradcam.jpg")
        cv2.imwrite(gradcam_path, cam_bgr)
        report["explainability"] = {"gradcam_path": gradcam_path}
        
        # 11. Generate final visual report
        # Fix #13: blend GradCAM with CLEAN original, then draw detection boxes on top
        final_vis = cv2.addWeighted(image_bgr, 0.5, cam_bgr, 0.5, 0)
        for det in report["damages"]:
            bbox = det["bbox"]
            cls_name = det["damage_type"]
            conf = det["confidence"]
            cv2.rectangle(final_vis, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
            cv2.putText(final_vis, f"{cls_name} {conf:.2f}", (bbox[0], bbox[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(final_vis,
                    f"Severity: {report['severity']['label']} ({confidence:.2f})",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        cv2.imwrite(str(out_dir / "final_visualization.jpg"), final_vis)
    else:
        # Save default images if no detection to prevent 404 errors in app
        cv2.imwrite(str(out_dir / "final_visualization.jpg"), image_bgr)
        blank_cam = np.zeros_like(image_bgr)
        cv2.imwrite(str(out_dir / "gradcam.jpg"), blank_cam)
        report["explainability"] = {"gradcam_path": str(out_dir / "gradcam.jpg")}
        
    cv2.imwrite(str(out_dir / "original.jpg"), image_bgr)
    cv2.imwrite(str(out_dir / "detection.jpg"), vis_detect)
    cv2.imwrite(str(out_dir / "segmentation.jpg"), vis_seg)
    
    # 12. Generate JSON report
    with open(out_dir / "prediction.json", "w") as f:
        json.dump(report, f, indent=4)
        
    print(f"Pipeline finished. Output saved to {out_dir}")

if __name__ == "__main__":
    main()
