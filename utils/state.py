import streamlit as st
from data.sample_data import CAMPAIGNS


DEMO_EMAIL = "demo@akovate.ai"
DEMO_PASSWORD = "Akovate@123"
ROLES = [
    "Brand",
    "Creator / Influencer",
    "Freelancer",
    "Agency",
    "Legal Professional",
    "Sustainability Partner",
    "Admin",
]
def _default_campaigns():
    records = []

    for i, row in CAMPAIGNS.iterrows():
        records.append(
            {
                "id": f"campaign-{i + 1}",
                "campaign": row["campaign"],
                "objective": row["objective"],
                "budget": row["budget"],
                "status": row["status"],
                "roas": row["roas"],
                "brief": {
                    "objective": row["objective"],
                    "product": row["campaign"],
                    "budget": 500000,
                    "duration": 21,
                    "audience": "Urban Gen Z and young millennials",
                    "sustainability": True,
                },
            }
        )

    return records


def init_state():
    defaults = {
        "authenticated": False,
        "user_email": "",
        "brand_name": "Akovate Demo Brand",
        "industry": "Technology",
        "city": "Hyderabad",
        "audience": "Urban Gen Z and young millennials",
        "values": [
            "Growth",
            "Creator authenticity",
            "Sustainability",
        ],
        "role": "Brand",
        "profile": {},
        "campaign_library": _default_campaigns(),
        "selected_campaign_id": None,
        "campaign_brief": None,
        "campaign_strategy": None,
        "campaign_caption": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def selected_campaign():
    selected_id = st.session_state.get("selected_campaign_id")

    for campaign in st.session_state.get("campaign_library", []):
        if campaign["id"] == selected_id:
            return campaign

    return None


def select_campaign(campaign_id):
    st.session_state["selected_campaign_id"] = campaign_id

    campaign = next(
        (
            c
            for c in st.session_state["campaign_library"]
            if c["id"] == campaign_id
        ),
        None,
    )

    if campaign:
        st.session_state["campaign_brief"] = campaign.get("brief")
        st.session_state["campaign_strategy"] = None
        st.session_state["campaign_caption"] = None


def logout():
    st.session_state["authenticated"] = False
    st.session_state["user_email"] = ""
    st.session_state["selected_campaign_id"] = None
    st.session_state["campaign_brief"] = None
    st.session_state["campaign_strategy"] = None
