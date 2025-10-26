import cv2
import numpy as np
from typing import Dict, List, Tuple

class PropertyDetector:
    def __init__(self):
        self.component_classifiers = {
            'roof': self._detect_roof,
            'walls': self._detect_walls,
            'windows': self._detect_windows,
            'doors': self._detect_doors,
            'foundation': self._detect_foundation
        }
    
    def detect_property_components(self, image) -> Dict:
        """Detect various property components in image"""
        if isinstance(image, str):
            image = cv2.imread(image)
            if image is None:
                image = np.zeros((100,100,3), dtype=np.uint8)
        results = {}
        
        for component, detector in self.component_classifiers.items():
            results[component] = detector(image)
        
        summary = {'num_components': len(results)}
        return {'properties': results, 'property_summary': summary}
    
    def _detect_roof(self, image: np.ndarray) -> Dict:
        """Detect roof area in image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Look for triangular/sloped shapes in upper portion
        upper_half = gray[:gray.shape[0]//2, :]
        edges = cv2.Canny(upper_half, 50, 150)
        
        # Find lines (roof edges)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        roof_area = 0
        if lines is not None:
            # Estimate roof area based on detected lines
            roof_area = len(lines) * 1000  # Simplified calculation
        
        return {
            'detected': lines is not None,
            'estimated_area': roof_area,
            'condition': 'unknown'
        }
    
    def _detect_walls(self, image: np.ndarray) -> Dict:
        """Detect wall areas in image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Look for vertical lines (wall edges)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=80)
        
        vertical_lines = 0
        if lines is not None:
            for line in lines:
                rho, theta = line[0]
                # Check if line is roughly vertical
                if abs(theta - np.pi/2) < 0.3:
                    vertical_lines += 1
        
        return {
            'detected': vertical_lines > 0,
            'vertical_edges': vertical_lines,
            'material': 'unknown'
        }
    
    def _detect_windows(self, image: np.ndarray) -> List[Dict]:
        """Detect windows in image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Use template matching for rectangular shapes
        # Simplified: look for dark rectangular regions
        _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        windows = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 1000 < area < 50000:  # Filter by size
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                
                # Windows are typically rectangular
                if 0.5 < aspect_ratio < 2.0:
                    windows.append({
                        'bbox': (x, y, w, h),
                        'area': area,
                        'aspect_ratio': aspect_ratio
                    })
        
        return windows
    
    def _detect_doors(self, image: np.ndarray) -> List[Dict]:
        """Detect doors in image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Look for tall rectangular shapes
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        doors = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 2000 < area < 100000:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                
                # Doors are typically tall rectangles
                if 0.3 < aspect_ratio < 0.8:
                    doors.append({
                        'bbox': (x, y, w, h),
                        'area': area,
                        'aspect_ratio': aspect_ratio
                    })
        
        return doors
    
    def _detect_foundation(self, image: np.ndarray) -> Dict:
        """Detect foundation area in image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Look in bottom portion of image
        bottom_third = gray[2*gray.shape[0]//3:, :]
        
        # Look for horizontal lines (foundation edge)
        edges = cv2.Canny(bottom_third, 50, 150)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=50)
        
        horizontal_lines = 0
        if lines is not None:
            for line in lines:
                rho, theta = line[0]
                # Check if line is roughly horizontal
                if abs(theta) < 0.3 or abs(theta - np.pi) < 0.3:
                    horizontal_lines += 1
        
        return {
            'detected': horizontal_lines > 0,
            'horizontal_edges': horizontal_lines,
            'material': 'concrete'  # Default assumption
        }
    
    def segment_property(self, image: np.ndarray) -> Dict:
        """Segment property into different regions"""
        if isinstance(image, str):
            image = cv2.imread(image)
            if image is None:
                image = np.zeros((100,100,3), dtype=np.uint8)
        h, w = image.shape[:2]
        
        # Simple region segmentation
        regions = {
            'roof': image[:h//3, :],
            'walls': image[h//3:2*h//3, :],
            'foundation': image[2*h//3:, :]
        }
        
        # Create masks for each region
        masks = {}
        for region_name, region_img in regions.items():
            mask = np.ones(region_img.shape[:2], dtype=np.uint8) * 255
            masks[region_name] = mask
        
        return {
            'regions': regions,
            'masks': masks,
            'segmentation_method': 'horizontal_thirds'
        }
    # backwards compatible alias
    def detect_components(self, image):
        return self.detect_property_components(image)
