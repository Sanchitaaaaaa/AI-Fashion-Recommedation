import cv2
import numpy as np
from typing import Dict, Any, Optional


def analyze_skin_tone(image: np.ndarray, raw_landmarks=None) -> Dict[str, Any]:
    """
    Analyze skin tone from image.

    Strategy:
      - If MediaPipe landmarks are available, crop to the face bounding box,
        then sample only the LEFT and RIGHT CHEEK patches (forehead also used).
        Cheeks + forehead are the most neutral, evenly lit skin areas —
        they avoid lips (too red/dark), eyes (too dark), hair (too dark).
      - If no landmarks, fall back to a centre-crop heuristic.

    We do NOT use the HSV skin mask on the face crop because on a tight
    face region it pulls in lip/shadow pixels and shifts the L value dark.
    Instead we directly average the cheek patch pixels in LAB space.
    """
    try:
        h, w = image.shape[:2]

        if raw_landmarks is not None:
            avg_b, avg_g, avg_r = _sample_cheeks(image, raw_landmarks, h, w)
        else:
            avg_b, avg_g, avg_r = _sample_centre_crop(image, h, w)

        # Convert to LAB and read lightness
        avg_color_bgr = np.uint8([[[avg_b, avg_g, avg_r]]])
        avg_color_lab = cv2.cvtColor(avg_color_bgr, cv2.COLOR_BGR2LAB)
        l_val = avg_color_lab[0, 0, 0]

        skin_tone, confidence = _classify_skin_tone(l_val, avg_r, avg_g, avg_b)

        print(f"✅ Skin Tone Analysis Complete:")
        print(f"   Skin Tone:  {skin_tone} (confidence {confidence})")
        print(f"   L Value:    {l_val}  RGB=({avg_r:.1f},{avg_g:.1f},{avg_b:.1f})")

        return {
            "skin_tone":            skin_tone,
            "skin_tone_confidence": confidence,
        }

    except Exception as e:
        print(f"Skin tone analysis error: {str(e)}")
        return {
            "skin_tone":            "Unknown",
            "skin_tone_confidence": 0.0,
        }


def _sample_cheeks(image: np.ndarray, landmarks, h: int, w: int):
    """
    Sample pixel colors from cheek and forehead patches using face landmarks.

    MediaPipe pose landmark indices for face:
      0  = nose tip
      2  = left eye (inner)
      5  = right eye (inner)
      7  = left ear
      8  = right ear
      9  = mouth left
      10 = mouth right

    Cheek patches are placed:
      - Left cheek:  between left ear (7) and nose (0), at mid-height
      - Right cheek: between right ear (8) and nose (0), at mid-height
      - Forehead:    above nose (0), between eyes (2,5)

    Each patch is a 20x20 pixel region. We average all three together.
    This gives a clean skin color reading with no lip/eye/hair contamination.
    """
    try:
        nose    = landmarks[0]
        l_eye   = landmarks[2]
        r_eye   = landmarks[5]
        l_ear   = landmarks[7]
        r_ear   = landmarks[8]

        # Convert normalised coords to pixels
        nose_x, nose_y   = int(nose.x * w),  int(nose.y * h)
        l_ear_x, l_ear_y = int(l_ear.x * w), int(l_ear.y * h)
        r_ear_x, r_ear_y = int(r_ear.x * w), int(r_ear.y * h)
        l_eye_x, l_eye_y = int(l_eye.x * w), int(l_eye.y * h)
        r_eye_x, r_eye_y = int(r_eye.x * w), int(r_eye.y * h)

        patch_size = max(15, int(0.03 * min(h, w)))  # ~3% of image, min 15px

        def get_patch_mean(cx, cy):
            x1 = max(0, cx - patch_size)
            y1 = max(0, cy - patch_size)
            x2 = min(w, cx + patch_size)
            y2 = min(h, cy + patch_size)
            patch = image[y1:y2, x1:x2]
            if patch.size == 0:
                return None
            return (
                float(np.mean(patch[:, :, 0])),  # B
                float(np.mean(patch[:, :, 1])),  # G
                float(np.mean(patch[:, :, 2])),  # R
            )

        # Left cheek: midpoint between left ear and nose, same y as nose
        lc_x = (l_ear_x + nose_x) // 2
        lc_y = nose_y

        # Right cheek: midpoint between right ear and nose, same y as nose
        rc_x = (r_ear_x + nose_x) // 2
        rc_y = nose_y

        # Forehead: above nose, between eyes
        fh_x = (l_eye_x + r_eye_x) // 2
        fh_y = max(0, min(l_eye_y, r_eye_y) - patch_size * 2)

        patches = []
        for cx, cy in [(lc_x, lc_y), (rc_x, rc_y), (fh_x, fh_y)]:
            result = get_patch_mean(cx, cy)
            if result is not None:
                patches.append(result)

        if not patches:
            return _sample_centre_crop(image, int(image.shape[0]), int(image.shape[1]))

        avg_b = np.mean([p[0] for p in patches])
        avg_g = np.mean([p[1] for p in patches])
        avg_r = np.mean([p[2] for p in patches])

        print(f"   Cheek patches sampled: {len(patches)} (lc, rc, forehead)")
        return avg_b, avg_g, avg_r

    except Exception as e:
        print(f"   Cheek sampling failed: {e} — using fallback")
        return _sample_centre_crop(image, h, w)


def _sample_centre_crop(image: np.ndarray, h: int, w: int):
    """
    Fallback: average the upper-centre region of the image.
    Assumes the face occupies the upper-centre area.
    Uses HSV mask to filter out obvious non-skin pixels.
    """
    y1, y2 = h // 8, h // 2
    x1, x2 = w // 4, 3 * w // 4
    crop = image[y1:y2, x1:x2]

    hsv  = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,
                       np.array([0, 20, 70],  dtype=np.uint8),
                       np.array([20, 255, 255], dtype=np.uint8))
    skin_bool = mask > 0

    if np.sum(skin_bool) < 50:
        return float(np.mean(crop[:,:,0])), float(np.mean(crop[:,:,1])), float(np.mean(crop[:,:,2]))

    return (
        float(np.mean(crop[:,:,0][skin_bool])),
        float(np.mean(crop[:,:,1][skin_bool])),
        float(np.mean(crop[:,:,2][skin_bool])),
    )


def _classify_skin_tone(l_value: float, r: float, g: float, b: float) -> tuple:
    """
    Classify skin tone from LAB lightness (L) and RGB channels.

    L thresholds are calibrated for cheek/forehead patches in good lighting.
    Cheek patches read slightly brighter than whole-image averages, so
    the thresholds are shifted down ~5 points compared to the old full-image version.

    Fitzpatrick scale approximate mapping:
      Fair   → Type I-II  (very light, burns easily)
      Medium → Type III   (light-medium, tans gradually)
      Tan    → Type IV    (olive/medium-dark, tans easily)
      Deep   → Type V-VI  (dark brown to very dark)
    """
    # Fair: very high lightness
    if l_value > 195:
        return "Fair", 0.90

    # Fair: high lightness
    elif 165 < l_value <= 195:
        return "Fair", 0.85

    # Medium: check warm undertone (r > b means warm/yellow, common for medium)
    elif 135 < l_value <= 165:
        confidence = 0.85 if r > b else 0.80
        return "Medium", confidence

    # Tan: medium-dark
    elif 105 < l_value <= 135:
        return "Tan", 0.85

    # Deep: dark
    elif l_value <= 105:
        return "Deep", 0.85

    else:
        return "Medium", 0.70