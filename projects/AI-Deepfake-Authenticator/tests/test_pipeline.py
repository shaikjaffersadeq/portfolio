import os
import sys
import tempfile
from pathlib import Path
import cv2
import numpy as np
import pytest

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.audio.acoustic_detector import AcousticForensicDetector
from src.fusion.multimodal_scorer import MultimodalFusionScorer
from src.fusion.report_generator import ForensicReportGenerator
from src.vision.spatial_detector import SpatialArtifactDetector
from src.vision.temporal_detector import TemporalConsistencyDetector

@pytest.fixture
def scorer():
    """Initializes a standard multimodal fusion scorer instance."""
    return MultimodalFusionScorer(
        spatial_weight=0.45,
        temporal_weight=0.25,
        acoustic_weight=0.30
    )


@pytest.fixture
def dummy_image_file():
    """Creates a temporary 224x224 RGB image for vision testing."""
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    img = np.random.randint(50, 200, (224, 224, 3), dtype=np.uint8)
    cv2.imwrite(temp_file.name, img)
    temp_file.close()
    yield temp_file.name
    if os.path.exists(temp_file.name):
        os.remove(temp_file.name)

def test_scorer_authentic_fusion(scorer):
    """Verifies that high-authenticity unimodal scores yield an authentic verdict."""
    spatial_report = {"authenticity_index": 88.0}
    temporal_report = {"temporal_authenticity_index": 90.0}
    acoustic_report = {"acoustic_authenticity_index": 85.0}

    result = scorer.fuse_predictions(spatial_report, temporal_report, acoustic_report)

    assert result["overall_authenticity_index"] >= 75.0
    assert result["verdict"] == "AUTHENTIC / ORIGINAL"
    assert result["risk_level"] == "LOW RISK"

def test_scorer_forensic_veto_rule(scorer):
    """
    Verifies that localized visual tampering (< 52%) triggers the Forensic Veto,
    preventing genuine audio from bailing out a manipulated face.
    """
    spatial_report = {"authenticity_index": 35.0}
    temporal_report = {"temporal_authenticity_index": 85.0}
    acoustic_report = {"acoustic_authenticity_index": 90.0}

    result = scorer.fuse_predictions(spatial_report, temporal_report, acoustic_report)

    assert result["overall_authenticity_index"] < 58.0
    assert "Tampering localized" in result["forensic_note"]
    assert result["risk_level"] in ["HIGH RISK", "LIKELY MANIPULATED / SYNTHETIC", "SUSPICIOUS / INCONCLUSIVE"]

def test_scorer_missing_modality(scorer):
    """Verifies weight renormalization when video media has no audio track."""
    spatial_report = {"authenticity_index": 80.0}
    temporal_report = {"temporal_authenticity_index": 80.0}
    acoustic_report = {"error": "No audio"}

    result = scorer.fuse_predictions(spatial_report, temporal_report, acoustic_report)

    assert result["overall_authenticity_index"] == 80.0
    assert "acoustic" not in result["active_weights"]

def test_spatial_detector_evaluation(dummy_image_file):
    """Verifies that the spatial artifact detector returns a bounded authenticity index."""
    detector = SpatialArtifactDetector()
    score = detector.evaluate_face_authenticity(dummy_image_file)

    assert isinstance(score, float)
    assert 0.0 <= score <= 100.0

def test_temporal_detector_optical_flow():
    """Verifies that frame difference and motion instability computation succeed."""
    detector = TemporalConsistencyDetector()
    frame1 = np.zeros((100, 100), dtype=np.uint8)
    frame2 = np.ones((100, 100), dtype=np.uint8) * 20

    instability = detector.calculate_frame_difference(frame1, frame2)
    assert isinstance(instability, float)
    assert instability >= 0.0

def test_report_generator_sha256(dummy_image_file):
    """Verifies that the cryptographic SHA-256 hash generator outputs a valid 64-char string."""
    reporter = ForensicReportGenerator()
    sha256_hash = reporter.compute_sha256(dummy_image_file)

    assert len(sha256_hash) == 64
    assert isinstance(sha256_hash, str)

def test_acoustic_detector_initialization():
    """Verifies that the acoustic detector initializes with the configured sample rate."""
    detector = AcousticForensicDetector(sample_rate=16000)
    assert detector.sample_rate == 16000
