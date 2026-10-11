"""
Risk Engine package for evaluating agricultural risks based on weather and plant profiles.
Phase 7: Risk Engine.
"""
from flask import Blueprint

risk_bp = Blueprint('risk_engine', __name__)

from . import routes
