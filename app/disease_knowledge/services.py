"""
Services for interacting with disease and treatment data.
"""
from ..extensions import get_db

def get_disease_info(class_name: str) -> dict:
    """
    Fetch comprehensive disease info, including categorized treatments.
    If the class is not in the DB, returns a fallback structure.
    """
    db = get_db()
    
    # 1. Fetch Disease Base Info
    disease_doc = db['diseases'].find_one({'class_name': class_name})
    
    if not disease_doc:
        # Fallback if DB hasn't been seeded yet for this class
        display_name = class_name.replace('___', ' - ').replace('_', ' ')
        crop = display_name.split(' - ')[0] if ' - ' in display_name else 'Unknown'
        return {
            'class_name': class_name,
            'disease_name': display_name,
            'crop': crop,
            'description': 'Information not yet available in the database.',
            'symptoms': [],
            'treatments': {
                'organic': [],
                'chemical': [],
                'preventive': []
            }
        }
        
    # 2. Fetch Treatments mapped to this disease
    treatment_docs = list(db['treatments'].find({'disease_class': class_name}))
    
    treatments = {
        'organic': [],
        'chemical': [],
        'preventive': []
    }
    
    for t in treatment_docs:
        cat = t.get('category', 'organic').lower()
        if cat in treatments:
            treatments[cat].append({
                'instructions': t.get('instructions', []),
                'safety_warnings': t.get('safety_warnings', []),
                'source': t.get('source', '')
            })
            
    return {
        'class_name': disease_doc.get('class_name'),
        'disease_name': disease_doc.get('disease_name'),
        'crop': disease_doc.get('crop'),
        'description': disease_doc.get('description'),
        'symptoms': disease_doc.get('symptoms', []),
        'treatments': treatments
    }
