from utils.state import (
    DEMO_EMAIL,
    DEMO_PASSWORD,
    ROLES,
    get_supabase,
    init_state,
    load_user_data,
    logout,
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

PUBLIC_PAGES = {"🏠 Home", "🔐 Login", "🧭 Onboarding", "📚 Campaign Library", "⚙️ Settings", "🌐 Platform Network"}
CAMPAIGN_PAGES = {
    "📊 Dashboard",
    "🎯 Create Campaign",
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
    return page in CAMPAIGN_PAGES and selected_campaign() is None


def render_login():
    st.title("Welcome to Akovate")
    st.subheader("Sign in to your marketing collaboration workspace")
    st.caption(
        "Create your own workspace or use the built-in demo account."
    )

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

                # Keep the existing Akovate demo account.
                if (
                    email_clean == DEMO_EMAIL
                    and password == DEMO_PASSWORD
                ):
                    st.session_state["authenticated"] = True
                    st.session_state["user_email"] = DEMO_EMAIL
                    st.session_state["user_id"] = "demo-user"
                    st.session_state["is_demo"] = True
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
                            response = (
                                supabase.auth.sign_in_with_password(
                                    {
                                        "email": email_clean,
                                        "password": password,
                                    }
                                )
                            )

                            user = response.user

                            if user:
                                st.session_state["authenticated"] = True
                                st.session_state["user_email"] = (
                                    user.email or email_clean
                                )
                                st.session_state["user_id"] = user.id
                                st.session_state["is_demo"] = False
                                st.session_state["login_error"] = ""

                                load_user_data(
                                    user.id,
                                    user.email or email_clean,
                                )

                                if st.session_state.get("profile_complete"):
                                    st.session_state["current_page"] = "🏠 Home"
                                else:
                                    st.session_state["current_page"] = "🧭 Onboarding"

                                st.success("Login successful.")
                                st.rerun()
                            else:
                                st.error(
                                    "Login could not be completed."
                                )

                        except Exception as exc:
                            message = str(exc)

                            if "Email not confirmed" in message:
                                st.error(
                                    "Please verify your email address first, "
                                    "then log in."
                                )
                            else:
                                st.error(
                                    "Invalid email or password."
                                )

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

            role = st.selectbox(
                "Workspace role",
                ROLES,
                key="signup_role",
            )

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
                st.error(
                    "Password must contain at least 6 characters."
                )

            elif password != confirm_password:
                st.error("Passwords do not match.")

            elif email_clean == DEMO_EMAIL:
                st.error(
                    "That email is reserved for the Akovate demo account."
                )

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

                            # If Supabase immediately returns a session,
                            # log the user in. Otherwise ask them to verify
                            # their email first.
                            if response.session:
                                st.session_state["authenticated"] = True
                                st.session_state["user_email"] = (
                                    user.email or email_clean
                                )
                                st.session_state["user_id"] = user.id
                                st.session_state["is_demo"] = False
                                st.session_state["role"] = role
                                st.session_state["brand_name"] = (
                                    name.strip()
                                )

                                load_user_data(
                                    user.id,
                                    user.email or email_clean,
                                )

                                st.session_state["current_page"] = (
                                    "🧭 Onboarding"
                                )
                                st.success(
                                    "Account created successfully."
                                )
                                st.rerun()
                            else:
                                st.success(
                                    "Account created. "
                                    "Please check your email and verify "
                                    "your account before logging in."
                                )

                    except Exception as exc:
                        message = str(exc)

                        if "already registered" in message.lower():
                            st.error(
                                "An account with this email already exists."
                            )
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
            st.success(f"Signed in as {st.session_state.get('user_email')}")
            role = st.selectbox("Workspace role", ROLES, index=ROLES.index(st.session_state.get("role", "Brand")))
            st.session_state["role"] = role

            campaign = selected_campaign()
            if campaign:
                st.markdown(f"**Selected campaign:** {campaign['campaign']}")
            else:
                st.warning("Select a campaign to unlock campaign workspaces.")

            nav = ["🏠 Home", "🧭 Onboarding", "📚 Campaign Library", "⚙️ Settings", "🌐 Platform Network"]
            if campaign:
                nav += list(CAMPAIGN_PAGES)
            else:
                nav += list(CAMPAIGN_PAGES)

            current = st.session_state.get("current_page", "🏠 Home")
            page = st.radio("Navigate", nav, index=nav.index(current) if current in nav else 0)
            if page != current:
                st.session_state["current_page"] = page
                st.rerun()

            st.divider()
            if st.button("Logout", use_container_width=True):
                logout()
                st.rerun()
        else:
            st.info("Please log in to use the workspace.")
            if st.button("Go to Login", use_container_width=True, type="primary"):
                go("🔐 Login")

        st.divider()
        st.caption("Prototype mode • No external API keys required")


def render_home():
    name = st.session_state.get("brand_name", "Akovate Demo Brand")
    role = st.session_state.get("role", "Brand")
    st.title(f"Welcome back, {name}")
    st.subheader("Your marketing workspace — from brief to measurable intelligence.")
    st.write(
        f"You are currently using Akovate as a **{role}**. Start with your campaign library, "
        "select a project, and unlock the complete campaign intelligence workflow."
    )

    c1, c2, c3, c4 = st.columns(4)
    metric_card(c1, "Campaigns", len(st.session_state["campaign_library"]), "Your project library")
    metric_card(c2, "Partners", PLATFORM_STATS["partners"], "Demo network")
    metric_card(c3, "Avg. match score", f'{PLATFORM_STATS["avg_match_score"]}%', "Explainable matching")
    metric_card(c4, "Green index", f'{PLATFORM_STATS["green"]}%', "Responsible marketing")

    st.markdown("### Start your journey")
    journey = [
        ("🔐", "Brand Login", "🔐 Login"),
        ("🧭", "Onboarding", "🧭 Onboarding"),
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
            if st.button(f"{icon} {label}", key=f"journey_{i}", use_container_width=True):
                if target in CAMPAIGN_PAGES and selected_campaign() is None:
                    st.warning("Select a campaign in Campaign Library first.")
                else:
                    go(target)

    st.markdown("### How Akovate works")
    a, b, c = st.columns(3)
    a.markdown("**AI layer**\n\nStrategy, explainable matching, content and analytics.")
    b.markdown("**Platform layer**\n\nBrands collaborate with creators, freelancers, agencies and specialist partners.")
    c.markdown("**Sustainability layer**\n\nResponsible campaign signals are measured alongside performance.")


def render_onboarding():
    role = st.session_state.get("role", "Brand")
    st.title(f"{role} Onboarding")
    st.caption("Your fields adapt automatically to the selected workspace role.")

    with st.form("role_onboarding"):
        if role == "Brand":
            name = st.text_input("Brand name", value=st.session_state.get("brand_name", "Akovate Demo Brand"))
            industry = st.selectbox("Industry", ["Beauty & Wellness", "FMCG", "Fashion", "Technology", "Food & Beverage", "Travel"])
            city = st.text_input("Primary market", value=st.session_state.get("city", "Hyderabad"))
            audience = st.text_area("Target audience", value=st.session_state.get("audience", "Urban Gen Z and young millennials"))
            values = st.multiselect("Brand priorities", ["Growth", "Trust", "Creator authenticity", "Sustainability", "Performance marketing", "Community"], default=st.session_state.get("values", ["Growth", "Creator authenticity", "Sustainability"]))
        elif role == "Creator / Influencer":
            name = st.text_input("Creator name")
            niche = st.selectbox("Primary niche", ["Technology", "Lifestyle", "Business", "Beauty & Wellness", "Fashion", "Food"])
            city = st.text_input("Base city", value="Hyderabad")
            audience = st.text_area("Audience profile", value="Gen Z and young millennials")
            values = st.multiselect("Creator strengths", ["Storytelling", "Education", "Comedy", "Reviews", "Sustainability", "Community"], default=["Storytelling"])
            industry = niche
        elif role == "Freelancer":
            name = st.text_input("Freelancer name")
            industry = st.selectbox("Specialisation", ["Video Editing", "Copywriting", "Photography", "Design", "Performance Marketing", "Content Strategy"])
            city = st.text_input("Base city", value="Hyderabad")
            audience = st.text_area("Client / audience focus", value="D2C and digital-first brands")
            values = st.multiselect("Capabilities", ["Fast turnaround", "Creative quality", "Analytics", "AI-enabled workflow", "Brand consistency"], default=["Creative quality"])
        elif role == "Agency":
            name = st.text_input("Agency name")
            industry = st.selectbox("Agency focus", ["Creator Marketing", "Digital Marketing", "Brand Strategy", "Performance Marketing", "Integrated Marketing"])
            city = st.text_input("Primary office", value="Hyderabad")
            audience = st.text_area("Client profile", value="Growth-stage brands")
            values = st.multiselect("Agency strengths", ["Strategy", "Creators", "Media", "Analytics", "Production", "Sustainability"], default=["Strategy", "Analytics"])
        elif role == "Legal Professional":
            name = st.text_input("Professional / firm name")
            industry = st.selectbox("Legal focus", ["Advertising Compliance", "IP & Copyright", "Contracts", "Influencer Agreements", "Data & Privacy"])
            city = st.text_input("Base city", value="Hyderabad")
            audience = st.text_area("Client focus", value="Brands and creators")
            values = st.multiselect("Services", ["Contract review", "IP review", "Disclosure compliance", "Privacy", "Risk assessment"], default=["Contract review"])
        elif role == "Sustainability Partner":
            name = st.text_input("Partner / organisation name")
            industry = st.selectbox("Sustainability focus", ["Low-carbon logistics", "Circularity", "Packaging", "ESG measurement", "Responsible production"])
            city = st.text_input("Base city", value="Hyderabad")
            audience = st.text_area("Partner ecosystem", value="Brands, agencies and campaign teams")
            values = st.multiselect("Capabilities", ["Measurement", "Audits", "Green production", "Training", "Reporting"], default=["Measurement"])
        else:
            name = st.text_input("Admin name")
            industry = st.selectbox("Operating area", ["Platform Operations", "Partnerships", "Analytics", "Compliance"])
            city = st.text_input("Base city", value="Hyderabad")
            audience = st.text_area("Operational scope", value="Akovate platform ecosystem")
            values = st.multiselect("Admin permissions", ["Campaigns", "Users", "Analytics", "Partners", "Settings"], default=["Campaigns", "Analytics"])

        submitted = st.form_submit_button("Save Profile", type="primary")

        if submitted:
        st.session_state.update(
            brand_name=name or st.session_state.get("brand_name", ""),
            industry=industry,
            city=city,
            audience=audience,
            values=values,
            profile={
                "id": st.session_state.get("user_id", ""),
                "email": st.session_state.get("user_email", ""),
                "name": name,
                "role": role,
                "industry": industry,
                "city": city,
                "audience": audience,
                "values": values,
            },
        )

        # Demo account stays local and keeps its demo experience.
        if st.session_state.get("is_demo"):
            st.session_state["profile_complete"] = True
            st.success(f"{role} profile saved successfully.")
        else:
            saved = save_profile()

            if saved:
                st.session_state["profile_complete"] = True
                st.success(
                    f"{role} profile saved successfully to your Akovate account."
                )
            else:
                st.error(
                    "Your profile could not be saved. "
                    "Please try again."
                )
def render_library():
    st.title("Campaign Library")
    st.caption("Select one campaign to unlock its contextual workspaces and analytics.")

    campaigns = st.session_state["campaign_library"]
    if not campaigns:
        st.info("No campaigns yet. Create your first campaign.")
        if st.button("Create Campaign", type="primary"):
            go("🎯 Create Campaign")
        return

    for campaign in campaigns:
        selected = campaign["id"] == st.session_state.get("selected_campaign_id")
        with st.container(border=True):
            left, mid, right = st.columns([3, 2, 1])
            left.markdown(f"### {campaign['campaign']}")
            left.write(f"Objective: **{campaign['objective']}** • Budget: **{campaign['budget']}**")
            mid.write(f"Status: **{campaign['status']}**")
            mid.write(f"ROAS benchmark: **{campaign['roas']}x**")
            if selected:
                right.success("Selected")
            elif right.button("Open", key=f"open_{campaign['id']}", use_container_width=True):
                select_campaign(campaign["id"])
                st.session_state["current_page"] = "📊 Dashboard"
                st.rerun()

    selected = selected_campaign()
    if selected:
        st.success(f"Current campaign: **{selected['campaign']}**")
        if st.button("Open Campaign Dashboard", type="primary"):
            go("📊 Dashboard")


def render_dashboard():
    campaign = selected_campaign()
    st.title(f"Dashboard · {campaign['campaign']}")
    st.caption("All metrics on this page are contextual to the selected campaign.")
    brief = campaign["brief"]
    roi = calculate_roi(brief)
    matches = match_creators(CREATORS, brief)
    cols = st.columns(4)
    metric_card(cols[0], "Objective", campaign["objective"], "Selected campaign")
    metric_card(cols[1], "Budget", campaign["budget"], "Campaign brief")
    metric_card(cols[2], "ROAS", f'{roi["roas"]}x', "Demo model")
    metric_card(cols[3], "Top creator match", f'{matches.iloc[0]["match_score"]}/100', matches.iloc[0]["creator"])

    st.markdown("### Campaign status")
    st.progress(min(1.0, 0.25 + (0.1 * len(matches))))
    st.write(f"Audience: **{brief['audience']}**")
    st.write(f"Duration: **{brief['duration']} days** • Sustainability goal: **{'Yes' if brief['sustainability'] else 'No'}**")

    st.markdown("### Quick actions")
    buttons = [("AI Strategy", "🎯 Create Campaign"), ("Talent Matching", "🤝 AI Talent Matching"), ("ROI", "📈 Influencer ROI"), ("Impact Dashboard", "🧠 Campaign Intelligence")]
    cols = st.columns(4)
    for col, (label, target) in zip(cols, buttons):
        if col.button(label, key=f"dash_{label}", use_container_width=True):
            go(target)


def render_create_campaign():
    current = selected_campaign()
    st.title("AI Campaign Generator")
    if current:
        st.caption(f"Editing / extending **{current['campaign']}**")
    else:
        st.caption("Create a campaign, then it will automatically become the selected project.")

    with st.form("campaign_form"):
        objective = st.selectbox("Primary objective", ["Awareness", "Leads", "Sales", "App installs", "Community growth", "Engagement"])
        product = st.text_input("Product / offer", value="Akovate AI Marketing Suite")
        budget = st.number_input("Budget (₹)", min_value=10000, value=500000, step=10000)
        duration = st.slider("Campaign duration (days)", 7, 60, 21)
        audience = st.text_area("Audience", value=st.session_state.get("audience", "Urban Gen Z and young millennials"))
        sustainability = st.checkbox("Include sustainability goal", value=True)
        generate = st.form_submit_button("Generate Campaign Strategy", type="primary")

    if generate:
        result = generate_strategy(objective, product, budget, duration, audience, sustainability)
        brief = {"objective": objective, "product": product, "budget": budget, "duration": duration, "audience": audience, "sustainability": sustainability}
        if current:
            current["objective"] = objective
            current["budget"] = f"₹{budget/100000:.1f}L" if budget >= 100000 else f"₹{budget:,}"
            current["brief"] = brief
            current["status"] = "Active"
            current["campaign"] = product
        else:
            new_id = f"campaign-{len(st.session_state['campaign_library']) + 1}"
            campaign = {"id": new_id, "campaign": product, "objective": objective, "budget": f"₹{budget/100000:.1f}L" if budget >= 100000 else f"₹{budget:,}", "status": "Planning", "roas": 4.5, "brief": brief}
            st.session_state["campaign_library"].append(campaign)
            select_campaign(new_id)
            current = campaign
        st.session_state["campaign_strategy"] = result
        st.session_state["campaign_brief"] = brief
        st.session_state["selected_campaign_id"] = current["id"]
        st.success(f"Strategy generated for {current['campaign']}.")

    result = st.session_state.get("campaign_strategy")
    if result and selected_campaign():
        st.markdown("### AI strategy")
        st.write(result["positioning"])
        c1, c2, c3 = st.columns(3)
        metric_card(c1, "Recommended creators", result["creator_count"], "Initial talent pool")
        metric_card(c2, "Content cadence", result["cadence"], "Suggested publishing rhythm")
        metric_card(c3, "Target ROAS", result["target_roas"], "Planning benchmark")
        st.markdown("**Content pillars**")
        for x in result["pillars"]:
            st.markdown(f"- {x}")
        st.markdown("**Measurement plan**")
        st.write(result["measurement"])


def render_matching():
    campaign = selected_campaign()
    st.title(f"AI Talent Matching · {campaign['campaign']}")
    brief = campaign["brief"]
    st.caption("Explainable recommendation score: audience 30%, content 25%, location 10%, engagement 15%, sustainability 10%, budget 10%.")
    matches = match_creators(CREATORS, brief)
    display = matches[["creator", "city", "category", "match_score", "engagement_rate", "audience_fit", "content_fit", "sustainability_fit", "budget_fit"]]
    st.dataframe(display, use_container_width=True, hide_index=True)

    selected = st.selectbox("Select a creator", matches["creator"].tolist())
    row = matches[matches["creator"] == selected].iloc[0]
    st.markdown("### Why Akovate recommends this creator")
    st.info(row["explanation"])
    a, b, c = st.columns(3)
    metric_card(a, "Match score", f'{row["match_score"]}/100', "Weighted fit")
    metric_card(b, "Engagement", f'{row["engagement_rate"]}%', "Creator signal")
    metric_card(c, "Sustainability", f'{row["sustainability_fit"]}/100', "Campaign fit")
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
        topic = st.text_input("Content topic", campaign["brief"].get("product", "Campaign content"))
        tone = st.selectbox("Tone", ["Trustworthy", "Energetic", "Educational", "Playful"])
        if st.button("Draft caption", type="primary"):
            st.session_state["campaign_caption"] = f"{topic} — {tone.lower()}, human-first and proof-led. Build better collaborations with Akovate."
        if st.session_state.get("campaign_caption"):
            st.success(st.session_state["campaign_caption"])


def render_roi():
    campaign = selected_campaign()
    st.title(f"Influencer ROI Analytics · {campaign['campaign']}")
    metrics = calculate_roi(campaign["brief"])
    cols = st.columns(4)
    metric_card(cols[0], "Reach", f'{metrics["reach"]:,}', "Estimated")
    metric_card(cols[1], "Conversions", f'{metrics["conversions"]:,}', "Attributed")
    metric_card(cols[2], "ROAS", f'{metrics["roas"]}x', "Demo model")
    metric_card(cols[3], "CPA", f'₹{metrics["cpa"]}', "Demo model")
    st.bar_chart({"Spend": [metrics["spend"]], "Revenue": [metrics["revenue"]]})


def render_sentiment():
    campaign = selected_campaign()
    st.title(f"Brand Sentiment Analysis · {campaign['campaign']}")
    text = st.text_area("Paste campaign comments / feedback", value="The creator explained the product clearly. Loved the honest demo and the practical tips. A few users asked for more pricing information.")
    if st.button("Analyze sentiment", type="primary"):
        s = analyze_sentiment(text)
        c1, c2, c3 = st.columns(3)
        metric_card(c1, "Positive", f'{s["positive"]}%', "Demo NLP")
        metric_card(c2, "Neutral", f'{s["neutral"]}%', "Demo NLP")
        metric_card(c3, "Negative", f'{s["negative"]}%', "Demo NLP")
        st.write(s["summary"])


def render_viral():
    campaign = selected_campaign()
    st.title(f"Viral Strategy Analyzer · {campaign['campaign']}")
    hook = st.text_area("Content hook", "Can AI find the right creator for a campaign?")
    format_name = st.selectbox("Format", ["Reel", "Carousel", "YouTube Short", "Story"])
    if st.button("Analyze virality", type="primary"):
        v = viral_score(hook, format_name)
        metric_card(st, "Virality readiness", f'{v["score"]}/100', "Hook + format + shareability")
        st.markdown("**Recommended actions**")
        for x in v["actions"]:
            st.markdown(f"- {x}")


def render_green():
    campaign = selected_campaign()
    st.title(f"Green Campaign Score · {campaign['campaign']}")
    logistics = st.slider("Low-carbon logistics", 0, 100, 80)
    digital = st.slider("Digital-first execution", 0, 100, 90)
    creator = st.slider("Creator sustainability fit", 0, 100, 85)
    accessibility = st.slider("Accessibility & inclusion", 0, 100, 82)
    if st.button("Calculate Green Score", type="primary"):
        g = green_score(logistics, digital, creator, accessibility)
        metric_card(st, "Green score", f'{g["score"]}/100', "Weighted demo index")
        st.write(g["explanation"])


def render_intelligence():
    campaign = selected_campaign()
    st.title(f"Campaign Intelligence Dashboard · {campaign['campaign']}")
    brief = campaign["brief"]
    roi = calculate_roi(brief)
    matches = match_creators(CREATORS, brief)
    sentiment = analyze_sentiment("Loved the honest creator demo and clear explanation. Some users asked for more pricing information.")
    viral = viral_score("Can AI find the right creator for a campaign?", "Reel")
    green = green_score(80, 90, 85, 82)
    impact = campaign_impact(roi, sentiment, viral, green)

    metric_card(st, "Impact score", f'{impact["impact_score"]}/100', "Combined decision-support index")
    st.write(impact["summary"])
    a, b, c, d = st.columns(4)
    metric_card(a, "ROAS", f'{roi["roas"]}x', "Performance")
    metric_card(b, "Positive sentiment", f'{sentiment["positive"]}%', "Brand health")
    metric_card(c, "Viral readiness", f'{viral["score"]}/100', "Content")
    metric_card(d, "Green score", f'{green["score"]}/100', "Responsible execution")
    st.markdown("### Recommended next actions")
    for action in impact["actions"]:
        st.markdown(f"- {action}")


def render_network():
    st.title("Platform Network")
    st.write("Akovate connects multiple participant types around a common campaign workflow.")
    cols = st.columns(6)
    for col, label in zip(cols, ["Brands", "Creators", "Freelancers", "Agencies", "Legal", "Sustainability"]):
        col.metric(label, "Connected", "Prototype")


def render_settings():
    st.title("Settings & Profile")
    st.caption("Manage your workspace identity and preferences.")
    with st.form("settings"):
        email = st.text_input("Account email", value=st.session_state.get("user_email", ""), disabled=True)
        role = st.selectbox("Workspace role", ROLES, index=ROLES.index(st.session_state.get("role", "Brand")))
        name = st.text_input("Display name / organisation", value=st.session_state.get("brand_name", "Akovate Demo Brand"))
        market = st.text_input("Primary market", value=st.session_state.get("city", "Hyderabad"))
        save = st.form_submit_button("Save Settings", type="primary")
    if save:
        st.session_state["role"] = role
        st.session_state["brand_name"] = name
        st.session_state["city"] = market
        st.success("Settings saved.")


render_sidebar()

if not st.session_state.get("authenticated"):
    render_login()
else:
    page = st.session_state.get("current_page", "🏠 Home")
    if campaign_required(page):
        st.title("Campaign workspace locked")
        st.info("Select a specific campaign from **Campaign Library** to unlock this workspace.")
        if st.button("Open Campaign Library", type="primary"):
            go("📚 Campaign Library")
    elif page == "🏠 Home":
        render_home()
    elif page == "🧭 Onboarding":
        render_onboarding()
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
