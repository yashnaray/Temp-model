import sys
import os
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)

sys.path.append(parent_dir)
from vision.change_detector import ChangeDetector
from vision.property_detector import PropertyDetector

def test_detect_changes():
    detector = ChangeDetector()
    current_image = "after.png" 
    historical_image = "before.png" 
    result = detector.detect_changes(current_image, historical_image)
    assert 'similarity_score' in result
    assert 'change_regions' in result
    assert 'change_types' in result
    assert 'change_summary' in result
    print(result)

def test_property_detector():
    detector = PropertyDetector()
    image_path = "after.png"
    result = detector.detect_components(image_path)
    assert 'properties' in result
    assert 'property_summary' in result
    print(result)

def main():
    test_detect_changes()

if __name__ == "__main__":
    main()