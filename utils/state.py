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
    """Return one persistent Supabase client for this Streamlit session.

    Keeping the same client instance is important because Supabase Auth
    stores the signed-in user's access token on the client. Creating a new
    client for every database call would lose that authenticated session and
    cause RLS-protected profile/campaign queries to fail.
    """
    if create_client is None:
        return None

    existing = st.session_state.get("_supabase_client")
    if existing is not None:
        return existing

    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")

    if not url or not key:
        return None

    try:
        client = create_client(url, key)
        st.session_state["_supabase_client"] = client
        return client
    except Exception as exc:
        st.session_state["supabase_error"] = str(exc)
        return None


def _default_campaigns():
    """Demo-only campaign records. Never used for real accounts."""
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
        "brand_name": "",
        "industry": "",
        "city": "",
        "audience": "",
        "values": [],
        "role": "",
        "profile": {},
        # Real users start with an empty library.
        # Demo campaigns are loaded only by the demo login path.
        "campaign_library": [],
        "selected_campaign_id": None,
        "campaign_brief": None,
        "campaign_strategy": None,
        "campaign_caption": None,
        "is_demo": False,
        "profile_complete": False,
        "current_page": "🔐 Login",
        "supabase_error": "",
        "app_state_version": 5,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Clear legacy demo/session data from earlier Akovate builds.
    if st.session_state.get("app_state_version") != 5:
        st.session_state["app_state_version"] = 5
        if not st.session_state.get("is_demo"):
            st.session_state["campaign_library"] = []
            st.session_state["selected_campaign_id"] = None
            st.session_state["campaign_brief"] = None
            st.session_state["campaign_strategy"] = None
            st.session_state["campaign_caption"] = None


def _normalise_role(role):
    if role in ROLES:
        return role
    return "Brand"


def load_user_data(user_id, email, auth_metadata=None):
    """
    Load a real user's profile and campaigns.

    If the profile row does not exist yet, the name/role captured in
    Supabase Auth metadata during signup becomes the user's profile.
    This prevents the demo profile from ever being used for real users.
    """
    supabase = get_supabase()

    if supabase is None:
        return False

    metadata = auth_metadata or {}
    metadata_name = (
        metadata.get("name")
        or metadata.get("full_name")
        or metadata.get("display_name")
        or ""
    )
    metadata_role = _normalise_role(metadata.get("role"))
    metadata_industry = metadata.get("industry") or ""
    metadata_city = metadata.get("city") or ""
    metadata_audience = metadata.get("audience") or ""
    metadata_values = metadata.get("values") or []
    if isinstance(metadata_values, str):
        metadata_values = [metadata_values]

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

            saved_name = profile.get("name") or ""
            saved_role = profile.get("role") or ""

            # Older builds could save the demo placeholder into a real
            # account. Auth metadata from signup is authoritative in that
            # case, so repair the profile automatically.
            if saved_name in ("", "Akovate Demo Brand") and metadata_name:
                saved_name = metadata_name
            name = saved_name or metadata_name or "Akovate User"

            if (
                not saved_role
                or saved_role == "Brand"
                and metadata_role != "Brand"
                and metadata_role in ROLES
            ):
                saved_role = metadata_role

            role = _normalise_role(saved_role or metadata_role)

            st.session_state["brand_name"] = name
            st.session_state["role"] = role
            st.session_state["industry"] = profile.get("industry") or metadata_industry
            st.session_state["city"] = profile.get("city") or metadata_city
            st.session_state["audience"] = profile.get("audience") or metadata_audience
            st.session_state["values"] = profile.get("values") or metadata_values
            st.session_state["profile"] = profile
            st.session_state["profile_complete"] = True

            if (
                profile.get("name") != name
                or _normalise_role(profile.get("role")) != role
                or (profile.get("industry") or "") != st.session_state.get("industry", "")
                or (profile.get("city") or "") != st.session_state.get("city", "")
                or (profile.get("audience") or "") != st.session_state.get("audience", "")
                or (profile.get("values") or []) != st.session_state.get("values", [])
            ):
                repaired_profile = {
                    "id": user_id,
                    "email": email,
                    "name": name,
                    "role": role,
                    "industry": st.session_state.get("industry", ""),
                    "city": st.session_state.get("city", ""),
                    "audience": st.session_state.get("audience", ""),
                    "values": st.session_state.get("values", []),
                }
                supabase.table("profiles").upsert(
                    repaired_profile,
                    on_conflict="id",
                ).execute()
                st.session_state["profile"] = repaired_profile

        else:
            # First successful login for a newly-created account.
            # Build the profile directly from Auth metadata.
            profile_data = {
                "id": user_id,
                "email": email,
                "name": metadata_name or "Akovate User",
                "role": metadata_role,
                "industry": metadata_industry,
                "city": metadata_city,
                "audience": metadata_audience,
                "values": metadata_values,
            }

            # The user is authenticated at this point, so the RLS policy
            # allows the user's own profile row to be inserted.
            (
                supabase.table("profiles")
                .upsert(profile_data, on_conflict="id")
                .execute()
            )

            st.session_state["brand_name"] = profile_data["name"]
            st.session_state["role"] = profile_data["role"]
            st.session_state["industry"] = metadata_industry
            st.session_state["city"] = metadata_city
            st.session_state["audience"] = metadata_audience
            st.session_state["values"] = metadata_values
            st.session_state["profile"] = profile_data
            st.session_state["profile_complete"] = True

        campaign_response = (
            supabase.table("campaigns")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        # This is the critical isolation rule:
        # a real user sees ONLY campaigns whose user_id is theirs.
        st.session_state["campaign_library"] = campaign_response.data or []
        st.session_state["selected_campaign_id"] = None
        st.session_state["campaign_brief"] = None
        st.session_state["campaign_strategy"] = None
        st.session_state["campaign_caption"] = None

        return True

    except Exception as exc:
        st.session_state["supabase_error"] = str(exc)
        return False


def save_profile():
    """Persist the currently authenticated user's profile."""
    supabase = get_supabase()
    user_id = st.session_state.get("user_id")

    if supabase is None or not user_id or user_id == "demo-user":
        return False

    profile_data = {
        "id": user_id,
        "email": st.session_state.get("user_email", ""),
        "name": st.session_state.get("brand_name", ""),
        "role": _normalise_role(st.session_state.get("role")),
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
        st.session_state["brand_name"] = profile_data["name"]
        st.session_state["role"] = profile_data["role"]
        st.session_state["profile_complete"] = True
        return True

    except Exception as exc:
        st.session_state["supabase_error"] = str(exc)
        return False


def save_campaign(campaign):
    """Persist a campaign to the currently authenticated user's library."""
    supabase = get_supabase()
    user_id = st.session_state.get("user_id")

    if supabase is None or not user_id:
        return None

    # Demo campaigns are kept local and never written to the real-user table.
    if user_id == "demo-user":
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


def update_campaign(campaign_id, campaign):
    """Update a real user's campaign. Demo campaigns are read-only."""
    user_id = st.session_state.get("user_id")
    if not user_id or st.session_state.get("is_demo") or user_id == "demo-user":
        return None

    supabase = get_supabase()
    if supabase is None:
        return None

    payload = {
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
            .update(payload)
            .eq("id", campaign_id)
            .eq("user_id", user_id)
            .execute()
        )
        if response.data:
            saved = response.data[0]
            for i, item in enumerate(st.session_state.get("campaign_library", [])):
                if str(item.get("id")) == str(campaign_id):
                    st.session_state["campaign_library"][i] = saved
                    break
            return saved
    except Exception as exc:
        st.session_state["supabase_error"] = str(exc)
    return None


def delete_campaign(campaign_id):
    """Delete a real user's campaign. Demo campaigns are never modified."""
    user_id = st.session_state.get("user_id")
    if not user_id or st.session_state.get("is_demo") or user_id == "demo-user":
        return False

    supabase = get_supabase()
    if supabase is None:
        return False

    try:
        (
            supabase.table("campaigns")
            .delete()
            .eq("id", campaign_id)
            .eq("user_id", user_id)
            .execute()
        )
        st.session_state["campaign_library"] = [
            c for c in st.session_state.get("campaign_library", [])
            if str(c.get("id")) != str(campaign_id)
        ]
        if str(st.session_state.get("selected_campaign_id")) == str(campaign_id):
            st.session_state["selected_campaign_id"] = None
            st.session_state["campaign_brief"] = None
            st.session_state["campaign_strategy"] = None
            st.session_state["campaign_caption"] = None
        return True
    except Exception as exc:
        st.session_state["supabase_error"] = str(exc)
        return False


def load_demo_data():
    """Load the original demo workspace without touching real-user data.

    Demo data remains local/prototype data. It is never inserted into,
    selected from, or overwritten in the real user's Supabase campaign
    library.
    """
    st.session_state["authenticated"] = True
    st.session_state["user_email"] = DEMO_EMAIL
    st.session_state["user_id"] = "demo-user"
    st.session_state["is_demo"] = True

    # Preserve original demo identity.
    st.session_state["brand_name"] = "Akovate Demo Brand"
    st.session_state["industry"] = "Technology"
    st.session_state["city"] = "Hyderabad"
    st.session_state["audience"] = "Urban Gen Z and young millennials"
    st.session_state["values"] = [
        "Growth",
        "Creator authenticity",
        "Sustainability",
    ]
    st.session_state["role"] = "Brand"
    st.session_state["profile_complete"] = True
    st.session_state["profile"] = {
        "id": "demo-user",
        "email": DEMO_EMAIL,
        "name": "Akovate Demo Brand",
        "role": "Brand",
        "industry": "Technology",
        "city": "Hyderabad",
        "audience": "Urban Gen Z and young millennials",
        "values": st.session_state["values"],
    }

    # Preserve original demo/sample campaigns.
    st.session_state["campaign_library"] = _default_campaigns()
    st.session_state["selected_campaign_id"] = None
    st.session_state["campaign_brief"] = None
    st.session_state["campaign_strategy"] = None
    st.session_state["campaign_caption"] = None
    st.session_state["current_page"] = "🏠 Home"



def selected_campaign():
    selected_id = st.session_state.get("selected_campaign_id")

    if not selected_id:
        return None

    for campaign in st.session_state.get("campaign_library", []):
        if str(campaign.get("id")) == str(selected_id):
            return campaign

    return None


def select_campaign(campaign_id):
    st.session_state["selected_campaign_id"] = campaign_id

    campaign = next(
        (
            c
            for c in st.session_state.get("campaign_library", [])
            if str(c.get("id")) == str(campaign_id)
        ),
        None,
    )

    if campaign:
        st.session_state["campaign_brief"] = campaign.get("brief") or {}
        st.session_state["campaign_strategy"] = None
        st.session_state["campaign_caption"] = None


def logout():
    supabase = get_supabase()

    if supabase is not None:
        try:
            supabase.auth.sign_out()
        except Exception:
            pass

    # Drop the authenticated client so the next login gets a clean auth session.
    st.session_state.pop("_supabase_client", None)

    # Fully clear user-specific state so the next login can never inherit
    # another account's name, role, or campaigns.
    for key, value in {
        "authenticated": False,
        "user_email": "",
        "user_id": "",
        "brand_name": "",
        "industry": "",
        "city": "",
        "audience": "",
        "values": [],
        "role": "",
        "profile": {},
        "campaign_library": [],
        "selected_campaign_id": None,
        "campaign_brief": None,
        "campaign_strategy": None,
        "campaign_caption": None,
        "is_demo": False,
        "profile_complete": False,
        "current_page": "🔐 Login",
        "supabase_error": "",
        "app_state_version": 5,
    }.items():
        st.session_state[key] = value
