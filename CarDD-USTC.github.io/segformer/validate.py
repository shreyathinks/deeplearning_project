import os
import torch
import numpy as np
import evaluate
from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation
import sys
from pathlib import Path

# Fix #3: ensure segformer/ is importable when run from any directory
sys.path.insert(0, str(Path(__file__).parent))

from dataset import SegFormerDataset
from torch.utils.data import DataLoader
import argparse
import json
from tqdm import tqdm
import torch.nn as nn

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=str, required=True, help="Path to best model dir")
    parser.add_argument("--data_dir", type=str, default="data/segformer")
    parser.add_argument("--split", type=str, default="test")
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--project", type=str, default="outputs/segformer_eval")
    parser.add_argument("--name", type=str, default="eval")
    return parser.parse_args()

def main():
    args = parse_args()
    print(f"Evaluating SegFormer checkpoint: {args.checkpoint} on split: {args.split}")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    feature_extractor = SegformerImageProcessor.from_pretrained(args.checkpoint)
    model = SegformerForSemanticSegmentation.from_pretrained(args.checkpoint)
    model.to(device)
    model.eval()
    
    eval_dataset = SegFormerDataset(args.data_dir, split=args.split, feature_extractor=feature_extractor)

    # Fix #18: add num_workers and pin_memory for better throughput
    dataloader = DataLoader(eval_dataset, batch_size=args.batch, shuffle=False,
                            num_workers=2, pin_memory=True)
    
    metric_iou = evaluate.load("mean_iou")
    
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating"):
            pixel_values = batch["pixel_values"].to(device)
            labels = batch["labels"].to(device)
            
            outputs = model(pixel_values=pixel_values)
            logits = outputs.logits
            
            upsampled_logits = nn.functional.interpolate(
                logits, size=labels.shape[-2:], mode="bilinear", align_corners=False
            )
            
            preds = upsampled_logits.argmax(dim=1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
    # Compute metrics
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    
    metrics = metric_iou.compute(
        predictions=all_preds,
        references=all_labels,
        num_labels=2,
        ignore_index=255,
        reduce_labels=False
    )
    
    results = {
        "mean_iou": metrics["mean_iou"],
        "mean_accuracy": metrics["mean_accuracy"],
        "iou_damage": metrics["per_category_iou"][1] if len(metrics["per_category_iou"]) > 1 else 0,
        "iou_background": metrics["per_category_iou"][0],
        "accuracy_damage": metrics["per_category_accuracy"][1] if len(metrics["per_category_accuracy"]) > 1 else 0,
        "accuracy_background": metrics["per_category_accuracy"][0]
    }
    
    out_dir = Path(args.project) / args.name
    out_dir.mkdir(parents=True, exist_ok=True)
    
    with open(out_dir / "segmentation_metrics.json", "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"Evaluation complete. Metrics saved to {out_dir / 'segmentation_metrics.json'}")

if __name__ == "__main__":
    main()
