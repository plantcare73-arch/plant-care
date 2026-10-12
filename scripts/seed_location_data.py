import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv

def seed_locations():
    load_dotenv()
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("DATABASE_NAME", "plant_disease_db")
    print(f"Connecting to MongoDB: {mongo_uri[:35]}... (DB: {db_name})")
    
    kwargs = {}
    if "mongodb+srv" in mongo_uri or "ssl=true" in mongo_uri.lower():
        kwargs["tlsCAFile"] = certifi.where()

    client = MongoClient(mongo_uri, **kwargs)
    db = client[db_name]
    
    # Experts in/around Bengaluru and Karnataka agricultural universities
    experts = [
        {
            "name": "Dr. Ramesh Kumar (UAS Bengaluru)",
            "specialty": "Plant Pathology & Crop Protection",
            "phone": "+91 80 2333 0153",
            "address": "GKVK Campus, Bellary Road, Bengaluru",
            "location": {"lat": 13.0763, "lng": 77.5753},
            "is_national": False
        },
        {
            "name": "Kisan Call Center (National Agri Helpline)",
            "specialty": "24/7 Expert Farmer Helpline (Free)",
            "phone": "1800-180-1551",
            "address": "Toll Free All India / Hebbal Center, Bengaluru",
            "location": {"lat": 13.0354, "lng": 77.5971},
            "is_national": True
        },
        {
            "name": "Krishi Vigyan Kendra (KVK Bengaluru)",
            "specialty": "Agronomy & Integrated Pest Management",
            "phone": "+91 80 2363 7235",
            "address": "Hadonahalli, Doddaballapura / Hebbal, Bengaluru",
            "location": {"lat": 13.0421, "lng": 77.5892},
            "is_national": False
        },
        {
            "name": "ICAR - Indian Institute of Horticultural Research (IIHR)",
            "specialty": "Horticulture & Fruit/Vegetable Diseases",
            "phone": "+91 80 2308 6100",
            "address": "Hessaraghatta Lake Post, Bengaluru",
            "location": {"lat": 13.1362, "lng": 77.4975},
            "is_national": False
        },
        {
            "name": "Agri Clinic & Agri Business Centre",
            "specialty": "Pest & Disease Management Clinic",
            "phone": "+91 80 2345 6789",
            "address": "Yelahanka New Town, Bengaluru",
            "location": {"lat": 13.1007, "lng": 77.5963},
            "is_national": False
        },
        {
            "name": "Dr. Sunita Sharma (Horticulture Specialist)",
            "specialty": "Foliar Diseases & Organic Cultivation",
            "phone": "+91 91234 56789",
            "address": "ITPL Main Road, Whitefield, Bengaluru",
            "location": {"lat": 12.9698, "lng": 77.7499},
            "is_national": False
        }
    ]
    
    # Stores in/around Bengaluru
    stores = [
        {
            "name": "Sri Lakshmi Agro Inputs & Seeds",
            "type": "Fertilizers, Bio-pesticides & Seeds",
            "phone": "+91 99887 76655",
            "address": "KR Market Main Road, Bengaluru",
            "location": {"lat": 12.9632, "lng": 77.5746}
        },
        {
            "name": "Kisan Agro Kendra & Supplies",
            "type": "Certified Seeds & Crop Medicines",
            "phone": "+91 98765 12345",
            "address": "Near APMC Yard, Yeshwanthpur, Bengaluru",
            "location": {"lat": 13.0285, "lng": 77.5409}
        },
        {
            "name": "Green Earth Farm Store",
            "type": "Neem Oil, Trichoderma & Organic Inputs",
            "phone": "+91 88990 01122",
            "address": "4th Block, Jayanagar, Bengaluru",
            "location": {"lat": 12.9299, "lng": 77.5824}
        },
        {
            "name": "Farmers Co-operative Society (Raitha Seva)",
            "type": "Subsidized Fertilizers & Sprayers",
            "phone": "+91 80 2233 4455",
            "address": "Sampige Road, Malleswaram, Bengaluru",
            "location": {"lat": 13.0031, "lng": 77.5714}
        },
        {
            "name": "Annapurna Agro Agencies",
            "type": "Micro-nutrients, Fungicides & Tools",
            "phone": "+91 80 2856 1122",
            "address": "BB Road, Yelahanka, Bengaluru",
            "location": {"lat": 13.1022, "lng": 77.5988}
        },
        {
            "name": "Karnataka Agro Chemicals",
            "type": "Plant Protection Chemicals & Drip Spares",
            "phone": "+91 98450 12890",
            "address": "Peenya 2nd Stage, Bengaluru",
            "location": {"lat": 13.0322, "lng": 77.5188}
        }
    ]
    
    db.experts.drop()
    db.stores.drop()
    db.agricultural_stores.drop()
    
    if experts:
        db.experts.insert_many(experts)
        print(f"Inserted {len(experts)} experts into 'experts' collection.")
        
    if stores:
        db.stores.insert_many(stores)
        # also populate agricultural_stores alias so any query works
        db.agricultural_stores.insert_many(stores)
        print(f"Inserted {len(stores)} stores into 'stores' and 'agricultural_stores'.")

if __name__ == "__main__":
    seed_locations()
