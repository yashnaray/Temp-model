# vision/condition_scorer.py
import cv2
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib

class ConditionScorer:
    def __init__(self):
        self.crack_detector = self._load_crack_model()
        self.material_classifier = self._load_material_model()
        
    def score_roof_condition(self, roof_image, roof_mask):
        features = {}
        
        features['missing_shingle_ratio'] = self._detect_missing_shingles(roof_image, roof_mask)
        
        features['color_uniformity'] = self._analyze_color_uniformity(roof_image, roof_mask)
        
        features['vegetation_coverage'] = self._detect_moss_coverage(roof_image, roof_mask)
        
        features['sagging_score'] = self._detect_roof_sagging(roof_image, roof_mask)
        
        condition_score = self._calculate_composite_score(features)
        return condition_score, features
    
    def _detect_missing_shingles(self, image, mask):
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        masked_edges = cv2.bitwise_and(edges, edges, mask=mask.astype(np.uint8))
        
        discontinuity_ratio = np.sum(masked_edges > 0) / np.sum(mask > 0)
        return discontinuity_ratio
    
    def analyze_foundation(self, foundation_image, foundation_mask):
        gray = cv2.cvtColor(foundation_image, cv2.COLOR_RGB2GRAY)
        
        cracks = self._enhanced_crack_detection(gray, foundation_mask)
        crack_severity = self._assess_crack_severity(cracks)
        
        return {
            'crack_density': len(cracks) / np.sum(foundation_mask),
            'max_crack_width': max([c['width'] for c in cracks]) if cracks else 0,
            'crack_pattern': self._classify_crack_pattern(cracks),
            'severity_score': crack_severity
        }
    def _enhanced_crack_detection(self, gray, mask):
        edges = cv2.Canny(gray, 50, 150)
        masked_edges = cv2.bitwise_and(edges, edges, mask=mask.astype(np.uint8))
        contours, _ = cv2.findContours(masked_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        cracks = []
        for contour in contours:
            crack = {
                'width': cv2.arcLength(contour, True),
                'length': cv2.contourArea(contour),
                'bounding_box': cv2.boundingRect(contour)
            }
            cracks.append(crack)

        return cracks
    def _classify_crack_pattern(self, cracks):
        if not cracks: return 'No cracks'

        avg_width = np.mean([c['width'] for c in cracks])
        avg_length = np.mean([c['length'] for c in cracks])

        if avg_width > 10 and avg_length > 10: return 'Uniformly distributed'
        elif avg_width > 10: return 'Longitudinal'
        elif avg_length > 10: return 'Lateral'
        else: return 'Clustered'
    
    def _assess_crack_severity(self, cracks):
        severity = 0
        for crack in cracks:
            if crack['width'] > 15: severity += 3
            elif crack['width'] > 5:severity += 2
            else: severity += 1
        return severity / len(cracks) if cracks else 0
    
    def _detect_moss_coverage(self, image, mask):
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            lower_green = np.array([30, 50, 50])
            upper_green = np.array([90, 255, 255])
            moss_mask = cv2.inRange(hsv, lower_green, upper_green)
            moss_pixels = np.sum(moss_mask & mask) / np.sum(mask)
            return moss_pixels
    
    def _detect_roof_sagging(self, image, mask):
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        masked_edges = cv2.bitwise_and(edges, edges, mask=mask.astype(np.uint8))
        sagging_score = np.sum(masked_edges) / np.sum(mask)
        return sagging_score
    
    def _load_crack_model(self):
            model = joblib.load('crack_detection_model.joblib')
            return model
    def _load_material_model(self):
        model = joblib.load('material_classification_model.joblib')
        return model
    def _analyze_color_uniformity(self, image, mask):
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        hue = hsv[:, :, 0]
        saturation = hsv[:, :, 1]
        value = hsv[:, :, 2]

        hue_uniformity = np.std(hue[mask > 0])
        saturation_uniformity = np.std(saturation[mask > 0])
        value_uniformity = np.std(value[mask > 0])

        return (hue_uniformity + saturation_uniformity + value_uniformity) / 3
    def _calculate_composite_score(self, features):
        weights = {
            'missing_shingle_ratio': -0.3,
            'color_uniformity': -0.3,
            'vegetation_coverage': -0.2,
            'sagging_score': -0.2
        }

        composite_score = sum(features[key] * weights[key] for key in weights)
        return composite_score
