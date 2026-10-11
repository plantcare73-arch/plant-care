"""
Weather service handling OpenWeatherMap API and MongoDB caching.
"""
import os
import requests
from datetime import datetime, timezone, timedelta
from flask import current_app
from ..extensions import get_db

class WeatherService:
    def __init__(self):
        self.api_key = os.environ.get('OPENWEATHERMAP_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        
    def get_weather(self, city, country_code=""):
        """
        Fetch weather data for a city. Uses MongoDB caching to respect API limits.
        Falls back to demo mode if API key is invalid or missing.
        """
        location_key = f"{city.lower().strip()},{country_code.lower().strip()}"
        
        # 1. Check cache first
        db = get_db()
        cache = db['weather_cache'].find_one({'location_key': location_key})
        if cache and cache['expires_at'].replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
            return cache['weather_data']
            
        # 2. Fetch from API if we have a key
        if self.api_key and self.api_key != 'your_copied_api_key_here':
            try:
                params = {
                    'q': location_key if country_code else city,
                    'appid': self.api_key,
                    'units': 'metric'
                }
                response = requests.get(self.base_url, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    weather_data = {
                        'temp': data['main']['temp'],
                        'humidity': data['main']['humidity'],
                        'description': data['weather'][0]['description'].capitalize(),
                        'icon': data['weather'][0]['icon'],
                        'rain': data.get('rain', {}).get('1h', 0) > 0 or 'rain' in data['weather'][0]['description'].lower(),
                        'is_demo': False
                    }
                    
                    # Cache the result for 30 minutes
                    db['weather_cache'].update_one(
                        {'location_key': location_key},
                        {'$set': {
                            'weather_data': weather_data,
                            'expires_at': datetime.now(timezone.utc) + timedelta(minutes=30)
                        }},
                        upsert=True
                    )
                    return weather_data
                else:
                    current_app.logger.warning(f"Weather API failed with status {response.status_code}")
            except Exception as e:
                current_app.logger.error(f"Weather API exception: {str(e)}")
                
        # 3. Fallback to Demo Mode
        return self._get_demo_weather()
        
    def _get_demo_weather(self):
        """Returns mock weather data for development/fallback."""
        return {
            'temp': 24.5,
            'humidity': 65,
            'description': 'Demo: Partly cloudy',
            'icon': '02d',
            'rain': False,
            'is_demo': True
        }

def get_irrigation_advice(weather_data, crop_type):
    """
    Returns simple irrigation advice based on current weather and crop type.
    """
    if weather_data['rain']:
        return "Rain is expected. Hold off on watering to prevent over-saturation and root rot."
        
    if weather_data['temp'] > 30 and weather_data['humidity'] < 50:
        return f"{crop_type} requires extra hydration during hot, dry periods. Water deeply early in the morning."
        
    if weather_data['humidity'] > 80:
        return f"High humidity detected. Avoid overhead watering to reduce the risk of fungal diseases in {crop_type}."
        
    return "Weather conditions are optimal. Maintain your regular watering schedule."
