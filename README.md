# Car Damage Detection & Severity Assessment Pipeline

An end-to-end Deep Learning system and interactive portfolio for vision-based vehicle damage detection, semantic segmentation, severity assessment, and visual explainability.

---

## 📌 Project Overview

This repository integrates computer vision models into a unified 3-stage pipeline:
1. **Damage Detection (YOLOv8s):** Detects 6 classes of damage (Dent, Scratch, Crack, Glass Shatter, Lamp Broken, Tire Flat) with bounding boxes.
2. **Damage Segmentation (SegFormer):** High-precision pixel-level damage boundary segmentation using Transformer architectures.
3. **Severity Classification & Explainability (ResNet-18 + Grad-CAM):** Classifies damage severity into Minor, Moderate, or Severe, and generates Grad-CAM heatmaps showing the structural failure points analyzed by the model.

---

## 📁 Repository Structure

```
.
├── CarDD-USTC.github.io/       # Core Deep Learning Project
│   ├── app.py                  # Flask Web Application for interactive demo
│   ├── pipeline/               # Unified inference pipeline (final_pipeline.py)
│   ├── yolo/                   # YOLOv8 training, validation, and inference
│   ├── segformer/              # SegFormer training and validation scripts
│   ├── severity/               # ResNet-18 severity classifier
│   ├── explainability/         # Grad-CAM heatmap visualization
│   ├── webapp/                 # Flask UI templates and static assets
│   ├── data_tools/             # Data preprocessing and conversion utilities
│   ├── docs/                   # Project documentation and research papers
│   ├── code/                   # Baseline benchmarks (MMDetection, SOD)
│   ├── requirements.txt        # Python dependencies
│   ├── Project_Report.md       # Comprehensive evaluation report & metrics
│   └── PROJECT_STATE.md        # Current engineering status
├── portfolio/                  # React + Vite + Tailwind showcase portfolio
│   ├── src/                    # Portfolio components and visual pipeline
│   ├── package.json            # Frontend dependencies
│   └── vite.config.ts          # Vite build configuration
├── CarDD_Colab_Trainer.ipynb   # Google Colab notebook for GPU training
├── .gitignore                  # Git ignore rules for datasets, weights & node_modules
└── README.md                   # Repository overview and setup guide
```

---

## 🚀 Quick Start

### 1. Python Deep Learning Environment & Web App

Navigate to `CarDD-USTC.github.io`:
```bash
cd CarDD-USTC.github.io
pip install -r requirements.txt
```

#### Run the Web Application:
```bash
python app.py
```
Open your browser at `http://localhost:5000` to upload car damage photos and view real-time detection, segmentation masks, and Grad-CAM explainability heatmaps.

#### Run the End-to-End Pipeline via CLI:
```bash
python pipeline/final_pipeline.py --image test_img.jpg --output-dir outputs/demo
```

---

### 2. Interactive Showcase Portfolio

The project includes a modern React frontend showcasing the architecture, metrics, and pipeline:

```bash
cd portfolio
npm install
npm run dev
```

---

### 3. Google Colab Training

To train the models on cloud GPUs (T4 / V100 / A100):
1. Open `CarDD_Colab_Trainer.ipynb` in Google Colab.
2. Mount your Google Drive and follow the phase-by-phase cells.

---

## 📊 Performance Summary

| Model Stage | Primary Metric | Score | Key Results |
| :--- | :--- | :--- | :--- |
| **YOLOv8s** (Detection) | mAP50 | **72.6%** | High accuracy on severe damages (99% glass shatter, 92% flat tire) |
| **SegFormer** (Segmentation) | Mean IoU | **80.9%** | Precise irregular boundary tracing |
| **ResNet-18** (Severity) | Accuracy / F1 | **63.1% / 67.4%** | 3-tier severity classification with Grad-CAM attribution |

---

## 📦 Datasets and Model Weights

To keep the repository clean and under GitHub size limits:
- Raw datasets (6+ GB) and trained checkpoint files (`.pt`, `.safetensors`) are excluded via `.gitignore`.
- Datasets can be acquired via the [CarDD Dataset](https://cardd-ustc.github.io/).
- Pretrained checkpoints should be placed into their respective directories (`runs/` or `outputs/`) as detailed in `CarDD-USTC.github.io/README.md`.
