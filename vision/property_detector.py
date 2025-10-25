import cv2
import numpy as np

class PropertyDetector:
    def __init__(self):
        self.cascade_classifiers = {
            'window': cv2.CascadeClassifier(),
            'door': cv2.CascadeClassifier()
        }
        
        self.property_classes = {
            'roof': 0, 'wall': 1, 'window': 2, 'door': 3,
            'foundation': 4, 'deck': 5, 'fence': 6, 'pool': 7
        }
    
    def detect_components(self, image):
        components = {}
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Initial component detection: IMPROVE
        for i, contour in enumerate(contours[:5]):
            x, y, w, h = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            
            if area > 1000:
                component_type = self._classify_component(w, h, area)
                components[f"{component_type}_{i}"] = {
                    'bbox': [x, y, x+w, y+h],
                    'confidence': 0.8,
                    'area': area
                }
        
        return {'properties': components, 'property_summary': len(components)}
    
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
    
    def _classify_component(self, width, height, area):
        aspect_ratio = width / height if height > 0 else 1
        
        if aspect_ratio > 2: return 'roof'
        elif aspect_ratio < 0.5: return 'wall'
        elif area < 5000: return 'window'
        else: return 'door'
    
    def _extract_feature_height(self, door_data):
        if not door_data or 'bbox' not in door_data: return None
        
        bbox = door_data['bbox']
        return bbox[3] - bbox[1]  # height = y2 - y1