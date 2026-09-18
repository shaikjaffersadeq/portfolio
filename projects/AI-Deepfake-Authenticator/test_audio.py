import os
import argparse
from src.audio.acoustic_detector import AcousticForensicDetector

def main():
    parser = argparse.ArgumentParser(description="Test Acoustic Forensics Detector")
    parser.add_argument("--audio", type=str, default="data/processed/sample/audio_16k.wav", help="Path to extracted 16kHz audio track")
    args = parser.parse_args()

    audio_file = args.audio

    if not os.path.exists(audio_file):
        print(f"[!] Error: Audio file not found at '{audio_file}'.")
        print("    Run Phase 1 (test_ingestion.py) first to generate the audio track.")
        return

    print(f"[*] Initializing Acoustic Forensic Detector (Mel-Spectrogram + ResNet)...")
    detector = AcousticForensicDetector()

    print(f"[*] Analyzing spectral harmonics: {audio_file}")
    report = detector.analyze_audio_track(audio_file)

    print("\n--- Acoustic Forensics Report ---")
    print(f"Audio Duration       : {report['total_duration_seconds']}s")
    print(f"Segments Evaluated   : {report['segments_evaluated']}")
    print(f"Synthetic Voice Risk : {report['mean_synthetic_risk']:.4f}")
    print(f"Acoustic Authenticity: {report['acoustic_authenticity_index']:.2f}%")
    print("---------------------------------\n")
    print("[✓] Acoustic forensics analysis complete.")

if __name__ == "__main__":
    main()