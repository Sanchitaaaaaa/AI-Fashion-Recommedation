"""
mediapipe_service.py
────────────────────
MediaPipe Pose-based body analyser + FaceDetection-based skin tone detector.

Fixes in v3.1  (body-type classification)
──────────────────────────────────────────
ROOT CAUSE: Inverted Triangle was winning for every person due to 3 compounding bugs:

  BUG 1 — _score_above / _score_below used `margin = threshold * 0.15`.
           For threshold=1.08, margin=0.162 — so any SHR down to 0.92
           still earned ~63% of the full Inverted Triangle SHR score.
           FIX: use a fixed absolute margin of 0.06 for both helpers.

  BUG 2 — Inverted Triangle WHR range was [0.70, 0.90], which covers
           ~80% of real people.  IT bodies actually have a SLIM waist
           relative to their wide shoulders; WHR should be < 0.78.
           FIX: changed IT WHR to _score_below(whr, 0.78) instead of
           _score(whr, 0.70, 0.90).

  BUG 3 — IT BWR threshold was 1.10, which is trivially met because
           bust_width = shoulder*0.60 + chest*0.40 and waist is clamped
           to hip*0.65 — almost every person exceeds 1.10.
           FIX: raised IT BWR threshold to 1.25.

No other logic (skin tone, height, landmarks, image handling) was changed.
"""

import cv2
import numpy as np
import mediapipe as mp

from app.services.body_shape_model import (
    analyze_body_shape
)

# ============================================================
# MEDIAPIPE SETUP
# ============================================================

mp_pose = mp.solutions.pose

pose = mp_pose.Pose(

    static_image_mode=True,

    model_complexity=2,

    enable_segmentation=True,

    min_detection_confidence=0.5,
)

# ============================================================
# SKIN TONE DETECTION
# ============================================================

def detect_skin_tone(image):

    try:

        # ====================================================
        # RGB CONVERSION
        # ====================================================

        rgb = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        # ====================================================
        # MEDIAPIPE RESULTS
        # ====================================================

        results = pose.process(rgb)

        if not results.pose_landmarks:

            return "Medium"

        landmarks = (
            results.pose_landmarks.landmark
        )

        h, w = image.shape[:2]

        # ====================================================
        # SHOULDER REGION
        # ====================================================

        ls = landmarks[11]
        rs = landmarks[12]

        x1 = int(min(ls.x, rs.x) * w)
        x2 = int(max(ls.x, rs.x) * w)

        y1 = int(min(ls.y, rs.y) * h)

        y2 = int(y1 + h * 0.12)

        # ====================================================
        # CLAMP
        # ====================================================

        x1 = max(0, x1)
        x2 = min(w, x2)

        y1 = max(0, y1)
        y2 = min(h, y2)

        # ====================================================
        # CROP REGION
        # ====================================================

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
        Score-based classifier across 5 body types.

        Reference ranges:
        ┌──────────────────────┬───────────┬───────────┬───────────┐
        │ Body Type            │  SHR      │  WHR      │  BWR      │
        ├──────────────────────┼───────────┼───────────┼───────────┤
        │ Hourglass            │ 0.97–1.05 │ < 0.76    │ > 1.20    │
        │ Pear (Triangle)      │ < 0.93    │ 0.72–0.86 │ any       │
        │ Inverted Triangle    │ > 1.10    │ < 0.78    │ > 1.25    │  ← tightened
        │ Rectangle (Banana)   │ 0.93–1.10 │ 0.80–0.93 │ 1.05–1.22 │
        │ Apple (Round/Oval)   │ 0.90–1.10 │ > 0.88    │ < 1.15    │
        └──────────────────────┴───────────┴───────────┴───────────┘

        FIX v3.1: _score_above / _score_below now use a fixed absolute
        margin of 0.06 (was threshold * 0.15 which was far too wide).
        IT WHR changed from range [0.70, 0.90] to _score_below(0.78).
        IT BWR threshold raised from 1.10 → 1.25.
        """
        scores: Dict[str, float] = {
            "Hourglass":         0.0,
            "Pear":              0.0,
            "Inverted Triangle": 0.0,
            "Rectangle":         0.0,
            "Apple":             0.0,
        }

        # ── Hourglass: balanced shoulders/hips, slim waist, defined bust
        scores["Hourglass"]         += self._score(shr, 0.97, 1.05, 2.0)
        scores["Hourglass"]         += self._score_below(whr, 0.76, 2.5)
        scores["Hourglass"]         += self._score_above(bwr, 1.20, 2.0)

        # ── Pear: narrower shoulders than hips
        scores["Pear"]              += self._score_below(shr, 0.93, 3.0)
        scores["Pear"]              += self._score(whr, 0.72, 0.86, 1.5)

        # ── Inverted Triangle: notably wider shoulders, slim waist & hips
        #    FIX: SHR threshold raised to 1.10 (was 1.08)
        #    FIX: WHR now _score_below(0.78) — IT has a slim waist,
        #         NOT a broad [0.70-0.90] range that covers everyone
        #    FIX: BWR threshold raised to 1.25 (was 1.10 — too easy)
        scores["Inverted Triangle"] += self._score_above(shr, 1.10, 3.0)
        scores["Inverted Triangle"] += self._score_below(whr, 0.78, 1.5)
        scores["Inverted Triangle"] += self._score_above(bwr, 1.25, 1.5)

        # ── Rectangle: similar shoulder/waist/hip widths
        scores["Rectangle"]         += self._score(shr, 0.93, 1.10, 2.0)
        scores["Rectangle"]         += self._score(whr, 0.80, 0.93, 2.0)
        scores["Rectangle"]         += self._score(bwr, 1.05, 1.22, 1.5)

        # ── Apple: wide waist relative to hips
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
        """Full score inside [lo, hi]; linearly decays to 0 outside."""
        if lo <= val <= hi:
            return weight
        margin = (hi - lo) * 0.4
        if val < lo:
            return weight * max(0.0, 1.0 - (lo - val) / margin)
        return weight * max(0.0, 1.0 - (val - hi) / margin)

    @staticmethod
    def _score_above(val: float, threshold: float,
                     weight: float = 1.0) -> float:
        """
        Full score when val >= threshold.
        FIX v3.1: margin is now a fixed 0.06 (absolute), NOT threshold*0.15.
        The old formula gave a margin of ~0.16 for threshold=1.08, meaning
        someone with SHR=0.92 still earned 63% of the Inverted Triangle score.
        """
        if val >= threshold:
            return weight
        margin = 0.06   # fixed absolute — tight, realistic grace zone
        return weight * max(0.0, 1.0 - (threshold - val) / margin)

    @staticmethod
    def _score_below(val: float, threshold: float,
                     weight: float = 1.0) -> float:
        """
        Full score when val <= threshold.
        FIX v3.1: same fixed-margin change as _score_above.
        """
        if val <= threshold:
            return weight
        margin = 0.06   # fixed absolute
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

        if skin_region.size == 0:

            return "Medium"

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


        lab = cv2.cvtColor(

            skin_region,

            cv2.COLOR_BGR2LAB
        )

        l_channel = lab[:, :, 0]

        brightness = np.mean(
            l_channel
        )

        # ====================================================
        # CLASSIFICATION
        # ====================================================

        if brightness > 190:

            return "Fair"

        elif brightness > 160:

            return "Light Medium"

        elif brightness > 125:

            return "Medium"

        elif brightness > 95:

            return "Tan"

        else:

            return "Deep"

    except Exception as e:

        print(
            f"❌ Skin tone error: {e}"
        )

        return "Medium"

# ============================================================
# HEIGHT CATEGORY
# ============================================================

def estimate_height_category(landmarks):

    try:

        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]

        left_ankle = landmarks[27]
        right_ankle = landmarks[28]

        shoulder_y = (
            left_shoulder.y +
            right_shoulder.y
        ) / 2

        ankle_y = (
            left_ankle.y +
            right_ankle.y
        ) / 2

        body_height = abs(
            ankle_y - shoulder_y
        )

        # ====================================================
        # CATEGORY
        # ====================================================

        if body_height > 0.72:

            return "Tall"

        elif body_height > 0.60:

            return "Average"

        else:

            return "Petite"

    except:

        return "Average"

# ============================================================
# MAIN ANALYSIS FUNCTION
# ============================================================

def analyze_body_measurements(image_path):

    try:

        # ====================================================
        # LOAD IMAGE
        # ====================================================

        image = cv2.imread(image_path)

        if image is None:

            return {

                "success": False,

                "error":
                    "Image not found"
            }

        # ====================================================
        # RGB
        # ====================================================

        rgb = cv2.cvtColor(

            image,

            cv2.COLOR_BGR2RGB
        )

        # ====================================================
        # MEDIAPIPE
        # ====================================================

        results = pose.process(rgb)

        if not results.pose_landmarks:

            return {

                "success": False,

                "error":
                    "Body not detected"
            }

        landmarks = (
            results.pose_landmarks.landmark
        )

        # ====================================================
        # VISIBILITY VALIDATION
        # ====================================================

        important_points = [

            landmarks[11],
            landmarks[12],
            landmarks[23],
            landmarks[24],
        ]

        visibility_score = np.mean([

            lm.visibility

            for lm in important_points
        ])

        if visibility_score < 0.45:

            return {

                "success": False,

                "error":
                    "Body visibility too low"
            }

        # ====================================================
        # YOLO BODY SHAPE ANALYSIS
        # ====================================================

        body_result = analyze_body_shape(
            image_path
        )

        body_type = body_result.get(

            "body_type",

            "Rectangle"
        )

        body_confidence = body_result.get(

            "confidence",

            0.0
        )

        measurements = body_result.get(

            "measurements",

            {}
        )

        print(
            f"✅ YOLO Body Shape: {body_type}"
        )

        # ====================================================
        # SKIN TONE
        # ====================================================

        skin_tone = detect_skin_tone(
            image
        )

        print(
            f"✅ Skin Tone: {skin_tone}"
        )

        # ====================================================
        # HEIGHT CATEGORY
        # ====================================================

        height_category = (
            estimate_height_category(
                landmarks
            )
        )

        # ====================================================
        # RESPONSE
        # ====================================================

        return {

            "success": True,

            "body_type":
                body_type,

            "body_confidence":
                body_confidence,

            "skin_tone":
                skin_tone,

            "height_category":
                height_category,

            "measurements":
                measurements,
        }

    except Exception as e:

        print(
            f"❌ MediaPipe analysis error: {e}"
        )

        return {

            "success": False,

            "error": str(e)
        }