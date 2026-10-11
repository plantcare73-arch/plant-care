"""
Reviews routes.
"""
from datetime import datetime, timezone
from flask import render_template, request, session, flash, redirect, url_for

from . import reviews_bp
from ..extensions import get_db
from ..utils.decorators import login_required
from ..utils.validation import validate_rating, sanitize_string


@reviews_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    db = get_db()
    reviews_col = db['reviews']

    if request.method == 'POST':
        try:
            rating = validate_rating(request.form.get('rating'))
            comment = sanitize_string(request.form.get('comment', ''))
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('reviews.index'))
            
        review = {
            'user_id': session['user_id'],
            'user_name': session['user_name'],
            'rating': rating,
            'comment': comment,
            'created_at': datetime.now(timezone.utc),
        }
        reviews_col.insert_one(review)
        flash('Thank you for your review!', 'success')
        return redirect(url_for('reviews.index'))

    all_reviews = list(reviews_col.find().sort('created_at', -1).limit(20))
    return render_template('reviews.html', reviews=all_reviews)
