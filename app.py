import streamlit as st
from utils.ui import inject_css, logo, metric_card

from utils.state import (
    DEMO_EMAIL,
    DEMO_PASSWORD,
    ROLES,
    get_supabase,
    init_state,
    load_user_data,
    load_demo_data,
    logout,
    save_campaign,
    save_profile,
    select_campaign,
    selected_campaign,
)
from data.sample_data import CREATORS, PLATFORM_STATS
from ai.strategy import generate_strategy
from ai.matching import match_creators
from ai.roi import calculate_roi
from ai.sentiment import analyze_sentiment
from ai.viral import viral_score
from ai.green import green_score
from ai.impact import campaign_impact


st.set_page_config(
    page_title="Akovate | AI Marketing Collaboration",
    page_icon="assets/akovate_exact_logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
init_state()

# Never allow demo data to leak into a real user's workspace.
if (
    st.session_state.get("authenticated")
    and not st.session_state.get("is_demo")
    and st.session_state.get("user_id")
    and st.session_state.get("user_id") != "demo-user"
    and st.session_state.get("brand_name") == "Akovate Demo Brand"
):
    st.session_state["brand_name"] = ""
    st.session_state["campaign_library"] = []
    st.session_state["selected_campaign_id"] = None
    st.session_state["campaign_brief"] = None
    st.session_state["campaign_strategy"] = None
    st.session_state["campaign_caption"] = None

PUBLIC_PAGES = {
    "🏠 Home",
    "🔐 Login",
    "📚 Campaign Library",
    "⚙️ Settings",
    "🌐 Platform Network",
}

CAMPAIGN_WORKSPACE_PAGES = {
    "📊 Dashboard",
    "🤝 AI Talent Matching",
    "🧩 Campaign Workspace",
    "📈 Influencer ROI",
    "💬 Brand Sentiment",
    "🔥 Viral Strategy",
    "🌱 Green Campaign Score",
    "🧠 Campaign Intelligence",
}


def go(page):
    st.session_state["current_page"] = page
    st.rerun()


def campaign_required(page):
    return page in CAMPAIGN_WORKSPACE_PAGES and selected_campaign() is None


def render_login():
    st.title("Welcome to Akovate")
    st.subheader("Sign in to your marketing collaboration workspace")
    st.caption("Create your own workspace or use the built-in demo account.")

    login_tab, signup_tab = st.tabs(["🔐 Login", "✨ Create Account"])

    with login_tab:
        left, right = st.columns([1.25, 1])

        with left:
            with st.form("login_form"):
                email = st.text_input(
                    "Email",
                    placeholder="you@example.com",
                    key="login_email",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Your password",
                    key="login_password",
                )
                submitted = st.form_submit_button(
                    "Login",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                email_clean = email.strip().lower()

                if email_clean == DEMO_EMAIL and password == DEMO_PASSWORD:
                    # DEMO MODE IS FULLY ISOLATED.
                    # Preserve the original demo profile and demo campaign
                    # library. Never mix demo data with real-user Supabase data.
                    load_demo_data()
                    st.session_state["login_error"] = ""
                    st.session_state["current_page"] = "🏠 Home"
                    st.success("Demo login successful.")
                    st.rerun()

                else:
                    supabase = get_supabase()

                    if supabase is None:
                        st.error(
                            "Akovate could not connect to the account service. "
                            "Please check the app configuration."
                        )
                    else:
                        try:
                            response = supabase.auth.sign_in_with_password(
                                {
                                    "email": email_clean,
                                    "password": password,
                                }
                            )

                            user = response.user

                            if user:
                                # Never carry another account's in-memory
                                # campaigns/profile into this login.
                                st.session_state["campaign_library"] = []
                                st.session_state["selected_campaign_id"] = None
                                st.session_state["campaign_brief"] = None
                                st.session_state["campaign_strategy"] = None
                                st.session_state["campaign_caption"] = None
                                st.session_state["authenticated"] = True
                                st.session_state["user_email"] = (
                                    user.email or email_clean
                                )
                                st.session_state["user_id"] = user.id
                                st.session_state["is_demo"] = False
                                st.session_state["login_error"] = ""

                                loaded = load_user_data(
                                    user.id,
                                    user.email or email_clean,
                                    getattr(user, "user_metadata", None),
                                )

                                if not loaded:
                                    st.session_state["authenticated"] = False
                                    st.session_state["is_demo"] = False
                                    st.session_state["campaign_library"] = []
                                    detail = st.session_state.get("supabase_error", "")
                                    st.error(
                                        "Your account was authenticated, but Akovate "
                                        "could not load your profile and campaign data. "
                                        "Please try logging in again."
                                    )
                                    if detail:
                                        st.caption(
                                            "Database connection detail: "
                                            + detail[:300]
                                        )
                                else:
                                    st.session_state["current_page"] = "🏠 Home"
                                    st.success("Login successful.")
                                    st.rerun()
                            else:
                                st.error("Login could not be completed.")

                        except Exception as exc:
                            message = str(exc)

                            if "Email not confirmed" in message:
                                st.error(
                                    "Please verify your email address first, "
                                    "then log in."
                                )
                            else:
                                st.error("Invalid email or password.")

        with right:
            st.info(
                "**Demo account**\n\n"
                f"Email: `{DEMO_EMAIL}`\n\n"
                f"Password: `{DEMO_PASSWORD}`"
            )

            st.markdown("### What you can explore")
            st.markdown(
                "- Personal campaign library\n"
                "- Explainable creator matching\n"
                "- ROI, sentiment and viral analytics\n"
                "- Green score and campaign intelligence"
            )

    with signup_tab:
        st.markdown("### Create your Akovate account")
        st.caption(
            "Your account will have its own profile and campaign workspace."
        )

        with st.form("signup_form"):
            name = st.text_input(
                "Name / Organisation",
                placeholder="Your name or organisation",
            )
            email = st.text_input(
                "Email",
                placeholder="you@example.com",
                key="signup_email",
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Create a password",
                key="signup_password",
            )
            confirm_password = st.text_input(
                "Confirm password",
                type="password",
                placeholder="Repeat your password",
                key="signup_confirm_password",
            )
            role = st.selectbox("Workspace role", ROLES, key="signup_role")

            create_account = st.form_submit_button(
                "Create Account",
                type="primary",
                use_container_width=True,
            )

        if create_account:
            email_clean = email.strip().lower()

            if not name.strip():
                st.error("Please enter your name or organisation.")
            elif not email_clean:
                st.error("Please enter your email address.")
            elif len(password) < 6:
                st.error("Password must contain at least 6 characters.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif email_clean == DEMO_EMAIL:
                st.error("That email is reserved for the Akovate demo account.")
            else:
                supabase = get_supabase()

                if supabase is None:
                    st.error(
                        "Akovate could not connect to the account service."
                    )
                else:
                    try:
                        response = supabase.auth.sign_up(
                            {
                                "email": email_clean,
                                "password": password,
                                "options": {
                                    "data": {
                                        "name": name.strip(),
                                        "role": role,
                                    }
                                },
                            }
                        )

                        if response.user:
                            user = response.user

                            if response.session:
                                st.session_state["authenticated"] = True
                                st.session_state["user_email"] = (
                                    user.email or email_clean
                                )
                                st.session_state["user_id"] = user.id
                                st.session_state["is_demo"] = False
                                st.session_state["role"] = role
                                st.session_state["brand_name"] = name.strip()
                                st.session_state["profile_complete"] = False

                                loaded = load_user_data(
                                    user.id,
                                    user.email or email_clean,
                                    getattr(user, "user_metadata", None),
                                )

                                if loaded:
                                    st.session_state["current_page"] = "🏠 Home"
                                    st.success("Account created successfully.")
                                    st.rerun()
                                else:
                                    st.error(
                                        "Account created, but Akovate could not "
                                        "load your profile. Please log in again."
                                    )
                            else:
                                st.success(
                                    "Account created. Please check your email "
                                    "and verify your account before logging in."
                                )

                    except Exception as exc:
                        message = str(exc)

                        if "already registered" in message.lower():
                            st.error("An account with this email already exists.")
                        else:
                            st.error(
                                "Account creation failed. "
                                "Please check your details and try again."
                            )


def render_sidebar():
    with st.sidebar:
        logo()
        st.markdown("### AKOVATE")
        st.caption("AI-POWERED MARKETING COLLABORATION PLATFORM")

        if st.session_state.get("authenticated"):
            st.success(
                f"Signed in as {st.session_state.get('user_email')}"
            )

            current_role = st.session_state.get("role", "Brand")
            st.markdown("**Workspace role**")
            st.info(current_role)

            campaign = selected_campaign()

            if campaign:
                st.markdown(
                    f"**Selected campaign:** {campaign.get('campaign', 'Campaign')}"
                )
            else:
                st.warning(
                    "Select a campaign to unlock campaign workspaces."
                )

            nav = [
                "🏠 Home",
                            "📚 Campaign Library",
                "⚙️ Settings",
                "🌐 Platform Network",
            ]
            nav += ["🎯 Create Campaign"] + list(CAMPAIGN_WORKSPACE_PAGES)

            current = st.session_state.get("current_page", "🏠 Home")
            page = st.radio(
                "Navigate",
                nav,
                index=nav.index(current) if current in nav else 0,
            )

            if page != current:
                st.session_state["current_page"] = page
                st.rerun()

            st.divider()

            if st.button("Logout", use_container_width=True):
                logout()
                st.rerun()

        else:
            st.info("Please log in to use the workspace.")

            if st.button(
                "Go to Login",
                use_container_width=True,
                type="primary",
            ):
                go("🔐 Login")

        st.divider()
        st.caption("Prototype mode • No external API keys required")


def render_home():
    name = st.session_state.get("brand_name") or "Akovate User"
    role = st.session_state.get("role", "Brand")

    st.title(f"Welcome back, {name}")
    st.subheader(
        "Your marketing workspace — from brief to measurable intelligence."
    )
    st.write(
        f"You are currently using Akovate as a **{role}**. "
        "Start with your campaign library, select a project, and unlock "
        "the complete campaign intelligence workflow."
    )

    c1, c2, c3, c4 = st.columns(4)
    metric_card(
        c1,
        "Campaigns",
        len(st.session_state["campaign_library"]),
        "Your project library",
    )
    metric_card(
        c2,
        "Partners",
        PLATFORM_STATS["partners"],
        "Demo network",
    )
    metric_card(
        c3,
        "Avg. match score",
        f'{PLATFORM_STATS["avg_match_score"]}%',
        "Explainable matching",
    )
    metric_card(
        c4,
        "Green index",
        f'{PLATFORM_STATS["green"]}%',
        "Responsible marketing",
    )

    st.markdown("### Start your journey")

    journey = [
        ("🔐", "Login", "🔐 Login"),
        ("📚", "Campaign Library", "📚 Campaign Library"),
        ("🎯", "Campaign Brief", "🎯 Create Campaign"),
        ("🤖", "AI Strategy", "🎯 Create Campaign"),
        ("🤝", "Talent Matching", "🤝 AI Talent Matching"),
        ("🧩", "Collaboration", "🧩 Campaign Workspace"),
        ("📈", "ROI", "📈 Influencer ROI"),
        ("💬", "Sentiment", "💬 Brand Sentiment"),
        ("🔥", "Viral Strategy", "🔥 Viral Strategy"),
        ("🌱", "Green Score", "🌱 Green Campaign Score"),
        ("🧠", "Impact Dashboard", "🧠 Campaign Intelligence"),
    ]

    cols = st.columns(4)

    for i, (icon, label, target) in enumerate(journey):
        with cols[i % 4]:
            if st.button(
                f"{icon} {label}",
                key=f"journey_{i}",
                use_container_width=True,
            ):
                if target in CAMPAIGN_WORKSPACE_PAGES and selected_campaign() is None:
                    st.warning(
                        "Select a campaign in Campaign Library first."
                    )
                else:
                    go(target)

    st.markdown("### How Akovate works")

    a, b, c = st.columns(3)
    a.markdown(
        "**AI layer**\n\n"
        "Strategy, explainable matching, content and analytics."
    )
    b.markdown(
        "**Platform layer**\n\n"
        "Brands collaborate with creators, freelancers, agencies "
        "and specialist partners."
    )
    c.markdown(
        "**Sustainability layer**\n\n"
        "Responsible campaign signals are measured alongside performance."
    )


def render_library():
    st.title("Campaign Library")
    st.caption(
        "Select one campaign to unlock its contextual workspaces and analytics."
    )

    campaigns = st.session_state["campaign_library"]

    if not campaigns:
        st.info("No campaigns yet. Create your first campaign.")

        if st.button("Create Campaign", type="primary"):
            go("🎯 Create Campaign")

        return

    for campaign in campaigns:
        selected = (
            str(campaign.get("id"))
            == str(st.session_state.get("selected_campaign_id"))
        )

        with st.container(border=True):
            left, mid, right = st.columns([3, 2, 1])

            left.markdown(f"### {campaign.get('campaign', 'Campaign')}")
            left.write(
                f"Objective: **{campaign.get('objective', '')}** • "
                f"Budget: **{campaign.get('budget', '')}**"
            )

            mid.write(f"Status: **{campaign.get('status', '')}**")
            mid.write(f"ROAS benchmark: **{campaign.get('roas', 0)}x**")

            if selected:
                right.success("Selected")
            elif right.button(
                "Open",
                key=f"open_{campaign.get('id')}",
                use_container_width=True,
            ):
                select_campaign(campaign["id"])
                st.session_state["current_page"] = "📊 Dashboard"
                st.rerun()

    selected = selected_campaign()

    if selected:
        st.success(
            f"Current campaign: **{selected.get('campaign', 'Campaign')}**"
        )

        if st.button("Open Campaign Dashboard", type="primary"):
            go("📊 Dashboard")


def render_dashboard():
    campaign = selected_campaign()

    st.title(f"Dashboard · {campaign['campaign']}")
    st.caption(
        "All metrics on this page are contextual to the selected campaign."
    )

    brief = campaign["brief"]
    roi = calculate_roi(brief)
    matches = match_creators(CREATORS, brief)

    cols = st.columns(4)

    metric_card(
        cols[0],
        "Objective",
        campaign["objective"],
        "Selected campaign",
    )
    metric_card(
        cols[1],
        "Budget",
        campaign["budget"],
        "Campaign brief",
    )
    metric_card(
        cols[2],
        "ROAS",
        f'{roi["roas"]}x',
        "Demo model",
    )
    metric_card(
        cols[3],
        "Top creator match",
        f'{matches.iloc[0]["match_score"]}/100',
        matches.iloc[0]["creator"],
    )

    st.markdown("### Campaign status")
    st.progress(min(1.0, 0.25 + (0.1 * len(matches))))
    st.write(f"Audience: **{brief['audience']}**")
    st.write(
        f"Duration: **{brief['duration']} days** • "
        f"Sustainability goal: **{'Yes' if brief['sustainability'] else 'No'}**"
    )

    st.markdown("### Quick actions")

    buttons = [
        ("AI Strategy", "🎯 Create Campaign"),
        ("Talent Matching", "🤝 AI Talent Matching"),
        ("ROI", "📈 Influencer ROI"),
        ("Impact Dashboard", "🧠 Campaign Intelligence"),
    ]

    cols = st.columns(4)

    for col, (label, target) in zip(cols, buttons):
        if col.button(
            label,
            key=f"dash_{label}",
            use_container_width=True,
        ):
            go(target)


def render_create_campaign():
    current = selected_campaign()

    st.title("AI Campaign Generator")

    if current:
        st.caption(f"Editing / extending **{current['campaign']}**")
    else:
        st.caption(
            "Create a campaign, then it will automatically become "
            "the selected project."
        )

    with st.form("campaign_form"):
        objective = st.selectbox(
            "Primary objective",
            [
                "Awareness",
                "Leads",
                "Sales",
                "App installs",
                "Community growth",
                "Engagement",
            ],
        )
        product = st.text_input(
            "Product / offer",
            value="Akovate AI Marketing Suite",
        )
        budget = st.number_input(
            "Budget (₹)",
            min_value=10000,
            value=500000,
            step=10000,
        )
        duration = st.slider(
            "Campaign duration (days)",
            7,
            60,
            21,
        )
        audience = st.text_area(
            "Audience",
            value=st.session_state.get(
                "audience",
                "Urban Gen Z and young millennials",
            ),
        )
        sustainability = st.checkbox(
            "Include sustainability goal",
            value=True,
        )

        generate = st.form_submit_button(
            "Generate Campaign Strategy",
            type="primary",
        )

    if generate:
        result = generate_strategy(
            objective,
            product,
            budget,
            duration,
            audience,
            sustainability,
        )

        brief = {
            "objective": objective,
            "product": product,
            "budget": budget,
            "duration": duration,
            "audience": audience,
            "sustainability": sustainability,
        }

        budget_display = (
            f"₹{budget / 100000:.1f}L"
            if budget >= 100000
            else f"₹{budget:,}"
        )

        if current:
            current["objective"] = objective
            current["budget"] = budget_display
            current["brief"] = brief
            current["status"] = "Active"
            current["campaign"] = product
        else:
            campaign = {
                "campaign": product,
                "objective": objective,
                "budget": budget_display,
                "status": "Planning",
                "roas": 4.5,
                "brief": brief,
            }

            if st.session_state.get("is_demo"):
                new_id = (
                    f"campaign-{len(st.session_state['campaign_library']) + 1}"
                )
                campaign["id"] = new_id
                st.session_state["campaign_library"].append(campaign)
                select_campaign(new_id)
                current = campaign
            else:
                saved = save_campaign(campaign)

                if saved:
                    current = saved
                    select_campaign(saved["id"])
                else:
                    st.error(
                        "The campaign could not be saved. "
                        "Please check your account connection and try again."
                    )
                    return

        st.session_state["campaign_strategy"] = result
        st.session_state["campaign_brief"] = brief
        st.session_state["selected_campaign_id"] = current["id"]

        st.success(f"Strategy generated for {current['campaign']}.")

    result = st.session_state.get("campaign_strategy")

    if result and selected_campaign():
        st.markdown("### AI strategy")
        st.write(result["positioning"])

        c1, c2, c3 = st.columns(3)

        metric_card(
            c1,
            "Recommended creators",
            result["creator_count"],
            "Initial talent pool",
        )
        metric_card(
            c2,
            "Content cadence",
            result["cadence"],
            "Suggested publishing rhythm",
        )
        metric_card(
            c3,
            "Target ROAS",
            result["target_roas"],
            "Planning benchmark",
        )

        st.markdown("**Content pillars**")

        for x in result["pillars"]:
            st.markdown(f"- {x}")

        st.markdown("**Measurement plan**")
        st.write(result["measurement"])


def render_matching():
    campaign = selected_campaign()

    st.title(f"AI Talent Matching · {campaign['campaign']}")
    brief = campaign["brief"]

    st.caption(
        "Explainable recommendation score: audience 30%, content 25%, "
        "location 10%, engagement 15%, sustainability 10%, budget 10%."
    )

    matches = match_creators(CREATORS, brief)

    display = matches[
        [
            "creator",
            "city",
            "category",
            "match_score",
            "engagement_rate",
            "audience_fit",
            "content_fit",
            "sustainability_fit",
            "budget_fit",
        ]
    ]

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
    )

    selected = st.selectbox(
        "Select a creator",
        matches["creator"].tolist(),
    )

    row = matches[matches["creator"] == selected].iloc[0]

    st.markdown("### Why Akovate recommends this creator")
    st.info(row["explanation"])

    a, b, c = st.columns(3)

    metric_card(
        a,
        "Match score",
        f'{row["match_score"]}/100',
        "Weighted fit",
    )
    metric_card(
        b,
        "Engagement",
        f'{row["engagement_rate"]}%',
        "Creator signal",
    )
    metric_card(
        c,
        "Sustainability",
        f'{row["sustainability_fit"]}/100',
        "Campaign fit",
    )

    st.markdown("**Strengths**")
    st.write(row["strengths"])

    st.markdown("**Trade-offs to consider**")
    st.write(row["tradeoffs"])


def render_workspace():
    campaign = selected_campaign()

    st.title(f"Campaign Workspace · {campaign['campaign']}")

    left, right = st.columns([2, 1])

    with left:
        st.markdown("### Campaign board")
        st.checkbox("Brief approved", value=True)
        st.checkbox("Creator shortlist confirmed", value=True)
        st.checkbox("Legal review completed", value=False)
        st.checkbox("Content draft approved", value=False)
        st.checkbox("Campaign published", value=False)

    with right:
        st.markdown("### AI Content Assistant")

        topic = st.text_input(
            "Content topic",
            campaign["brief"].get(
                "product",
                "Campaign content",
            ),
        )

        tone = st.selectbox(
            "Tone",
            [
                "Trustworthy",
                "Energetic",
                "Educational",
                "Playful",
            ],
        )

        if st.button("Draft caption", type="primary"):
            st.session_state["campaign_caption"] = (
                f"{topic} — {tone.lower()}, human-first and proof-led. "
                "Build better collaborations with Akovate."
            )

        if st.session_state.get("campaign_caption"):
            st.success(st.session_state["campaign_caption"])


def render_roi():
    campaign = selected_campaign()

    st.title(f"Influencer ROI Analytics · {campaign['campaign']}")

    metrics = calculate_roi(campaign["brief"])
    cols = st.columns(4)

    metric_card(
        cols[0],
        "Reach",
        f'{metrics["reach"]:,}',
        "Estimated",
    )
    metric_card(
        cols[1],
        "Conversions",
        f'{metrics["conversions"]:,}',
        "Attributed",
    )
    metric_card(
        cols[2],
        "ROAS",
        f'{metrics["roas"]}x',
        "Demo model",
    )
    metric_card(
        cols[3],
        "CPA",
        f'₹{metrics["cpa"]}',
        "Demo model",
    )

    st.bar_chart(
        {
            "Spend": [metrics["spend"]],
            "Revenue": [metrics["revenue"]],
        }
    )


def render_sentiment():
    campaign = selected_campaign()

    st.title(f"Brand Sentiment Analysis · {campaign['campaign']}")

    text = st.text_area(
        "Paste campaign comments / feedback",
        value=(
            "The creator explained the product clearly. Loved the honest "
            "demo and the practical tips. A few users asked for more "
            "pricing information."
        ),
    )

    if st.button("Analyze sentiment", type="primary"):
        sentiment = analyze_sentiment(text)

        c1, c2, c3 = st.columns(3)

        metric_card(
            c1,
            "Positive",
            f'{sentiment["positive"]}%',
            "Demo NLP",
        )
        metric_card(
            c2,
            "Neutral",
            f'{sentiment["neutral"]}%',
            "Demo NLP",
        )
        metric_card(
            c3,
            "Negative",
            f'{sentiment["negative"]}%',
            "Demo NLP",
        )

        st.write(sentiment["summary"])


def render_viral():
    campaign = selected_campaign()

    st.title(f"Viral Strategy Analyzer · {campaign['campaign']}")

    hook = st.text_area(
        "Content hook",
        "Can AI find the right creator for a campaign?",
    )

    format_name = st.selectbox(
        "Format",
        [
            "Reel",
            "Carousel",
            "YouTube Short",
            "Story",
        ],
    )

    if st.button("Analyze virality", type="primary"):
        viral = viral_score(hook, format_name)

        metric_card(
            st,
            "Virality readiness",
            f'{viral["score"]}/100',
            "Hook + format + shareability",
        )

        st.markdown("**Recommended actions**")

        for x in viral["actions"]:
            st.markdown(f"- {x}")


def render_green():
    campaign = selected_campaign()

    st.title(f"Green Campaign Score · {campaign['campaign']}")

    logistics = st.slider(
        "Low-carbon logistics",
        0,
        100,
        80,
    )
    digital = st.slider(
        "Digital-first execution",
        0,
        100,
        90,
    )
    creator = st.slider(
        "Creator sustainability fit",
        0,
        100,
        85,
    )
    accessibility = st.slider(
        "Accessibility & inclusion",
        0,
        100,
        82,
    )

    if st.button("Calculate Green Score", type="primary"):
        green = green_score(
            logistics,
            digital,
            creator,
            accessibility,
        )

        metric_card(
            st,
            "Green score",
            f'{green["score"]}/100',
            "Weighted demo index",
        )

        st.write(green["explanation"])


def render_intelligence():
    campaign = selected_campaign()

    st.title(
        f"Campaign Intelligence Dashboard · {campaign['campaign']}"
    )

    brief = campaign["brief"]
    roi = calculate_roi(brief)
    matches = match_creators(CREATORS, brief)
    sentiment = analyze_sentiment(
        "Loved the honest creator demo and clear explanation. "
        "Some users asked for more pricing information."
    )
    viral = viral_score(
        "Can AI find the right creator for a campaign?",
        "Reel",
    )
    green = green_score(80, 90, 85, 82)
    impact = campaign_impact(
        roi,
        sentiment,
        viral,
        green,
    )

    metric_card(
        st,
        "Impact score",
        f'{impact["impact_score"]}/100',
        "Combined decision-support index",
    )

    st.write(impact["summary"])

    a, b, c, d = st.columns(4)

    metric_card(
        a,
        "ROAS",
        f'{roi["roas"]}x',
        "Performance",
    )
    metric_card(
        b,
        "Positive sentiment",
        f'{sentiment["positive"]}%',
        "Brand health",
    )
    metric_card(
        c,
        "Viral readiness",
        f'{viral["score"]}/100',
        "Content",
    )
    metric_card(
        d,
        "Green score",
        f'{green["score"]}/100',
        "Responsible execution",
    )

    st.markdown("### Recommended next actions")

    for action in impact["actions"]:
        st.markdown(f"- {action}")


def render_network():
    st.title("Platform Network")
    st.write(
        "Akovate connects multiple participant types around a common "
        "campaign workflow."
    )

    cols = st.columns(6)

    for col, label in zip(
        cols,
        [
            "Brands",
            "Creators",
            "Freelancers",
            "Agencies",
            "Legal",
            "Sustainability",
        ],
    ):
        col.metric(label, "Connected", "Prototype")


def render_settings():
    st.title("Settings & Profile")
    st.caption("Manage your workspace identity and preferences.")

    with st.form("settings"):
        email = st.text_input(
            "Account email",
            value=st.session_state.get("user_email", ""),
            disabled=True,
        )

        current_role = st.session_state.get("role", "Brand")
        st.text_input(
            "Workspace role",
            value=current_role,
            disabled=True,
        )

        name = st.text_input(
            "Display name / organisation",
            value=st.session_state.get(
                "brand_name",
                "",
            ),
        )

        market = st.text_input(
            "Primary market",
            value=st.session_state.get(
                "city",
                "",
            ),
        )

        save = st.form_submit_button(
            "Save Settings",
            type="primary",
        )

    if save:
        st.session_state["brand_name"] = name
        st.session_state["city"] = market

        if st.session_state.get("is_demo"):
            st.success("Settings saved.")
        else:
            if save_profile():
                st.session_state["profile_complete"] = True
                st.success("Settings saved to your Akovate account.")
            else:
                st.error(
                    "Settings could not be saved. Please try again."
                )


render_sidebar()

if not st.session_state.get("authenticated"):
    render_login()

else:
    page = st.session_state.get(
        "current_page",
        "🏠 Home",
    )

    if campaign_required(page):
        st.title("Campaign workspace locked")
        st.info(
            "Select a specific campaign from **Campaign Library** "
            "to unlock this workspace."
        )

        if st.button(
            "Open Campaign Library",
            type="primary",
        ):
            go("📚 Campaign Library")

    elif page == "🏠 Home":
        render_home()

    elif page == "📚 Campaign Library":
        render_library()

    elif page == "📊 Dashboard":
        render_dashboard()

    elif page == "🎯 Create Campaign":
        render_create_campaign()

    elif page == "🤝 AI Talent Matching":
        render_matching()

    elif page == "🧩 Campaign Workspace":
        render_workspace()

    elif page == "📈 Influencer ROI":
        render_roi()

    elif page == "💬 Brand Sentiment":
        render_sentiment()

    elif page == "🔥 Viral Strategy":
        render_viral()

    elif page == "🌱 Green Campaign Score":
        render_green()

    elif page == "🧠 Campaign Intelligence":
        render_intelligence()

    elif page == "🌐 Platform Network":
        render_network()

    elif page == "⚙️ Settings":
        render_settings()

    elif page == "🔐 Login":
        render_login()
