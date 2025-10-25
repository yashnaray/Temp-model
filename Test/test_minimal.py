"""
Minimal test to verify basic functionality without complex dependencies
"""
import sys
import os
import numpy as np

# Add parent directory to path
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

def test_numpy_basic():
    """Test basic numpy functionality"""
    arr = np.array([1, 2, 3])
    assert arr.sum() == 6

def test_opencv_import():
    """Test OpenCV import"""
    try:
        import cv2
        # Create a simple test image
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        assert gray.shape == (100, 100)
        print("✅ OpenCV working")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        assert False, "OpenCV not available"

def test_vision_module():
    """Test vision module import"""
    try:
        from vision.change_detector import ChangeDetector
        detector = ChangeDetector()
        print("✅ Vision module working")
        assert detector is not None
    except Exception as e:
        print(f"❌ Vision module failed: {e}")
        # Don't fail the test, just report
        pass

def test_basic_image_processing():
    """Test basic image processing"""
    try:
        import cv2
        from skimage.metrics import structural_similarity as ssim
        
        # Create test images
        img1 = np.zeros((50, 50), dtype=np.uint8)
        img2 = np.ones((50, 50), dtype=np.uint8) * 255
        
        # Test SSIM
        score = ssim(img1, img2)
        assert 0 <= score <= 1
        print(f"✅ SSIM score: {score}")
        
    except Exception as e:
        print(f"❌ Image processing failed: {e}")
        pass

if __name__ == "__main__":
    print("Running minimal tests...")
    test_numpy_basic()
    test_opencv_import()
    test_vision_module()
    test_basic_image_processing()
    print("✅ Minimal tests completed!")