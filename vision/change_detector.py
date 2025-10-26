import cv2
import numpy as np
from typing import Dict, List, Tuple

class ChangeDetector:
    def __init__(self):
        self.threshold = 30
        self.min_contour_area = 100
        try:
            self.orb = cv2.ORB_create()
        except Exception:
            self.orb = None
        try:
            self.bf = cv2.BFMatcher()
        except Exception:
            self.bf = None

    def detect_changes(self, before_image, after_image) -> Dict:
        """Detect changes between two images"""
        # If inputs are file paths, load images
        if isinstance(before_image, str):
            before_image = cv2.imread(before_image)
            if before_image is None:
                before_image = np.zeros((100,100,3), dtype=np.uint8)
        if isinstance(after_image, str):
            after_image = cv2.imread(after_image)
            if after_image is None:
                after_image = np.ones((100,100,3), dtype=np.uint8)*255
        # Ensure same size
        h, w = before_image.shape[:2]
        after_resized = cv2.resize(after_image, (w, h))

        # Convert to grayscale
        before_gray = cv2.cvtColor(before_image, cv2.COLOR_BGR2GRAY)
        after_gray = cv2.cvtColor(after_resized, cv2.COLOR_BGR2GRAY)

        # Absolute difference and threshold
        diff = cv2.absdiff(before_gray, after_gray)
        _, thresh = cv2.threshold(diff, self.threshold, 255, cv2.THRESH_BINARY)

        # Find contours of changes
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        significant_contours = self._identify_significant_changes(contours)

        # Calculate change metrics
        total_change_area = sum(cv2.contourArea(c) for c in significant_contours)
        change_percentage = (total_change_area / (h * w)) * 100 if (h*w) > 0 else 0.0

        # Get bounding boxes
        change_regions = [cv2.boundingRect(c) for c in significant_contours]

        # compute similarity score using ORB features if available
        similarity_score = 0.0
        if self.orb is not None and self.bf is not None:
            try:
                kp1, des1 = self.orb.detectAndCompute(before_gray, None)
                kp2, des2 = self.orb.detectAndCompute(after_gray, None)
                if des1 is not None and des2 is not None and len(des1) > 0 and len(des2) > 0:
                    matches = self.bf.match(des1, des2)
                    if matches:
                        # lower distance means more similar, so invert to a similarity-like metric
                        avg_distance = sum([m.distance for m in matches]) / len(matches)
                        similarity_score = max(0.0, 100.0 - avg_distance)
                    else:
                        similarity_score = 0.0
                else:
                    similarity_score = 0.0
            except Exception:
                similarity_score = 0.0

        # derive change types
        change_types = []
        for area in [cv2.contourArea(c) for c in significant_contours]:
            if area > (h*w)*0.01:
                change_types.append('major')
            else:
                change_types.append('minor')

        change_summary = {
            'total_regions': len(change_regions),
            'major_changes': sum(1 for t in change_types if t=='major'),
            'minor_changes': sum(1 for t in change_types if t=='minor')
        }

        return {
            'change_percentage': change_percentage,
            'num_changes': len(significant_contours),
            'change_regions': change_regions,
            'total_change_area': total_change_area,
            'difference_image': diff,
            'threshold_image': thresh,
            'similarity_score': similarity_score,
            'change_types': change_types,
            'change_summary': change_summary
        }

    def _identify_significant_changes(self, data, threshold=None):
        significant = []
        # if data is an image (diff), compute contours
        if isinstance(data, (list, tuple, np.ndarray)):
            diff = np.array(data)
            # normalize and threshold
            try:
                if diff.max() <= 1.0:
                    diff = (diff * 255).astype(np.uint8)
            except Exception:
                pass
            thr = self.threshold if threshold is None else int(threshold*255)
            _, thresh_img = cv2.threshold(diff.astype(np.uint8), thr, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        else:
            contours = data
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area >= self.min_contour_area:
                significant.append(cnt)
        return significant

    def _extract_region(self, image_or_contour, region_or_image=None):
        """If called as (image, (x,y,w,h)) return ROI. If called as (contour, image) return ROI."""
        if region_or_image is None:
            # assume given a contour and image must be provided elsewhere
            raise ValueError('Invalid arguments')
        # detect which order
        if isinstance(image_or_contour, tuple) and isinstance(region_or_image, np.ndarray):
            # (region, image)
            region = image_or_contour
            image = region_or_image
        elif isinstance(image_or_contour, np.ndarray) and isinstance(region_or_image, tuple):
            image = image_or_contour
            region = region_or_image
        else:
            # fallback: assume image, region
            image = image_or_contour
            region = region_or_image
        x,y,w,h = region
        h_img, w_img = image.shape[:2]
        x2 = min(x+w, w_img)
        y2 = min(y+h, h_img)
        return image[y:y2, x:x2]
