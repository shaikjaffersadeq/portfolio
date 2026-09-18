import io
import json
import os
from pathlib import Path
import sys
import tempfile
import zipfile

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image
import streamlit as st

from src.audio.acoustic_detector import AcousticForensicDetector
from src.explainability.gradcam import GradCAMExplainer
from src.fusion.multimodal_scorer import MultimodalFusionScorer
from src.fusion.report_generator import ForensicReportGenerator
from src.ingestion.processor import MediaProcessor
from src.vision.spatial_detector import SpatialArtifactDetector
from src.vision.temporal_detector import TemporalConsistencyDetector

st.set_page_config(
    page_title="AI Deepfake Authenticator",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Multimodal AI Deepfake & Synthetic Media Authenticator")
st.caption("Tri-modal forensic engine inspecting spatial tampering, inter-frame flow continuity, and vocoder frequencies.")

# Sidebar Configuration
st.sidebar.header("Pipeline Weights")
spatial_w = st.sidebar.slider("Spatial Weight", 0.1, 0.8, 0.45, 0.05)
temporal_w = st.sidebar.slider("Temporal Weight", 0.1, 0.8, 0.25, 0.05)
acoustic_w = round(max(0.0, 1.0 - (spatial_w + temporal_w)), 2)
st.sidebar.info(f"Acoustic Weight Auto-Balanced: **{acoustic_w}**")

uploaded_file = st.sidebar.file_uploader("Upload video for analysis", type=["mp4", "mov", "avi", "mkv"])


def create_evidence_zip(audit_json, faces_dir, heatmaps_dir, audio_path):
    """Packages all forensic artifacts into an in-memory ZIP bundle."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("forensic_audit_report.json", json.dumps(audit_json, indent=4))
        
        if os.path.exists(audio_path):
            zip_file.write(audio_path, arcname="extracted_audio/audio_16k.wav")
            
        if os.path.exists(faces_dir):
            for f in os.listdir(faces_dir):
                zip_file.write(os.path.join(faces_dir, f), arcname=f"face_crops/{f}")
                
        if os.path.exists(heatmaps_dir):
            for h in os.listdir(heatmaps_dir):
                zip_file.write(os.path.join(heatmaps_dir, h), arcname=f"gradcam_heatmaps/{h}")

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_video_path = tmp_file.name

    st.subheader("1. Ingested Media Stream")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.video(temp_video_path)
    with col2:
        st.write(f"**Filename:** {uploaded_file.name}")
        st.write(f"**Size:** {round(len(uploaded_file.getvalue()) / (1024 * 1024), 2)} MB")
        run_button = st.button("🚀 Run Complete Forensic Verification", type="primary")

    if run_button:
        with st.spinner("Executing tri-branch forensic pipeline..."):
            base_dir = tempfile.mkdtemp()
            audio_path = os.path.join(base_dir, "audio_16k.wav")
            faces_dir = os.path.join(base_dir, "faces")
            heatmaps_dir = os.path.join(base_dir, "heatmaps")

            processor = MediaProcessor()
            has_audio = processor.extract_audio(temp_video_path, audio_path)
            crop_count = processor.extract_face_crops(temp_video_path, faces_dir, frame_interval=5)

            vision_detector = SpatialArtifactDetector()
            spatial_report = vision_detector.analyze_face_directory(faces_dir)

            temporal_detector = TemporalConsistencyDetector()
            temporal_report = temporal_detector.analyze_sequence(faces_dir)

            acoustic_report = {}
            if has_audio and os.path.exists(audio_path):
                acoustic_detector = AcousticForensicDetector()
                audio_report = acoustic_detector.analyze_audio_track(audio_path)
            else:
                audio_report = {"error": "No audio track available."}

            explainer = GradCAMExplainer(model=vision_detector)
            heatmaps = explainer.generate_batch_heatmaps(faces_dir, heatmaps_dir, max_frames=4)

            scorer = MultimodalFusionScorer(
                spatial_weight=spatial_w,
                temporal_weight=temporal_w,
                acoustic_weight=acoustic_w
            )
            verdict_data = scorer.fuse_predictions(spatial_report, temporal_report, audio_report)

            reporter = ForensicReportGenerator()
            audit_json = reporter.generate_report(temp_video_path, verdict_data, spatial_report, temporal_report, audio_report)
            evidence_zip_bytes = create_evidence_zip(audit_json, faces_dir, heatmaps_dir, audio_path)

        st.divider()

        m1, m2, m3 = st.columns(3)
        m1.metric("Authenticity Score", f"{verdict_data['overall_authenticity_index']}%")
        m2.metric("Verdict", verdict_data["verdict"])
        m3.metric("Risk Level", verdict_data["risk_level"])

        if "forensic_note" in verdict_data:
            st.info(f"📌 **Forensic Note:** {verdict_data['forensic_note']}")

        t1, t2, t3, t4 = st.tabs([
            "👁️ Spatial Vision",
            "⏱️ Temporal Coherence",
            "🎙️ Acoustic Spectrum",
            "🔥 Explainability (Grad-CAM)"
        ])

        with t1:
            st.write(f"**Spatial Score:** `{verdict_data['sub_scores']['spatial_visual']}%`")
            if os.path.exists(faces_dir) and os.listdir(faces_dir):
                crops = [os.path.join(faces_dir, f) for f in os.listdir(faces_dir)[:4]]
                cols = st.columns(len(crops))
                for idx, path in enumerate(crops):
                    cols[idx].image(Image.open(path), caption=f"Face Crop {idx+1}", use_container_width=True)

        with t2:
            st.write(f"**Temporal Score:** `{verdict_data['sub_scores']['temporal_coherence']}%`")
            st.write(f"**Boundary Jitter / Anomaly Cues:** {temporal_report.get('detected_flicker_events', 'N/A')}")
            st.write(f"**Mean Motion Instability:** {temporal_report.get('mean_temporal_instability', 'N/A')}")

        with t3:
            st.write(f"**Acoustic Score:** `{verdict_data['sub_scores']['acoustic_spectrum']}%`")
            if has_audio and os.path.exists(audio_path):
                st.audio(audio_path, format="audio/wav")
                st.write(f"**Mean Synthetic Voice Probability:** {audio_report.get('mean_synthetic_risk', 'N/A')}")
            else:
                st.info("No audio track detected in source media.")

        with t4:
            st.write("Grad-CAM overlays highlighting anomalous pixel clusters (red zones):")
            if heatmaps:
                h_cols = st.columns(len(heatmaps))
                for idx, path in enumerate(heatmaps):
                    h_cols[idx].image(Image.open(path), caption=f"Attention Map {idx+1}", use_container_width=True)

        st.divider()

        # Evidence Export
        st.subheader("📦 Forensic Custody & Evidence Export")
        c_left, c_right = st.columns(2)
        with c_left:
            st.download_button(
                label="📥 Download JSON Audit Report",
                data=json.dumps(audit_json, indent=4),
                file_name=f"audit_{Path(uploaded_file.name).stem}.json",
                mime="application/json",
                use_container_width=True
            )
        with c_right:
            st.download_button(
                label="📦 Download Complete Evidence Vault (.zip)",
                data=evidence_zip_bytes,
                file_name=f"evidence_vault_{Path(uploaded_file.name).stem}.zip",
                mime="application/zip",
                use_container_width=True
            )
else:
    st.info("👈 Upload a media file from the left sidebar to start detection.")