"""
Promote a user to Admin role in MongoDB.

Usage:
    python scripts/promote_admin.py                    # Promotes the first registered user
    python scripts/promote_admin.py farmer@example.com # Promotes specific user by email
"""

import os
import sys
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows consoles to prevent cp1252 UnicodeEncodeError
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


def promote_user(target_email=None):
    load_dotenv()
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("DATABASE_NAME", "plant_disease_db")

    kwargs = {"serverSelectionTimeoutMS": 5000}
    if "mongodb+srv" in mongo_uri or "ssl=true" in mongo_uri.lower():
        kwargs["tlsCAFile"] = certifi.where()

    try:
        client = MongoClient(mongo_uri, **kwargs)
        db = client[db_name]
        
        # Test connection
        client.admin.command('ping')
    except Exception as e:
        print(f"[ERROR] Failed to connect to MongoDB at {mongo_uri[:35]}...")
        print(f"   Error: {e}")
        print("   Please check that MongoDB is running or that MONGODB_URI in .env is correct.")
        sys.exit(1)

    query = {"email": target_email} if target_email else {}
    user = db.users.find_one(query)

    if user:
        db.users.update_one({"_id": user["_id"]}, {"$set": {"role": "admin"}})
        print(f"[OK] Successfully promoted '{user.get('email')}' (ID: {user['_id']}) to role 'admin'.")
    else:
        if target_email:
            print(f"[WARNING] No user found with email '{target_email}'.")
        else:
            print("[WARNING] No users found in database. Register a user in the web application first.")


if __name__ == "__main__":
    email_arg = sys.argv[1] if len(sys.argv) > 1 else None
    promote_user(email_arg)
