import os
import cv2

def plot_boxes(image, boxes, class_names):
    """
    Utility to plot YOLO format boxes on an image
    """
    for box in boxes:
        cls, conf, x1, y1, x2, y2 = box
        label = f"{class_names[int(cls)]} {conf:.2f}"
        cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(image, label, (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    return image
