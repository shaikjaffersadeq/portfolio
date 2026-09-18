from typing import Dict, Any


class MultimodalFusionScorer:
    def __init__(
        self,
        spatial_weight: float = 0.45,
        temporal_weight: float = 0.25,
        acoustic_weight: float = 0.30
    ):
        self.spatial_weight = spatial_weight
        self.temporal_weight = temporal_weight
        self.acoustic_weight = acoustic_weight

    def fuse_predictions(
        self,
        spatial_report: Dict[str, Any],
        temporal_report: Dict[str, Any],
        acoustic_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        has_spatial = "authenticity_index" in spatial_report and "error" not in spatial_report
        has_temporal = "temporal_authenticity_index" in temporal_report and "error" not in temporal_report
        has_acoustic = "acoustic_authenticity_index" in acoustic_report and "error" not in acoustic_report

        valid_scores = []
        weighted_sum = 0.0
        active_weights = {}

        if has_spatial:
            s_score = spatial_report["authenticity_index"]
            weighted_sum += s_score * self.spatial_weight
            active_weights["spatial"] = self.spatial_weight
            valid_scores.append(("spatial", s_score))

        if has_temporal:
            t_score = temporal_report["temporal_authenticity_index"]
            weighted_sum += t_score * self.temporal_weight
            active_weights["temporal"] = self.temporal_weight
            valid_scores.append(("temporal", t_score))

        if has_acoustic:
            a_score = acoustic_report["acoustic_authenticity_index"]
            weighted_sum += a_score * self.acoustic_weight
            active_weights["acoustic"] = self.acoustic_weight
            valid_scores.append(("acoustic", a_score))

        total_weight = sum(active_weights.values())
        if total_weight == 0:
            return {"verdict": "ERROR", "overall_authenticity_index": 0.0, "risk_level": "FAILED"}

        raw_index = weighted_sum / total_weight

        # --- FORENSIC VETO PRINCIPLE ---
        # If any primary modality shows clear generative tampering (< 52%),
        # real secondary tracks (e.g. real audio) cannot override it.
        min_modality, min_score = min(valid_scores, key=lambda x: x[1])
        
        if min_score < 52.0:
            # Anchor the final score to the compromised modality
            final_index = round((min_score * 0.70) + (raw_index * 0.30), 2)
            tamper_flag = f"Tampering localized in {min_modality} modality."
        else:
            final_index = round(raw_index, 2)
            tamper_flag = "No severe unimodal tampering detected."

        # Calibrated Forensic Risk Scale
        if final_index >= 75.0:
            verdict = "AUTHENTIC / ORIGINAL"
            risk_level = "LOW RISK"
        elif final_index >= 58.0:
            verdict = "PROBABLE AUTHENTIC (COMPRESSION NOISE)"
            risk_level = "LOW-MODERATE RISK"
        elif final_index >= 45.0:
            verdict = "SUSPICIOUS / INCONCLUSIVE"
            risk_level = "MODERATE RISK"
        elif final_index >= 28.0:
            verdict = "LIKELY MANIPULATED / SYNTHETIC"
            risk_level = "HIGH RISK"
        else:
            verdict = "CONFIRMED DEEPFAKE / FACE-SWAP"
            risk_level = "CRITICAL RISK"

        return {
            "overall_authenticity_index": final_index,
            "verdict": verdict,
            "risk_level": risk_level,
            "forensic_note": tamper_flag,
            "active_weights": active_weights,
            "sub_scores": {
                "spatial_visual": spatial_report.get("authenticity_index", "N/A"),
                "temporal_coherence": temporal_report.get("temporal_authenticity_index", "N/A"),
                "acoustic_spectrum": acoustic_report.get("acoustic_authenticity_index", "N/A")
            }
        }