"""
Weather package for fetching and caching weather data.
Phase 6: Weather Integration.
"""
from flask import Blueprint

weather_bp = Blueprint('weather', __name__)

from . import routes
