# 12 - Testing Strategy

## 1. Unit Testing
Framework: `pytest`

**Focus Areas:**
- **Validation Utilities**: Test `validate_email`, `validate_password`, and especially `validate_image_upload` (using mocked file objects and real invalid files).
- **Domain Services**: Test the risk engine logic independently of the web layer by passing synthetic weather data and rules.
- **Model Manager**: Test model loading logic, fallback modes, and prediction formatting using mocked TensorFlow returns.

## 2. Integration Testing
**Focus Areas:**
- **API Endpoints**: Use Flask's `test_client` to test route accessibility, parameter validation, and response structures.
- **Database Operations**: Ensure records are correctly inserted, updated, and retrieved from MongoDB.
- **Authentication Flow**: Test register, login, session creation, and logout. Ensure protected routes return `401 Unauthorized` without a session.

## 3. End-to-End (Manual/UI)
- Verify image upload flow from the browser.
- Verify translations render correctly.
- Verify responsive design on mobile viewport sizes.

## 4. Test Data & Mocks
- External APIs (Weather, Maps) must be mocked using `responses` or `unittest.mock` to prevent flaky tests and API rate limits.
- A "demo mode" in `ModelManager` should be used during CI to avoid loading massive `.h5` files into memory for basic route testing.
