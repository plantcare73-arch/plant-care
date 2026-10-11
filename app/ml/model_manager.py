"""
Model Manager for wrapping the CNN model.
Handles lazy loading, inference, and fallback "demo" mode.
"""
import os
import random
import logging
from .preprocessing import preprocess_image


class ModelManager:
    """
    Singleton wrapper for the ML Model.
    Ensures model is only loaded once in memory.
    Falls back to demo mode if model is missing or fails to load.
    """
    
    # 38 classes trained in the PlantVillage dataset (subset shown here)
    # We define a subset for demo mode, or the full list if we have it.
    CLASS_LABELS = [
        'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
        'Blueberry___healthy',
        'Cherry_(including_sour)___Powdery_mildew', 'Cherry_(including_sour)___healthy',
        'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_', 
        'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy',
        'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape___healthy',
        'Orange___Haunglongbing_(Citrus_greening)',
        'Peach___Bacterial_spot', 'Peach___healthy',
        'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy',
        'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy',
        'Raspberry___healthy',
        'Soybean___healthy',
        'Squash___Powdery_mildew',
        'Strawberry___Leaf_scorch', 'Strawberry___healthy',
        'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight',
        'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite',
        'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus',
        'Tomato___healthy'
    ]

    def __init__(self):
        self._model = None
        self._is_demo = False
        self._loaded = False
        self.logger = logging.getLogger(__name__)

    def load_model(self, model_path: str):
        """Load the model into memory. Falls back to demo mode on failure."""
        if self._loaded:
            return

        if not os.path.exists(model_path):
            self.logger.warning(f"Model file not found at {model_path}. Starting in DEMO MODE.")
            self._is_demo = True
            self._loaded = True
            return

        try:
            self.logger.info("Loading TensorFlow model...")
            import tensorflow as tf
            self._model = tf.keras.models.load_model(model_path)
            self._is_demo = False
            self.logger.info("TensorFlow model loaded successfully.")
        except Exception as e:
            self.logger.error("Failed to load TensorFlow model. Falling back to DEMO MODE.", exc_info=True)
            self._is_demo = True
        finally:
            self._loaded = True

    def predict(self, image_path: str) -> dict:
        """
        Run inference on an image.
        Returns a dict containing the predicted class, confidence, and all predictions.
        """
        if not self._loaded:
            raise RuntimeError("Model is not loaded. Call load_model first.")

        if self._is_demo:
            return self._predict_demo(image_path)
        
        return self._predict_tf(image_path)

    def _predict_tf(self, image_path: str) -> dict:
        """Actual inference using TensorFlow."""
        try:
            processed_image = preprocess_image(image_path)
            
            # predictions is an array of shape (1, num_classes)
            preds = self._model.predict(processed_image)[0]
            
            # Find the top class
            predicted_idx = int(preds.argmax())
            confidence = float(preds[predicted_idx])
            
            # If the model has fewer outputs than our full list, we might have an index error.
            # Handle safely:
            if predicted_idx < len(self.CLASS_LABELS):
                predicted_class = self.CLASS_LABELS[predicted_idx]
            else:
                predicted_class = f"Unknown_Class_{predicted_idx}"
                
            all_predictions = {}
            for i, score in enumerate(preds):
                if i < len(self.CLASS_LABELS):
                    all_predictions[self.CLASS_LABELS[i]] = float(score)

            return {
                'predicted_class': predicted_class,
                'confidence': confidence,
                'all_predictions': all_predictions
            }
        except Exception as e:
            self.logger.error(f"Inference failed: {e}", exc_info=True)
            raise RuntimeError(f"Failed to run model prediction: {str(e)}")

    def _predict_demo(self, image_path: str) -> dict:
        """Mock inference for development/fallback."""
        self.logger.info(f"[DEMO] Predicting for image: {image_path}")
        
        # Pick a random class
        predicted_idx = random.randint(0, len(self.CLASS_LABELS) - 1)
        predicted_class = self.CLASS_LABELS[predicted_idx]
        
        # Generate fake probabilities
        all_predictions = {}
        total = 0
        for label in self.CLASS_LABELS:
            score = random.uniform(0.001, 0.05)
            all_predictions[label] = score
            total += score
            
        # Ensure the selected class is the highest
        confidence = random.uniform(0.70, 0.99)
        all_predictions[predicted_class] = confidence
        
        # Normalize (rough)
        factor = 1.0 / (total + confidence)
        for label in all_predictions:
            all_predictions[label] = round(all_predictions[label] * factor, 4)
            
        # Re-assign exact confidence after normalization for output consistency
        confidence = all_predictions[predicted_class]

        return {
            'predicted_class': predicted_class,
            'confidence': confidence,
            'all_predictions': all_predictions
        }

    def is_loaded(self) -> bool:
        return self._loaded and not self._is_demo

    def is_demo_mode(self) -> bool:
        return self._is_demo


# Global singleton instance
model_manager = ModelManager()
