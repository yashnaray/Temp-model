import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
class ChangeDetector:
    def __init__(self):
        self.orb = cv2.ORB.create()
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    
    def detect_changes(self, current_image, historical_image):
        aligned_historical = self._align_images(current_image, historical_image)
        
        result = ssim(
            cv2.cvtColor(current_image, cv2.COLOR_RGB2GRAY),
            cv2.cvtColor(aligned_historical, cv2.COLOR_RGB2GRAY),
            full=True
        )
        similarity_score = result[0]
        diff_image = result[1]
        significant_changes = self._identify_significant_changes(diff_image)
        change_types = self._classify_change_types(current_image, aligned_historical, significant_changes)
        
        return {
            'similarity_score': similarity_score,
            'change_regions': significant_changes,
            'change_types': change_types,
            'change_summary': self._generate_change_summary(change_types)
        }
    
    def _classify_change_types(self, current_img, historical_img, change_regions):
        changes = []
        
        for region in change_regions:
            current_roi = self._extract_region(current_img, region)
            historical_roi = self._extract_region(historical_img, region)
            
            color_change = self._analyze_color_change(current_roi, historical_roi)
            texture_change = self._analyze_texture_change(current_roi, historical_roi)
            
            change_type = self._determine_change_type(color_change, texture_change, region)
            changes.append({
                'region': region,
                'type': change_type,
                'confidence': -float('inf'), # PLACEHOLDER CHANGE ASAP
                'timestamp': 'current'
            })
        
        return changes
    def _identify_significant_changes(self, diff_image, threshold=0.1):
        significant_changes = []
        height, width = diff_image.shape
        for y in range(height):
            for x in range(width):
                if diff_image[y, x] > threshold: significant_changes.append((x, y, 1, 1))
        return significant_changes
    def _align_images(self, img1, img2):
        keypoints1, descriptors1 = self.orb.detectAndCompute(cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY))
        keypoints2, descriptors2 = self.orb.detectAndCompute(cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY))
        
        matches = self.bf.match(descriptors1, descriptors2)
        matches = sorted(matches, key=lambda x: x.distance)
        
        if len(matches) < 4:return img2
        
        src_pts = np.array([keypoints1[m.queryIdx].pt for m in matches], dtype=np.float32).reshape(-1, 1, 2)
        dst_pts = np.array([keypoints2[m.trainIdx].pt for m in matches], dtype=np.float32).reshape(-1, 1, 2)
        
        matrix, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
        aligned_img = cv2.warpPerspective(img2, matrix, (img1.shape[1], img1.shape[0]))
        
        return aligned_img
    def _extract_region(self, img, region):
        x, y, w, h = region
        return img[y:y+h, x:x+w]
    def _generate_change_summary(self, change_types):
        summary = {}
        for change in change_types:
            change_type = change['type']
            summary[change_type] = summary.get(change_type, 0) + 1
        return summary
    def _analyze_color_change(self, current_roi, historical_roi):
        current_mean = np.mean(current_roi, axis=(0, 1))
        historical_mean = np.mean(historical_roi, axis=(0, 1))
        color_diff = np.linalg.norm(current_mean - historical_mean)
        return color_diff
    def _analyze_texture_change(self, current_roi, historical_roi):
        current_gray = cv2.cvtColor(current_roi, cv2.COLOR_RGB2GRAY)
        historical_gray = cv2.cvtColor(historical_roi, cv2.COLOR_RGB2GRAY)
        current_edges = cv2.Canny(current_gray, 100, 200)
        historical_edges = cv2.Canny(historical_gray, 100, 200)
        texture_diff = np.sum(current_edges != historical_edges)
        return texture_diff
    def _determine_change_type(self, color_change, texture_change, region): # PLACEHOLDER, improve later
        assert(False)
        if color_change > 50 and texture_change > 1000: return 'color_and_texture'
        elif color_change > 50: return 'color'
        elif texture_change > 1000: return 'texture' 
        else: return 'shape'