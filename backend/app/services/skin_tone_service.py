import cv2
import numpy as np
from typing import Dict, Any

def analyze_skin_tone(image: np.ndarray) -> Dict[str, Any]:
    """
    Analyze skin tone from image
    
    Args:
        image: Input image (numpy array)
    
    Returns:
        Dictionary with skin_tone and confidence
    """
    try:
        # Convert BGR to HSV for better skin tone detection
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Define skin color range in HSV
        # Lower and upper bounds for skin tone
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Create mask for skin
        mask = cv2.inRange(hsv_image, lower_skin, upper_skin)
        
        # Get skin pixels
        skin_pixels = cv2.bitwise_and(image, image, mask=mask)
        
        # Convert to RGB for analysis
        skin_rgb = cv2.cvtColor(skin_pixels, cv2.COLOR_BGR2RGB)
        
        # Calculate average color
        skin_mask_bool = mask > 0
        
        if np.sum(skin_mask_bool) == 0:
            # No skin detected, use face region as fallback
            h, w = image.shape[:2]
            face_region = image[h//4:h*3//4, w//4:w*3//4]
            avg_b = np.mean(face_region[:,:,0])
            avg_g = np.mean(face_region[:,:,1])
            avg_r = np.mean(face_region[:,:,2])
        else:
            avg_b = np.mean(image[:,:,0][skin_mask_bool])
            avg_g = np.mean(image[:,:,1][skin_mask_bool])
            avg_r = np.mean(image[:,:,2][skin_mask_bool])
        
        # Convert to LAB color space for better skin tone classification
        # Create a small image with average color
        avg_color_bgr = np.uint8([[[avg_b, avg_g, avg_r]]])
        avg_color_lab = cv2.cvtColor(avg_color_bgr, cv2.COLOR_BGR2LAB)
        
        l_val = avg_color_lab[0,0,0]  # Lightness
        
        # Classify skin tone based on lightness
        skin_tone, confidence = _classify_skin_tone(l_val, avg_r, avg_g, avg_b)
        
        print(f"✅ Skin Tone Analysis Complete:")
        print(f"   Skin Tone: {skin_tone}")
        print(f"   Confidence: {confidence}")
        print(f"   L Value: {l_val}")
        
        return {
            "skin_tone": skin_tone,
            "skin_tone_confidence": confidence,
        }
    
    except Exception as e:
        print(f"Skin tone analysis error: {str(e)}")
        return {
            "skin_tone": "Unknown",
            "skin_tone_confidence": 0.0,
        }


def _classify_skin_tone(l_value: float, r: float, g: float, b: float) -> tuple:
    """
    Classify skin tone based on color values
    
    Args:
        l_value: Lightness value (0-255)
        r: Red channel value
        g: Green channel value
        b: Blue channel value
    
    Returns:
        Tuple of (skin_tone, confidence)
    """
    
    # Very light skin tone (Fair/Very Light)
    if l_value > 200:
        return "Fair", 0.90
    
    # Light to medium (Fair to Medium)
    elif 170 < l_value <= 200:
        return "Fair", 0.85
    
    # Medium skin tone
    elif 140 < l_value <= 170:
        # Check if more yellow/warm (Medium to Tan)
        if r > b:
            return "Medium", 0.85
        else:
            return "Medium", 0.80
    
    # Medium to Tan
    elif 110 < l_value <= 140:
        return "Tan", 0.85
    
    # Deep/Dark skin tone
    elif l_value <= 110:
        return "Deep", 0.85
    
    # Default
    else:
        return "Medium", 0.70