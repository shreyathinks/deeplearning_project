import torch
from ultralytics import YOLO

class DamageDetector:
    def __init__(self, checkpoint_path, conf_threshold=0.20):
        self.model = YOLO(checkpoint_path)
        self.conf_threshold = conf_threshold
        
    def detect(self, image_bgr):
        # Apply Test-Time Augmentation (augment=True) and upscale resolution (imgsz=1024)
        # to force the AI to look closer at small scratches.
        results = self.model(image_bgr, conf=self.conf_threshold, augment=True, imgsz=1024, verbose=False)[0]
        
        detections = []
        for box in results.boxes:
            cls_id = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            
            detections.append({
                "damage_type": self.model.names[cls_id],
                "class_id": cls_id,
                "confidence": conf,
                "bbox": [int(x1), int(y1), int(x2), int(y2)]
            })
            
        return detections
