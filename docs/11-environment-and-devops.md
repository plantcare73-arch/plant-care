# 11 - Environment and DevOps

## Environments
1. **Development**: Local execution. Uses `.env` for secrets, `FLASK_ENV=development`. Uses `python run.py`. Database is a local or Atlas development MongoDB cluster.
2. **Testing**: CI environment. Uses mocked external APIs and a localized/in-memory MongoDB (like mongomock) or a clean test database.
3. **Production**: Dockerized execution. Uses a WSGI server (Gunicorn). No debug mode. Centralized logging.

## Dockerization
The application will be packaged using Docker.
- `Dockerfile`: Defines the Python 3.9+ image, installs OpenCV/TensorFlow system dependencies, and installs Python requirements.
- `docker-compose.yml`: (Optional for local dev) Defines the web service and a local MongoDB instance.

## CI/CD (GitHub Actions)
- **Trigger**: Push to `main` or Pull Requests.
- **Jobs**:
  - `lint`: Runs `flake8` or `pylint`.
  - `test`: Runs `pytest` suite.
  - `build`: Builds the Docker image to ensure it compiles successfully.

## Secrets Management
Secrets (MongoDB URIs, API keys, Flask Secret Key) must NEVER be committed to version control. They are strictly loaded via environment variables or a `.env` file during development.
