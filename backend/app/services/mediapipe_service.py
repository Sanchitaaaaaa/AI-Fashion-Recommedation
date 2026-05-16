"""
mediapipe_service.py  v5.0
──────────────────────────
MediaPipe Pose-based body analyser + FaceDetection-based skin tone detector.

ROOT CAUSE (why every version still returned Inverted Triangle)
──────────────────────────────────────────────────────────────
MediaPipe's shoulder landmarks sit at the JOINT (deltoid socket), NOT at the
outer silhouette edge of the body. Hip landmarks sit much closer to the true
silhouette edge. This means raw landmark-X distances always make shoulders
look relatively WIDER than they are → SHR is inflated → Inverted Triangle
wins every time. Scoring tweaks alone cannot fix this.

THE FIX (v5.0)
──────────────
1. SILHOUETTE SCAN: at each body level (shoulder / bust / waist / hip) we
   scan horizontally across the image to find where the body silhouette
   actually is, rather than trusting raw landmark X coordinates.
   - Build a foreground mask (GrabCut, fallback to HSV background removal).
   - At each body-level Y, walk inward from both edges to find the body width.
   - Blend 60% silhouette width + 40% landmark width for robustness.

2. HARD-GATE PENALTIES in the classifier: if a body type's primary defining
   criterion is clearly not met, its score is multiplied by 0.05, making it
   virtually impossible to win accidentally.
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

VISIBILITY_THRESHOLD = 0.50


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
# SILHOUETTE WIDTH MEASUREMENT
# =========================================================

def _build_body_mask(bgr: np.ndarray) -> np.ndarray:
    """
    Returns a uint8 binary mask (255 = foreground/body, 0 = background).
    Tries GrabCut first; falls back to HSV background subtraction.
    """
    h, w = bgr.shape[:2]

    # GrabCut with centre rectangle
    rect = (int(w * 0.08), int(h * 0.03), int(w * 0.84), int(h * 0.94))
    mask_gc = np.zeros((h, w), np.uint8)
    bgd_mdl = np.zeros((1, 65), np.float64)
    fgd_mdl = np.zeros((1, 65), np.float64)

    try:
        cv2.grabCut(bgr, mask_gc, rect, bgd_mdl, fgd_mdl, 5,
                    cv2.GC_INIT_WITH_RECT)
        fg_mask = np.where(
            (mask_gc == cv2.GC_FGD) | (mask_gc == cv2.GC_PR_FGD),
            255, 0
        ).astype(np.uint8)
        if np.sum(fg_mask > 0) / (h * w) >= 0.08:
            return fg_mask
    except Exception:
        pass

    # Fallback: remove bright low-saturation background (white/grey backdrops)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    bg_mask = cv2.inRange(
        hsv,
        np.array([0,   0, 180], np.uint8),
        np.array([180, 40, 255], np.uint8),
    )
    fg_mask = cv2.bitwise_not(bg_mask)
    kernel  = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN,  kernel)
    return fg_mask


def _silhouette_width_at_y(mask: np.ndarray, y: int,
                            band: int = 6) -> Optional[float]:
    """
    Scan horizontally at row y (±band rows) in the binary mask.
    Returns width between leftmost and rightmost foreground column,
    or None if fewer than 10 foreground columns found.
    """
    h, w = mask.shape
    y0 = max(0, y - band)
    y1 = min(h, y + band + 1)
    cols = np.where(np.any(mask[y0:y1, :] > 128, axis=0))[0]
    if len(cols) < 10:
        return None
    return float(cols[-1] - cols[0])


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
            model_selection=1,
            min_detection_confidence=0.4,
        )

    # =====================================================
    # MAIN ENTRY POINT
    # =====================================================

    def analyze(self, image: np.ndarray) -> Dict[str, Any]:
        try:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w, _   = image.shape
            results   = self.pose.process(image_rgb)

            if not results.pose_landmarks:
                print("❌ No body detected by MediaPipe Pose")
                return self._empty_result()

            lm = results.pose_landmarks.landmark

            l_shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
            r_shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            l_hip      = lm[mp_pose.PoseLandmark.LEFT_HIP]
            r_hip      = lm[mp_pose.PoseLandmark.RIGHT_HIP]
            l_ankle    = lm[mp_pose.PoseLandmark.LEFT_ANKLE]
            r_ankle    = lm[mp_pose.PoseLandmark.RIGHT_ANKLE]
            l_wrist    = lm[mp_pose.PoseLandmark.LEFT_WRIST]
            r_wrist    = lm[mp_pose.PoseLandmark.RIGHT_WRIST]
            nose       = lm[mp_pose.PoseLandmark.NOSE]

            if not _visible(l_shoulder, r_shoulder, l_hip, r_hip):
                print("❌ Core landmarks not visible")
                return self._empty_result()

            ls_px   = _px(l_shoulder, w, h)
            rs_px   = _px(r_shoulder, w, h)
            lh_px   = _px(l_hip,      w, h)
            rh_px   = _px(r_hip,      w, h)
            la_px   = _px(l_ankle,    w, h)
            ra_px   = _px(r_ankle,    w, h)
            lw_px   = _px(l_wrist,    w, h)
            rw_px   = _px(r_wrist,    w, h)
            nose_px = _px(nose,       w, h)

            mid_shoulder = _mid(ls_px, rs_px)
            mid_hip      = _mid(lh_px, rh_px)
            mid_ankle    = _mid(la_px, ra_px)

            # ── Landmark-based widths ──────────────────────────
            lm_shoulder_w = _dist_x(ls_px, rs_px)
            lm_hip_w      = _dist_x(lh_px, rh_px)

            mid_bust_l = _mid(ls_px, lh_px)
            mid_bust_r = _mid(rs_px, rh_px)
            lm_bust_w  = _dist_x(mid_bust_l, mid_bust_r)

            waist_l = (ls_px[0]*0.40 + lh_px[0]*0.60,
                       ls_px[1]*0.40 + lh_px[1]*0.60)
            waist_r = (rs_px[0]*0.40 + rh_px[0]*0.60,
                       rs_px[1]*0.40 + rh_px[1]*0.60)
            lm_waist_w = _dist_x(waist_l, waist_r)

            # ── Silhouette-based widths ────────────────────────
            body_mask = _build_body_mask(image)

            def _sil(y_float):
                return _silhouette_width_at_y(body_mask, int(y_float))

            sil_shoulder_w = _sil(mid_shoulder[1])
            sil_hip_w      = _sil(mid_hip[1])
            sil_bust_w     = _sil((mid_shoulder[1] + mid_hip[1]) / 2)
            sil_waist_w    = _sil(waist_l[1])

            # ── Blend: 60% silhouette + 40% landmark ──────────
            def _blend(sil, lm_val, alpha=0.60):
                if sil is None or sil < lm_val * 0.5:
                    return lm_val
                return alpha * sil + (1 - alpha) * lm_val

            shoulder_width = _blend(sil_shoulder_w, lm_shoulder_w)
            hip_width      = _blend(sil_hip_w,      lm_hip_w)
            bust_width     = _blend(sil_bust_w,     lm_bust_w)
            waist_width    = _blend(sil_waist_w,    lm_waist_w)

            # Refine waist with wrist gap when arms hang at side
            if _visible(l_wrist, r_wrist):
                wrist_gap   = _dist_x(lw_px, rw_px)
                wrist_mid_y = (lw_px[1] + rw_px[1]) / 2
                waist_y     = (waist_l[1] + waist_r[1]) / 2
                if abs(wrist_mid_y - waist_y) < h * 0.12:
                    waist_width = waist_width * 0.50 + wrist_gap * 0.50

            # Sanity clamp
            waist_width = float(np.clip(waist_width,
                                        hip_width * 0.65,
                                        hip_width * 0.98))

            # ── Height measurements ────────────────────────────
            torso_length = _dist_y(mid_shoulder, mid_hip)
            leg_length   = _dist_y(mid_hip,      mid_ankle)

            # ── Ratios ─────────────────────────────────────────
            shoulder_hip_ratio = shoulder_width / (hip_width    + 1e-6)
            waist_hip_ratio    = waist_width    / (hip_width    + 1e-6)
            bust_waist_ratio   = bust_width     / (waist_width  + 1e-6)
            leg_torso_ratio    = leg_length     / (torso_length + 1e-6)

            print("\n========== MEASUREMENTS (px) ==========")
            print(f"Shoulder: {shoulder_width:.1f}  "
                  f"(lm={lm_shoulder_w:.1f}, sil={sil_shoulder_w})")
            print(f"Bust    : {bust_width:.1f}  "
                  f"(lm={lm_bust_w:.1f}, sil={sil_bust_w})")
            print(f"Waist   : {waist_width:.1f}  "
                  f"(lm={lm_waist_w:.1f}, sil={sil_waist_w})")
            print(f"Hip     : {hip_width:.1f}  "
                  f"(lm={lm_hip_w:.1f}, sil={sil_hip_w})")
            print("\n========== BODY RATIOS ==========")
            print(f"Shoulder/Hip : {shoulder_hip_ratio:.3f}")
            print(f"Waist/Hip    : {waist_hip_ratio:.3f}")
            print(f"Bust/Waist   : {bust_waist_ratio:.3f}")
            print(f"Leg/Torso    : {leg_torso_ratio:.3f}")

            body_type, bt_confidence = self._classify_body_type(
                shoulder_hip_ratio, waist_hip_ratio, bust_waist_ratio,
            )
            height_category = self._classify_height(leg_torso_ratio)
            skin_tone, skin_confidence = self.detect_skin_tone(image, image_rgb)

            print("\n========== FINAL ANALYSIS ==========")
            print(f"Body Type  : {body_type}  (conf={bt_confidence:.2f})")
            print(f"Height Cat.: {height_category}")
            print(f"Skin Tone  : {skin_tone}  (conf={skin_confidence:.2f})")

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
    # BODY TYPE CLASSIFICATION  (v5.0)
    # =====================================================

    def _classify_body_type(
        self,
        shr: float,
        whr: float,
        bwr: float,
    ) -> Tuple[str, float]:
        """
        Score-based classifier with hard-gate penalties.

        Each body type has ONE primary criterion. If it is clearly not met,
        a 0.05 multiplier is applied — making that type nearly impossible to win.

        ┌──────────────────────┬──────────────┬──────────────┬──────────────┐
        │ Body Type            │ SHR          │ WHR          │ BWR          │
        ├──────────────────────┼──────────────┼──────────────┼──────────────┤
        │ Hourglass            │ 0.95 – 1.07  │ < 0.74       │ > 1.22       │
        │ Pear                 │ < 0.93       │ 0.70 – 0.88  │ —            │
        │ Inverted Triangle    │ > 1.12       │ < 0.75       │ > 1.28       │
        │ Rectangle            │ 0.93 – 1.12  │ 0.78 – 0.94  │ 1.02 – 1.28  │
        │ Apple                │ 0.88 – 1.12  │ > 0.86       │ < 1.20       │
        └──────────────────────┴──────────────┴──────────────┴──────────────┘
        """
        scores: Dict[str, float] = {
            "Hourglass":         0.0,
            "Pear":              0.0,
            "Inverted Triangle": 0.0,
            "Rectangle":         0.0,
            "Apple":             0.0,
        }

        # Hourglass — slim waist + defined bust curve
        scores["Hourglass"] += self._score(shr, 0.95, 1.07, 1.5)
        scores["Hourglass"] += self._score_below(whr, 0.74, 3.0)
        scores["Hourglass"] += self._score_above(bwr, 1.22, 3.0)

        # Pear — narrow shoulders vs hips
        scores["Pear"] += self._score_below(shr, 0.93, 4.5)
        scores["Pear"] += self._score(whr, 0.70, 0.88, 2.0)
        scores["Pear"] += self._score_below(bwr, 1.30, 1.0)

        # Inverted Triangle — wide shoulders, slim waist & hips
        scores["Inverted Triangle"] += self._score_above(shr, 1.12, 4.5)
        scores["Inverted Triangle"] += self._score_below(whr, 0.75, 2.0)
        scores["Inverted Triangle"] += self._score_above(bwr, 1.28, 2.0)

        # Rectangle — similar widths throughout, no strong curves
        scores["Rectangle"] += self._score(shr, 0.93, 1.12, 2.5)
        scores["Rectangle"] += self._score(whr, 0.78, 0.94, 3.0)
        scores["Rectangle"] += self._score(bwr, 1.02, 1.28, 1.5)

        # Apple — wide waist relative to hips
        scores["Apple"] += self._score_above(whr, 0.86, 4.5)
        scores["Apple"] += self._score(shr, 0.88, 1.12, 1.5)
        scores["Apple"] += self._score_below(bwr, 1.20, 1.5)

        # ── Hard-gate penalties ────────────────────────────────
        # Hourglass: needs slim waist AND defined curve
        if whr > 0.82 or bwr < 1.10:
            scores["Hourglass"] *= 0.05

        # Pear: shoulders must be clearly narrower than hips
        if shr >= 1.0:
            scores["Pear"] *= 0.05

        # Inverted Triangle: the critical gate
        # shr < 1.05 → near-zero chance of being IT
        # shr 1.05–1.10 → partial penalty (grey zone)
        if shr < 1.05:
            scores["Inverted Triangle"] *= 0.05
        elif shr < 1.10:
            scores["Inverted Triangle"] *= 0.30

        # Rectangle: waist must be in the straight zone
        if whr < 0.68 or whr > 0.97:
            scores["Rectangle"] *= 0.10

        # Apple: waist must be clearly elevated
        if whr < 0.80:
            scores["Apple"] *= 0.05

        best_type  = max(scores, key=scores.__getitem__)
        best_score = scores[best_type]
        total      = sum(scores.values()) + 1e-6
        confidence = round(0.70 + (best_score / total) * 0.27, 2)

        print("\n========== BODY TYPE SCORES (post-penalty) ==========")
        for k, v in sorted(scores.items(), key=lambda x: -x[1]):
            print(f"  {k:<22}: {v:.4f}")

        return best_type, confidence

    # ---- scoring helpers ----------------------------------------

    @staticmethod
    def _score(val: float, lo: float, hi: float,
               weight: float = 1.0) -> float:
        if lo <= val <= hi:
            return weight
        margin = (hi - lo) * 0.4
        if val < lo:
            return weight * max(0.0, 1.0 - (lo - val) / margin)
        return weight * max(0.0, 1.0 - (val - hi) / margin)

    @staticmethod
    def _score_above(val: float, threshold: float,
                     weight: float = 1.0) -> float:
        if val >= threshold:
            return weight
        margin = 0.06
        return weight * max(0.0, 1.0 - (threshold - val) / margin)

    @staticmethod
    def _score_below(val: float, threshold: float,
                     weight: float = 1.0) -> float:
        if val <= threshold:
            return weight
        margin = 0.06
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

            face_bgr      = cv2.cvtColor(face_crop, cv2.COLOR_RGB2BGR)
            skin_mask_arr = _skin_mask(face_bgr)
            masked_pixels = face_bgr[skin_mask_arr]
            if len(masked_pixels) < 30:
                masked_pixels = face_bgr.reshape(-1, 3)

            sample = masked_pixels.reshape(-1, 1, 3).astype(np.uint8)
            lab    = cv2.cvtColor(sample, cv2.COLOR_BGR2LAB)
            brightness = float(np.percentile(lab[:, 0, 0].astype(float), 60))
            warmth     = float(np.mean(lab[:, 0, 1].astype(float)))

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

    def _extract_face_region(self, rgb_image, h, w):
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
            fh, fw = y2 - y1, x2 - x1
            crop = rgb_image[y1 + int(fh*0.15):y1 + int(fh*0.65),
                             x1 + int(fw*0.25):x2 - int(fw*0.25)]
            return crop if crop.size > 0 else None
        except Exception:
            return None

    def _fallback_face_crop(self, bgr_image, h, w):
        best_crop, best_count = None, 0
        for y_lo, y_hi, x_lo, x_hi in [
            (0.05, 0.22, 0.38, 0.62),
            (0.10, 0.28, 0.30, 0.70),
            (0.03, 0.18, 0.40, 0.60),
        ]:
            crop = bgr_image[int(h*y_lo):int(h*y_hi),
                             int(w*x_lo):int(w*x_hi)]
            if crop.size == 0:
                continue
            count = int(np.sum(_skin_mask(crop)))
            if count > best_count:
                best_count = count
                best_crop  = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        return best_crop

    # =====================================================
    # EMPTY RESULT
    # =====================================================

    def _empty_result(self) -> Dict[str, Any]:
        return {
            "body_type":            "Rectangle",
            "body_type_confidence": 0.0,
            "height_category":      "Average",
            "skin_tone":            "Medium",
            "skin_tone_confidence": 0.0,
            "features": {
                "shoulder_width_px":  0.0,
                "bust_width_px":      0.0,
                "waist_width_px":     0.0,
                "hip_width_px":       0.0,
                "shoulder_hip_ratio": 0.0,
                "waist_hip_ratio":    0.0,
                "bust_waist_ratio":   0.0,
            },
        }


# =========================================================
# MODULE-LEVEL SKIN HELPERS
# =========================================================

def _skin_mask(bgr_crop: np.ndarray) -> np.ndarray:
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
    L = brightness / 2.55
    A = warmth - 128.0
    print(f"CIE L*={L:.1f}  A*={A:.1f}")
    if L >= 70:
        return "Fair", 0.92
    elif L >= 62:
        return ("Light Medium", 0.87) if A <= 6 else ("Fair", 0.85)
    elif L >= 52:
        return "Light Medium", 0.88
    elif L >= 42:
        return ("Medium", 0.87) if A > 8 else ("Light Medium", 0.84)
    elif L >= 30:
        return "Medium", 0.87
    elif L >= 20:
        return ("Tan", 0.86) if A > 5 else ("Medium", 0.84)
    elif L >= 12:
        return "Tan", 0.85
    else:
        return "Deep", 0.88


# =========================================================
# SINGLETON  +  PUBLIC API
# =========================================================

_analyzer = BodyAnalyzer()


def analyze_body_measurements(image: np.ndarray) -> Dict[str, Any]:
    """
    Main entry point called by your FastAPI route.

    Parameters
    ----------
    image : np.ndarray — BGR image (cv2.imread / camera frame).
                         Minimum: 480×640. Full-body, front-facing.
                         Plain/solid backgrounds improve silhouette accuracy.

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