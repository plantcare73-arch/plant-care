# 06 - API Contracts

APIs follow RESTful conventions. All endpoints returning JSON data prefix with `/api/v1/`.
(Traditional server-rendered HTML routes are documented in 03-information-architecture.md).

## General Response Format
Success:
```json
{
  "success": true,
  "data": { ... }
}
```

Error:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": { ... }
  }
}
```

## Endpoints

### `POST /api/v1/predictions/detect`
Performs ML inference on an uploaded leaf image.
- **Auth**: Required
- **Request (Multipart Form)**:
  - `leaf_image`: File (PNG, JPG, max 10MB)
- **Response (200)**:
  ```json
  {
    "success": true,
    "data": {
      "prediction_id": "5f8a9b...",
      "predicted_class": "Potato___Early_blight",
      "confidence": 0.942,
      "model_version": "1.0.0"
    }
  }
  ```
- **Errors**: `400 BAD_REQUEST` (Invalid image), `413 PAYLOAD_TOO_LARGE`

### `GET /api/v1/diseases/:class_name`
Fetches structured disease and treatment metadata.
- **Auth**: Optional
- **Response (200)**:
  ```json
  {
    "success": true,
    "data": {
      "disease_name": "Early Blight",
      "crop": "Potato",
      "symptoms": ["..."],
      "treatments": [
        { "category": "chemical", "instructions": ["..."], "safety_warnings": ["..."] }
      ]
    }
  }
  ```

### `GET /api/v1/weather`
Fetches cached or live weather for the user's location.
- **Auth**: Required
- **Query Params**: `lat`, `lng`
- **Response (200)**:
  ```json
  {
    "success": true,
    "data": {
      "temp": 24.5,
      "humidity": 82,
      "conditions": "Rain",
      "source": "OpenWeatherMap"
    }
  }
  ```
- **Errors**: `503 EXTERNAL_SERVICE_ERROR`

### `GET /health`
System health check.
- **Auth**: None
- **Response (200)**:
  ```json
  {
    "status": "healthy",
    "database": "healthy",
    "model": "loaded"
  }
  ```
