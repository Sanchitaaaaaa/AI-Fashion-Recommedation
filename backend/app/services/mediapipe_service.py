import cv2
import mediapipe as mp

mp_pose = mp.solutions.pose

def extract_landmarks(image_path: str):
    image = cv2.imread(image_path)
    if image is None:
        return None

    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(
            cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        )

    if not results.pose_landmarks:
        return None

    return results.pose_landmarks.landmark
