# 02 - User Stories and Acceptance Criteria

## 1. Authentication
**Story**: As a farmer, I want to register and log in so that my history and predictions are securely saved.
- **Acceptance Criteria**:
  - Given valid credentials, the system creates a user and stores the password securely (hashed).
  - Given an existing email, the system rejects the registration.
  - Given invalid login credentials, the system displays an error and denies access.

## 2. Image Upload and Prediction
**Story**: As a farmer, I want to upload a leaf image to get an instant disease prediction.
- **Acceptance Criteria**:
  - Given a valid supported leaf image, when the authenticated user uploads it, then the system validates and preprocesses the image.
  - The system returns a supported disease class and stores the prediction.
  - The system displays the confidence score clearly.
  - If the image is not a valid image format, the system rejects the upload with an error message.

## 3. Low-Confidence Results
**Story**: As a farmer, I want to know if the AI is unsure about its prediction so I don't apply the wrong treatment.
- **Acceptance Criteria**:
  - Given a prediction with a confidence score < 70%, the system displays a clear warning.
  - The system advises consulting a qualified agricultural expert instead of heavily relying on the result.

## 4. Treatment Recommendations
**Story**: As a farmer, I want to see how to treat the disease so I can save my crop.
- **Acceptance Criteria**:
  - Given a high-confidence prediction, the system displays structured treatment options.
  - Treatments are categorized (organic, chemical, preventive).
  - Chemical treatments include safety disclaimers.

## 5. Follow-Up & Reminders
**Story**: As a farmer, I want to set a reminder to re-check my plant after applying treatment.
- **Acceptance Criteria**:
  - A user can create a reminder tied to a specific prediction/plant.
  - The system displays the reminder on the dashboard when due.

## 6. Weather & Alerts
**Story**: As a farmer, I want to see weather data and disease risk alerts so I can apply preventive measures.
- **Acceptance Criteria**:
  - The system fetches current weather for the user's location.
  - If weather conditions trigger a disease risk rule, an alert is displayed on the dashboard.

## 7. Multilingual Support
**Story**: As a farmer who speaks Kannada or Hindi, I want to use the interface in my local language.
- **Acceptance Criteria**:
  - The user can select a language preference (English, Kannada, Hindi).
  - UI elements translate accordingly (excluding structural disease IDs).

## 8. Admin Workflows
**Story**: As an admin, I want to update disease treatment information without changing code.
- **Acceptance Criteria**:
  - Admins can log in and view the disease management interface.
  - Admins can create or edit disease symptoms and treatments.
