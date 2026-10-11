from flask import Blueprint

bp = Blueprint('location', __name__)

from app.location import routes
