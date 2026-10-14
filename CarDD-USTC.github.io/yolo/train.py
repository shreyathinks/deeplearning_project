import os
import sys
import json
import torch
import shutil
import argparse
from pathlib import Path
from ultralytics import YOLO
import datetime

def parse_args():
    parser = argparse.ArgumentParser(description="Train YOLOv8 on CarDD dataset")
    parser.add_argument("--config", type=str, default="configs/yolo/yolov8s.yaml", help="Path to config file")
    parser.add_argument("--model", type=str, default="yolov8s.pt", help="Base model to load")
    parser.add_argument("--data", type=str, default="data/yolo/data.yaml", help="Path to data.yaml")
    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--name", type=str, default="yolov8s_v1", help="Experiment name")
    parser.add_argument("--project", type=str, default="outputs/yolo", help="Project directory")
    return parser.parse_args()

def save_experiment_config(args, save_dir):
    config = {
        "random_seed": args.seed,
        "python_version": sys.version,
        "pytorch_version": torch.__version__,
        "cuda_version": torch.version.cuda if torch.cuda.is_available() else "None",
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None",
        "ultralytics_version": __import__('ultralytics').__version__,
        "dataset_manifest_version": "v1",
        "model_configuration": args.model,
        "training_parameters": vars(args),
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    with open(Path(save_dir) / "experiment_config.json", "w") as f:
        json.dump(config, f, indent=4)

def main():
    args = parse_args()
    print(f"Starting YOLOv8 training: {args.name}")
    
    # 1. Load pretrained YOLOv8 weights
    model = YOLO(args.model)
    
    # 3. Set deterministic seed (handled partly by Ultralytics internally via deterministic=True, but we ensure it)
    
    # 4 & 5. Train using train split and validate on validation split
    # Ultralytics natively reads train/val splits from the data.yaml
    results = model.train(
        data=args.data,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        seed=args.seed,
        name=args.name,
        project=args.project,
        deterministic=True,
        save=True,        # 6. Save best checkpoint
        plots=True,       # 7. Save training curves
        val=True          # validate
    )
    
    # Determine the directory where ultralytics saved the results
    # The train() method returns a dictionary/object, or we can just get the save_dir from model.trainer
    save_dir = Path(model.trainer.save_dir) if hasattr(model, 'trainer') and model.trainer else Path(args.project) / args.name
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # 8. Save metrics and configs
    save_experiment_config(args, save_dir)
    
    # Write a summary metrics file based on the ultralytics results.csv
    results_csv = save_dir / "results.csv"
    if results_csv.exists():
        import pandas as pd
        df = pd.read_csv(results_csv)
        df.columns = df.columns.str.strip()
        last_epoch = df.iloc[-1]
        
        metrics = {
            "mAP50": float(last_epoch.get("metrics/mAP50(B)", 0)),
            "mAP50-95": float(last_epoch.get("metrics/mAP50-95(B)", 0)),
            "precision": float(last_epoch.get("metrics/precision(B)", 0)),
            "recall": float(last_epoch.get("metrics/recall(B)", 0)),
            "fitness": float(last_epoch.get("fitness", 0))
        }
        
        with open(save_dir / "metrics.json", "w") as f:
            json.dump(metrics, f, indent=4)
            
    print(f"Training completed. Checkpoints and logs saved to {save_dir}")

if __name__ == "__main__":
    main()
