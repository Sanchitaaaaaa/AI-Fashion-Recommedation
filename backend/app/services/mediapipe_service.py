import mediapipe as mp
import cv2
import numpy as np
from typing import Dict, Any, Optional, Tuple

# Initialize MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

class BodyAnalyzer:
    def __init__(self):
        self.pose = mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            min_detection_confidence=0.5
        )

    def analyze(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze body measurements from image"""
        try:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w, _ = image.shape

            results = self.pose.process(image_rgb)

            if not results.pose_landmarks:
                return self._empty_result()

            landmarks = results.pose_landmarks.landmark

            # ── Key landmark points ────────────────────────────────────────
            left_shoulder  = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_hip       = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
            right_hip      = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
            left_ankle     = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
            right_ankle    = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]
            left_wrist     = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
            right_wrist    = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
            left_elbow     = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
            right_elbow    = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]

            # ── Pixel measurements ─────────────────────────────────────────
            shoulder_width = abs(right_shoulder.x - left_shoulder.x) * w
            hip_width      = abs(right_hip.x - left_hip.x) * w

            shoulder_y = (left_shoulder.y + right_shoulder.y) / 2 * h
            hip_y      = (left_hip.y + right_hip.y) / 2 * h
            ankle_y    = (left_ankle.y + right_ankle.y) / 2 * h

            torso_len = abs(hip_y - shoulder_y)
            leg_len   = abs(ankle_y - hip_y)

            # ── Bust width: proxy using shoulder + outer arm geometry ──────
            # Bust sits ~25% down from shoulder to hip on the torso.
            # We estimate it as slightly wider than shoulder for females
            # (accounting for MediaPipe under-reporting shoulder extremes).
            bust_width = self._estimate_bust_width(
                image, shoulder_y, hip_y, w, h,
                left_shoulder, right_shoulder, left_elbow, right_elbow
            )

            # ── Waist estimation (multi-strategy) ─────────────────────────
            waist_width = self._estimate_waist_width_robust(
                image, shoulder_y, hip_y, w, h,
                left_shoulder, right_shoulder,
                left_elbow, right_elbow,
                shoulder_width, hip_width
            )

            # ── Ratios ─────────────────────────────────────────────────────
            # Use bust as the "top" measurement — more reliable than shoulders alone
            effective_top = max(bust_width, shoulder_width)

            shoulder_hip_ratio = effective_top / (hip_width + 0.001)
            waist_hip_ratio    = waist_width / (hip_width + 0.001)
            bust_waist_ratio   = effective_top / (waist_width + 0.001)
            leg_torso_ratio    = leg_len / (torso_len + 0.001)

            arm_spread = abs(right_wrist.x - left_wrist.x) * w
            arm_body_ratio = arm_spread / (shoulder_width + 0.001)

            print(f"   shoulder_width={shoulder_width:.1f}  bust_width={bust_width:.1f}  "
                  f"hip_width={hip_width:.1f}  waist_width={waist_width:.1f}")
            print(f"   S/H={shoulder_hip_ratio:.3f}  W/H={waist_hip_ratio:.3f}  "
                  f"B/W={bust_waist_ratio:.3f}  L/T={leg_torso_ratio:.3f}")

            body_type, confidence = self._classify_body_type(
                shoulder_hip_ratio, waist_hip_ratio, bust_waist_ratio
            )

            height_category = self._classify_height(leg_torso_ratio)

            return {
                "body_type":             body_type,
                "body_type_confidence":  confidence,
                "height_category":       height_category,
                "raw_landmarks":         landmarks,
                "features": {
                    "shoulder_hip_ratio": round(shoulder_hip_ratio, 3),
                    "waist_hip_ratio":    round(waist_hip_ratio, 3),
                    "bust_waist_ratio":   round(bust_waist_ratio, 3),
                    "leg_torso_ratio":    round(leg_torso_ratio, 3),
                    "arm_body_ratio":     round(arm_body_ratio, 3),
                }
            }

        except Exception as e:
            print(f"Body analysis error: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._empty_result()

    def _empty_result(self) -> Dict[str, Any]:
        return {
            "body_type":            "Unknown",
            "body_type_confidence": 0.0,
            "height_category":      "Average",
            "raw_landmarks":        None,
            "features": {
                "shoulder_hip_ratio": 0.0,
                "waist_hip_ratio":    0.0,
                "bust_waist_ratio":   0.0,
                "leg_torso_ratio":    0.0,
                "arm_body_ratio":     0.0,
            }
        }

    def _estimate_bust_width(
        self, image, shoulder_y, hip_y, w, h,
        left_shoulder, right_shoulder,
        left_elbow, right_elbow
    ) -> float:
        """
        Estimate bust width at ~22% down the torso from shoulders.
        Strategy:
          1. Try edge detection at bust level.
          2. Fall back to shoulder_width * 1.05 (bust is typically slightly
             wider than MediaPipe-detected shoulder points which clip inner edges).
        """
        try:
            shoulder_width = abs(right_shoulder.x - left_shoulder.x) * w
            bust_y = int(shoulder_y + (hip_y - shoulder_y) * 0.22)

            band = max(4, int(h * 0.025))
            y1 = max(0, bust_y - band)
            y2 = min(h, bust_y + band)

            # Widen horizontal search slightly beyond shoulders
            ls_x = int(left_shoulder.x * w)
            rs_x = int(right_shoulder.x * w)
            margin = int(w * 0.06)
            x_left  = max(0, min(ls_x, rs_x) - margin)
            x_right = min(w, max(ls_x, rs_x) + margin)

            roi = image[y1:y2, x_left:x_right]
            if roi.size == 0:
                raise ValueError("Empty ROI")

            bust_px = self._edge_width(roi)
            if bust_px is None:
                raise ValueError("Edge detection failed")

            # Sanity: bust should be 90%–130% of shoulder width
            if bust_px < shoulder_width * 0.90 or bust_px > shoulder_width * 1.30:
                raise ValueError(f"Bust {bust_px:.1f} outside plausible range")

            return float(bust_px)

        except Exception as ex:
            print(f"   Bust fallback ({ex}): shoulder*1.05")
            shoulder_width = abs(right_shoulder.x - left_shoulder.x) * w
            return shoulder_width * 1.05

    def _estimate_waist_width_robust(
        self, image, shoulder_y, hip_y, w, h,
        left_shoulder, right_shoulder,
        left_elbow, right_elbow,
        shoulder_width, hip_width
    ) -> float:
        """
        Multi-strategy waist estimation (in priority order):

        Strategy 1 — Elbow-based anatomical proxy:
          The elbows hang at approximately waist level when arms are relaxed.
          Waist width ≈ inner distance between elbows (minus arm thickness ~8%).
          This works well on solid-colored outfits where Canny struggles.

        Strategy 2 — Edge detection at waist level (~45% down torso):
          Canny edges with a wider ROI and looser sanity bounds.

        Strategy 3 — Geometric interpolation:
          Waist = hip_width * 0.82  (average female WHR is ~0.75–0.85)
          Avoids the shoulder*0.82 fallback which inflated Apple misclassifications.
        """
        # ── Strategy 1: Elbow-gap proxy ────────────────────────────────────
        try:
            elbow_gap = abs(right_elbow.x - left_elbow.x) * w
            # Arms against body → elbow gap ≈ waist width
            # Arms slightly out → subtract arm thickness (~8% each side)
            arm_thickness_factor = 0.84
            waist_from_elbows = elbow_gap * arm_thickness_factor

            # Sanity: waist 65%–100% of shoulder width, 70%–105% of hip width
            if (shoulder_width * 0.65 <= waist_from_elbows <= shoulder_width * 1.00 and
                    hip_width * 0.70 <= waist_from_elbows <= hip_width * 1.05):
                print(f"   Waist via elbow-gap: {waist_from_elbows:.1f}")
                return float(waist_from_elbows)
            else:
                raise ValueError(f"Elbow waist {waist_from_elbows:.1f} out of bounds")
        except Exception as ex:
            print(f"   Elbow strategy failed: {ex}")

        # ── Strategy 2: Edge detection at waist zone ──────────────────────
        try:
            # Try both 45% and 52% torso positions
            for frac in [0.45, 0.52, 0.40]:
                waist_y = int(shoulder_y + (hip_y - shoulder_y) * frac)
                band = max(5, int(h * 0.04))
                y1 = max(0, waist_y - band)
                y2 = min(h, waist_y + band)

                ls_x = int(left_shoulder.x * w)
                rs_x = int(right_shoulder.x * w)
                margin = int(w * 0.05)
                x_left  = max(0, min(ls_x, rs_x) - margin)
                x_right = min(w, max(ls_x, rs_x) + margin)

                roi = image[y1:y2, x_left:x_right]
                if roi.size == 0:
                    continue

                waist_px = self._edge_width(roi)
                if waist_px is None:
                    continue

                # Relaxed sanity: 60%–100% of shoulder width
                if shoulder_width * 0.60 <= waist_px <= shoulder_width * 1.00:
                    print(f"   Waist via edge detection (frac={frac}): {waist_px:.1f}")
                    return float(waist_px)

            raise ValueError("Edge detection: no valid result at any fraction")
        except Exception as ex:
            print(f"   Edge strategy failed: {ex}")

        # ── Strategy 3: Hip-based geometric interpolation ─────────────────
        # WHR of 0.80 is a reasonable average; avoids the old shoulder*0.82 bug
        # which was shoulder-anchored and caused Apple misclassification
        waist_fallback = hip_width * 0.80
        print(f"   Waist via hip interpolation fallback: {waist_fallback:.1f}")
        return float(waist_fallback)

    def _edge_width(self, roi: np.ndarray) -> Optional[float]:
        """
        Run Canny edge detection on roi and return the 10–90th percentile
        column span. Returns None if fewer than 5 edge columns found.
        """
        gray  = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blur  = cv2.GaussianBlur(gray, (5, 5), 0)
        # Try adaptive threshold — better for solid/low-contrast garments
        edges = cv2.Canny(blur, 20, 80)

        cols_with_edges = np.where(edges.sum(axis=0) > 0)[0]
        if len(cols_with_edges) < 5:
            return None

        left_edge  = np.percentile(cols_with_edges, 10)
        right_edge = np.percentile(cols_with_edges, 90)
        return float(right_edge - left_edge)

    def _classify_body_type(self, s_h: float, w_h: float, b_w: float) -> Tuple[str, float]:
        """
        Classify body type using THREE measurements for much higher accuracy.

        Parameters
        ----------
        s_h : shoulder(bust)_width / hip_width
              > 1.0  → top-heavy
              < 1.0  → bottom-heavy (pear)
              ~1.0   → balanced

        w_h : waist_width / hip_width
              < 0.75 → well-defined waist
              > 0.85 → straighter / fuller midsection

        b_w : bust_width / waist_width
              > 1.20 → pronounced waist definition (hourglass signal)
              < 1.10 → minimal waist definition

        Classification Logic (priority order)
        ──────────────────────────────────────────────────────────────────────
        PEAR              s_h < 0.92
                          Hips clearly wider than shoulders/bust.

        HOURGLASS         0.92 ≤ s_h ≤ 1.12  AND  w_h < 0.78  AND  b_w > 1.18
                          Balanced top/bottom, clearly nipped waist.

        INVERTED TRIANGLE s_h > 1.18  AND  w_h < 0.88
                          Significantly broader shoulders, waist not overly wide.

        APPLE             s_h > 1.08  AND  w_h > 0.88
                          Broad top AND wide/full waist (carries weight in middle).

        RECTANGLE         0.88 ≤ s_h ≤ 1.18  AND  0.78 ≤ w_h ≤ 0.92
                          Balanced proportions, minimal waist definition.
                          (Most common — wide fallback band)

        FALLBACK          Rectangle
        ──────────────────────────────────────────────────────────────────────

        KEY FIX vs old code:
        - Apple threshold raised from w_h ≥ 0.90 → w_h > 0.88  (same)
          BUT s_h raised from > 1.10 → > 1.08, making Apple harder to trigger.
        - Rectangle now explicitly catches 0.88–1.18 S/H range, which is where
          most "normal" bodies (including the olive-dress image) fall.
        - Hourglass requires bust_waist ratio > 1.18 as a THIRD condition,
          preventing false hourglass from slightly low W/H alone.
        """

        print(f"   Classifying: s_h={s_h:.3f}  w_h={w_h:.3f}  b_w={b_w:.3f}")

        # 1. PEAR — hips clearly wider than bust/shoulders
        if s_h < 0.92:
            return "Pear", 0.88

        # 2. HOURGLASS — balanced shoulders & hips, pronounced waist nip
        if 0.92 <= s_h <= 1.12 and w_h < 0.78 and b_w > 1.18:
            return "Hourglass", 0.90

        # 3. INVERTED TRIANGLE — shoulders dominate, waist reasonably defined
        if s_h > 1.18 and w_h < 0.88:
            return "Inverted Triangle", 0.87

        # 4. APPLE — broad top AND wide/full waist
        #    Requires BOTH conditions to be clearly met — avoids false positives
        if s_h > 1.12 and w_h > 0.88:
            return "Apple", 0.85

        # 5. RECTANGLE — balanced all around, moderate waist definition
        #    Widened band: catches most average/athletic builds correctly
        if 0.88 <= s_h <= 1.18 and 0.72 <= w_h <= 0.92:
            return "Rectangle", 0.85

        # 6. FALLBACK — Rectangle is statistically the most common body type
        return "Rectangle", 0.72

    def _classify_height(self, leg_torso_ratio: float) -> str:
        """
        Classify height from leg-to-torso ratio.
        > 1.35  → Tall
        < 1.00  → Petite
        else    → Average
        """
        if leg_torso_ratio > 1.35:
            return "Tall"
        elif leg_torso_ratio < 1.0:
            return "Petite"
        else:
            return "Average"


analyzer = BodyAnalyzer()


def analyze_body_measurements(image: np.ndarray) -> Dict[str, Any]:
    result = analyzer.analyze(image)
    print(f"✅ Body Analysis Complete:")
    print(f"   Body Type:       {result['body_type']} ({result['body_type_confidence']})")
    print(f"   Height Category: {result['height_category']}")
    print(f"   S/H Ratio:       {result['features']['shoulder_hip_ratio']}")
    print(f"   W/H Ratio:       {result['features']['waist_hip_ratio']}")
    print(f"   B/W Ratio:       {result['features']['bust_waist_ratio']}")
    print(f"   Leg/Torso:       {result['features']['leg_torso_ratio']}")
    return result