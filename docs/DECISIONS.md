# Architectural Decisions Record (ADR)

## DECISION 1: Monolithic Modular Architecture
- **Date**: [Current Date]
- **Context**: The existing app is a single `app.py` script. The system needs to scale to support weather, user tracking, and admin features.
- **Decision**: Refactor into a modular monolith using Flask Blueprints rather than splitting into microservices.
- **Rationale**: Microservices introduce unnecessary operational complexity (networking, separate deployments, distributed tracing) for a project of this size. A modular monolith provides the code organization benefits without the operational overhead.

## DECISION 2: Database Engine - MongoDB
- **Date**: [Current Date]
- **Context**: The existing app uses MongoDB. The data model involves highly variable structured data (treatments have different fields, risk rules vary).
- **Decision**: Retain MongoDB. Do not migrate to a relational database (SQL).
- **Rationale**: The dynamic nature of ML predictions, disease data, and risk rules maps well to a NoSQL document store. Migrating to SQL would provide no immediate benefit and delay feature development.

## DECISION 3: ML Abstraction Layer (ModelManager)
- **Date**: [Current Date]
- **Context**: TensorFlow models are heavy and slow to load. Loading them per-request or in global scope randomly causes memory leaks.
- **Decision**: Implement a singleton `ModelManager` class loaded explicitly on app startup (or first request). It must support a "demo mode".
- **Rationale**: Controls memory usage, allows for graceful degradation if the `.h5` file is missing, and makes unit testing the web layer easier (by mocking the manager).

## DECISION 4: No ML Retraining
- **Date**: [Current Date]
- **Context**: The prompt requests a robust system, but the ML model only supports specific classes and lacks severity data.
- **Decision**: Explicitly rule out modifying, retraining, or simulating AI capabilities the model doesn't possess.
- **Rationale**: "Never fake AI" is a core tenet. The platform must be built *around* the existing model's constraints, not by hallucinating capabilities.

## DECISION 5: Multilingual Localization Architecture
- **Date**: [Current Date]
- **Context**: Farmers in India primarily speak regional languages (Kannada, Hindi) alongside English.
- **Decision**: Adopt Flask-Babel with GNU gettext PO/MO catalogs and session-based locale negotiation (`/set-language/<lang>`).
- **Rationale**: Industry-standard, low overhead, no external runtime translation API dependencies, and deterministic offline compilation.

## DECISION 6: Security Hardening and Role Isolation
- **Date**: [Current Date]
- **Context**: Public web app handling uploads, authentication, and admin privileges.
- **Decision**: Enforce Flask-WTF CSRF tokens on state-changing requests, HttpOnly session cookies, file extension/MIME verification on image uploads, path traversal sanitation, and role-based access decorators (`@login_required`, `@admin_required`). Admin users cannot suspend their own account to prevent lockouts.
- **Rationale**: Defense-in-depth preventing OWASP Top 10 vulnerabilities (CSRF, XSS, Path Traversal, Privilege Escalation).

## DECISION 7: Testing Strategy with Isolated Test Database
- **Date**: [Current Date]
- **Context**: End-to-end tests must be repeatable, non-flaky, and safe to execute in CI without wiping production data.
- **Decision**: Use `pytest` with a dedicated `TestingConfig` (`DATABASE_NAME='plant_disease_test_db'`), session fixtures, and `ModelManager` demo fallback.
- **Rationale**: Clean collection isolation before each test, fast execution without requiring heavy GPU inference, and 100% automated coverage across auth, ML inference, risk evaluation, and admin operations.

## DECISION 8: Production Containerization and CI/CD
- **Date**: [Current Date]
- **Context**: Production deployment requires reliable container orchestration and automated regression prevention.
- **Decision**: Standardize on a Debian-slim Python 3.11 Docker image running as a non-root `appuser`, WSGI via Gunicorn with 3 workers and healthchecks. CI pipeline executes linting, translation compilation, and full test suite on push and PR.
- **Rationale**: Ensures reproducibility across environments, eliminates "works on my machine" defects, and enforces zero regressions.
