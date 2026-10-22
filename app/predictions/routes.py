"""
Predictions routes.
"""
import os
import base64
from datetime import datetime, timezone
from bson.objectid import ObjectId
from flask import (
    render_template, request, redirect, url_for,
    session, flash, current_app, send_from_directory, Response,
)

from . import predictions_bp
from ..extensions import get_db
from ..utils.decorators import login_required
from ..utils.validation import validate_image_upload

@predictions_bp.route('/detect', methods=['GET', 'POST'])
@login_required
def detect():
    if request.method == 'POST':
        try:
            filepath, filename = validate_image_upload(request.files.get('leaf_image'))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('detect.html')

        try:
            # Use ModelManager for inference
            from ..ml.model_manager import model_manager
            
            prediction_results = model_manager.predict(filepath)
            predicted_class = prediction_results['predicted_class']
            confidence = prediction_results['confidence']
            all_predictions = prediction_results['all_predictions']
            
            # Fetch comprehensive disease and treatment info
            from ..disease_knowledge.services import get_disease_info
            disease_info = get_disease_info(predicted_class)
            
            # Use the display name from the DB if available
            display_name = disease_info['disease_name']

            db = get_db()
            predictions_col = db['predictions']
            
            # Read and compress/encode image as base64 backup for persistent rendering across Render restarts
            image_b64 = None
            try:
                import base64
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as f_img:
                        image_b64 = base64.b64encode(f_img.read()).decode('utf-8')
            except Exception as b64_err:
                current_app.logger.warning("Could not encode base64 image backup: %s", b64_err)

            prediction_record = {
                'user_id': session['user_id'],
                'image_filename': filename,
                'image_b64': image_b64,
                'predicted_class': predicted_class,
                'display_name': display_name,
                'confidence': confidence,
                'all_predictions': all_predictions,
                'disease_info': disease_info,
                'created_at': datetime.now(timezone.utc),
            }
            result = predictions_col.insert_one(prediction_record)
            prediction_id = str(result.inserted_id)

            return redirect(url_for('predictions.result', prediction_id=prediction_id))
            
        except Exception as e:
            current_app.logger.error("Detection failed: %s", e)
            flash(f'Prediction failed: {str(e)}', 'error')
            return render_template('detect.html')

    return render_template('detect.html')


@predictions_bp.route('/result/<prediction_id>')
@login_required
def result(prediction_id):
    db = get_db()
    try:
        prediction = db['predictions'].find_one({
            '_id': ObjectId(prediction_id),
            'user_id': session['user_id'],
        })
    except Exception:
        flash('Invalid prediction ID.', 'error')
        return redirect(url_for('predictions.history'))

    if not prediction:
        flash('Prediction not found.', 'error')
        return redirect(url_for('predictions.history'))

    return render_template('result.html', prediction=prediction)


@predictions_bp.route('/history')
@login_required
def history():
    user_id = session['user_id']
    page = request.args.get('page', 1, type=int)
    per_page = 10

    db = get_db()
    predictions_col = db['predictions']
    
    # Build query with filters
    query = {'user_id': user_id}
    
    crop_filter = request.args.get('crop')
    if crop_filter:
        query['disease_info.crop'] = crop_filter
        
    disease_filter = request.args.get('disease')
    if disease_filter:
        query['disease_info.disease'] = disease_filter

    total = predictions_col.count_documents(query)
    predictions = list(
        predictions_col.find(query)
        .sort('created_at', -1)
        .skip((page - 1) * per_page)
        .limit(per_page)
    )
    
    unique_crops = predictions_col.distinct('disease_info.crop', {'user_id': user_id})
    unique_diseases = predictions_col.distinct('disease_info.disease', {'user_id': user_id})
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        'history.html',
        predictions=predictions,
        page=page,
        total_pages=total_pages,
        total=total,
        unique_crops=unique_crops,
        unique_diseases=unique_diseases,
        current_crop=crop_filter,
        current_disease=disease_filter
    )


@predictions_bp.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    upload_dir = current_app.config['UPLOAD_DIR']
    file_path = os.path.join(upload_dir, filename)
    
    # 1. If file exists on filesystem, serve it directly
    if os.path.exists(file_path):
        return send_from_directory(upload_dir, filename)
        
    # 2. Ephemeral disk fallback: retrieve base64 backup from MongoDB
    try:
        db = get_db()
        doc = db['predictions'].find_one({'image_filename': filename})
        if doc and doc.get('image_b64'):
            img_bytes = base64.b64decode(doc['image_b64'])
            mime_type = 'image/png' if filename.endswith('.png') else 'image/jpeg'
            return Response(img_bytes, mimetype=mime_type)
    except Exception as e:
        current_app.logger.warning("Failed to serve fallback image from DB: %s", e)
        
    # 3. If neither available, return 404
    return send_from_directory(upload_dir, filename)
