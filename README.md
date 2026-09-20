# Akovate — Cloud-Ready MVP

A responsive Streamlit prototype for an AI-powered Marketing Collaboration & Intelligence SaaS.

## Important architecture decision

**Google Colab is not required to run the live app.**

Use:
- GitHub = permanent source code
- Streamlit Community Cloud = live web hosting
- Colab = optional development/testing only

## Features

- Brand onboarding
- Campaign strategy generator
- Explainable AI talent matching
- Campaign collaboration workspace
- Content assistant
- Influencer ROI
- Sentiment analysis
- Viral strategy analyzer
- Green Campaign Score
- Campaign Intelligence dashboard
- Platform network effects view
- Mobile-responsive UI
- No external API key required for the demo

## Deploy

1. Push this folder to a GitHub repository.
2. Open Streamlit Community Cloud.
3. Choose **Create app**.
4. Select your GitHub repository.
5. Branch: `main`
6. Main file: `app.py`
7. Choose an app URL such as `akovate-mpb` if available.
8. Deploy.

The app then runs independently of Google Colab.

## Production note

The AI modules in this MVP are deterministic demo logic. For production, replace them with authenticated model APIs, a database, real user authentication, secure file storage, background jobs, observability, and proper privacy controls.
