import os
import torch
from torch.utils.data import DataLoader
import sys
from pathlib import Path

# Fix #2: ensure severity/ is importable when run from any directory
sys.path.insert(0, str(Path(__file__).parent))

from dataset import SeverityDataset
from model import SeverityClassifier
import argparse
import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, balanced_accuracy_score, confusion_matrix
import albumentations as A
from albumentations.pytorch import ToTensorV2

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=str, required=True, help="Path to best_severity.pt")
    parser.add_argument("--manifest", type=str, default="data/manifests/severity_manifest.csv")
    parser.add_argument("--img_dir", type=str, default="data/CarDD_COCO")
    parser.add_argument("--split", type=str, default="test")
    parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--project", type=str, default="outputs/severity_eval")
    parser.add_argument("--name", type=str, default="eval")
    return parser.parse_args()

def main():
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    val_transform = A.Compose([
        A.Resize(224, 224),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2(),
    ])

    # Fix #10: load shared labels_map from the checkpoint directory if available,
    # otherwise fall back to building from the full dataset.
    labels_map = None
    labels_map_path = Path(args.checkpoint).parent / "labels_map.json"
    if labels_map_path.exists():
        with open(labels_map_path, "r") as f:
            labels_map = json.load(f)
        print(f"Loaded labels_map from {labels_map_path}")
    else:
        print("[WARNING] labels_map.json not found. Building from full dataset — may be inconsistent.")
        full_ds = SeverityDataset(args.manifest, args.img_dir, split=None)
        labels_map = full_ds.labels_map

    dataset = SeverityDataset(args.manifest, args.img_dir, split=args.split,
                              transform=val_transform, labels_map=labels_map)

    # Fix #18: add num_workers and pin_memory for consistent perf with training
    dataloader = DataLoader(dataset, batch_size=args.batch, shuffle=False,
                            num_workers=2, pin_memory=True)
    
    model = SeverityClassifier(num_classes=dataset.num_classes)
    # Fix #22: weights_only=True to suppress FutureWarning
    model.load_state_dict(torch.load(args.checkpoint, map_location=device, weights_only=True))
    model.to(device)
    model.eval()
    
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for images, features, labels in dataloader:
            images = images.to(device)
            features = features.to(device)
            
            logits = model(images, features)
            preds = logits.argmax(dim=1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())
            
    # Metrics
    acc = accuracy_score(all_labels, all_preds)
    bal_acc = balanced_accuracy_score(all_labels, all_preds)
    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
        all_labels, all_preds, average='macro')
    precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(
        all_labels, all_preds, average='weighted')
    
    metrics = {
        "accuracy": acc,
        "balanced_accuracy": bal_acc,
        "macro_precision": precision_macro,
        "macro_recall": recall_macro,
        "macro_f1": f1_macro,
        "weighted_precision": precision_weighted,
        "weighted_recall": recall_weighted,
        "weighted_f1": f1_weighted
    }
    
    out_dir = Path(args.project) / args.name
    out_dir.mkdir(parents=True, exist_ok=True)
    
    with open(out_dir / "severity_metrics.json", "w") as f:
        json.dump(metrics, f, indent=4)
        
    # Confusion Matrix
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(8, 6))
    class_names = [k for k, v in sorted(dataset.labels_map.items(), key=lambda item: item[1])]
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names)
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Severity Confusion Matrix')
    plt.savefig(out_dir / "confusion_matrix.png")
    plt.close()
    
    print(f"Evaluation complete. Metrics saved to {out_dir}")

if __name__ == "__main__":
    main()
