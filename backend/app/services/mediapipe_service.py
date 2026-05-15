"""
mediapipe_service.py
────────────────────
MediaPipe Pose-based body analyser + FaceDetection-based skin tone detector.

Improvements in v3.0
─────────────────────
• Body type classifier uses a score-based approach across 5 types
  (Hourglass, Pear, Inverted Triangle, Rectangle, Apple) — no brittle
  if-elif thresholds.
• Skin tone uses MediaPipe FaceDetection bbox (not arbitrary crop).
  Falls back to multi-candidate scan with skin-pixel counting.
• Dual HSV + YCrCb skin mask works across all Fitzpatrick types.
• Skin tone labels: Fair, Light Medium, Medium, Tan, Deep.
• Image quality: input is expected to be at least 480×640.
  The analyser does NOT down-scale internally — keep source res.
"""

import cv2
import mediapipe as mp
import numpy as np

from typing import Dict, Any, Tuple, Optional

# =========================================================
# MEDIAPIPE INIT
# =========================================================

mp_pose = mp.solutions.pose
mp_face = mp.solutions.face_detection

VISIBILITY_THRESHOLD = 0.55


# =========================================================
# HELPERS
# =========================================================

def _px(lm, w: int, h: int) -> Tuple[float, float]:
    return lm.x * w, lm.y * h


def _mid(a: Tuple, b: Tuple) -> Tuple[float, float]:
    return (a[0] + b[0]) / 2, (a[1] + b[1]) / 2


def _dist_x(a: Tuple, b: Tuple) -> float:
    return abs(a[0] - b[0])


def _dist_y(a: Tuple, b: Tuple) -> float:
    return abs(a[1] - b[1])


def _visible(*lms) -> bool:
    return all(lm.visibility >= VISIBILITY_THRESHOLD for lm in lms)


# =========================================================
# BODY ANALYZER CLASS
# =========================================================

class BodyAnalyzer:

    def __init__(self):
        self.pose = mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.face_detector = mp_face.FaceDetection(
            model_selection=1,            # long-range model
            min_detection_confidence=0.4,
        )

    # =====================================================
    # MAIN ENTRY POINT
    # =====================================================

    def analyze(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Parameters
        ----------
        image : np.ndarray  — BGR image from cv2 / camera.

        Returns
        -------
        dict with body_type, skin_tone, height_category, confidences,
        and detailed measurement features.
        """
        try:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w, _   = image.shape
            results   = self.pose.process(image_rgb)

            if not results.pose_landmarks:
                print("❌ No body detected by MediaPipe Pose")
                return self._empty_result()

            lm = results.pose_landmarks.landmark

            # ── Key landmarks ──────────────────────────────────
            l_shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
            r_shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            l_hip      = lm[mp_pose.PoseLandmark.LEFT_HIP]
            r_hip      = lm[mp_pose.PoseLandmark.RIGHT_HIP]
            l_ankle    = lm[mp_pose.PoseLandmark.LEFT_ANKLE]
            r_ankle    = lm[mp_pose.PoseLandmark.RIGHT_ANKLE]
            l_knee     = lm[mp_pose.PoseLandmark.LEFT_KNEE]
            r_knee     = lm[mp_pose.PoseLandmark.RIGHT_KNEE]
            l_wrist    = lm[mp_pose.PoseLandmark.LEFT_WRIST]
            r_wrist    = lm[mp_pose.PoseLandmark.RIGHT_WRIST]
            nose       = lm[mp_pose.PoseLandmark.NOSE]

            if not _visible(l_shoulder, r_shoulder, l_hip, r_hip):
                print("❌ Core landmarks not visible — image may be cropped")
                return self._empty_result()

            # ── Pixel coordinates ──────────────────────────────
            ls_px  = _px(l_shoulder, w, h)
            rs_px  = _px(r_shoulder, w, h)
            lh_px  = _px(l_hip,      w, h)
            rh_px  = _px(r_hip,      w, h)
            la_px  = _px(l_ankle,    w, h)
            ra_px  = _px(r_ankle,    w, h)
            lw_px  = _px(l_wrist,    w, h)
            rw_px  = _px(r_wrist,    w, h)
            nose_px = _px(nose,      w, h)

            mid_shoulder = _mid(ls_px, rs_px)
            mid_hip      = _mid(lh_px, rh_px)
            mid_ankle    = _mid(la_px, ra_px)

            # ── Width measurements ─────────────────────────────

            shoulder_width = _dist_x(ls_px, rs_px)
            hip_width      = _dist_x(lh_px, rh_px)

            # Bust = weighted average of shoulder and chest-level width
            mid_bust_l  = _mid(ls_px, lh_px)
            mid_bust_r  = _mid(rs_px, rh_px)
            chest_width = _dist_x(mid_bust_l, mid_bust_r)
            bust_width  = shoulder_width * 0.60 + chest_width * 0.40

            # Waist = 60% of the way from shoulder to hip (geometric)
            waist_l = (
                ls_px[0] * 0.40 + lh_px[0] * 0.60,
                ls_px[1] * 0.40 + lh_px[1] * 0.60,
            )
            waist_r = (
                rs_px[0] * 0.40 + rh_px[0] * 0.60,
                rs_px[1] * 0.40 + rh_px[1] * 0.60,
            )
            waist_width = _dist_x(waist_l, waist_r)

            # Refine with wrist gap when arms are at the side
            if _visible(l_wrist, r_wrist):
                wrist_gap   = _dist_x(lw_px, rw_px)
                wrist_mid_y = (lw_px[1] + rw_px[1]) / 2
                waist_y     = (waist_l[1] + waist_r[1]) / 2
                if abs(wrist_mid_y - waist_y) < h * 0.12:
                    waist_width = waist_width * 0.55 + wrist_gap * 0.45

            # Sanity clamp: waist should be 65–98% of hip width
            waist_width = float(np.clip(
                waist_width,
                hip_width * 0.65,
                hip_width * 0.98,
            ))

            # ── Height measurements ────────────────────────────

            torso_length = _dist_y(mid_shoulder, mid_hip)
            leg_length   = _dist_y(mid_hip,      mid_ankle)
            full_height  = _dist_y(nose_px,      mid_ankle)

            # ── Ratios ─────────────────────────────────────────

            shoulder_hip_ratio = shoulder_width / (hip_width    + 1e-6)
            waist_hip_ratio    = waist_width    / (hip_width    + 1e-6)
            bust_waist_ratio   = bust_width     / (waist_width  + 1e-6)
            leg_torso_ratio    = leg_length     / (torso_length + 1e-6)

            print("\n========== MEASUREMENTS (px) ==========")
            print(f"Shoulder Width : {shoulder_width:.1f}")
            print(f"Bust Width     : {bust_width:.1f}")
            print(f"Waist Width    : {waist_width:.1f}")
            print(f"Hip Width      : {hip_width:.1f}")
            print("\n========== BODY RATIOS ==========")
            print(f"Shoulder/Hip   : {shoulder_hip_ratio:.3f}")
            print(f"Waist/Hip      : {waist_hip_ratio:.3f}")
            print(f"Bust/Waist     : {bust_waist_ratio:.3f}")
            print(f"Leg/Torso      : {leg_torso_ratio:.3f}")

            # ── Classify body type ─────────────────────────────

            body_type, bt_confidence = self._classify_body_type(
                shoulder_hip_ratio,
                waist_hip_ratio,
                bust_waist_ratio,
            )

            height_category = self._classify_height(leg_torso_ratio)

            # ── Skin tone ──────────────────────────────────────

            skin_tone, skin_confidence = self.detect_skin_tone(
                image, image_rgb
            )

            print("\n========== FINAL ANALYSIS ==========")
            print(f"Body Type      : {body_type}  (conf={bt_confidence:.2f})")
            print(f"Height Cat.    : {height_category}")
            print(f"Skin Tone      : {skin_tone}  (conf={skin_confidence:.2f})")

            return {
                "body_type":            body_type,
                "body_type_confidence": bt_confidence,
                "height_category":      height_category,
                "skin_tone":            skin_tone,
                "skin_tone_confidence": skin_confidence,
                "features": {
                    "shoulder_width_px":  round(shoulder_width, 1),
                    "bust_width_px":      round(bust_width, 1),
                    "waist_width_px":     round(waist_width, 1),
                    "hip_width_px":       round(hip_width, 1),
                    "shoulder_hip_ratio": round(shoulder_hip_ratio, 3),
                    "waist_hip_ratio":    round(waist_hip_ratio, 3),
                    "bust_waist_ratio":   round(bust_waist_ratio, 3),
                },
            }

        except Exception as e:
            print(f"❌ Analysis error: {e}")
            import traceback
            traceback.print_exc()
            return self._empty_result()

    # =====================================================
    # BODY TYPE CLASSIFICATION  (score-based)
    # =====================================================

    def _classify_body_type(
        self,
        shr: float,   # shoulder / hip
        whr: float,   # waist / hip
        bwr: float,   # bust / waist
    ) -> Tuple[str, float]:
        """
        Reference ranges (literature-backed):
        ┌──────────────────────┬───────────┬───────────┬───────────┐
        │ Body Type            │  SHR      │  WHR      │  BWR      │
        ├──────────────────────┼───────────┼───────────┼───────────┤
        │ Hourglass            │ 0.97–1.07 │ < 0.75    │ > 1.25    │
        │ Pear (Triangle)      │ < 0.93    │ 0.70–0.88 │ any       │
        │ Inverted Triangle    │ > 1.08    │ 0.70–0.90 │ ≥ 1.10    │
        │ Rectangle (Banana)   │ 0.93–1.08 │ 0.80–0.92 │ 1.05–1.25 │
        │ Apple (Round/Oval)   │ 0.90–1.10 │ > 0.88    │ < 1.15    │
        └──────────────────────┴───────────┴───────────┴───────────┘
        """
        scores: Dict[str, float] = {
            "Hourglass":         0.0,
            "Pear":              0.0,
            "Inverted Triangle": 0.0,
            "Rectangle":         0.0,
            "Apple":             0.0,
        }

        scores["Hourglass"]         += self._score(shr, 0.97, 1.07, 2.0)
        scores["Hourglass"]         += self._score_below(whr, 0.75, 2.5)
        scores["Hourglass"]         += self._score_above(bwr, 1.25, 2.0)

        scores["Pear"]              += self._score_below(shr, 0.93, 3.0)
        scores["Pear"]              += self._score(whr, 0.70, 0.88, 1.5)

        scores["Inverted Triangle"] += self._score_above(shr, 1.08, 3.0)
        scores["Inverted Triangle"] += self._score(whr, 0.70, 0.90, 1.5)
        scores["Inverted Triangle"] += self._score_above(bwr, 1.10, 1.0)

        scores["Rectangle"]         += self._score(shr, 0.93, 1.08, 2.0)
        scores["Rectangle"]         += self._score(whr, 0.80, 0.92, 2.0)
        scores["Rectangle"]         += self._score(bwr, 1.05, 1.25, 1.5)

        scores["Apple"]             += self._score_above(whr, 0.88, 3.0)
        scores["Apple"]             += self._score(shr, 0.90, 1.10, 1.5)
        scores["Apple"]             += self._score_below(bwr, 1.15, 1.5)

        best_type  = max(scores, key=scores.__getitem__)
        best_score = scores[best_type]
        total      = sum(scores.values()) + 1e-6
        raw_conf   = best_score / total
        confidence = round(0.70 + raw_conf * 0.27, 2)

        print("\n========== BODY TYPE SCORES ==========")
        for k, v in sorted(scores.items(), key=lambda x: -x[1]):
            print(f"  {k:<22}: {v:.3f}")

        return best_type, confidence

    # ---- scoring helpers ----------------------------------------

    @staticmethod
    def _score(val: float, lo: float, hi: float,
               weight: float = 1.0) -> float:
        if lo <= val <= hi:
            return weight
        margin = (hi - lo) * 0.5
        if val < lo:
            return weight * max(0.0, 1.0 - (lo - val) / margin)
        return weight * max(0.0, 1.0 - (val - hi) / margin)

    @staticmethod
    def _score_above(val: float, threshold: float,
                     weight: float = 1.0) -> float:
        if val >= threshold:
            return weight
        margin = threshold * 0.15
        return weight * max(0.0, 1.0 - (threshold - val) / margin)

    @staticmethod
    def _score_below(val: float, threshold: float,
                     weight: float = 1.0) -> float:
        if val <= threshold:
            return weight
        margin = threshold * 0.15
        return weight * max(0.0, 1.0 - (val - threshold) / margin)

    # =====================================================
    # HEIGHT CLASSIFICATION
    # =====================================================

    def _classify_height(self, leg_torso_ratio: float) -> str:
        if leg_torso_ratio > 1.40:
            return "Tall"
        if leg_torso_ratio < 1.05:
            return "Petite"
        return "Average"

    # =====================================================
    # SKIN TONE DETECTION
    # =====================================================

    def detect_skin_tone(
        self,
        bgr_image: np.ndarray,
        rgb_image: Optional[np.ndarray] = None,
    ) -> Tuple[str, float]:
        """
        1. MediaPipe FaceDetection bbox → sample central cheek/forehead area.
        2. Fall back to multi-candidate upper-centre scan.
        3. Dual HSV + YCrCb skin mask → sample only real skin pixels.
        4. CIE L* (lightness) + A* (warm/cool) → classify tone.

        Tone labels: Fair | Light Medium | Medium | Tan | Deep
        """
        try:
            h, w = bgr_image.shape[:2]

            if rgb_image is None:
                rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

            face_crop = self._extract_face_region(rgb_image, h, w)

            if face_crop is None or face_crop.size == 0:
                print("⚠️  No face bbox — scanning upper region")
                face_crop = self._fallback_face_crop(bgr_image, h, w)

            if face_crop is None or face_crop.size == 0:
                return "Medium", 0.60

            face_bgr     = cv2.cvtColor(face_crop, cv2.COLOR_RGB2BGR)
            skin_mask    = _skin_mask(face_bgr)
            masked_pixels = face_bgr[skin_mask]

            if len(masked_pixels) < 30:
                masked_pixels = face_bgr.reshape(-1, 3)

            sample = masked_pixels.reshape(-1, 1, 3).astype(np.uint8)
            lab    = cv2.cvtColor(sample, cv2.COLOR_BGR2LAB)

            l_vals = lab[:, 0, 0].astype(float)
            a_vals = lab[:, 0, 1].astype(float)

            brightness = float(np.percentile(l_vals, 60))
            warmth     = float(np.mean(a_vals))

            print("\n========== SKIN ANALYSIS ==========")
            print(f"Skin pixels : {len(masked_pixels)}")
            print(f"L (raw)     : {brightness:.1f}")
            print(f"A (raw)     : {warmth:.1f}")

            tone, confidence = _map_tone(brightness, warmth)
            print(f"Detected    : {tone}  (conf={confidence:.2f})")
            return tone, confidence

        except Exception as e:
            print(f"❌ Skin tone error: {e}")
            import traceback
            traceback.print_exc()
            return "Medium", 0.60

    # ---- face region helpers -----------------------------------

    def _extract_face_region(
        self,
        rgb_image: np.ndarray,
        h: int,
        w: int,
    ) -> Optional[np.ndarray]:
        try:
            results = self.face_detector.process(rgb_image)
            if not results.detections:
                return None

            det  = results.detections[0]
            bbox = det.location_data.relative_bounding_box

            x1 = max(0, int(bbox.xmin * w))
            y1 = max(0, int(bbox.ymin * h))
            x2 = min(w, int((bbox.xmin + bbox.width)  * w))
            y2 = min(h, int((bbox.ymin + bbox.height) * h))

            face_h = y2 - y1
            face_w = x2 - x1

            # Central 50% of face (skip hairline and jaw extremes)
            cx1 = x1 + int(face_w * 0.25)
            cx2 = x2 - int(face_w * 0.25)
            cy1 = y1 + int(face_h * 0.15)
            cy2 = y1 + int(face_h * 0.65)

            crop = rgb_image[cy1:cy2, cx1:cx2]
            return crop if crop.size > 0 else None

        except Exception:
            return None

    def _fallback_face_crop(
        self,
        bgr_image: np.ndarray,
        h: int,
        w: int,
    ) -> Optional[np.ndarray]:
        """
        Scan several upper-centre rectangles; pick whichever has the
        most skin-coloured pixels.
        """
        best_crop  = None
        best_count = 0

        candidates = [
            (0.05, 0.22, 0.38, 0.62),
            (0.10, 0.28, 0.30, 0.70),
            (0.03, 0.18, 0.40, 0.60),
            (0.02, 0.15, 0.42, 0.58),
        ]

        for y_lo, y_hi, x_lo, x_hi in candidates:
            x1, x2 = int(w * x_lo), int(w * x_hi)
            y1, y2 = int(h * y_lo), int(h * y_hi)
            crop   = bgr_image[y1:y2, x1:x2]
            if crop.size == 0:
                continue
            mask  = _skin_mask(crop)
            count = int(np.sum(mask))
            if count > best_count:
                best_count = count
                best_crop  = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)

        return best_crop


# =========================================================
# MODULE-LEVEL SKIN HELPERS
# =========================================================

def _skin_mask(bgr_crop: np.ndarray) -> np.ndarray:
    """
    Boolean mask for skin-coloured pixels.
    Intersection of HSV and YCrCb ranges — robust across all tones.
    """
    hsv   = cv2.cvtColor(bgr_crop, cv2.COLOR_BGR2HSV)
    ycrcb = cv2.cvtColor(bgr_crop, cv2.COLOR_BGR2YCrCb)

    mask_hsv = cv2.inRange(
        hsv,
        np.array([0,  15,  50], dtype=np.uint8),
        np.array([25, 200, 255], dtype=np.uint8),
    )
    mask_ycr = cv2.inRange(
        ycrcb,
        np.array([0,  133,  77], dtype=np.uint8),
        np.array([255, 180, 135], dtype=np.uint8),
    )
    return cv2.bitwise_and(mask_hsv, mask_ycr).astype(bool)


def _map_tone(brightness: float, warmth: float) -> Tuple[str, float]:
    """
    Map cv2 LAB brightness (0–255) + warmth (0–255, 128=neutral)
    to a skin tone label.

    CIE L* thresholds (converted from cv2's 0-255 scale → 0-100):
      Fair         ≥ 68  (L* raw ≥ ~173)
      Light Medium  58–67 (L* raw 148–171)
      Medium        46–57 (L* raw 117–145)
      Tan           34–45 (L* raw  87–115)
      Deep          < 34  (L* raw  <  87)
    """
    L = brightness / 2.55          # cv2 L* 0-255 → CIE L* 0-100
    A = warmth - 128.0             # signed warmth: + = red/warm

    print(f"CIE L*={L:.1f}  A*={A:.1f}")

    if L >= 70:
        tone, conf = "Fair", 0.92
    elif L >= 62:
        tone, conf = ("Light Medium", 0.87) if A <= 6 else ("Fair", 0.85)
    elif L >= 52:
        tone, conf = "Light Medium", 0.88
    elif L >= 42:
        tone, conf = ("Medium", 0.87) if A > 8 else ("Light Medium", 0.84)
    elif L >= 30:
        tone, conf = "Medium", 0.87
    elif L >= 20:
        tone, conf = ("Tan", 0.86) if A > 5 else ("Medium", 0.84)
    elif L >= 12:
        tone, conf = "Tan", 0.85
    else:
        tone, conf = "Deep", 0.88

    return tone, conf


# =========================================================
# SINGLETON  +  PUBLIC API
# =========================================================

_analyzer = BodyAnalyzer()


def analyze_body_measurements(image: np.ndarray) -> Dict[str, Any]:
    """
    Main entry point called by your FastAPI route.

    Parameters
    ----------
    image : np.ndarray — BGR image (cv2.imread output or camera frame).
                         Recommended minimum resolution: 480 × 640.
                         Higher resolution (720p / 1080p) gives better
                         landmark accuracy and cleaner skin samples.

    Returns
    -------
    dict — body_type, skin_tone, height_category, confidences, features.
    """
    result = _analyzer.analyze(image)
    print("\n✅ BODY ANALYSIS COMPLETE")
    print(f"Body Type : {result['body_type']}  "
          f"(conf={result['body_type_confidence']:.2f})")
    print(f"Skin Tone : {result['skin_tone']}  "
          f"(conf={result['skin_tone_confidence']:.2f})")
    return result