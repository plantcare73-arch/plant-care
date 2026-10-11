"""Reminders blueprint for scheduling plant care follow-ups."""
from flask import Blueprint

reminders_bp = Blueprint('reminders', __name__)

from . import routes
