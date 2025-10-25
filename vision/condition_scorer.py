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
        """Comprehensive roof condition scoring (1-10)"""
        features = {}
        
        # 1. Detect missing shingles
        features['missing_shingle_ratio'] = self._detect_missing_shingles(roof_image, roof_mask)
        
        # 2. Detect discoloration/aging
        features['color_uniformity'] = self._analyze_color_uniformity(roof_image, roof_mask)
        
        # 3. Detect moss/algae growth
        features['vegetation_coverage'] = self._detect_moss_coverage(roof_image, roof_mask)
        
        # 4. Detect structural sagging
        features['sagging_score'] = self._detect_roof_sagging(roof_image, roof_mask)
        
        # Combine features for final score
        condition_score = self._calculate_composite_score(features)
        return condition_score, features
    
    def _detect_missing_shingles(self, image, mask):
        """Use edge detection and pattern analysis"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Apply mask and look for irregular edge patterns
        masked_edges = cv2.bitwise_and(edges, edges, mask=mask.astype(np.uint8))
        
        # Count edge discontinuities (potential missing shingles)
        discontinuity_ratio = np.sum(masked_edges > 0) / np.sum(mask > 0)
        return discontinuity_ratio
    
    def analyze_foundation(self, foundation_image, foundation_mask):
        """Foundation crack and settlement analysis"""
        # Convert to grayscale
        gray = cv2.cvtColor(foundation_image, cv2.COLOR_RGB2GRAY)
        
        # Enhanced crack detection
        cracks = self._enhanced_crack_detection(gray, foundation_mask)
        
        # Analyze crack patterns
        crack_severity = self._assess_crack_severity(cracks)
        
        return {
            'crack_density': len(cracks) / np.sum(foundation_mask),
            'max_crack_width': max([c['width'] for c in cracks]) if cracks else 0,
            'crack_pattern': self._classify_crack_pattern(cracks),
            'severity_score': crack_severity
        }