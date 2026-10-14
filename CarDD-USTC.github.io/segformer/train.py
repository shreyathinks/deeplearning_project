import torch
import numpy as np
import evaluate
from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation
from transformers import TrainingArguments, Trainer
import sys
from pathlib import Path

# Fix #3: ensure segformer/ is importable when run from any directory
sys.path.insert(0, str(Path(__file__).parent))

from dataset import SegFormerDataset
import argparse
import torch.nn as nn

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="data/segformer")
    parser.add_argument("--model", type=str, default="nvidia/mit-b0")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--lr", type=float, default=6e-5)
    parser.add_argument("--project", type=str, default="outputs/segformer")
    parser.add_argument("--name", type=str, default="segformer_b0_v1")
    return parser.parse_args()

class DiceLoss(nn.Module):
    def __init__(self, smooth=1.0):
        super(DiceLoss, self).__init__()
        self.smooth = smooth

    def forward(self, probs, targets):
        # Fix #9: mask out ignore index (255) before computing Dice loss
        valid = targets != 255
        probs = probs[valid]
        targets = targets[valid]

        probs = probs.view(-1)
        targets = targets.view(-1)
        
        intersection = (probs * targets).sum()
        dice = (2. * intersection + self.smooth) / (probs.sum() + targets.sum() + self.smooth)
        return 1 - dice

class CustomTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        
        # Upsample logits to label size
        upsampled_logits = nn.functional.interpolate(
            logits, size=labels.shape[-2:], mode="bilinear", align_corners=False
        )
        
        # Loss 1: Cross Entropy (ignore_index=255 is handled natively)
        ce_loss_fn = nn.CrossEntropyLoss(ignore_index=255)
        ce_loss = ce_loss_fn(upsampled_logits, labels)
        
        # Loss 2: Dice Loss (Fix #9: invalid pixels masked inside DiceLoss.forward)
        dice_loss_fn = DiceLoss()
        probs = torch.softmax(upsampled_logits, dim=1)[:, 1, ...]
        dice_loss = dice_loss_fn(probs, labels.float())
        
        # Loss = 0.5 * CE + 0.5 * Dice
        loss = 0.5 * ce_loss + 0.5 * dice_loss
        
        return (loss, outputs) if return_outputs else loss

def main():
    args = parse_args()
    print(f"Training SegFormer: {args.name}")
    
    feature_extractor = SegformerImageProcessor.from_pretrained(args.model)
    feature_extractor.do_reduce_labels = False  # background=0, damage=1
    
    train_dataset = SegFormerDataset(args.data_dir, split="train", feature_extractor=feature_extractor)
    val_dataset = SegFormerDataset(args.data_dir, split="val", feature_extractor=feature_extractor)
    
    # 2 classes: background(0), damage(1)
    id2label = {0: "background", 1: "damage"}
    label2id = {"background": 0, "damage": 1}
    
    model = SegformerForSemanticSegmentation.from_pretrained(
        args.model,
        num_labels=2,
        id2label=id2label,
        label2id=label2id,
        ignore_mismatched_sizes=True
    )
    
    metric = evaluate.load("mean_iou")
    
    def compute_metrics(eval_pred):
        logits, labels = eval_pred

        # Fix #14: upsample logits to label size (more accurate than downsampling labels)
        # logits shape from HF Trainer: [B, num_classes, H_small, W_small]
        # labels shape: [B, H_full, W_full]
        logits_tensor = torch.from_numpy(logits).float()          # [B, C, H_s, W_s]
        labels_tensor = torch.from_numpy(labels).long()           # [B, H, W]
        target_size = labels_tensor.shape[-2:]                     # (H, W)
        upsampled_logits = nn.functional.interpolate(
            logits_tensor, size=target_size, mode="bilinear", align_corners=False
        )                                                          # [B, C, H, W]
        predictions = upsampled_logits.argmax(dim=1).numpy()      # [B, H, W]

        metrics = metric.compute(
            predictions=predictions,
            references=labels,
            num_labels=2,
            ignore_index=255,
            reduce_labels=False
        )
        return {
            "mean_iou": metrics["mean_iou"],
            "mean_accuracy": metrics["mean_accuracy"],
            "iou_damage": metrics["per_category_iou"][1] if len(metrics["per_category_iou"]) > 1 else 0
        }
            
    out_dir = Path(args.project) / args.name
    
    training_args = TrainingArguments(
        output_dir=str(out_dir),
        learning_rate=args.lr,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch,
        per_device_eval_batch_size=args.batch,
        save_total_limit=3,
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_steps=50,
        remove_unused_columns=False,
        load_best_model_at_end=True,
        metric_for_best_model="iou_damage",
        greater_is_better=True,
        # Fix #15: only enable fp16 when a CUDA GPU is available
        fp16=torch.cuda.is_available(),
    )
    
    trainer = CustomTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
    )
    # If a checkpoint exists in the output directory, resume from it
    import glob
    checkpoints = glob.glob(str(out_dir / "checkpoint-*"))
    if checkpoints:
        trainer.train(resume_from_checkpoint=True)
    else:
        trainer.train()
    
    # Save best model
    trainer.save_model(str(out_dir / "best"))
    feature_extractor.save_pretrained(str(out_dir / "best"))
    
    print(f"SegFormer training complete. Best model saved to {out_dir / 'best'}")

if __name__ == "__main__":
    main()
