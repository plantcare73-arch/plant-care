"""
Reminders routes for Treatment & Follow-up (Phase 5).
"""
from datetime import datetime, timezone
from bson.objectid import ObjectId
from flask import render_template, request, redirect, url_for, session, flash

from . import reminders_bp
from ..extensions import get_db
from ..utils.decorators import login_required


@reminders_bp.route('/')
@login_required
def index():
    """List user's active and past reminders."""
    db = get_db()
    user_id = session['user_id']
    
    # We join with plants collection to get plant name
    try:
        reminders_cursor = db['reminders'].aggregate([
            {'$match': {'user_id': user_id}},
            {'$addFields': {'plant_obj_id': {'$toObjectId': '$plant_id'}}},
            {'$lookup': {
                'from': 'plants',
                'localField': 'plant_obj_id',
                'foreignField': '_id',
                'as': 'plant_info'
            }},
            {'$unwind': {'path': '$plant_info', 'preserveNullAndEmptyArrays': True}},
            {'$sort': {'due_date': 1}}
        ])
        reminders = list(reminders_cursor)
    except Exception:
        # Fallback for environments or mock drivers lacking $toObjectId expression support
        raw_reminders = list(db['reminders'].find({'user_id': user_id}).sort('due_date', 1))
        for r in raw_reminders:
            p_id = r.get('plant_id')
            if p_id:
                try:
                    r['plant_info'] = db['plants'].find_one({'_id': ObjectId(p_id)})
                except Exception:
                    r['plant_info'] = None
            else:
                r['plant_info'] = None
        reminders = raw_reminders
    
    # Separate into pending and completed
    now = datetime.now(timezone.utc)
    pending = []
    completed = []
    
    for r in reminders:
        if r.get('status') == 'completed':
            completed.append(r)
        else:
            r['is_overdue'] = r.get('due_date') and r['due_date'].replace(tzinfo=timezone.utc) < now
            pending.append(r)
            
    return render_template('reminders/index.html', pending=pending, completed=completed)


@reminders_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Create a new reminder."""
    db = get_db()
    user_id = session['user_id']
    
    if request.method == 'POST':
        plant_id = request.form.get('plant_id')
        title = request.form.get('title', '').strip()
        due_date_str = request.form.get('due_date')
        
        if not title or not due_date_str:
            flash('Title and Due Date are required.', 'error')
            return redirect(url_for('reminders.add'))
            
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            # Set to end of day in UTC for simplicity or keep as midnight
        except ValueError:
            flash('Invalid date format.', 'error')
            return redirect(url_for('reminders.add'))
            
        db['reminders'].insert_one({
            'user_id': user_id,
            'plant_id': plant_id,  # Can be empty string for general reminders
            'title': title,
            'status': 'pending',
            'due_date': due_date,
            'created_at': datetime.now(timezone.utc)
        })
        
        flash('Reminder scheduled.', 'success')
        
        # If redirected from a specific plant view, we could return there
        next_url = request.form.get('next')
        if next_url:
            return redirect(next_url)
            
        return redirect(url_for('reminders.index'))
        
    # GET request - fetch plants for dropdown
    plants = list(db['plants'].find({'user_id': user_id}).sort('name', 1))
    preselect_plant = request.args.get('plant_id')
    return render_template('reminders/add.html', plants=plants, preselect_plant=preselect_plant)


@reminders_bp.route('/<reminder_id>/complete', methods=['POST'])
@login_required
def complete(reminder_id):
    """Mark a reminder as completed."""
    db = get_db()
    result = db['reminders'].update_one(
        {'_id': ObjectId(reminder_id), 'user_id': session['user_id']},
        {'$set': {'status': 'completed', 'completed_at': datetime.now(timezone.utc)}}
    )
    
    if result.modified_count:
        flash('Reminder marked as completed!', 'success')
    else:
        flash('Reminder not found.', 'error')
        
    return redirect(url_for('reminders.index'))
