# 09 - Engineering Scope Definition

## What Is In Scope
- Refactoring the monolithic Flask app into a modular architecture.
- Upgrading MongoDB integrations to use structured collections and indexes.
- Creating an abstraction layer for the ML model (`ModelManager`) to handle memory safely.
- Implementing a robust treatment engine that maps predicted classes to actionable advice.
- Adding weather integration and a rule-based disease risk engine.
- Adding a "Care Case" feature for tracking plant health over time.
- Basic multilingual support (English, Kannada, Hindi) for the UI.
- Comprehensive Unit and Integration testing for the Flask backend.

## What Is Out Of Scope
- **Retraining the CNN Model**: The existing `.h5` model weights and architecture remain unchanged. The system must adapt to what the model can do.
- **Severity Estimation**: The current ML model is a classifier, not an object detection or segmentation model. It cannot estimate the percentage of leaf area affected. This feature will not be faked.
- **Mobile Native Apps**: The system remains a responsive web application. No iOS/Android native development is included.
- **Real-time Push Notifications**: Alerting will be restricted to in-app dashboard alerts rather than SMS or Push notifications to limit scope complexity.
- **Hardware Integrations**: IoT sensors for soil moisture or direct drone image uploads are out of scope.
