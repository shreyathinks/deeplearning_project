import os
import argparse
from pathlib import Path
from ultralytics import YOLO

def parse_args():
    parser = argparse.ArgumentParser(description="Predict using YOLOv8 on CarDD dataset")
    parser.add_argument("--checkpoint", type=str, required=True, help="Path to best.pt")
    parser.add_argument("--source", type=str, required=True, help="Path to image or directory")
    parser.add_argument("--project", type=str, default="outputs/yolo_predict", help="Project directory")
    parser.add_argument("--name", type=str, default="exp", help="Experiment name")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    parser.add_argument("--save-txt", action="store_true", help="Save results to txt")
    parser.add_argument("--save-conf", action="store_true", help="Save confidences in txt")
    return parser.parse_args()

def main():
    args = parse_args()
    print(f"Running inference with checkpoint: {args.checkpoint} on {args.source}")
    
    model = YOLO(args.checkpoint)
    
    results = model.predict(
        source=args.source,
        project=args.project,
        name=args.name,
        conf=args.conf,
        save=True,          # Save plotted images
        save_txt=args.save_txt,
        save_conf=args.save_conf
    )
    
    print(f"Inference completed. Results saved to {Path(args.project) / args.name}")

if __name__ == "__main__":
    main()
