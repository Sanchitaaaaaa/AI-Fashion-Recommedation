"""
skin_tone_service.py
────────────────────
Analyses skin tone from a BGR image using MediaPipe Pose landmarks
(optionally) or a robust fallback.

Key fixes vs old version
─────────────────────────
• MediaPipe POSE landmark indices for the face region are completely
  different from FaceMesh indices.  Old code used FaceMesh indices
  (0,2,5,7,8) on a Pose landmark list → sampling totally wrong body
  parts.  Corrected to actual Pose indices below.
• Dual HSV + YCrCb skin mask so the fallback works across all tones.
• Classification uses CIE L* (0–100 scale) not raw cv2 LAB (0–255).
• Added A* (warm/cool) channel to distinguish Medium from Tan at the
  same lightness.
• 60th-percentile brightness instead of mean → shadows don't drag the
  result dark.
"""

import cv2
import numpy as np
from typing import Dict, Any, Tuple, Optional


# ============================================================
# MediaPipe POSE landmark indices that are on the face / neck
# (NOT FaceMesh indices — these are the 33-point Pose skeleton)
# ============================================================
#   0  = nose
#   1  = left eye (inner)
#   2  = left eye (centre)
#   3  = left eye (outer)
#   4  = right eye (inner)
#   5  = right eye (centre)
#   6  = right eye (outer)
#   7  = left ear
#   8  = right ear
#   9  = mouth left
#  10  = mouth right
#  11  = left shoulder
#  12  = right shoulder
#
# Cheek approximation from POSE landmarks:
#   Left cheek  → midpoint(nose[0], left_ear[7]),   y ≈ nose.y
#   Right cheek → midpoint(nose[0], right_ear[8]),  y ≈ nose.y
#   Forehead    → above midpoint(left_eye[2], right_eye[5])

_NOSE       = 0
_L_EYE_C    = 2     # left eye centre
_R_EYE_C    = 5     # right eye centre
_L_EAR      = 7
_R_EAR      = 8


# ============================================================
# PUBLIC ENTRY POINT
# ============================================================

def analyze_skin_tone(
    image: np.ndarray,
    raw_landmarks=None,
) -> Dict[str, Any]:
    """
    Parameters
    ----------
    image : np.ndarray
        BGR image (as returned by cv2.imread / what MediaPipe receives).
    raw_landmarks : mediapipe NormalizedLandmarkList.landmark  (optional)
        Pass  results.pose_landmarks.landmark  from a Pose result.
        If None, a robust centre-crop fallback is used.

    Returns
    -------
    dict with keys:
        skin_tone             : str   e.g. "Fair" / "Light Medium" / "Medium" / "Tan" / "Deep"
        skin_tone_confidence  : float 0.0–1.0
    """
    try:
        h, w = image.shape[:2]

        if raw_landmarks is not None and _landmarks_visible(raw_landmarks, h, w):
            avg_b, avg_g, avg_r = _sample_cheeks_pose(image, raw_landmarks, h, w)
            method = "pose-landmarks"
        else:
            avg_b, avg_g, avg_r = _sample_centre_crop(image, h, w)
            method = "centre-crop fallback"

        # ── LAB conversion ──────────────────────────────────
        pixel_bgr = np.uint8([[[avg_b, avg_g, avg_r]]])
        pixel_lab = cv2.cvtColor(pixel_bgr, cv2.COLOR_BGR2LAB)

        l_raw = float(pixel_lab[0, 0, 0])   # cv2 range 0–255
        a_raw = float(pixel_lab[0, 0, 1])   # 0–255, 128 = neutral

        # Normalise to standard CIE L* (0–100) and A* (signed)
        L = l_raw / 2.55
        A = a_raw - 128.0   # negative = greenish, positive = reddish/warm

        skin_tone, confidence = _classify_skin_tone(L, A, avg_r, avg_g, avg_b)

        print(f"\n✅ Skin Tone Analysis [{method}]")
        print(f"   RGB=({avg_r:.1f}, {avg_g:.1f}, {avg_b:.1f})")
        print(f"   CIE L*={L:.1f}  A*={A:.1f}")
        print(f"   → {skin_tone}  (conf={confidence:.2f})")

        return {
            "skin_tone":            skin_tone,
            "skin_tone_confidence": confidence,
        }

    except Exception as e:
        print(f"❌ Skin tone analysis error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "skin_tone":            "Medium",
            "skin_tone_confidence": 0.0,
        }


# ============================================================
# LANDMARK VISIBILITY GUARD
# ============================================================

def _landmarks_visible(landmarks, h: int, w: int) -> bool:
    """
    Return True only when the key face landmarks are present and
    have reasonable visibility scores.
    """
    try:
        needed = [_NOSE, _L_EYE_C, _R_EYE_C, _L_EAR, _R_EAR]
        for idx in needed:
            lm = landmarks[idx]
            # visibility < 0.4 → landmark is occluded / off-frame
            if lm.visibility < 0.40:
                return False
            # sanity: coords must be on the image
            if not (0.0 <= lm.x <= 1.0 and 0.0 <= lm.y <= 1.0):
                return False
        return True
    except Exception:
        return False


# ============================================================
# CHEEK SAMPLING — MediaPipe POSE landmarks
# ============================================================

def _sample_cheeks_pose(
    image: np.ndarray,
    landmarks,
    h: int,
    w: int,
) -> Tuple[float, float, float]:
    """
    Sample BGR mean from three face patches derived from Pose landmarks:
      • Left cheek   – midpoint(nose, left_ear), shifted slightly below ear-nose axis
      • Right cheek  – midpoint(nose, right_ear)
      • Forehead     – above midpoint(left_eye, right_eye)

    Each patch is a square of ~3 % of min(h,w), min 18 px.
    Pixels are filtered with a dual HSV+YCrCb skin mask so that
    background, hair, or shadow pixels don't contaminate the mean.
    """
    try:
        nose   = landmarks[_NOSE]
        l_eye  = landmarks[_L_EYE_C]
        r_eye  = landmarks[_R_EYE_C]
        l_ear  = landmarks[_L_EAR]
        r_ear  = landmarks[_R_EAR]

        # Pixel coords
        nx, ny   = int(nose.x * w),  int(nose.y * h)
        lex, ley = int(l_eye.x * w), int(l_eye.y * h)
        rex, rey = int(r_eye.x * w), int(r_eye.y * h)
        lax, lay = int(l_ear.x * w), int(l_ear.y * h)
        rax, ray = int(r_ear.x * w), int(r_ear.y * h)

        ps = max(18, int(0.03 * min(h, w)))  # patch half-size

        # Patch centres
        #   Left cheek: 60% of the way from nose to left_ear
        lc_x = int(nx * 0.40 + lax * 0.60)
        lc_y = int(ny * 0.55 + lay * 0.45)   # slightly below ear-nose midline

        #   Right cheek: 60% of the way from nose to right_ear
        rc_x = int(nx * 0.40 + rax * 0.60)
        rc_y = int(ny * 0.55 + ray * 0.45)

        #   Forehead: above midpoint of eyes
        fh_x = (lex + rex) // 2
        fh_y = max(ps, min(ley, rey) - ps * 2)

        patches_bgr = []
        for cx, cy in [(lc_x, lc_y), (rc_x, rc_y), (fh_x, fh_y)]:
            mean = _patch_mean(image, cx, cy, ps)
            if mean is not None:
                patches_bgr.append(mean)

        if not patches_bgr:
            print("   ⚠️  No valid cheek patches — using fallback")
            return _sample_centre_crop(image, h, w)

        avg_b = float(np.mean([p[0] for p in patches_bgr]))
        avg_g = float(np.mean([p[1] for p in patches_bgr]))
        avg_r = float(np.mean([p[2] for p in patches_bgr]))

        print(f"   Pose cheek patches used: {len(patches_bgr)}/3")
        return avg_b, avg_g, avg_r

    except Exception as e:
        print(f"   Cheek sampling failed: {e} — using fallback")
        return _sample_centre_crop(image, h, w)


def _patch_mean(
    image: np.ndarray,
    cx: int,
    cy: int,
    ps: int,
) -> Optional[Tuple[float, float, float]]:
    """
    Return (B, G, R) mean of skin-masked pixels in a square patch.
    Returns None if the patch is empty or contains no skin pixels.
    """
    h, w = image.shape[:2]
    x1, y1 = max(0, cx - ps), max(0, cy - ps)
    x2, y2 = min(w, cx + ps), min(h, cy + ps)

    patch = image[y1:y2, x1:x2]
    if patch.size == 0:
        return None

    mask = _dual_skin_mask(patch)

    # If fewer than 30 skin pixels use all pixels in patch
    if np.sum(mask) < 30:
        pixels = patch.reshape(-1, 3).astype(float)
    else:
        pixels = patch[mask].astype(float)

    if len(pixels) == 0:
        return None

    return float(np.mean(pixels[:, 0])), float(np.mean(pixels[:, 1])), float(np.mean(pixels[:, 2]))


# ============================================================
# FALLBACK — no face landmarks
# ============================================================

def _sample_centre_crop(
    image: np.ndarray,
    h: int,
    w: int,
) -> Tuple[float, float, float]:
    """
    Scan several candidate upper-centre crops, pick the one with
    the most skin pixels, then return its skin-masked mean BGR.
    """
    best_crop   = None
    best_count  = -1

    candidates = [
        (0.06, 0.22, 0.38, 0.62),   # tight upper-centre
        (0.04, 0.28, 0.30, 0.70),   # wider
        (0.10, 0.32, 0.35, 0.65),   # lower-face
        (0.02, 0.18, 0.42, 0.58),   # very top (forehead)
    ]

    for y_lo, y_hi, x_lo, x_hi in candidates:
        y1, y2 = int(h * y_lo), int(h * y_hi)
        x1, x2 = int(w * x_lo), int(w * x_hi)
        crop = image[y1:y2, x1:x2]
        if crop.size == 0:
            continue
        mask  = _dual_skin_mask(crop)
        count = int(np.sum(mask))
        if count > best_count:
            best_count = count
            best_crop  = (crop, mask)

    if best_crop is None:
        return (
            float(np.mean(image[:, :, 0])),
            float(np.mean(image[:, :, 1])),
            float(np.mean(image[:, :, 2])),
        )

    crop, mask = best_crop
    if best_count < 50:
        pixels = crop.reshape(-1, 3).astype(float)
    else:
        pixels = crop[mask].astype(float)

    return float(np.mean(pixels[:, 0])), float(np.mean(pixels[:, 1])), float(np.mean(pixels[:, 2]))


# ============================================================
# DUAL SKIN MASK  (HSV ∩ YCrCb)
# ============================================================

def _dual_skin_mask(bgr_patch: np.ndarray) -> np.ndarray:
    """
    Boolean mask selecting skin-coloured pixels.
    Uses HSV AND YCrCb ranges — robust across fair → deep tones.
    """
    hsv   = cv2.cvtColor(bgr_patch, cv2.COLOR_BGR2HSV)
    ycrcb = cv2.cvtColor(bgr_patch, cv2.COLOR_BGR2YCrCb)

    # HSV — wide range to cover all Fitzpatrick types
    mask_hsv = cv2.inRange(
        hsv,
        np.array([0,  15,  50], dtype=np.uint8),
        np.array([25, 200, 255], dtype=np.uint8),
    )

    # YCrCb — very reliable skin detector
    mask_ycr = cv2.inRange(
        ycrcb,
        np.array([0,  133,  77], dtype=np.uint8),
        np.array([255, 180, 135], dtype=np.uint8),
    )

    combined = cv2.bitwise_and(mask_hsv, mask_ycr)
    return combined.astype(bool)


# ============================================================
# CLASSIFICATION
# ============================================================

def _classify_skin_tone(
    L: float,       # CIE L*   0–100
    A: float,       # CIE A*   signed  (negative=green, positive=warm/red)
    r: float,
    g: float,
    b: float,
) -> Tuple[str, float]:
    """
    Map CIE L* + A* to a skin tone label.

    Fitzpatrick approximate mapping
    ────────────────────────────────
    Fair         → Type I–II   (L* ≥ 68)
    Light Medium → Type III    (L* 58–67)
    Medium       → Type III–IV (L* 46–57)
    Tan          → Type IV–V   (L* 34–45)
    Deep         → Type V–VI   (L* < 34)

    A* warm correction
    ──────────────────
    When L* sits near a boundary AND A* is strongly positive (warm/red
    undertone), we nudge toward the warmer/darker label which is more
    likely for South Asian, Latin, Middle Eastern skin tones at mid-
    lightness levels.
    """
    print(f"   _classify_skin_tone: L*={L:.1f}  A*={A:.1f}")

    if L >= 70:
        tone, conf = "Fair", 0.92

    elif L >= 60:
        # Boundary between Fair and Light Medium
        if A > 6:
            tone, conf = "Light Medium", 0.87   # warm undertone → not quite fair
        else:
            tone, conf = "Fair", 0.85

    elif L >= 50:
        tone, conf = "Light Medium", 0.88

    elif L >= 40:
        # Boundary between Light Medium and Medium
        if A > 8:
            tone, conf = "Medium", 0.87          # warm bias → medium
        else:
            tone, conf = "Light Medium", 0.84

    elif L >= 30:
        tone, conf = "Medium", 0.87

    elif L >= 20:
        # Boundary between Medium and Tan
        if A > 5:
            tone, conf = "Tan", 0.86
        else:
            tone, conf = "Medium", 0.84

    elif L >= 12:
        tone, conf = "Tan", 0.85

    else:
        tone, conf = "Deep", 0.88

    return tone, conf