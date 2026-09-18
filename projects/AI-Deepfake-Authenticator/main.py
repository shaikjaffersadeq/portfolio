import os
import argparse
from src.ingestion.processor import MediaProcessor
from src.vision.spatial_detector import SpatialArtifactDetector
from src.vision.temporal_detector import TemporalConsistencyDetector
from src.audio.acoustic_detector import AcousticForensicDetector
from src.fusion.multimodal_scorer import MultimodalFusionScorer


def run_authenticator(video_path: str):
    if not os.path.exists(video_path):
        print(f"[!] Target file '{video_path}' does not exist.")
        return

    base_name = os.path.splitext(os.path.basename(video_path))[0]
    processed_dir = os.path.join("data", "processed", base_name)
    audio_output = os.path.join(processed_dir, "audio_16k.wav")
    faces_output = os.path.join(processed_dir, "faces")

    print("\n=======================================================")
    print("      AI MULTIMODAL DEEPFAKE & SYNTHETIC AUTHENTICATOR  ")
    print("=======================================================\n")
    print(f"[*] Target Video: {video_path}")

    # 1. Media Separation
    print("\n--- [1/4] Media Ingestion & Face Extraction ---")
    processor = MediaProcessor()
    audio_ready = processor.extract_audio(video_path, audio_output)
    crop_count = processor.extract_face_crops(video_path, faces_output, frame_interval=5)
    print(f"  -> Extracted {crop_count} faces | Audio ready: {audio_ready}")

    # 2. Spatial Forensics
    print("\n--- [2/4] Spatial Artifact Detection (EfficientNet) ---")
    spatial_detector = SpatialArtifactDetector()
    spatial_report = spatial_detector.analyze_face_directory(faces_output)
    print(f"  -> Spatial Authenticity : {spatial_report.get('authenticity_index', 'N/A')}%")

    # 3. Temporal Forensics
    print("\n--- [3/4] Temporal Consistency Analysis (Optical Flow) ---")
    temporal_detector = TemporalConsistencyDetector()
    temporal_report = temporal_detector.analyze_sequence(faces_output)
    print(f"  -> Temporal Authenticity: {temporal_report.get('temporal_authenticity_index', 'N/A')}%")

    # 4. Acoustic Forensics
    print("\n--- [4/4] Acoustic Forensics (Mel-Spectrogram + ResNet) ---")
    acoustic_report = {}
    if audio_ready and os.path.exists(audio_output):
        acoustic_detector = AcousticForensicDetector()
        audio_report = acoustic_detector.analyze_audio_track(audio_output)
        print(f"  -> Acoustic Authenticity: {audio_report.get('acoustic_authenticity_index', 'N/A')}%")
    else:
        audio_report = {"error": "No audio stream available."}
        print("  -> Skipped (no audio stream found).")

    # Multimodal Tri-Branch Fusion
    scorer = MultimodalFusionScorer()
    verdict_data = scorer.fuse_predictions(spatial_report, temporal_report, audio_report)

    # Output Card
    print("\n=======================================================")
    print("                 FINAL FORENSIC VERDICT                ")
    print("=======================================================")
    print(f" Authenticity Index   : {verdict_data['overall_authenticity_index']}%")
    print(f" Verdict              : {verdict_data['verdict']}")
    print(f" Risk Assessment      : {verdict_data['risk_level']}")
    print("-------------------------------------------------------")
    print(f" - Spatial Score      : {verdict_data['sub_scores']['spatial_visual']}% (Weight: 40%)")
    print(f" - Temporal Score     : {verdict_data['sub_scores']['temporal_coherence']}% (Weight: 30%)")
    print(f" - Acoustic Score     : {verdict_data['sub_scores']['acoustic_spectrum']}% (Weight: 30%)")
    print("=======================================================\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multimodal Deepfake Authenticator")
    parser.add_argument("--video", type=str, default="data/raw/sample.mp4", help="Path to input video")
    args = parser.parse_args()

    run_authenticator(args.video)