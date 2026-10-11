# 07 - Monorepo Structure

The project uses a monolithic modular architecture structured to group related domain logic together.

```text
plant-disease-detection-system/
│
├── app/                        # Main Application Package
│   ├── __init__.py             # App factory
│   ├── config.py               # Environment configuration
│   ├── extensions.py           # DB, caching initialization
│   ├── errors.py               # Centralized error handlers
│   ├── logging_config.py       # JSON & Text logging setup
│   │
│   ├── auth/                   # Authentication Domain
│   │   ├── routes.py
│   │   └── services.py
│   │
│   ├── predictions/            # Prediction Domain
│   │   ├── routes.py
│   │   └── services.py
│   │
│   ├── disease_knowledge/      # Disease & Treatment Domain
│   │   └── services.py
│   │
│   ├── ml/                     # Machine Learning Domain
│   │   ├── model_manager.py    # CNN loader and wrapper
│   │   └── preprocessing.py    # Image validation/resize logic
│   │
│   ├── integrations/           # External Services
│   │   ├── weather.py
│   │   └── maps.py
│   │
│   └── utils/                  # Shared utilities
│       ├── validation.py
│       └── decorators.py
│
├── models/                     # Trained ML Models (.h5)
│
├── uploads/                    # Temporary Image Uploads
│
├── static/                     # CSS, JS, Assets
│
├── templates/                  # HTML Templates
│   ├── base.html
│   ├── auth/
│   ├── predictions/
│   └── admin/
│
├── docs/                       # Project Documentation (PRD, Specs)
│
├── tests/                      # Unit & Integration Tests
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_predictions.py
│
├── run.py                      # Application Entry Point
├── requirements.txt            # Python Dependencies
├── .env.example                # Environment Config Template
└── .gitignore
```
