import cv2
import numpy as np
# from sklearn.ensemble import RandomForestRegressor
import joblib

class ConditionScorer:
    def __init__(self):
        self.crack_detector = self._load_crack_model()
        self.material_classifier = self._load_material_model()

    def score_condition(self, image, mask=None):
        """Generic condition scorer that aggregates several metrics."""
        if mask is None:
            mask = np.ones(image.shape[:2], dtype=np.uint8)
        roof_score = self._detect_missing_shingles(image, mask)
        color_uniformity = self._analyze_color_uniformity(image, mask)
        # return simple dict
        return {
            'missing_shingle_ratio': roof_score,
            'color_uniformity': color_uniformity,
            'combined_score': float(max(0.0, 1.0 - roof_score))
        }
        
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
        try:
            model = joblib.load('crack_detection_model.h5')
            return model
        except Exception:
            # Return dummy detector with predict method
            class Dummy:
                def predict(self, x):
                    return [0 for _ in range(len(x))]
            return Dummy()
    def _load_material_model(self):
        try:
            model = joblib.load('material_classification_model.h5')
            return model
        except Exception:
            class DummyMat:
                def predict(self, x):
                    # return class 6 (Misc) for any input
                    return [6 for _ in range(len(x))]
            return DummyMat()
    
    def classify_material(self, image):
        """Classify material type in image"""
        # Preprocess image for material classification
        processed_image = self._preprocess_for_material(image)
        prediction = self.material_classifier.predict(processed_image)
        
        # Material class mappings
        material_classes = {
            0: "Cardboard",
            1: "Glass", 
            2: "Metal",
            3: "Paper",
            4: "Plastic",
            5: "Trash",
            6: "Misc"
        }
        
        predicted_class = np.argmax(prediction)
        confidence = np.max(prediction)
        
        return {
            'material': material_classes[predicted_class],
            'confidence': float(confidence),
            'class_id': int(predicted_class)
        }
    
    def _preprocess_for_material(self, image):
        """Preprocess image for material classification model"""
        # Resize to model input size (assuming 224x224)
        resized = cv2.resize(image, (224, 224))
        # Normalize pixel values
        normalized = resized.astype(np.float32) / 255.0
        # Add batch dimension
        return np.expand_dims(normalized, axis=0)
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
    
    def analyze_material_condition(self, image, mask=None):
        """Analyze material condition including type and degradation"""
        material_info = self.classify_material(image)
        
        # Material-specific condition analysis
        condition_factors = {
            'material_type': material_info['material'],
            'material_confidence': material_info['confidence']
        }
        
        if mask is not None:
            if material_info['material'] in ['Metal', 'Glass']:
                condition_factors['corrosion_score'] = self._detect_corrosion(image, mask)
            elif material_info['material'] in ['Cardboard', 'Paper']:
                condition_factors['moisture_damage'] = self._detect_moisture_damage(image, mask)
            elif material_info['material'] == 'Plastic':
                condition_factors['uv_degradation'] = self._detect_uv_damage(image, mask)
        
        return condition_factors
    
    def _detect_corrosion(self, image, mask):
        """Detect corrosion in metal/glass materials"""
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        # Look for rust/corrosion colors (browns, oranges)
        lower_rust = np.array([5, 50, 50])
        upper_rust = np.array([25, 255, 255])
        rust_mask = cv2.inRange(hsv, lower_rust, upper_rust)
        corrosion_ratio = np.sum(rust_mask & mask) / np.sum(mask)
        return corrosion_ratio
    
    def _detect_moisture_damage(self, image, mask):
        """Detect moisture damage in paper/cardboard materials"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        # Look for dark spots indicating moisture damage
        dark_threshold = np.percentile(gray[mask > 0], 25)
        moisture_mask = gray < dark_threshold
        moisture_ratio = np.sum(moisture_mask & mask) / np.sum(mask)
        return moisture_ratio
    
    def _detect_uv_damage(self, image, mask):
        """Detect UV damage in plastic materials"""
        # UV damage often appears as fading or color changes
        color_variance = np.var(image[mask > 0], axis=0)
        uv_damage_score = np.mean(color_variance) / 255.0
        return uv_damage_score
