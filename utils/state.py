import streamlit as st
from data.sample_data import CAMPAIGNS

try:
    from supabase import create_client
except ImportError:
    create_client = None


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


def get_supabase():
    """Return the configured Supabase client, or None if not configured."""
    if create_client is None:
        return None

    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")

    if not url or not key:
        return None

    try:
        return create_client(url, key)
    except Exception:
        return None


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
        "user_id": "",
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
        "is_demo": False,
        "profile_complete": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def load_user_data(user_id, email):
    """Load the user's profile and campaigns from Supabase."""
    supabase = get_supabase()

    if supabase is None:
        return False

    try:
        profile_response = (
            supabase.table("profiles")
            .select("*")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )

        profile_rows = profile_response.data or []

        if profile_rows:
            profile = profile_rows[0]

            st.session_state["brand_name"] = (
                profile.get("name")
                or st.session_state.get("brand_name")
                or "Akovate User"
            )
            st.session_state["role"] = (
                profile.get("role")
                or st.session_state.get("role")
                or "Brand"
            )
            st.session_state["industry"] = profile.get("industry") or ""
            st.session_state["city"] = profile.get("city") or ""
            st.session_state["audience"] = profile.get("audience") or ""
            st.session_state["values"] = profile.get("values") or []
            st.session_state["profile"] = profile
            st.session_state["profile_complete"] = True

        else:
            # New authenticated user: do NOT use demo profile defaults.
            # Preserve the name/role captured during account creation.
            st.session_state["brand_name"] = (
                st.session_state.get("brand_name")
                if st.session_state.get("brand_name")
                not in ("Akovate Demo Brand", "")
                else ""
            )
            st.session_state["role"] = (
                st.session_state.get("role")
                if st.session_state.get("role") in ROLES
                else "Brand"
            )
            st.session_state["industry"] = ""
            st.session_state["city"] = ""
            st.session_state["audience"] = ""
            st.session_state["values"] = []
            st.session_state["profile"] = {
                "id": user_id,
                "email": email,
                "name": st.session_state["brand_name"],
                "role": st.session_state["role"],
                "industry": "",
                "city": "",
                "audience": "",
                "values": [],
            }
            st.session_state["profile_complete"] = False
        campaign_response = (
            supabase.table("campaigns")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        campaigns = campaign_response.data or []

        st.session_state["campaign_library"] = campaigns
        st.session_state["selected_campaign_id"] = None
        st.session_state["campaign_brief"] = None
        st.session_state["campaign_strategy"] = None
        st.session_state["campaign_caption"] = None

        return True

    except Exception as exc:
        st.session_state["supabase_error"] = str(exc)
        return False


def save_profile():
    """Save the current user's profile to Supabase."""
    supabase = get_supabase()
    user_id = st.session_state.get("user_id")

    if supabase is None or not user_id:
        return False

    profile_data = {
        "id": user_id,
        "email": st.session_state.get("user_email", ""),
        "name": st.session_state.get("brand_name", ""),
        "role": st.session_state.get("role", "Brand"),
        "industry": st.session_state.get("industry", ""),
        "city": st.session_state.get("city", ""),
        "audience": st.session_state.get("audience", ""),
        "values": st.session_state.get("values", []),
    }

    try:
        supabase.table("profiles").upsert(
            profile_data,
            on_conflict="id",
        ).execute()

        st.session_state["profile"] = profile_data
        return True

    except Exception as exc:
        st.session_state["supabase_error"] = str(exc)
        return False


def save_campaign(campaign):
    """Save a campaign belonging to the currently authenticated user."""
    supabase = get_supabase()
    user_id = st.session_state.get("user_id")

    if supabase is None or not user_id:
        return None

    campaign_data = {
        "user_id": user_id,
        "campaign": campaign.get("campaign", ""),
        "objective": campaign.get("objective", ""),
        "budget": str(campaign.get("budget", "")),
        "status": campaign.get("status", "Draft"),
        "roas": campaign.get("roas"),
        "brief": campaign.get("brief", {}),
    }

    try:
        response = (
            supabase.table("campaigns")
            .insert(campaign_data)
            .execute()
        )

        if response.data:
            saved = response.data[0]
            st.session_state["campaign_library"].insert(0, saved)
            return saved

    except Exception as exc:
        st.session_state["supabase_error"] = str(exc)

    return None


def selected_campaign():
    selected_id = st.session_state.get("selected_campaign_id")

    for campaign in st.session_state.get("campaign_library", []):
        if str(campaign.get("id")) == str(selected_id):
            return campaign

    return None


def select_campaign(campaign_id):
    st.session_state["selected_campaign_id"] = campaign_id

    campaign = next(
        (
            c
            for c in st.session_state["campaign_library"]
            if str(c.get("id")) == str(campaign_id)
        ),
        None,
    )

    if campaign:
        st.session_state["campaign_brief"] = campaign.get("brief")
        st.session_state["campaign_strategy"] = None
        st.session_state["campaign_caption"] = None


def logout():
    supabase = get_supabase()

    if supabase is not None:
        try:
            supabase.auth.sign_out()
        except Exception:
            pass

    st.session_state["authenticated"] = False
    st.session_state["user_email"] = ""
    st.session_state["user_id"] = ""
    st.session_state["selected_campaign_id"] = None
    st.session_state["campaign_brief"] = None
    st.session_state["campaign_strategy"] = None
    st.session_state["campaign_caption"] = None
    st.session_state["is_demo"] = False
