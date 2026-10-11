# 01 - Product Requirements Document (PRD)

## 1. Product Vision
The **AI Plant Care** system is an intelligent agricultural assistance platform that helps farmers quickly detect plant diseases, receive actionable treatment recommendations, and manage crop health over time.

## 2. Target Users
1. **Farmers / Growers**: Primary users who upload leaf images, view disease predictions, track crop health, and receive weather/risk alerts.
2. **Administrators**: System managers who maintain disease knowledge bases, update treatment protocols, manage users, and monitor analytics.

## 3. Agricultural Problem
Farmers often lack immediate access to agricultural experts, leading to delayed disease diagnosis and incorrect treatment applications. This results in crop yield losses, unnecessary chemical usage, and reduced profitability.

## 4. Functional Requirements

### 4.1 Disease Detection
- The system must accept user-uploaded leaf images (PNG, JPG, JPEG).
- It must perform image validation and preprocessing (resize to 224x224, normalization).
- It must pass the image through a trained CNN model to classify the disease.
- It must display the predicted class alongside the model's confidence score.
- **Rule**: Never fake AI. The system must only predict classes it was trained on.

### 4.2 Treatment Engine
- The system must provide structured treatment recommendations based on the predicted disease.
- Recommendations must be categorized (Organic, Biological, Chemical, Preventive).
- Chemical treatments must include proper safety warnings.
- **Rule**: Never manufacture treatment advice; it must come from the structured knowledge base.

### 4.3 Weather and Environment
- The system must fetch and display relevant current weather conditions.
- It must evaluate weather data against crop-specific risk rules to generate disease outbreak alerts.
- It must provide basic irrigation advice based on weather and crop context.

### 4.4 Farmer Support and Tracking
- Farmers must be able to view their prediction history.
- Farmers must be able to create follow-up reminders to re-evaluate plants.
- Farmers must be able to log "Before/After" tracking of treatment progress.
- The system must assist in locating nearby agricultural stores and experts.

### 4.5 Multilingual Support
- The user interface must support English, Kannada, and Hindi.

## 5. Non-Functional Requirements
- **Performance**: API responses should take <500ms (excluding model inference). Total prediction time should aim for <5s.
- **Security**: Secure authentication, password hashing, and user-scoped data access.
- **Availability**: Offline mode must gracefully support basic prediction where feasible (e.g., cached data).
- **Scalability**: The architecture must support the addition of new crop/disease classes without structural rewrites.
