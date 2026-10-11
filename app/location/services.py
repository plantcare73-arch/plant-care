import math
from flask import current_app
from app.extensions import get_db

class LocationService:
    @staticmethod
    def get_nearby_experts(lat, lng, radius_km=50):
        """Find experts within radius_km."""
        try:
            return LocationService._find_nearby("experts", lat, lng, radius_km)
        except Exception as e:
            current_app.logger.error(f"Error fetching nearby experts: {e}")
            return []

    @staticmethod
    def get_nearby_stores(lat, lng, radius_km=50):
        """Find stores within radius_km."""
        try:
            return LocationService._find_nearby("stores", lat, lng, radius_km)
        except Exception as e:
            current_app.logger.error(f"Error fetching nearby stores: {e}")
            return []

    @staticmethod
    def _find_nearby(collection_name, lat, lng, radius_km):
        # We will use simple haversine in python for now, fetching all and sorting, 
        # assuming a small dataset. For production, use MongoDB $geoNear.
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
                if dist <= radius_km:
                    item['distance'] = dist
                    results.append(item)
                    
        # Sort by distance
        results.sort(key=lambda x: x['distance'])
        return results

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        """
        Calculate the great circle distance in kilometers between two points 
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a)) 
        r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
        return c * r
