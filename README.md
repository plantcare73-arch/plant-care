# AI Plant Disease Detection System

A production-grade, modular web application designed to help farmers and gardeners identify plant diseases using Artificial Intelligence. Built with Flask, MongoDB, and TensorFlow, this platform provides actionable treatment plans, tracks plant health over time, and manages daily agricultural tasks.

🌐 **Live URL:** [https://plantcare-kwo0.onrender.com/](https://plantcare-kwo0.onrender.com/)

---

## 🌟 Key Features

*   **AI Disease Detection**: Upload an image of a plant leaf and receive an instant prediction of the crop type and potential disease using a Convolutional Neural Network (CNN).
*   **Demo / Fallback Mode**: If the TensorFlow model isn't downloaded, the system gracefully falls back to a simulated demo mode, allowing testing without large model weights.
*   **Disease Knowledge Base**: Structured repository of plant diseases mapping to organic, chemical, and preventive treatment plans.
*   **Plant Profiles**: Create and track specific crops (e.g., "Greenhouse Tomato #1").
*   **Care Logging & Reminders**: Log treatments applied to individual plants and schedule follow-up tasks to stay on top of farm maintenance.
*   **Secure Authentication**: Role-based access control, hashed passwords, session timeouts, and full CSRF protection across all forms.
*   **Structured Logging & Error Handling**: Production-ready JSON logging and centralized, user-friendly error pages.

## 🏗️ Architecture

The system uses a **Flask Application Factory** pattern to ensure clean separation of concerns:

```text
plantcare/
├── app/
│   ├── admin/             # Admin dashboard & user management
│   ├── auth/              # Registration, login, and password resets
│   ├── disease_knowledge/ # Disease and treatment database lookups
│   ├── main/              # Landing page and user dashboard
│   ├── ml/                # TensorFlow model loading and inference
│   ├── plants/            # User plant profiles and care history
│   ├── predictions/       # Image upload and detection routes
│   └── reminders/         # Task scheduling
├── docs/                  # Project specifications and ADRs
├── models/                # ML weights (e.g. model_weights.h5)
├── scripts/               # DB seed scripts and utilities
├── static/                # CSS, JS, and Images
├── templates/             # Jinja2 HTML templates
├── uploads/               # User-uploaded leaf images
└── run.py                 # Application entry point
```

## 🛠️ Tech Stack

*   **Backend Framework**: Python / Flask (v2.3)
*   **Database**: MongoDB (PyMongo)
*   **Machine Learning**: TensorFlow / Keras, NumPy, Pillow
*   **Frontend**: HTML5, Vanilla CSS, Bootstrap 5.3, FontAwesome
*   **Security**: Flask-WTF (CSRF), bcrypt, itsdangerous (Token generation)

## 🚀 Installation & Setup

### Prerequisites
*   Python 3.9+
*   MongoDB (running locally on default port `27017` or via Atlas)

### 1. Clone the repository
```bash
git clone https://github.com/plantcare73-arch/plantcare.git
cd plantcare
```

### 2. Set up the virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```ini
APP_ENV=development
SECRET_KEY=your-super-secret-key-here
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=plant_disease_db
LOG_LEVEL=INFO
```

### 5. Seed the Database
Run the provided scripts to populate the initial disease knowledge base, treatments, and nearby agricultural stores/pathologists:
```bash
python scripts/seed_diseases.py
python scripts/seed_location_data.py
```

### 6. Add the ML Model (Optional)
To use actual AI predictions rather than Demo Mode, place your trained Keras model inside the `models/` directory:
```bash
# Path should be: models/model_weights.h5
```

### 7. Run the Application
```bash
python run.py
```
The application will be available at `http://127.0.0.1:5000`.

---

## 🐳 Docker & Docker Compose Setup

Run the entire platform including MongoDB and the hardened Gunicorn WSGI server with a single command:

```bash
docker compose up --build
```

The application runs on `http://localhost:5000` with automated healthchecks on `/health` and isolated data volumes for uploads and database files.

---

## 🧪 Running the Automated Test Suite

The test suite contains 36 unit, integration, and security tests covering authentication, image validation, prediction pipelines, admin operations, weather risk evaluation, CSRF, and user isolation:

```bash
pytest -v
```

---

## 🌐 Multilingual Localization

The platform natively supports English, Hindi (`hi`), and Kannada (`kn`). Translation catalogs can be compiled anytime using:

```bash
python -m babel.messages.frontend compile -d app/translations
```

---

## 📜 Development Roadmap (Implementation Plan)

- [x] Phase 1: Foundation (App Factory, Blueprints, MongoDB Integration, Structured Logging)
- [x] Phase 2: Core ML (ModelManager singleton, inference pipeline, fallback demo mode)
- [x] Phase 3: Disease Knowledge Base (Structured organic, chemical, and biological recommendations)
- [x] Phase 4: Farmer History (Plant profiles, filtering, care activities)
- [x] Phase 5: Treatment & Follow-up (Task scheduling, reminders, tracking)
- [x] Phase 6: Weather (OpenWeatherMap adapter, caching, humidity & temp metrics)
- [x] Phase 7: Risk Engine (Weather-driven rule engine for late blight and heat stress)
- [x] Phase 8: Location Services (Agricultural experts and equipment store discovery)
- [x] Phase 9: Multilingual (English, Hindi, Kannada with language switcher)
- [x] Phase 10: Offline Capability (PWA manifest, service worker offline fallback)
- [x] Phase 11: Admin Portal (Dashboard metrics, user suspension, disease/rules CRUD, audit logs)
- [x] Phase 12: Hardening & Deployment (Docker, Docker Compose, CI/CD, 36 automated pytest tests)

---

## 📄 License
This project is for educational and research purposes.
