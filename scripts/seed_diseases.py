import os
import sys
from datetime import datetime, timezone

# Add the parent directory to sys.path so we can import 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from dotenv import load_dotenv

def seed():
    load_dotenv()
    app = create_app()
    
    with app.app_context():
        print("Clearing old diseases/treatments...")
        db['diseases'].delete_many({})
        db['treatments'].delete_many({})
        
        now = datetime.now(timezone.utc)
        
        diseases = [
            {
                'class_name': 'Potato___Early_blight',
                'crop': 'Potato',
                'disease_name': 'Early Blight',
                'description': 'Early blight is a common disease of potato caused by the fungus Alternaria solani. It primarily affects leaves, but can also infect stems and tubers.',
                'symptoms': [
                    'Small, dark brown to black spots on older leaves.',
                    'Spots enlarge and often develop a target-like pattern of concentric rings.',
                    'Severe infection causes leaves to yellow and dry up.'
                ],
                'created_at': now
            },
            {
                'class_name': 'Potato___Late_blight',
                'crop': 'Potato',
                'disease_name': 'Late Blight',
                'description': 'Late blight is a devastating disease caused by the oomycete Phytophthora infestans. It was responsible for the Irish Potato Famine.',
                'symptoms': [
                    'Irregular, water-soaked spots on leaves that turn dark brown or black.',
                    'White fungal growth may appear on the underside of leaves in humid conditions.',
                    'Tubers develop dark, reddish-brown patches beneath the skin.'
                ],
                'created_at': now
            },
            {
                'class_name': 'Potato___healthy',
                'crop': 'Potato',
                'disease_name': 'Healthy Potato Plant',
                'description': 'The plant appears completely healthy with no visible signs of fungal or bacterial infection.',
                'symptoms': [],
                'created_at': now
            }
        ]
        
        print("Inserting diseases...")
        db['diseases'].insert_many(diseases)
        
        treatments = [
            {
                'disease_class': 'Potato___Early_blight',
                'category': 'preventive',
                'instructions': [
                    'Use certified disease-free seeds.',
                    'Practice crop rotation (do not plant potatoes or tomatoes in the same soil consecutively).',
                    'Ensure adequate spacing for air circulation to keep leaves dry.'
                ]
            },
            {
                'disease_class': 'Potato___Early_blight',
                'category': 'chemical',
                'instructions': [
                    'Apply fungicides containing chlorothalonil or mancozeb at the first sign of disease.',
                    'Reapply every 7-14 days according to manufacturer instructions.'
                ],
                'safety_warnings': [
                    'Wear protective gloves and mask during application.',
                    'Do not harvest within 7 days of the last application.'
                ]
            },
            {
                'disease_class': 'Potato___Late_blight',
                'category': 'chemical',
                'instructions': [
                    'Use targeted fungicides (e.g., metalaxyl, cymoxanil) immediately upon detection.',
                    'Destroy infected plants to prevent spores from spreading to healthy crops.'
                ],
                'safety_warnings': [
                    'Chemicals are highly toxic to aquatic life. Do not apply near water sources.'
                ]
            }
        ]
        
        print("Inserting treatments...")
        db['treatments'].insert_many(treatments)
        
        print("Seeding complete!")

if __name__ == "__main__":
    seed()
