def classify_body_shape(landmarks):
    """
    Simple body shape mapping using shoulder & hip landmarks
    """

    # Example MediaPipe landmark indices
    LEFT_SHOULDER = landmarks[11]
    RIGHT_SHOULDER = landmarks[12]
    LEFT_HIP = landmarks[23]
    RIGHT_HIP = landmarks[24]

    shoulder_width = abs(LEFT_SHOULDER.x - RIGHT_SHOULDER.x)
    hip_width = abs(LEFT_HIP.x - RIGHT_HIP.x)
    ratio = shoulder_width / hip_width if hip_width else 0

    if ratio > 1.2:
        return "Inverted Triangle"
    elif ratio < 0.9:
        return "Pear"
    else:
        return "Rectangle"
