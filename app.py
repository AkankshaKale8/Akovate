import streamlit as st
from utils.ui import inject_css, logo, metric_card
from utils.state import init_state
from data.sample_data import CAMPAIGNS, CREATORS, PLATFORM_STATS
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

# ---------- Sidebar ----------
with st.sidebar:
    logo()
    st.markdown("### AKOVATE")
    st.caption("AI-POWERED MARKETING COLLABORATION PLATFORM")
    role = st.selectbox(
        "Workspace role",
        ["Brand", "Creator / Influencer", "Freelancer", "Agency", "Legal Professional", "Sustainability Partner", "Admin"],
        index=0,
    )
    st.session_state["role"] = role
    page = st.radio(
        "Navigate",
        [
            "🏠 Home",
            "🧭 Brand Onboarding",
            "📊 Dashboard",
            "🎯 Create Campaign",
            "🤝 AI Talent Matching",
            "🧩 Campaign Workspace",
            "📈 Influencer ROI",
            "💬 Brand Sentiment",
            "🔥 Viral Strategy",
            "🌱 Green Campaign Score",
            "🧠 Campaign Intelligence",
            "🌐 Platform Network",
        ],
    )
    st.divider()
    st.caption("Prototype mode • No external API keys required")
    st.caption("Deploy from GitHub to Streamlit Community Cloud.")

# ---------- Home ----------
if page == "🏠 Home":
    st.title("Akovate")
    st.subheader("From campaign brief to measurable marketing intelligence.")
    st.write(
        "Akovate connects brands with creators, freelancers, agencies, legal professionals "
        "and sustainability partners, then adds explainable AI to improve campaign planning, "
        "matching, collaboration and measurement."
    )

    c1, c2, c3, c4 = st.columns(4)
    metric_card(c1, "Active campaigns", PLATFORM_STATS["active_campaigns"], "Live demo network")
    metric_card(c2, "Partners", PLATFORM_STATS["partners"], "All participant types")
    metric_card(c3, "Avg. match score", f'{PLATFORM_STATS["avg_match_score"]}%', "Explainable matching")
    metric_card(c4, "Green campaigns", f'{PLATFORM_STATS["green"]}%', "Sustainability index")

    st.markdown("### End-to-end campaign journey")
    steps = [
        "Brand Login", "Onboarding", "Campaign Brief", "AI Strategy",
        "Talent Matching", "Collaboration", "ROI", "Sentiment",
        "Viral Strategy", "Green Score", "Impact Dashboard"
    ]
    cols = st.columns(4)
    for i, step in enumerate(steps):
        cols[i % 4].info(f"**{i+1}. {step}**")

    st.markdown("### Why Akovate?")
    a, b, c = st.columns(3)
    a.markdown("**AI layer**\n\nStrategy, matching, content, analytics and explainability.")
    b.markdown("**Platform layer**\n\nMulti-sided collaboration across brands and specialist partners.")
    c.markdown("**Sustainability layer**\n\nGreen campaign scoring and measurable responsible-marketing signals.")

# ---------- Onboarding ----------
elif page == "🧭 Brand Onboarding":
    st.title("Brand Onboarding")
    st.caption("Create a lightweight campaign-ready brand profile.")

    with st.form("onboarding"):
        name = st.text_input("Brand name", value=st.session_state.get("brand_name", "Akovate Demo Brand"))
        industry = st.selectbox("Industry", ["Beauty & Wellness", "FMCG", "Fashion", "Technology", "Food & Beverage", "Travel"])
        city = st.text_input("Primary market", value="Hyderabad")
        audience = st.text_area("Target audience", value="Urban Gen Z and young millennials seeking practical, credible solutions.")
        values = st.multiselect("Brand priorities", ["Growth", "Trust", "Creator authenticity", "Sustainability", "Performance marketing", "Community"], default=["Growth", "Creator authenticity", "Sustainability"])
        submitted = st.form_submit_button("Save Brand Profile", type="primary")

    if submitted:
        st.session_state.update(
            brand_name=name,
            industry=industry,
            city=city,
            audience=audience,
            values=values,
        )
        st.success("Brand profile saved. Your next step is campaign creation.")

# ---------- Dashboard ----------
elif page == "📊 Dashboard":
    st.title("Brand Dashboard")
    st.caption(f"Welcome back, {st.session_state.get('brand_name', 'Akovate Demo Brand')}.")
    cols = st.columns(4)
    metric_card(cols[0], "Campaigns", len(CAMPAIGNS), "Demo portfolio")
    metric_card(cols[1], "Creators", len(CREATORS), "Available talent")
    metric_card(cols[2], "Avg. ROAS", "4.8x", "Portfolio benchmark")
    metric_card(cols[3], "Sentiment", "82%", "Positive demo signal")

    st.markdown("### Active campaigns")
    st.dataframe(CAMPAIGNS, use_container_width=True, hide_index=True)

# ---------- Create Campaign ----------
elif page == "🎯 Create Campaign":
    st.title("AI Campaign Generator")
    st.caption("Turn a brief into a structured campaign plan without an external AI key.")

    with st.form("campaign"):
        objective = st.selectbox("Primary objective", ["Awareness", "Leads", "Sales", "App installs", "Community growth"])
        product = st.text_input("Product / offer", value="Akovate AI Marketing Suite")
        budget = st.number_input("Budget (₹)", min_value=10000, value=500000, step=10000)
        duration = st.slider("Campaign duration (days)", 7, 60, 21)
        audience = st.text_area("Audience", value=st.session_state.get("audience", "Urban Gen Z and young millennials"))
        sustainability = st.checkbox("Include sustainability goal", value=True)
        generate = st.form_submit_button("Generate Campaign Strategy", type="primary")

    if generate:
        result = generate_strategy(objective, product, budget, duration, audience, sustainability)
        st.session_state["campaign_strategy"] = result
        st.session_state["campaign_brief"] = {
            "objective": objective, "product": product, "budget": budget,
            "duration": duration, "audience": audience, "sustainability": sustainability
        }
        st.success("Strategy generated.")

    result = st.session_state.get("campaign_strategy")
    if result:
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

# ---------- Matching ----------
elif page == "🤝 AI Talent Matching":
    st.title("AI Talent Matching")
    brief = st.session_state.get("campaign_brief", {
        "objective": "Awareness", "product": "Akovate AI Marketing Suite",
        "budget": 500000, "duration": 21, "audience": "Urban Gen Z", "sustainability": True
    })
    st.caption("Explainable scoring: audience, content, location, engagement, sustainability and budget fit.")

    matches = match_creators(CREATORS, brief)
    st.dataframe(matches, use_container_width=True, hide_index=True)

    selected = st.selectbox("Select a creator", matches["creator"].tolist())
    row = matches[matches["creator"] == selected].iloc[0]
    st.markdown("### Why this match?")
    st.write(row["explanation"])
    a, b, c = st.columns(3)
    metric_card(a, "Match score", f'{row["match_score"]}/100', "Explainable")
    metric_card(b, "Engagement", f'{row["engagement_rate"]}%', "Creator signal")
    metric_card(c, "Sustainability", f'{row["sustainability_fit"]}/100', "Campaign fit")

# ---------- Workspace ----------
elif page == "🧩 Campaign Workspace":
    st.title("Campaign Workspace")
    st.caption("A single collaboration surface for the brand and selected partners.")

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
        topic = st.text_input("Content topic", "AI-powered campaign matching")
        tone = st.selectbox("Tone", ["Trustworthy", "Energetic", "Educational", "Playful"])
        if st.button("Draft caption", type="primary"):
            st.session_state["caption"] = (
                f"{topic} — {tone.lower()}, human-first and proof-led. "
                "Build better collaborations with Akovate."
            )
        if st.session_state.get("caption"):
            st.success(st.session_state["caption"])

# ---------- ROI ----------
elif page == "📈 Influencer ROI":
    st.title("Influencer ROI Analytics")
    metrics = calculate_roi()
    cols = st.columns(4)
    metric_card(cols[0], "Reach", f'{metrics["reach"]:,}', "Estimated")
    metric_card(cols[1], "Conversions", f'{metrics["conversions"]:,}', "Attributed")
    metric_card(cols[2], "ROAS", f'{metrics["roas"]}x', "Demo model")
    metric_card(cols[3], "CPA", f'₹{metrics["cpa"]}', "Demo model")
    st.bar_chart({"Spend": [metrics["spend"]], "Revenue": [metrics["revenue"]]})

# ---------- Sentiment ----------
elif page == "💬 Brand Sentiment":
    st.title("Brand Sentiment Analysis")
    text = st.text_area(
        "Paste campaign comments / feedback",
        value="The creator explained the product clearly. Loved the honest demo and the practical tips. "
              "A few users asked for more pricing information."
    )
    if st.button("Analyze sentiment", type="primary"):
        s = analyze_sentiment(text)
        c1, c2, c3 = st.columns(3)
        metric_card(c1, "Positive", f'{s["positive"]}%', "Demo NLP")
        metric_card(c2, "Neutral", f'{s["neutral"]}%', "Demo NLP")
        metric_card(c3, "Negative", f'{s["negative"]}%', "Demo NLP")
        st.write(s["summary"])

# ---------- Viral ----------
elif page == "🔥 Viral Strategy":
    st.title("Viral Strategy Analyzer")
    hook = st.text_area("Content hook", "Can AI find the right creator for a campaign?")
    format_name = st.selectbox("Format", ["Reel", "Carousel", "YouTube Short", "Story"])
    if st.button("Analyze virality", type="primary"):
        v = viral_score(hook, format_name)
        metric_card(st, "Virality readiness", f'{v["score"]}/100', "Hook + format + shareability")
        st.markdown("**Recommended actions**")
        for x in v["actions"]:
            st.markdown(f"- {x}")

# ---------- Green ----------
elif page == "🌱 Green Campaign Score":
    st.title("Green Campaign Score")
    st.caption("A transparent demo score for responsible campaign design.")
    logistics = st.slider("Low-carbon logistics", 0, 100, 80)
    digital = st.slider("Digital-first execution", 0, 100, 90)
    creator = st.slider("Creator sustainability fit", 0, 100, 85)
    accessibility = st.slider("Accessibility & inclusion", 0, 100, 82)
    if st.button("Calculate Green Score", type="primary"):
        g = green_score(logistics, digital, creator, accessibility)
        metric_card(st, "Green score", f'{g["score"]}/100', "Weighted demo index")
        st.write(g["explanation"])

# ---------- Intelligence ----------
elif page == "🧠 Campaign Intelligence":
    st.title("Campaign Intelligence Dashboard")
    roi = calculate_roi()
    sentiment = analyze_sentiment("Great honest campaign. Useful content and strong creator fit.")
    viral = viral_score("Can AI find the right creator for a campaign?", "Reel")
    green = green_score(80, 90, 85, 82)
    impact = campaign_impact(roi, sentiment, viral, green)

    cols = st.columns(5)
    metric_card(cols[0], "ROAS", f'{roi["roas"]}x', "Performance")
    metric_card(cols[1], "Sentiment", f'{sentiment["positive"]}%', "Brand health")
    metric_card(cols[2], "Virality", f'{viral["score"]}/100', "Content readiness")
    metric_card(cols[3], "Green", f'{green["score"]}/100', "Sustainability")
    metric_card(cols[4], "Impact", f'{impact["impact_score"]}/100', "Composite index")

    st.markdown("### Executive interpretation")
    st.write(impact["summary"])
    st.markdown("### Next actions")
    for action in impact["actions"]:
        st.markdown(f"- {action}")

# ---------- Network ----------
elif page == "🌐 Platform Network":
    st.title("Platform Network Effects")
    st.caption("A simple admin view demonstrating the multi-sided platform model.")
    c1, c2, c3, c4 = st.columns(4)
    metric_card(c1, "Brands", "42", "Demand side")
    metric_card(c2, "Creators", "318", "Supply side")
    metric_card(c3, "Agencies", "26", "Service side")
    metric_card(c4, "Specialists", "74", "Legal + sustainability + freelance")

    st.markdown("### Network loop")
    st.success("More brands → more campaigns → more creator opportunities → richer performance data → better matching → stronger platform value.")
    st.markdown("### Governance")
    st.write("Akovate's demo design keeps matching explainable, supports responsible content rules, and makes sustainability a measurable campaign dimension.")
