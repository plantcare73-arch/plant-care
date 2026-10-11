from flask import render_template, request, jsonify, session
from bson.objectid import ObjectId
from app.extensions import get_db
from app.location import bp
from app.location.services import LocationService

@bp.route('/')
def index():
    """Render the location services page."""
    user_id = session.get('user_id')
    saved_coords = None
    if user_id:
        try:
            db = get_db()
            user = db['users'].find_one({'_id': ObjectId(user_id)})
            if user and 'last_coords' in user:
                saved_coords = user['last_coords']
        except Exception:
            pass
    return render_template('location/index.html', saved_coords=saved_coords)

@bp.route('/api/nearby')
def nearby():
    """API endpoint to get nearby experts and stores based on lat/lng."""
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', default=50, type=int)
    
    if not lat or not lng:
        return jsonify({"error": "Latitude and longitude are required"}), 400
        
    experts = LocationService.get_nearby_experts(lat, lng, radius)
    stores = LocationService.get_nearby_stores(lat, lng, radius)
    
    # Save coordinates in user profile if logged in
    user_id = session.get('user_id')
    if user_id:
        try:
            db = get_db()
            db['users'].update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'last_coords': {'lat': lat, 'lng': lng}}}
            )
        except Exception:
            pass

    # Format for JSON serialization (convert ObjectId to string if present)
    for e in experts:
        e['_id'] = str(e['_id']) if '_id' in e else None
    for s in stores:
        s['_id'] = str(s['_id']) if '_id' in s else None
        
    return jsonify({
        "experts": experts,
        "stores": stores
    })
