from app.extensions import get_db

class AdminService:
    @staticmethod
    def get_dashboard_stats():
        """Retrieve key metrics for the admin dashboard."""
        db = get_db()
        return {
            "total_users": db.users.count_documents({}),
            "total_predictions": db.predictions.count_documents({}),
            "total_plants": db.plants.count_documents({}),
            "total_reminders": db.reminders.count_documents({})
        }

    @staticmethod
    def get_all_users():
        db = get_db()
        return list(db.users.find({}, {"password_hash": 0}).sort("created_at", -1))

    @staticmethod
    def suspend_user(user_id):
        from bson.objectid import ObjectId
        db = get_db()
        # Toggle suspended status
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            new_status = not user.get("suspended", False)
            db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"suspended": new_status}})

    @staticmethod
    def get_all_diseases():
        db = get_db()
        return list(db.diseases.find({}).sort("name", 1))

    @staticmethod
    def update_disease(class_name, data):
        db = get_db()
        db.diseases.update_one({"class_name": class_name}, {"$set": data}, upsert=True)

    @staticmethod
    def get_all_treatments():
        db = get_db()
        return list(db.treatments.find({}))

    @staticmethod
    def update_treatment(class_name, data):
        db = get_db()
        db.treatments.update_one({"disease_class": class_name}, {"$set": data}, upsert=True)

    @staticmethod
    def get_all_risk_rules():
        db = get_db()
        return list(db.risk_rules.find({}))

    @staticmethod
    def add_or_update_risk_rule(data):
        db = get_db()
        db.risk_rules.update_one(
            {"disease_class": data['disease_class'], "crop": data['crop']},
            {"$set": data},
            upsert=True
        )

    @staticmethod
    def delete_risk_rule(disease_class, crop):
        db = get_db()
        db.risk_rules.delete_one({"disease_class": disease_class, "crop": crop})

    @staticmethod
    def log_action(user_id, action, target_type=None, target_id=None, details=None):
        from datetime import datetime, timezone
        db = get_db()
        log_entry = {
            "user_id": user_id,
            "action": action,
            "target_type": target_type,
            "target_id": target_id,
            "details": details or {},
            "created_at": datetime.now(timezone.utc)
        }
        db.audit_logs.insert_one(log_entry)

    @staticmethod
    def get_audit_logs(limit=20):
        db = get_db()
        return list(db.audit_logs.find({}).sort("created_at", -1).limit(limit))
