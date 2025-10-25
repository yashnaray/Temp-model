# vision/property_detector.py
import cv2
import torch
import numpy as np
from ultralytics import YOLO
import mediapipe as mp

class PropertyDetector:
    def __init__(self):
        self.segmentation_model = YOLO('yolov8n-seg.pt')
        self.mediapipe_pose = mp.solutions.pose.Pose()
        
        self.property_classes = {
            'roof': 0, 'wall': 1, 'window': 2, 'door': 3,
            'foundation': 4, 'deck': 5, 'fence': 6, 'pool': 7
        }
    
    def detect_components(self, image):
        results = self.segmentation_model(image)
        
        components = {}
        for result in results:
            masks = result.masks
            boxes = result.boxes
            classes = result.names
            
            for i, mask in enumerate(masks):
                class_name = classes[int(boxes.cls[i])]
                if class_name in self.property_classes:
                    components[class_name] = {
                        'mask': mask.data.cpu().numpy(),
                        'confidence': boxes.conf[i].cpu().numpy(),
                        'bbox': boxes.xyxy[i].cpu().numpy()
                    }
        
        return components
    
    def estimate_measurements(self, image, components):
        door_height_pixels = self._extract_feature_height(components.get('door', {}))
        actual_door_height = 2.0 # Most doors especially in houses are 2m in length
        
        scale_factor = actual_door_height / door_height_pixels if door_height_pixels else None
        
        measurements = {}
        for comp_name, comp_data in components.items():
            if scale_factor and 'bbox' in comp_data:
                bbox = comp_data['bbox']
                width_pixels = bbox[2] - bbox[0]
                height_pixels = bbox[3] - bbox[1]
                
                measurements[comp_name] = {
                    'width_m': width_pixels * scale_factor,
                    'height_m': height_pixels * scale_factor,
                    'area_sq_m': (width_pixels * height_pixels) * (scale_factor ** 2)
                }
        
        return measurements

    def _extract_feature_height(self, door_data):
        if not door_data or 'mask' not in door_data: return None

        mask = door_data['mask']
        y, x = np.where(mask > 0)
        if len(y) == 0 or len(x) == 0:
            return None

        min_y, max_y = np.min(y), np.max(y)
        min_x, max_x = np.min(x), np.max(x)

        door_height_pixels = max_y - min_y

        return door_height_pixels