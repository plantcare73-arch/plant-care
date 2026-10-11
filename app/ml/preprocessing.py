"""
Image preprocessing for ML model inference.
"""
import numpy as np
from PIL import Image


def preprocess_image(image_path: str, target_size=(224, 224)) -> np.ndarray:
    """
    Load an image, resize it to target size, and normalize for the model.
    Returns a numpy array of shape (1, H, W, C).
    """
    try:
        # Open and convert to RGB (removes alpha channel if present)
        img = Image.open(image_path).convert('RGB')
        
        # Resize
        img = img.resize(target_size)
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Normalize to [0, 1] as typical for ResNet/MobileNet based models
        img_array = img_array.astype('float32') / 255.0
        
        # Expand dimensions to add batch size: (1, 224, 224, 3)
        img_batch = np.expand_dims(img_array, axis=0)
        
        return img_batch
    except Exception as e:
        raise ValueError(f"Failed to preprocess image: {str(e)}")
