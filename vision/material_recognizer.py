import cv2
import numpy as np
from typing import Dict, List, Tuple

class MaterialRecognizer:
    def __init__(self, model_path='material_classification_model.h5'):
        self.model = self._load_model(model_path)
        self.material_classes = {
            0: "Cardboard",
            1: "Glass", 
            2: "Metal",
            3: "Paper",
            4: "Plastic",
            5: "Trash",
            6: "Misc"
        }
        
    def _load_model(self, model_path):
        """Load the material classification model. If tensorflow is unavailable return None."""
        try:
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
            tf.get_logger().setLevel('ERROR')
            return tf.keras.models.load_model(model_path)
        except Exception as e:
            # Suppress detailed error messages
            return None
    
    def classify_material(self, image: np.ndarray) -> Dict:
        """Classify material type in image"""
        if self.model is None:
            return {'material': 'Unknown', 'confidence': 0.0, 'class_id': -1}
        
        processed_image = self._preprocess_image(image)
        prediction = self.model.predict(processed_image, verbose=0)
        
        predicted_class = np.argmax(prediction[0])
        confidence = np.max(prediction[0])
        
        return {
            'material': self.material_classes[predicted_class],
            'confidence': float(confidence),
            'class_id': int(predicted_class),
            'all_probabilities': {self.material_classes[i]: float(prob) 
                                for i, prob in enumerate(prediction[0])}
        }
    
    def classify_multiple_regions(self, image: np.ndarray, regions: List[Tuple]) -> List[Dict]:
        """Classify materials in multiple regions of an image"""
        results = []
        for region in regions:
            x, y, w, h = region
            roi = image[y:y+h, x:x+w]
            if roi.size > 0:
                result = self.classify_material(roi)
                result['region'] = region
                results.append(result)
        return results
    
    def detect_material_boundaries(self, image: np.ndarray, threshold: float = 0.8) -> List[Dict]:
        """Detect different material regions in an image"""
        # Simple grid-based approach
        h, w = image.shape[:2]
        grid_size = 64
        regions = []
        
        for y in range(0, h - grid_size, grid_size // 2):
            for x in range(0, w - grid_size, grid_size // 2):
                roi = image[y:y+grid_size, x:x+grid_size]
                result = self.classify_material(roi)
                
                if result['confidence'] > threshold:
                    result['bbox'] = (x, y, grid_size, grid_size)
                    regions.append(result)
        
        return self._merge_similar_regions(regions)
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for material classification"""
        # Resize to model input size
        resized = cv2.resize(image, (224, 224))
        # Normalize pixel values
        normalized = resized.astype(np.float32) / 255.0
        # Add batch dimension
        return np.expand_dims(normalized, axis=0)
    
    def _merge_similar_regions(self, regions: List[Dict]) -> List[Dict]:
        """Merge adjacent regions with same material type"""
        if not regions:
            return []
        
        merged = []
        used = set()
        
        for i, region in enumerate(regions):
            if i in used:
                continue
                
            similar_regions = [region]
            used.add(i)
            
            for j, other_region in enumerate(regions[i+1:], i+1):
                if j in used:
                    continue
                    
                if (region['material'] == other_region['material'] and 
                    self._regions_adjacent(region['bbox'], other_region['bbox'])):
                    similar_regions.append(other_region)
                    used.add(j)
            
            # Merge bounding boxes
            merged_bbox = self._merge_bboxes([r['bbox'] for r in similar_regions])
            avg_confidence = np.mean([r['confidence'] for r in similar_regions])
            
            merged.append({
                'material': region['material'],
                'confidence': avg_confidence,
                'class_id': region['class_id'],
                'bbox': merged_bbox,
                'region_count': len(similar_regions)
            })
        
        return merged
    
    def _regions_adjacent(self, bbox1: Tuple, bbox2: Tuple, threshold: int = 32) -> bool:
        """Check if two bounding boxes are adjacent"""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        # Check if regions overlap or are close
        return (abs(x1 - x2) < threshold and abs(y1 - y2) < threshold)
    
    def _merge_bboxes(self, bboxes: List[Tuple]) -> Tuple:
        """Merge multiple bounding boxes into one"""
        if not bboxes:
            return (0, 0, 0, 0)
        
        min_x = min(bbox[0] for bbox in bboxes)
        min_y = min(bbox[1] for bbox in bboxes)
        max_x = max(bbox[0] + bbox[2] for bbox in bboxes)
        max_y = max(bbox[1] + bbox[3] for bbox in bboxes)
        
        return (min_x, min_y, max_x - min_x, max_y - min_y)
    
    def get_material_properties(self, material: str) -> Dict:
        """Get properties of detected material"""
        properties = {
            "Cardboard": {"durability": "low", "water_resistance": "poor", "recyclable": True},
            "Glass": {"durability": "high", "water_resistance": "excellent", "recyclable": True},
            "Metal": {"durability": "high", "water_resistance": "good", "recyclable": True},
            "Paper": {"durability": "low", "water_resistance": "poor", "recyclable": True},
            "Plastic": {"durability": "medium", "water_resistance": "good", "recyclable": True},
            "Trash": {"durability": "unknown", "water_resistance": "unknown", "recyclable": False},
            "Misc": {"durability": "unknown", "water_resistance": "unknown", "recyclable": False}
        }
        
        return properties.get(material, {"durability": "unknown", "water_resistance": "unknown", "recyclable": False})
    def recognize_materials(self, image):
        try:
            regions = self.detect_material_boundaries(image)
            return self._merge_similar_regions(regions)
        except Exception:
            # fallback to classifying full image
            return [self.classify_material(image)]
