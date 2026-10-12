import math
from flask import current_app
from app.extensions import get_db

class LocationService:
    # 24/7 National Farmer Support Hotlines across India
    NATIONAL_EXPERTS = [
        {
            "name": "Kisan Call Center (Ministry of Agriculture)",
            "specialty": "All India Farmer Helpline (Toll-Free, 22 Languages)",
            "phone": "1800-180-1551",
            "address": "Toll-Free 6:00 AM - 10:00 PM Daily",
            "location": {"lat": 28.6139, "lng": 77.2090},
            "is_national": True,
            "distance": 0.0
        },
        {
            "name": "ICAR Farmer Advisory Portal & Clinic",
            "specialty": "Crop Pathology & Pest Diagnostics",
            "phone": "011-25841475",
            "address": "ICAR Pusa Institute, New Delhi / Regional KVKs",
            "location": {"lat": 28.6367, "lng": 77.1558},
            "is_national": True,
            "distance": 0.0
        }
    ]

    @staticmethod
    def get_nearby_experts(lat, lng, radius_km=50):
        """Find experts within radius_km, with fallback to national helplines."""
        try:
            results = LocationService._find_nearby("experts", lat, lng, radius_km)
            # If no local experts found within radius or small count, always include national toll-free helplines
            has_national = any(e.get('is_national') or '1800' in str(e.get('phone', '')) for e in results)
            if not has_national:
                results.extend(LocationService.NATIONAL_EXPERTS)
            return results
        except Exception as e:
            current_app.logger.error(f"Error fetching nearby experts: {e}")
            return LocationService.NATIONAL_EXPERTS

    @staticmethod
    def get_nearby_stores(lat, lng, radius_km=50):
        """Find stores within radius_km."""
        try:
            # Check 'stores' collection first, then 'agricultural_stores'
            results = LocationService._find_nearby("stores", lat, lng, radius_km)
            if not results:
                results = LocationService._find_nearby("agricultural_stores", lat, lng, radius_km)
            return results
        except Exception as e:
            current_app.logger.error(f"Error fetching nearby stores: {e}")
            return []

    @staticmethod
    def _find_nearby(collection_name, lat, lng, radius_km):
        db = get_db()
        collection = db[collection_name]
        items = list(collection.find({}))
        
        results = []
        for item in items:
            loc = item.get('location', {})
            item_lat = loc.get('lat')
            item_lng = loc.get('lng')
            
            if item_lat and item_lng:
                dist = LocationService.haversine(lat, lng, item_lat, item_lng)
                if dist <= radius_km or item.get('is_national'):
                    item_copy = dict(item)
                    item_copy['distance'] = round(dist, 1)
                    results.append(item_copy)
                    
        # Sort by distance
        results.sort(key=lambda x: x.get('distance', 9999))
        return results

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        """
        Calculate the great circle distance in kilometers between two points 
        on the earth (specified in decimal degrees)
        """
        lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a)) 
        r = 6371 # Radius of earth in kilometers
        return c * r
