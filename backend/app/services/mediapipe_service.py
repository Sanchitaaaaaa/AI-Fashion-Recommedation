import mediapipe as mp
import cv2
import numpy as np
from typing import Dict, Any

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
            # Convert to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w, _ = image.shape
            
            # Detect pose
            results = self.pose.process(image_rgb)
            
            if not results.pose_landmarks:
                return {
                    "body_type": "Unknown",
                    "body_type_confidence": 0.0,
                    "features": {
                        "shoulder_hip_ratio": 0.0,
                        "waist_hip_ratio": 0.0,
                        "leg_torso_ratio": 0.0,
                        "arm_body_ratio": 0.0,
                    }
                }
            
            landmarks = results.pose_landmarks.landmark
            
            # Get key points
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            left_hip = landmarks[23]
            right_hip = landmarks[24]
            left_knee = landmarks[25]
            right_knee = landmarks[26]
            left_ankle = landmarks[27]
            right_ankle = landmarks[28]
            left_wrist = landmarks[15]
            right_wrist = landmarks[16]
            left_elbow = landmarks[13]
            right_elbow = landmarks[14]
            
            # Calculate measurements
            shoulder_width = abs(right_shoulder.x - left_shoulder.x) * w
            hip_width = abs(right_hip.x - left_hip.x) * w
            shoulder_y = (left_shoulder.y + right_shoulder.y) / 2 * h
            hip_y = (left_hip.y + right_hip.y) / 2 * h
            ankle_y = (left_ankle.y + right_ankle.y) / 2 * h
            
            # Calculate waist (approximate)
            waist_y = (shoulder_y + hip_y) / 2
            
            # Ratios
            shoulder_hip_ratio = shoulder_width / (hip_width + 0.001)
            waist_hip_ratio = shoulder_width * 0.8 / (hip_width + 0.001)
            leg_torso_ratio = (ankle_y - hip_y) / (hip_y - shoulder_y + 0.001)
            arm_body_ratio = abs(left_wrist.x - left_shoulder.x) / (shoulder_width / 2 + 0.001)
            
            # Determine body type based on ratios
            body_type, confidence = self._classify_body_type(
                shoulder_hip_ratio,
                waist_hip_ratio,
                leg_torso_ratio
            )
            
            return {
                "body_type": body_type,
                "body_type_confidence": confidence,
                "features": {
                    "shoulder_hip_ratio": round(shoulder_hip_ratio, 3),
                    "waist_hip_ratio": round(waist_hip_ratio, 3),
                    "leg_torso_ratio": round(leg_torso_ratio, 3),
                    "arm_body_ratio": round(arm_body_ratio, 3),
                }
            }
        
        except Exception as e:
            print(f"Body analysis error: {str(e)}")
            return {
                "body_type": "Unknown",
                "body_type_confidence": 0.0,
                "features": {
                    "shoulder_hip_ratio": 0.0,
                    "waist_hip_ratio": 0.0,
                    "leg_torso_ratio": 0.0,
                    "arm_body_ratio": 0.0,
                }
            }

    def _classify_body_type(self, s_h_ratio: float, w_h_ratio: float, l_t_ratio: float) -> tuple:
        """Classify body type based on ratios"""
        
        # Hourglass: Similar shoulder and hip width, smaller waist
        if 0.9 < s_h_ratio < 1.1 and w_h_ratio < 0.75:
            return "Hourglass", 0.90
        
        # Apple: Broader shoulders, larger waist, narrower hips
        elif s_h_ratio > 1.05 and w_h_ratio > 0.85:
            return "Apple", 0.85
        
        # Pear: Narrower shoulders, larger hips
        elif s_h_ratio < 0.95 and w_h_ratio > 0.80:
            return "Pear", 0.85
        
        # Rectangle: Balanced shoulders and hips, less waist definition
        elif 0.95 < s_h_ratio < 1.05 and 0.75 < w_h_ratio < 0.85:
            return "Rectangle", 0.85
        
        # Inverted Triangle: Very broad shoulders, narrower hips
        elif s_h_ratio > 1.1 and w_h_ratio < 0.75:
            return "Inverted Triangle", 0.85
        
        # Default
        else:
            return "Rectangle", 0.70


# Create global analyzer instance
analyzer = BodyAnalyzer()


def analyze_body_measurements(image: np.ndarray) -> Dict[str, Any]:
    """
    Analyze body measurements from image
    
    Args:
        image: Input image (numpy array)
    
    Returns:
        Dictionary with body_type, confidence, and features
    """
    result = analyzer.analyze(image)
    
    print(f"✅ Body Analysis Complete:")
    print(f"   Body Type: {result['body_type']}")
    print(f"   Confidence: {result['body_type_confidence']}")
    print(f"   S/H Ratio: {result['features']['shoulder_hip_ratio']}")
    print(f"   W/H Ratio: {result['features']['waist_hip_ratio']}")
    
    return result