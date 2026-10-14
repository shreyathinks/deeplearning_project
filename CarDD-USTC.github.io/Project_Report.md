# Car Damage Detection & Severity Assessment (CarDD)
## Final Project Report

### 1. Executive Summary
This project implements an advanced, end-to-end Machine Learning pipeline designed to detect, trace, and assess the severity of car damages from raw images. Unlike traditional single-model approaches, this system utilizes a **three-stage neural network architecture** that mimics a real-world production pipeline.

### 2. System Architecture
The pipeline (`pipeline/final_pipeline.py`) chains together three specialized AI models:

1. **Damage Detection (YOLOv8s):** The first stage scans the image and draws bounding boxes around 6 specific types of damage (Dent, Scratch, Crack, Glass Shatter, Lamp Broken, Tire Flat).
2. **Damage Segmentation (SegFormer):** The second stage uses a Transformer-based architecture to precisely trace the exact pixel-level boundaries of the detected damages, separating the damage from the background car body.
3. **Severity Classification & Explainability (ResNet18):** The final stage takes the cropped damage and engineered features to classify the severity as Minor, Moderate, or Severe. It also utilizes **Grad-CAM** to generate a heat-map, proving to the user exactly *which* pixels the AI looked at to make its decision.

---

### 3. Official Evaluation Metrics
The models were officially evaluated against an unseen Test Set to verify real-world accuracy.

| Model Stage | Primary Metric | Score | Key Takeaways |
| :--- | :--- | :--- | :--- |
| **YOLOv8s (Detection)** | Overall mAP50 | **72.6%** | Achieved 99% accuracy on shattered glass and 92% on flat tires. |
| **YOLOv8s (Size-Buckets)**| Size-based mAP | **58.7%** (Large) | The model struggles with tiny damages (14.0% mAP) but excels at large damages. |
| **SegFormer (Segmentation)**| Mean IoU | **80.9%** | Exceptionally high pixel-perfect tracing accuracy for irregular boundary shapes. |
| **ResNet18 (Severity)** | Overall Accuracy | **63.1%** | Achieved a 67.4% Weighted F1-Score across the three severity classes. |

---

### 4. Qualitative Results (Inference)
When passing a test image (e.g., `000013.jpg`) through the integrated pipeline, the system successfully outputs a comprehensive `prediction.json` and a `final_visualization.jpg` dashboard. 

The dashboard provides visual proof of the system's effectiveness:
* **Left Panel:** YOLO bounding box correctly isolating the flat tire.
* **Middle Panel:** SegFormer mask precisely isolating the damaged tire pixels.
* **Right Panel:** Grad-CAM heat-map highlighting the exact structural failure point on the tire that caused the severity classification.

### 5. Future Improvements
If this project were to be scaled into a commercial product, the following steps would further increase accuracy:
1. **Model Scaling:** Upgrading the detection model from `YOLOv8s` (Small) to `YOLOv8x` (Extra Large).
2. **Extended Training:** Training all models for 300+ epochs on cloud GPUs (currently trained for 16-100 epochs).
3. **Focal Loss:** Implementing advanced loss functions to penalize the AI more heavily for missing under-represented classes (like "cracks" and "scratches").
