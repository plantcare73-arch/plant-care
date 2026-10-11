# 08 - Prediction & Risk Scoring Engine Specification

**Note**: This replaces the ecommerce scoring engine spec to match the agricultural context of this platform.

## 1. Model Confidence Score
The CNN returns a probability distribution across all trained classes. The `confidence` score is the probability of the highest-predicted class.

**Confidence Thresholds:**
- **`HIGH_CONFIDENCE` (>= 0.85)**: The system confidently asserts the diagnosis. Treatments are displayed normally.
- **`MEDIUM_CONFIDENCE` (0.70 - 0.84)**: The system displays the diagnosis but adds a notice that the image may be ambiguous.
- **`LOW_CONFIDENCE` (< 0.70)**: The system displays the top prediction but heavily emphasizes a disclaimer to consult an expert. The prediction is flagged in the database for potential review or retraining.

## 2. Disease Severity Score (Placeholder)
Currently, the CNN only performs *classification* (presence/absence of a disease), not *segmentation* or *severity estimation*.
- Until a severity model is deployed, the severity score must always return `not_available`.
- **CRITICAL RULE**: The system must NEVER convert a low CNN confidence score into a "low severity" metric. Confidence measures model certainty, not physical plant damage.

## 3. Disease Risk Score (Environmental)
An environmental risk score calculated independent of image predictions. It evaluates if current weather conditions favor a specific disease outbreak.

**Risk Rules (Example):**
- **Condition**: `Crop: Potato`, `Disease: Late Blight`
- **Rule**: If `Humidity > 90%` AND `Temperature between 10C and 25C` for > 2 days.
- **Risk Level**: `HIGH`

**Risk Levels:**
- `LOW`: Conditions are unfavorable for the disease. Standard preventative care applies.
- `MODERATE`: Conditions are moderately favorable. Increased monitoring recommended.
- `HIGH`: Conditions strongly favor an outbreak. Immediate preventative measures/spraying recommended.
- `UNKNOWN`: Weather data unavailable or no rules defined for the crop.
