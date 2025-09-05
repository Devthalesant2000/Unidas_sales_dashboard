## Dashboard Geral - Mentorados
import streamlit as st

st.set_page_config(layout="wide")

# --- PAGE SETUP ---
dash_page = st.Page(
    "Modules/Unidas_dashboard_month.py",
    title="Mês Atual",
    icon=":material/thumb_up:",
)

dash_YTD_page = st.Page(
    "Modules/Unidas_dashboard_YTD.py",
    title="YTD",
    icon=":material/thumb_up:",
)
# --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
# pg = st.navigation(pages=[about_page, project_1_page, project_2_page])

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Dashboard Unidas": [dash_page,dash_YTD_page],
    }
)

# --- SHARED ON ALL PAGES ---
# st.logo("assets/codingisfun_logo.png")


# --- RUN NAVIGATION ---
pg.run()
