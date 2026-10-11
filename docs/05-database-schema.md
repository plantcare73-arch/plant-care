# 05 - Database Schema

The system uses **MongoDB** as its primary datastore. All records are scoped to `user_id` where applicable to ensure data privacy.

## Collections

### 1. `users`
- `_id`: ObjectId
- `email`: String (Unique, Indexed)
- `password`: String (Bcrypt Hash)
- `name`: String
- `role`: String (enum: `farmer`, `admin`)
- `preferences`: Object { `language`: String }
- `created_at`: DateTime

### 2. `diseases`
- `_id`: ObjectId
- `class_name`: String (Unique, Indexed, maps to CNN output)
- `crop`: String
- `disease_name`: String
- `description`: String
- `symptoms`: Array of Strings
- `severity_supported`: Boolean
- `created_at`: DateTime

### 3. `treatments`
- `_id`: ObjectId
- `disease_class`: String (Indexed, Refers to `diseases.class_name`)
- `category`: String (enum: `organic`, `chemical`, `preventive`)
- `instructions`: Array of Strings
- `safety_warnings`: Array of Strings
- `source`: String
- `last_reviewed`: DateTime

### 4. `predictions`
- `_id`: ObjectId
- `user_id`: ObjectId (Indexed)
- `image_filename`: String
- `predicted_class`: String
- `confidence`: Float (0.0 to 1.0)
- `all_predictions`: Map<String, Float>
- `model_version`: String
- `created_at`: DateTime (Indexed)

### 5. `care_cases` (Before/After tracking)
- `_id`: ObjectId
- `user_id`: ObjectId (Indexed)
- `plant_id`: ObjectId (Optional)
- `initial_prediction_id`: ObjectId
- `follow_up_prediction_ids`: Array of ObjectIds
- `treatment_applied`: String
- `status`: String (enum: `ACTIVE`, `IMPROVING`, `RESOLVED`)
- `created_at`: DateTime
- `updated_at`: DateTime

### 6. `reminders`
- `_id`: ObjectId
- `user_id`: ObjectId (Indexed)
- `title`: String
- `due_date`: DateTime (Indexed)
- `status`: String (enum: `pending`, `completed`)
- `created_at`: DateTime

### 7. `risk_rules`
- `_id`: ObjectId
- `crop`: String
- `disease_class`: String
- `conditions`: Object (e.g., `{ humidity: { ">": 80 }, temp: { ">": 25 } }`)
- `risk_level`: String (enum: `LOW`, `MODERATE`, `HIGH`)
- `explanation`: String
- `enabled`: Boolean

### 8. `reviews`
- `_id`: ObjectId
- `user_id`: ObjectId
- `user_name`: String
- `rating`: Integer (1-5)
- `comment`: String
- `created_at`: DateTime
