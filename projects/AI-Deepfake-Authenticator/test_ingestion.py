import os
import sys
import argparse

print("[*] Script started. Initializing...", flush=True)

from src.ingestion.processor import MediaProcessor

def main():
    parser = argparse.ArgumentParser(description="Test Ingestion Pipeline")
    parser.add_argument("--video", type=str, default="data/raw/sample.mp4", help="Path to input video file")
    args = parser.parse_args()

    video_input = args.video
    print(f"[*] Checking video file: {video_input}", flush=True)

    if not os.path.exists(video_input):
        print(f"[!] Error: File '{video_input}' was not found.")
        print(f"    Current working directory: {os.getcwd()}")
        return

    base_name = os.path.splitext(os.path.basename(video_input))[0]
    output_audio = f"data/processed/{base_name}/audio_16k.wav"
    output_faces = f"data/processed/{base_name}/faces"

    print("[*] Loading MediaProcessor (PyTorch & MTCNN weights)...", flush=True)
    processor = MediaProcessor()
    print("[*] MediaProcessor loaded successfully.", flush=True)

    print("[1/2] Extracting audio stream via FFmpeg...", flush=True)
    audio_success = processor.extract_audio(video_input, output_audio)
    if audio_success:
        print(f"      Audio saved to: {output_audio}", flush=True)
    else:
        print("      Audio extraction failed or video contains no audio track.", flush=True)

    print("[2/2] Extracting face crops (1 frame every 5 frames)...", flush=True)
    crop_count = processor.extract_face_crops(video_input, output_faces, frame_interval=5)
    print(f"      Extracted {crop_count} face crops into: {output_faces}", flush=True)
    print("[✓] Ingestion step complete.", flush=True)

if __name__ == "__main__":
    main()