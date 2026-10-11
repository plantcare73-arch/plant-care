from pymongo import MongoClient

def promote_first_user():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["plant_disease_db"]
    user = db.users.find_one({})
    if user:
        db.users.update_one({"_id": user["_id"]}, {"$set": {"role": "admin"}})
        print(f"Promoted {user.get('email')} to admin.")
    else:
        print("No users found.")

if __name__ == "__main__":
    promote_first_user()
