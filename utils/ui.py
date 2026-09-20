import streamlit as st
from pathlib import Path

GREEN = "#2A7A0B"
GREEN_LIGHT = "#57A90B"
ORANGE = "#F47B00"
RED = "#D71920"
YELLOW = "#F8B708"
INK = "#182329"
CREAM = "#FFFDF7"

def inject_css():
    st.markdown(
        f"""
        <style>
        :root {{
            --ak-green: {GREEN};
            --ak-green-light: {GREEN_LIGHT};
            --ak-orange: {ORANGE};
            --ak-red: {RED};
            --ak-yellow: {YELLOW};
            --ak-ink: {INK};
        }}
        .stApp {{ background: {CREAM}; }}
        [data-testid="stSidebar"] {{ background: #f6fbf2; }}
        [data-testid="stMetric"] {{
            background: white;
            border: 1px solid #e6eadf;
            border-radius: 16px;
            padding: 14px;
        }}
        .stButton > button {{
            border-radius: 12px;
            border: 0;
            font-weight: 700;
        }}
        h1, h2, h3 {{ color: {INK}; }}
        @media (max-width: 768px) {{
            .block-container {{ padding: 1rem 0.8rem 2rem 0.8rem; }}
            h1 {{ font-size: 1.8rem; }}
            h2 {{ font-size: 1.35rem; }}
            [data-testid="stSidebar"] {{ min-width: 240px; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def logo():
    path = Path("assets/akovate_exact_logo.png")
    if path.exists():
        st.image(str(path), use_container_width=True)

def metric_card(container, label, value, caption=""):
    container.metric(label, value, caption)
