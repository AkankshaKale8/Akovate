import streamlit as st

def init_state():
    defaults = {
        "brand_name": "Akovate Demo Brand",
        "industry": "Technology",
        "city": "Hyderabad",
        "audience": "Urban Gen Z and young millennials",
        "values": ["Growth", "Creator authenticity", "Sustainability"],
        "campaign_brief": None,
        "campaign_strategy": None,
        "role": "Brand",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
