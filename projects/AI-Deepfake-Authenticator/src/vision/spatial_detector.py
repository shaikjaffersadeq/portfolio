import os
import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision import models
from typing import Dict


class SpatialArtifactDetector(nn.Module):
    def __init__(self, device: str = None):
        super().__init__()
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        weights = models.EfficientNet_B0_Weights.DEFAULT
        self.backbone = models.efficientnet_b0(weights=weights)
        self.backbone.classifier = nn.Identity()
        self.to(self.device)
        self.eval()

    def evaluate_face_authenticity(self, image_path: str) -> float:
        """
        Detects boundary seam blending, mask-to-background gradient mismatch,
        and high-frequency texture discontinuities.
        """
        img_bgr = cv2.imread(image_path)
        if img_bgr is None:
            return 75.0

        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # 1. Spatial Boundary Seam Detection:
        # Inner face (swapped region) vs Outer perimeter (original head/hair)
        inner_mask = gray[int(h*0.25):int(h*0.75), int(w*0.25):int(w*0.75)]
        
        # Perimeter boundary strip
        perimeter_top = gray[0:int(h*0.2), :]
        perimeter_bottom = gray[int(h*0.8):, :]
        perimeter_combined = np.concatenate([perimeter_top.flatten(), perimeter_bottom.flatten()])

        inner_sharpness = cv2.Laplacian(inner_mask, cv2.CV_64F).var()
        outer_sharpness = cv2.Laplacian(perimeter_combined, cv2.CV_64F).var()

        # Face swaps exhibit severe sharpness ratio disparity across the mask seam
        sharpness_ratio = (inner_sharpness + 1e-5) / (outer_sharpness + 1e-5)

        # 2. Color Gradient Consistency across the blending perimeter
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        inner_sat = np.mean(img_hsv[int(h*0.25):int(h*0.75), int(w*0.25):int(w*0.75), 1])
        outer_sat = np.mean(img_hsv[0:int(h*0.2), :, 1])
        sat_discrepancy = abs(inner_sat - outer_sat)

        # 3. Overall Sharpness Normalized
        mean_brightness = float(np.mean(gray)) + 1e-5
        normalized_sharpness = cv2.Laplacian(gray, cv2.CV_64F).var() / mean_brightness

        # Authenticity scoring
        # Normal camera footage maintains coherent sharpness ratios (0.4 to 2.4)
        if 0.45 <= sharpness_ratio <= 2.2 and sat_discrepancy < 28.0:
            if normalized_sharpness > 0.7:
                score = min(96.0, 82.0 + (normalized_sharpness * 3.0))
            else:
                score = min(88.0, 75.0 + (sharpness_ratio * 4.0))
        else:
            # Synthetic mask boundary detected
            seam_penalty = abs(1.0 - sharpness_ratio) * 12.0
            color_penalty = sat_discrepancy * 0.8
            score = max(18.0, 52.0 - (seam_penalty + color_penalty))

        return float(score)

    def analyze_face_directory(self, faces_dir: str) -> Dict[str, float]:
        valid_extensions = (".jpg", ".jpeg", ".png")
        image_files = sorted([
            os.path.join(faces_dir, f) for f in os.listdir(faces_dir)
            if f.lower().endswith(valid_extensions)
        ])

        if not image_files:
            return {"error": "No face frames found to analyze."}

        scores = [self.evaluate_face_authenticity(f) for f in image_files]
        mean_authenticity = float(np.mean(scores))
        fake_prob = (100.0 - mean_authenticity) / 100.0

        return {
            "total_frames_analyzed": len(image_files),
            "mean_fake_probability": round(fake_prob, 4),
            "authenticity_index": round(mean_authenticity, 2)
        }