# ============================================================
# FILE: backend/app/services/mediapipe_service.py
# ============================================================

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

        skin_region = image[
            y1:y2,
            x1:x2
        ]

        if skin_region.size == 0:

            return "Medium"

        # ====================================================
        # LAB COLOR SPACE
        # ====================================================

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