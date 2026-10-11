"""
Plants routes for Farmer History (Phase 4).
"""
from datetime import datetime, timezone
from bson.objectid import ObjectId
from flask import render_template, request, redirect, url_for, session, flash

from . import plants_bp
from ..extensions import get_db
from ..utils.decorators import login_required


@plants_bp.route('/')
@login_required
def index():
    """List user's registered plants."""
    db = get_db()
    user_id = session['user_id']
    
    plants = list(db['plants'].find({'user_id': user_id}).sort('created_at', -1))
    
    return render_template('plants/index.html', plants=plants)


@plants_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add a new plant/crop profile."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        crop_type = request.form.get('crop_type', '').strip()
        location = request.form.get('location', '').strip()
        
        if not name or not crop_type:
            flash('Plant name and crop type are required.', 'error')
            return render_template('plants/add.html')
            
        db = get_db()
        db['plants'].insert_one({
            'user_id': session['user_id'],
            'name': name,
            'crop_type': crop_type,
            'location': location,
            'status': 'Healthy',
            'created_at': datetime.now(timezone.utc)
        })
        
        flash(f'Plant "{name}" added successfully.', 'success')
        return redirect(url_for('plants.index'))
        
    return render_template('plants/add.html')


@plants_bp.route('/<plant_id>')
@login_required
def view(plant_id):
    """View details of a specific plant and its care cases/history."""
    db = get_db()
    try:
        plant = db['plants'].find_one({
            '_id': ObjectId(plant_id),
            'user_id': session['user_id']
        })
    except Exception:
        flash('Invalid plant ID.', 'error')
        return redirect(url_for('plants.index'))
        
    if not plant:
        flash('Plant not found.', 'error')
        return redirect(url_for('plants.index'))
        
    # Find care cases linked to this plant
    cases = list(db['care_cases'].find({'plant_id': str(plant['_id'])}).sort('created_at', -1))
        
    return render_template('plants/view.html', plant=plant, cases=cases)


@plants_bp.route('/<plant_id>/care', methods=['POST'])
@login_required
def add_care_case(plant_id):
    """Add a care activity to a plant."""
    db = get_db()
    try:
        plant = db['plants'].find_one({'_id': ObjectId(plant_id), 'user_id': session['user_id']})
    except Exception:
        flash('Invalid plant ID.', 'error')
        return redirect(url_for('plants.index'))
        
    if not plant:
        flash('Plant not found.', 'error')
        return redirect(url_for('plants.index'))
        
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    
    if not title:
        flash('Activity title is required.', 'error')
        return redirect(url_for('plants.view', plant_id=plant_id))
        
    db['care_cases'].insert_one({
        'user_id': session['user_id'],
        'plant_id': str(plant['_id']),
        'title': title,
        'description': description,
        'status': 'open',
        'created_at': datetime.now(timezone.utc)
    })
    
    flash('Care activity logged.', 'success')
    return redirect(url_for('plants.view', plant_id=plant_id))
