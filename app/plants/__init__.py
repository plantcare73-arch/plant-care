"""Plants blueprint for managing user's crops/plants."""
from flask import Blueprint

plants_bp = Blueprint('plants', __name__)

from . import routes
