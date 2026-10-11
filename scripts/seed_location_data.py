import os
from pymongo import MongoClient

def seed_locations():
    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["plant_disease_db"]
    
    # Dummy Experts in/around Bengaluru
    experts = [
        {
            "name": "Dr. Ramesh Kumar",
            "specialty": "Plant Pathology",
            "phone": "+91 98765 43210",
            "address": "GKVK Campus, Bellary Road, Bengaluru",
            "location": {"lat": 13.0763, "lng": 77.5753}
        },
        {
            "name": "Kisan Call Center",
            "specialty": "General Agriculture Advisory",
            "phone": "1800-180-1551",
            "address": "Hebbal, Bengaluru",
            "location": {"lat": 13.0354, "lng": 77.5971}
        },
        {
            "name": "Agri Clinic & Agri Business Centre",
            "specialty": "Pest Management",
            "phone": "+91 80 2345 6789",
            "address": "Yelahanka, Bengaluru",
            "location": {"lat": 13.1007, "lng": 77.5963}
        },
        {
            "name": "Dr. Sunita Sharma",
            "specialty": "Horticulture",
            "phone": "+91 91234 56789",
            "address": "Whitefield, Bengaluru",
            "location": {"lat": 12.9698, "lng": 77.7499}
        }
    ]
    
    # Dummy Stores in/around Bengaluru
    stores = [
        {
            "name": "Sri Lakshmi Agri Inputs",
            "type": "Fertilizers & Pesticides",
            "phone": "+91 99887 76655",
            "address": "KR Market, Bengaluru",
            "location": {"lat": 12.9632, "lng": 77.5746}
        },
        {
            "name": "Kisan Agro Kendra",
            "type": "Seeds & Fertilizers",
            "phone": "+91 98765 12345",
            "address": "Yeshwanthpur, Bengaluru",
            "location": {"lat": 13.0285, "lng": 77.5409}
        },
        {
            "name": "Green Earth Farm Store",
            "type": "Organic Farming Supplies",
            "phone": "+91 88990 01122",
            "address": "Jayanagar, Bengaluru",
            "location": {"lat": 12.9299, "lng": 77.5824}
        },
        {
            "name": "Farmers Co-op Society",
            "type": "General Farm Inputs",
            "phone": "+91 80 2233 4455",
            "address": "Malleswaram, Bengaluru",
            "location": {"lat": 13.0031, "lng": 77.5714}
        }
    ]
    
    db.experts.drop()
    db.stores.drop()
    
    if experts:
        db.experts.insert_many(experts)
        print(f"Inserted {len(experts)} experts.")
        
    if stores:
        db.stores.insert_many(stores)
        print(f"Inserted {len(stores)} stores.")

if __name__ == "__main__":
    seed_locations()
