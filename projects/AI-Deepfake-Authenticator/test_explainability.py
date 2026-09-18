import os
import argparse
from src.vision.spatial_detector import SpatialArtifactDetector
from src.explainability.gradcam import GradCAMExplainer

def main():
    parser = argparse.ArgumentParser(description="Test Explainability Heatmap Generator")
    parser.add_argument("--faces_dir", type=str, default="data/processed/sample/faces", help="Path to cropped faces")
    args = parser.parse_args()

    faces_path = args.faces_dir
    heatmaps_output = "data/processed/sample/heatmaps"

    if not os.path.exists(faces_path) or not os.listdir(faces_path):
        print(f"[!] Face crops directory not found at '{faces_path}'. Run ingestion first.")
        return

    print("[*] Initializing Spatial Model and Grad-CAM Explainer...")
    detector = SpatialArtifactDetector()
    explainer = GradCAMExplainer(model=detector)

    print(f"[*] Generating Grad-CAM heatmaps for suspicious regions...")
    heatmaps = explainer.generate_batch_heatmaps(faces_path, heatmaps_output, max_frames=5)

    print("\n--- Explainability Generation Complete ---")
    print(f"Heatmaps Exported : {len(heatmaps)}")
    print(f"Output Directory  : {heatmaps_output}")
    print("-------------------------------------------\n")
    print("[✓] Explainability test complete. You can open and view the generated heatmap images in VS Code.")

if __name__ == "__main__":
    main()