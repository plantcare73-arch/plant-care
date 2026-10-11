# 03 - Information Architecture

## 1. Sitemap / Navigation

The application uses a flat, accessible hierarchy suitable for mobile and desktop views.

### Public Routes
- `/` - Landing Page (Hero, How it works, Supported crops)
- `/login` - Authentication Login
- `/register` - Account Creation
- `/404` - Not Found Error
- `/500` - Server Error

### Farmer (Authenticated) Routes
- `/dashboard` - Overview (Stats, Recent Predictions, Active Alerts, Reminders)
- `/predictions/detect` - Upload Image & Run Prediction
- `/predictions/result/:id` - Detailed Prediction View (Confidence, Treatments)
- `/predictions/history` - Paginated Prediction History
- `/plants` - User's Saved Plants/Crops
- `/plants/:id` - Specific Plant details
- `/care-cases` - Ongoing Treatment tracking
- `/care-cases/:id` - Specific case details (Before/After comparison)
- `/weather` - Weather & Irrigation advice
- `/alerts` - Disease Outbreak Alerts
- `/experts` - Nearby Agricultural Experts
- `/stores` - Nearby Agricultural Stores
- `/reminders` - Treatment & Follow-up Reminders
- `/profile` / `/settings` - User settings and language preferences
- `/reviews` - System Feedback & Reviews

### Admin Routes
- `/admin/` - Admin Dashboard / Analytics
- `/admin/diseases` - Manage Disease Knowledge Base
- `/admin/treatments` - Manage Treatment Protocols
- `/admin/users` - User Management
- `/admin/risk-rules` - Configure Weather-based Risk Rules

## 2. Key User Flows

### Prediction Journey
1. User logs in and lands on Dashboard.
2. Clicks "Detect Disease" -> Reaches upload form.
3. Uploads image -> System validates -> Shows loading state.
4. Redirected to Result page -> Views Disease, Confidence, Symptoms, Treatments.
5. Can choose to "Create Care Case" or "Set Reminder".

### Treatment & Before/After Journey
1. User views an existing Care Case.
2. Clicks "Add Follow-up Image".
3. Uploads new image -> New Prediction generated.
4. System displays side-by-side comparison of initial state and current state.
5. User updates status (Improving, Worsening, Resolved).
