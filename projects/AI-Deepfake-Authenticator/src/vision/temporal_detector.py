import os
import cv2
import numpy as np
from typing import Dict, Any, List


class TemporalConsistencyDetector:
    def __init__(self, variance_threshold: float = 18.0):
        self.variance_threshold = variance_threshold

    def calculate_frame_difference(self, prev_gray: np.ndarray, curr_gray: np.ndarray) -> float:
        """
        Calculates normalized absolute difference and motion flow variance between two consecutive frames.
        """
        # Absolute frame difference
        diff = cv2.absdiff(prev_gray, curr_gray)
        mean_diff = np.mean(diff)

        # Farneback Dense Optical Flow to measure movement continuity
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, curr_gray, None,
            pyr_scale=0.5, levels=3, winsize=15,
            iterations=3, poly_n=5, poly_sigma=1.2, flags=0
        )
        flow_magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        flow_std = np.std(flow_magnitude)

        # Composite temporal jitter score
        temporal_instability = (mean_diff * 0.4) + (flow_std * 0.6)
        return float(temporal_instability)

    def analyze_sequence(self, faces_dir: str) -> Dict[str, Any]:
        """
        Evaluates temporal stability across all sequentially extracted face crops.
        """
        valid_exts = (".jpg", ".jpeg", ".png")
        frame_files = sorted([
            os.path.join(faces_dir, f) for f in os.listdir(faces_dir)
            if f.lower().endswith(valid_exts)
        ])

        if len(frame_files) < 2:
            return {
                "error": "Sequence too short for temporal evaluation (minimum 2 consecutive face crops required)."
            }

        prev_img = cv2.imread(frame_files[0], cv2.IMREAD_GRAYSCALE)
        instability_scores: List[float] = []
        flicker_events = 0

        for i in range(1, len(frame_files)):
            curr_img = cv2.imread(frame_files[i], cv2.IMREAD_GRAYSCALE)
            
            # Ensure standard matching dimensions
            if prev_img.shape != curr_img.shape:
                curr_img = cv2.resize(curr_img, (prev_img.shape[1], prev_img.shape[0]))

            instability = self.calculate_frame_difference(prev_img, curr_img)
            instability_scores.append(round(instability, 3))

            # Detect sharp unnatural frame-boundary jumps
            if instability > self.variance_threshold:
                flicker_events += 1

            prev_img = curr_img

        mean_instability = float(np.mean(instability_scores))
        flicker_ratio = flicker_events / len(instability_scores)

        # Calculate temporal authenticity index (lower jitter = higher authenticity)
        temporal_authenticity = max(0.0, min(100.0, 100.0 - (mean_instability * 2.5) - (flicker_ratio * 30.0)))

        return {
            "evaluated_transitions": len(instability_scores),
            "mean_temporal_instability": round(mean_instability, 3),
            "detected_flicker_events": flicker_events,
            "temporal_authenticity_index": round(temporal_authenticity, 2),
            "transition_timeline": instability_scores
        }