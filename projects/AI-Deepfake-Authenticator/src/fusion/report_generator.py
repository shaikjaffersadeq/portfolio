import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict


class ForensicReportGenerator:
    @staticmethod
    def compute_sha256(file_path: str) -> str:
        """Calculates SHA-256 checksum for cryptographic chain of custody."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def generate_report(
        self,
        video_path: str,
        verdict_data: Dict[str, Any],
        spatial_report: Dict[str, Any],
        temporal_report: Dict[str, Any],
        acoustic_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Constructs a comprehensive audit log dictionary."""
        file_hash = self.compute_sha256(video_path)
        timestamp = datetime.now(timezone.utc).isoformat()

        report = {
            "forensic_metadata": {
                "report_timestamp_utc": timestamp,
                "media_filename": os.path.basename(video_path),
                "media_sha256": file_hash,
                "authenticator_version": "1.2.0-tri-modal",
            },
            "verdict_summary": {
                "authenticity_index": verdict_data.get("overall_authenticity_index", 0.0),
                "categorical_verdict": verdict_data.get("verdict", "UNKNOWN"),
                "risk_assessment": verdict_data.get("risk_level", "UNKNOWN"),
                "weights_applied": verdict_data.get("active_weights", {}),
            },
            "modality_breakdown": {
                "spatial_visual_forensics": {
                    "authenticity_score": verdict_data["sub_scores"].get("spatial_visual"),
                    "frames_analyzed": spatial_report.get("total_frames_analyzed", 0),
                    "mean_fake_probability": spatial_report.get("mean_fake_probability", 0.0),
                },
                "temporal_continuity_forensics": {
                    "authenticity_score": verdict_data["sub_scores"].get("temporal_coherence"),
                    "transitions_evaluated": temporal_report.get("evaluated_transitions", 0),
                    "flicker_events_flagged": temporal_report.get("detected_flicker_events", 0),
                },
                "acoustic_spectral_forensics": {
                    "authenticity_score": verdict_data["sub_scores"].get("acoustic_spectrum"),
                    "audio_segments_evaluated": acoustic_report.get("segments_evaluated", 0),
                    "mean_synthetic_risk": acoustic_report.get("mean_synthetic_risk", 0.0),
                },
            },
        }
        return report

    def export_json(self, report: Dict[str, Any], output_path: str) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)
        return output_path