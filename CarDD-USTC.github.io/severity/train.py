import os
import torch
import torch.nn as nn
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
import albumentations as A
from albumentations.pytorch import ToTensorV2
from tqdm import tqdm

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=str, default="data/manifests/severity_manifest.csv")
    parser.add_argument("--img_dir", type=str, default="data/CarDD_COCO")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--project", type=str, default="outputs/severity")
    parser.add_argument("--name", type=str, default="severity_resnet18_v1")
    return parser.parse_args()

def main():
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    transform = A.Compose([
        A.Resize(224, 224),
        A.HorizontalFlip(p=0.5),
        A.RandomBrightnessContrast(p=0.2),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2(),
    ])
    
    val_transform = A.Compose([
        A.Resize(224, 224),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2(),
    ])

    # Fix #10: build a shared labels_map from the FULL dataset so train/val/test are consistent
    full_dataset = SeverityDataset(args.manifest, args.img_dir, split=None, transform=None)
    shared_labels_map = full_dataset.labels_map

    train_dataset = SeverityDataset(args.manifest, args.img_dir, split="train",
                                    transform=transform, labels_map=shared_labels_map)
    val_dataset = SeverityDataset(args.manifest, args.img_dir, split="val",
                                  transform=val_transform, labels_map=shared_labels_map)
    
    train_loader = DataLoader(train_dataset, batch_size=args.batch, shuffle=True,
                              num_workers=2, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch, shuffle=False,
                            num_workers=2, pin_memory=True)
    
    class_weights = train_dataset.get_class_weights().to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    
    model = SeverityClassifier(num_classes=train_dataset.num_classes)
    model.to(device)
    
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr, weight_decay=1e-4)
    
    out_dir = Path(args.project) / args.name
    out_dir.mkdir(parents=True, exist_ok=True)

    # Fix #8: save labels_map.json alongside the checkpoint so pipeline can load it
    with open(out_dir / "labels_map.json", "w") as f:
        json.dump(shared_labels_map, f, indent=4)
    print(f"Saved labels_map.json to {out_dir / 'labels_map.json'}")
    
    best_val_loss = float('inf')
    train_losses = []
    val_losses = []
    
    for epoch in range(args.epochs):
        model.train()
        running_loss = 0.0
        
        for images, features, labels in tqdm(train_loader, desc=f"Epoch {epoch+1}/{args.epochs}"):
            images = images.to(device)
            features = features.to(device)
            labels = labels.to(device)
            
            optimizer.zero_grad()
            logits = model(images, features)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * images.size(0)
            
        epoch_loss = running_loss / len(train_dataset)
        train_losses.append(epoch_loss)
        
        # Validation
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        with torch.no_grad():
            for images, features, labels in val_loader:
                images = images.to(device)
                features = features.to(device)
                labels = labels.to(device)
                
                logits = model(images, features)
                loss = criterion(logits, labels)
                val_loss += loss.item() * images.size(0)
                
                preds = logits.argmax(dim=1)
                correct += (preds == labels).sum().item()
                total += labels.size(0)
                
        epoch_val_loss = val_loss / len(val_dataset)
        val_acc = correct / total
        val_losses.append(epoch_val_loss)
        
        print(f"Train Loss: {epoch_loss:.4f} | Val Loss: {epoch_val_loss:.4f} | Val Acc: {val_acc:.4f}")
        
        if epoch_val_loss < best_val_loss:
            best_val_loss = epoch_val_loss
            torch.save(model.state_dict(), out_dir / "best_severity.pt")
            
    # Save training curves
    plt.plot(train_losses, label="Train Loss")
    plt.plot(val_losses, label="Val Loss")
    plt.legend()
    plt.savefig(out_dir / "training_curves.png")
    plt.close()
    
    print(f"Training complete. Best model saved to {out_dir / 'best_severity.pt'}")

if __name__ == "__main__":
    main()
