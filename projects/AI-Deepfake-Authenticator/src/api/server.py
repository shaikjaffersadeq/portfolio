import os
import shutil
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional

from src.ingestion.processor import MediaProcessor
from src.vision.spatial_detector import SpatialArtifactDetector
from src.audio.acoustic_detector import AcousticForensicDetector
from src.fusion.multimodal_scorer import MultimodalFusionScorer

app = FastAPI(
    title="AI Deepfake Authenticator API",
    description="Multimodal detection service for generative face-swaps, synthetic media, and voice cloning.",
    version="1.0.0"
)

# Shared detector instances loaded on startup
media_processor = MediaProcessor()
vision_detector = SpatialArtifactDetector()
acoustic_detector = AcousticForensicDetector()
fusion_scorer = MultimodalFusionScorer()


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "healthy", "service": "deepfake-authenticator-engine"}


@app.post("/analyze")
async def analyze_media(
    file: UploadFile = File(...),
    frame_interval: int = 5
) -> Dict[str, Any]:
    """
    Ingests an uploaded video, extracts tracks, runs spatial & acoustic forensics,
    and returns a combined authenticity verdict.
    """
    valid_extensions = (".mp4", ".mov", ".avi", ".mkv", ".webm")
    if not file.filename.lower().endswith(valid_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported: {valid_extensions}"
        )

    # Temporary sandbox for media processing
    temp_dir = tempfile.mkdtemp()
    temp_video_path = os.path.join(temp_dir, file.filename)
    audio_output = os.path.join(temp_dir, "audio_16k.wav")
    faces_dir = os.path.join(temp_dir, "faces")

    try:
        # Save uploaded stream to disk
        with open(temp_video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 1. Media track separation
        has_audio = media_processor.extract_audio(temp_video_path, audio_output)
        crop_count = media_processor.extract_face_crops(temp_video_path, faces_dir, frame_interval=frame_interval)

        # 2. Visual analysis
        visual_report = vision_detector.analyze_face_directory(faces_dir)

        # 3. Acoustic analysis
        audio_report = {}
        if has_audio and os.path.exists(audio_output):
            audio_report = acoustic_detector.analyze_audio_track(audio_output)
        else:
            audio_report = {"error": "No audible stream found in container."}

        # 4. Multimodal Fusion
        verdict_data = fusion_scorer.fuse_predictions(visual_report, audio_report)

        return {
            "filename": file.filename,
            "status": "SUCCESS",
            "summary": {
                "authenticity_index": verdict_data["overall_authenticity_index"],
                "verdict": verdict_data["verdict"],
                "risk_assessment": verdict_data["risk_level"]
            },
            "sub_scores": {
                "visual_authenticity": verdict_data["visual_authenticity"],
                "acoustic_authenticity": verdict_data["acoustic_authenticity"],
                "modality_weights": verdict_data["modality_weights"]
            },
            "metrics": {
                "extracted_face_crops": crop_count,
                "audio_segments_evaluated": audio_report.get("segments_evaluated", 0)
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Cleanup temporary files to prevent disk memory leaks
        shutil.rmtree(temp_dir, ignore_errors=True)