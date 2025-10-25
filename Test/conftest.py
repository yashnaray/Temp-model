import pytest
import sys
import os
import numpy as np

# Add parent directory to path for all tests
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

@pytest.fixture
def sample_image():
    """Provide a sample test image"""
    return np.zeros((100, 100, 3), dtype=np.uint8)

@pytest.fixture
def sample_image_pair():
    """Provide a pair of test images for comparison"""
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.ones((100, 100, 3), dtype=np.uint8) * 255
    return img1, img2

@pytest.fixture
def mock_cv_context():
    """Provide mock computer vision context"""
    return {
        'components': ['roof', 'walls', 'windows'],
        'condition_scores': {'roof': 8, 'walls': 7, 'windows': 9},
        'materials': ['shingle', 'brick', 'glass']
    }

@pytest.fixture
def mock_user_context():
    """Provide mock user context"""
    return {
        'user_type': 'inspector',
        'location': 'NYC',
        'property_type': 'residential'
    }

@pytest.fixture(scope="session")
def test_data_dir():
    """Provide test data directory path"""
    return os.path.join(os.path.dirname(__file__), "test_data")

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "vision: mark test as vision module test"
    )
    config.addinivalue_line(
        "markers", "rag: mark test as RAG module test"
    )
    config.addinivalue_line(
        "markers", "agents: mark test as agents module test"
    )