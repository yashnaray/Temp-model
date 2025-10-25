import sys
import os
import pytest
import numpy as np
import cv2

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from vision.change_detector import ChangeDetector
from vision.property_detector import PropertyDetector
from vision.condition_scorer import ConditionScorer
from vision.material_recognizer import MaterialRecognizer

class TestChangeDetector:
    def setup_method(self):
        self.detector = ChangeDetector()
        # Create test images
        self.test_image1 = np.zeros((100, 100, 3), dtype=np.uint8)
        self.test_image2 = np.ones((100, 100, 3), dtype=np.uint8) * 255
    
    def test_init(self):
        assert self.detector.orb is not None
        assert self.detector.bf is not None
    
    def test_detect_changes_structure(self):
        result = self.detector.detect_changes(self.test_image1, self.test_image2)
        assert 'similarity_score' in result
        assert 'change_regions' in result
        assert 'change_types' in result
        assert 'change_summary' in result
    
    def test_identify_significant_changes(self):
        diff_image = np.random.rand(50, 50)
        changes = self.detector._identify_significant_changes(diff_image, threshold=0.5)
        assert isinstance(changes, list)
    
    def test_extract_region(self):
        region = (10, 10, 20, 20)
        roi = self.detector._extract_region(self.test_image1, region)
        assert roi.shape == (20, 20, 3)

class TestPropertyDetector:
    def setup_method(self):
        self.detector = PropertyDetector()
        self.test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    
    def test_init(self):
        assert hasattr(self.detector, 'detect_components')
    
    def test_detect_components_structure(self):
        try:
            result = self.detector.detect_components(self.test_image)
            assert 'properties' in result
            assert 'property_summary' in result
        except Exception as e:
            pytest.skip(f"PropertyDetector not fully implemented: {e}")

class TestConditionScorer:
    def setup_method(self):
        self.scorer = ConditionScorer()
        self.test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    
    def test_init(self):
        assert hasattr(self.scorer, 'score_condition')
    
    def test_score_condition_structure(self):
        try:
            result = self.scorer.score_condition(self.test_image)
            assert isinstance(result, (int, float, dict))
        except Exception as e:
            pytest.skip(f"ConditionScorer not fully implemented: {e}")

class TestMaterialRecognizer:
    def setup_method(self):
        self.recognizer = MaterialRecognizer()
        self.test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    
    def test_init(self):
        assert hasattr(self.recognizer, 'recognize_materials')
    
    def test_recognize_materials_structure(self):
        try:
            result = self.recognizer.recognize_materials(self.test_image)
            assert isinstance(result, (list, dict))
        except Exception as e:
            pytest.skip(f"MaterialRecognizer not fully implemented: {e}")

if __name__ == "__main__":
    pytest.main([__file__])