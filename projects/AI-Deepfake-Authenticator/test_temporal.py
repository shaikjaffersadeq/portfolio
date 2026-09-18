import os
import argparse
from src.vision.temporal_detector import TemporalConsistencyDetector

def main():
    parser = argparse.ArgumentParser(description="Test Temporal Consistency Detector")
    parser.add_argument("--faces_dir", type=str, default="data/processed/sample/faces", help="Path to cropped faces")
    args = parser.parse_args()

    faces_path = args.faces_dir

    if not os.path.exists(faces_path) or len(os.listdir(faces_path)) < 2:
        print(f"[!] Error: Need at least 2 face crops in '{faces_path}' to evaluate temporal transitions.")
        return

    print(f"[*] Initializing Temporal Consistency Detector (Optical Flow & Inter-frame Variance)...")
    detector = TemporalConsistencyDetector()

    print(f"[*] Scanning temporal transitions across frames in: {faces_path}")
    report = detector.analyze_sequence(faces_path)

    print("\n--- Temporal Consistency Report ---")
    print(f"Transitions Evaluated    : {report['evaluated_transitions']}")
    print(f"Mean Temporal Instability: {report['mean_temporal_instability']}")
    print(f"High-Jitter Anomaly Cues : {report['detected_flicker_events']}")
    print(f"Temporal Authenticity    : {report['temporal_authenticity_index']:.2f}%")
    print("-----------------------------------\n")
    print("[✓] Temporal sequence evaluation complete.")

if __name__ == "__main__":
    main()