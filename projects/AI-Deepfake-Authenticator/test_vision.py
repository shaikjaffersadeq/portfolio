import os
import argparse
from src.vision.spatial_detector import SpatialArtifactDetector

def main():
    parser = argparse.ArgumentParser(description="Test Spatial Vision Detector")
    parser.add_argument("--faces_dir", type=str, default="data/processed/sample/faces", help="Path to cropped faces directory")
    args = parser.parse_args()

    faces_path = args.faces_dir

    if not os.path.exists(faces_path) or not os.listdir(faces_path):
        print(f"[!] Error: Face crops directory not found or empty at '{faces_path}'.")
        print("    Ensure Phase 1 ingestion ran successfully first.")
        return

    print(f"[*] Initializing Spatial Vision Detector...")
    detector = SpatialArtifactDetector()

    print(f"[*] Scanning face frames in: {faces_path}")
    results = detector.analyze_face_directory(faces_path)

    print("\n--- Visual Analysis Report ---")
    print(f"Frames Analyzed     : {results['total_frames_analyzed']}")
    print(f"Mean Fake Risk      : {results['mean_fake_probability']:.4f}")
    print(f"Authenticity Index  : {results['authenticity_index']:.2f}%")
    print("------------------------------\n")
    print("[✓] Spatial vision test complete.")

if __name__ == "__main__":
    main()