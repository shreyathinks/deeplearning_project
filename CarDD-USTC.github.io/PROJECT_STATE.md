# Project State

Current phase: Active Development — Pipeline, Training, and Web App complete
Completed:
  - Phase 0: Repository audit
  - Phase 1: YOLOv8 training & validation scripts
  - Phase 2: SegFormer training & validation scripts
  - Phase 3: Severity ResNet18 classifier (training + validation)
  - Phase 4: GradCAM explainability module
  - Phase 5: End-to-end inference pipeline (pipeline/final_pipeline.py)
  - Phase 6: Flask web application (app.py + webapp/)
  - Phase 7: Bug fixes across all modules (see git log)

Files added: requirements.txt, yolo/__init__.py, segformer/__init__.py
Files modified: pipeline/final_pipeline.py, app.py, severity/train.py, severity/validate.py,
                severity/dataset.py, segformer/train.py, segformer/validate.py,
                segformer/predict.py, segformer/dataset.py, explainability/gradcam.py,
                yolo/validate.py, webapp/templates/index.html

Known issues: None (25 issues identified and fixed — see project_issues.md)
Next phase: Phase 8 — Evaluation on test split and results logging
