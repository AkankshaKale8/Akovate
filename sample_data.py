import pandas as pd

CAMPAIGNS = pd.DataFrame([
    {"campaign": "Akovate Launch", "objective": "Awareness", "budget": "₹5L", "status": "Active", "roas": 4.8},
    {"campaign": "Creator Proof Series", "objective": "Engagement", "budget": "₹3L", "status": "Active", "roas": 4.2},
    {"campaign": "Green Growth", "objective": "Leads", "budget": "₹2.5L", "status": "Planning", "roas": 3.7},
])

CREATORS = pd.DataFrame([
    {"creator": "Aarav Mehta", "city": "Hyderabad", "category": "Technology", "engagement_rate": 6.8, "audience_fit": 92, "content_fit": 90, "sustainability_fit": 88, "budget_fit": 85},
    {"creator": "Riya Shah", "city": "Mumbai", "category": "Lifestyle", "engagement_rate": 7.4, "audience_fit": 88, "content_fit": 94, "sustainability_fit": 82, "budget_fit": 78},
    {"creator": "Kabir Rao", "city": "Bengaluru", "category": "Business", "engagement_rate": 5.9, "audience_fit": 95, "content_fit": 89, "sustainability_fit": 91, "budget_fit": 90},
    {"creator": "Meera Nair", "city": "Pune", "category": "Beauty & Wellness", "engagement_rate": 8.1, "audience_fit": 84, "content_fit": 96, "sustainability_fit": 87, "budget_fit": 82},
])

PLATFORM_STATS = {
    "active_campaigns": 3,
    "partners": 460,
    "avg_match_score": 91,
    "green": 78,
}
