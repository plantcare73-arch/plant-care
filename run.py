"""
Application entry point.
"""
import os
from app import create_app
from app.config import get_config

# Initialize configuration based on environment
config_class = get_config()

# Create the application
app = create_app(config_class)

if __name__ == '__main__':
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug)
