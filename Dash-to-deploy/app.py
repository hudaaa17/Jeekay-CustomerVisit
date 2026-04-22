import streamlit as st
from data_handling.load_data import load_and_preprocess_data
from data_handling.load_data import format_inr
from data_handling.load_data import to_excel
from datetime import datetime
from businesslogic.measure_creation import calculate_measures
from businesslogic.pdfgenerator import generate_visit_pdf
import re
from streamlit_cookies_controller import CookieController

from auth.firebase_config import init_firebase
from auth.login_page import show_login_page
from auth.admin_page import show_admin_page  

init_firebase()

if "cookie_controller" not in st.session_state:
    st.session_state["cookie_controller"] = CookieController()

cookie = st.session_state["cookie_controller"]

# ── Restore session from cookie on refresh ──
if not st.session_state.get("logging_out"):  # ← only restore if NOT logging out
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        uid_cookie   = cookie.get("uid")
        email_cookie = cookie.get("email")
        role_cookie  = cookie.get("role")

        if uid_cookie and email_cookie and role_cookie:
            st.session_state["logged_in"] = True
            st.session_state["uid"]       = uid_cookie
            st.session_state["email"]     = email_cookie
            st.session_state["role"]      = role_cookie

# ── Auth gate ──
if not st.session_state.get("logged_in"):
    st.session_state.pop("logging_out", None)  # clean up flag
    show_login_page()
    st.stop()

# ── Page routing ──
if st.session_state["role"] == "admin":
    if "page" not in st.session_state:
        st.session_state["page"] = "dashboard"

    with st.sidebar:
        email = st.session_state['email']
        st.markdown(
            f"""
            <div style="
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(201,168,76,0.4);
                border-radius: 8px;
                padding: 10px 14px;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                gap: 10px;
            ">
                <span style="font-size: 1.1rem;">👤</span>
                <span style="
                    color: #E8C97A;
                    font-family: 'Libre Baskerville', serif;
                    font-size: 13px;
                    font-weight: 700;
                    word-break: break-all;
                ">{email}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.divider()
        if st.button("Dashboard", key="nav_dash", use_container_width=True):
            st.session_state["page"] = "dashboard"
            st.rerun()
        if st.button("Admin Panel", key="nav_admin", use_container_width=True):
            st.session_state["page"] = "admin"
            st.rerun()
        st.divider()
        if st.button("Logout", key="logout_btn", use_container_width=True):
            for c in ["uid", "email", "role"]:
                try:
                    cookie.remove(c)
                except Exception:
                    pass
            for key in ["logged_in", "uid", "email", "role", "page", "logging_out"]:
                st.session_state.pop(key, None)
            st.rerun()

    if st.session_state["page"] == "admin":
        show_admin_page()
        st.stop()

else:
    with st.sidebar:
        st.markdown(f"👤 `{st.session_state['email']}`")
        st.divider()
        if st.button("Logout", key="logout_btn", use_container_width=True):
            for c in ["uid", "email", "role"]:
                try:
                    cookie.remove(c)
                except Exception:
                    pass
            for key in ["logged_in", "uid", "email", "role", "page", "logging_out"]:
                st.session_state.pop(key, None)
            st.rerun()



# ---- CONFIG ----
st.set_page_config(layout="wide")

# ---- CUSTOM CSS ----
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=IM+Fell+English:ital@0;1&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap');

/* ── Root variables ── */
:root {
    --navy:       #1B2A4A;
    --navy-light: #243556;
    --gold:       #C9A84C;
    --gold-light: #E8C97A;
    --cream:      #F5F1EA;
    --card-bg:    #FFFFFF;
    --text-main:  #1B2A4A;
    --text-muted: #5A6A85;
    --border:     #D9D0BE;
    --shadow:     0 4px 20px rgba(27,42,74,0.10);
}

/* ══════════════════════════════════════
   APP BACKGROUND & BASE FONT
══════════════════════════════════════ */
.stApp {
    background: var(--cream);
    font-family: 'Libre Baskerville', serif;
    font-size: 17px;
    color: var(--text-main);
}

/* ══════════════════════════════════════
   SIDEBAR
══════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: var(--navy) !important;
    border-right: 3px solid var(--gold);
}
section[data-testid="stSidebar"] * {
    color: #E8E4DC !important;
    font-family: 'Libre Baskerville', serif;
    font-size: 15px;
}
section[data-testid="stSidebar"] h2 {
    color: var(--gold-light) !important;
    font-family: 'IM Fell English', serif !important;
    font-size: 20px !important;
    letter-spacing: 0.5px;
}
section[data-testid="stSidebar"] .stSelectbox label {
    color: var(--gold-light) !important;
    font-family: 'Libre Baskerville', serif !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    letter-spacing: 0.6px;
    text-transform: uppercase;
}
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: var(--navy-light) !important;
    border: 1px solid var(--gold) !important;
    color: #E8E4DC !important;
    border-radius: 6px;
}

[data-testid="stSidebarCollapseButton"] {
    display: none !important;
}

/* ══════════════════════════════════════
   HEADINGS
══════════════════════════════════════ */
h1, h2, h3 {
    font-family: 'IM Fell English', serif !important;
    color: var(--navy) !important;
}
[data-testid="stSubheader"] {
    font-size: 24px !important;
    font-family: 'IM Fell English', serif !important;
    color: var(--navy) !important;
    border-bottom: 2px solid var(--gold);
    padding-bottom: 8px;
    margin-top: 28px !important;
    margin-bottom: 20px !important;
}

/* ══════════════════════════════════════
   KPI METRIC CARDS
══════════════════════════════════════ */
[data-testid="stMetric"] {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-top: 4px solid var(--gold);
    border-radius: 10px;
    padding: 20px 24px !important;
    box-shadow: var(--shadow);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 28px rgba(27,42,74,0.15);
}
[data-testid="stMetricLabel"] > div {
    font-size: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 1.4px !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    font-family: 'Libre Baskerville', serif !important;
    margin-bottom: 6px;
}
[data-testid="stMetricValue"] {
    font-size: 30px !important;
    font-weight: 700 !important;
    color: var(--navy) !important;
    font-family: 'Libre Baskerville', serif !important;
    line-height: 1.2;
}

/* ══════════════════════════════════════
   DATAFRAME TABLE
══════════════════════════════════════ */

/* Increase cell font */
[data-testid="stDataFrame"] div[role="gridcell"] {
    font-size: 30px !important;
}

/* Increase header font */
[data-testid="stDataFrame"] div[role="columnheader"] {
    font-size: 40px !important;
    font-weight: 600;
}

/* Optional: row height (makes it look less cramped) */
[data-testid="stDataFrame"] div[role="row"] {
    min-height: 35px;
}
[data-testid="stDataFrame"] {
    zoom: 1.1;
}
            
/* ══════════════════════════════════════
   DOWNLOAD BUTTON
══════════════════════════════════════ */
.stDownloadButton > button {
    background: var(--navy) !important;
    color: var(--gold-light) !important;
    border: 2px solid var(--gold) !important;
    border-radius: 8px !important;
    font-family: 'Libre Baskerville', serif !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    padding: 10px 28px !important;
    letter-spacing: 0.5px;
    transition: all 0.2s ease;
    margin-top: 10px;
}
.stDownloadButton > button:hover {
    background: var(--gold) !important;
    color: var(--navy) !important;
}

/* ══════════════════════════════════════
   CUSTOMER INSIGHT CARDS (HTML divs)
══════════════════════════════════════ */
.insight-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    box-shadow: var(--shadow);
    overflow: hidden;
    margin-bottom: 16px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.insight-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 28px rgba(27,42,74,0.15);
}
.insight-header {
    background: var(--navy);
    color: var(--gold-light) !important;
    font-family: 'Libre Baskerville', serif;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.4px;
    text-transform: uppercase;
    padding: 10px 16px;
    border-bottom: 2px solid var(--gold);
}
.insight-body {
    font-family: 'Libre Baskerville', serif;
    font-size: 15px;
    line-height: 1.8;
    color: var(--text-main);
    padding: 16px;
    min-height: 72px;
    background: var(--card-bg);
}

/* ── Reset Filters button ── */
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: var(--gold-light) !important;
    border: 1px solid var(--gold) !important;
    border-radius: 6px !important;
    font-family: 'Libre Baskerville', serif !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    letter-spacing: 0.8px;
    padding: 8px 12px !important;
    margin-bottom: 16px;
    width: 100%;
    transition: all 0.2s ease;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--gold) !important;
    color: var(--navy) !important;
}
            
/* ══════════════════════════════════════
   MISC
══════════════════════════════════════ */
hr {
    border-color: var(--border) !important;
    margin: 8px 0 !important;
}
[data-testid="column"] {
    padding-left: 8px !important;
    padding-right: 8px !important;
}
</style>
""", unsafe_allow_html=True)


df = load_and_preprocess_data()


# -----------------------------
# -----------------------------
# 🔍 FILTERS (LEFT PANEL)
# -----------------------------
st.sidebar.header("Filters")

# Reset button
if st.sidebar.button("🔄  Reset Filters", use_container_width=True, key="reset_filters_btn"):
    st.session_state["branch_filter"] = "All"
    st.session_state["area_filter"] = "All"
    st.session_state["customer_filter"] = "All"
    st.session_state["industry_filter"] = "All"

# Filters — all with session_state keys now
branch = st.sidebar.selectbox(
    "Branch", ["All"] + sorted(df["Branch"].dropna().unique().tolist()),
    key="branch_filter"
)
area = st.sidebar.selectbox(
    "Area", ["All"] + sorted(df["Area"].dropna().unique().tolist()),
    key="area_filter"
)
customer = st.sidebar.selectbox(
    "Customer", ["All"] + sorted(df["Customer"].dropna().unique().tolist()),
    key="customer_filter"
)
industry = st.sidebar.selectbox(
    "Industry", ["All"] + sorted(df["Industry"].dropna().unique().tolist()),
    key="industry_filter"
)

# Apply filters
filtered_df = df.copy()

if branch != "All":
    filtered_df = filtered_df[filtered_df["Branch"] == branch]

if area != "All":
    filtered_df = filtered_df[filtered_df["Area"] == area]

if customer != "All":
    filtered_df = filtered_df[filtered_df["Customer"] == customer]

if industry != "All":
    filtered_df = filtered_df[filtered_df["Industry"] == industry]

# -----------------------------
# 📊 MEASURES
# -----------------------------
measures = calculate_measures(filtered_df)

# -----------------------------
# 🔢 KPI SECTION
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Visits", measures["Total Visits"])
col2.metric("Latest Visit", measures["Latest Visit Date"])
col3.metric("Days Since Last Visit", measures["Days Since Last Visit"])
col4.metric("Follow-up Status", measures["Follow-up Status"])

col5, col6, col7, col8, col9 = st.columns(5)

col5.metric("Upcoming Follow-up", measures["Upcoming Follow-up Date"])
col6.metric("Days Until Follow-up", measures["Days Until Follow-up"])
col7.metric("Oldest Bill Date", measures["Oldest Bill Date (Customer)"])
col8.metric("Total Outstanding",  format_inr(measures['Total Outstanding']))
if customer!="All":
    col9.metric("Outstanding Days", measures["Outstanding Days"])

# -----------------------------
# 📋 TABLE (TOP RIGHT)
# -----------------------------
st.subheader("Visit History")

display_cols = [
    "Date",
    "Customer",
    "Customer Team",
    "Our Products offered / discussed",
    "Oldest Bill Date",
    "Period (Days)",
    "Total Outstanding",
    "Competitor products / prices",
    "Company Updates",
    "Market / End Market Updates",
    "Other Remarks",
    "Follow up",
    "Follow up Date"
]

display_df = (
    filtered_df
    .sort_values("Date", ascending=False)[display_cols]
    .reset_index(drop=True)
)

display_df.index = display_df.index + 1
display_df.index.name = "Sr No"

st.dataframe(display_df, width="stretch")


excel_data = to_excel(display_df)

st.download_button(
    label="Download as Excel",
    data=excel_data,
    file_name="Visit_History.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

#-- File Name generation (Dynamic)
today = datetime.now().strftime("%d%b") 
filters = []

if branch != "All":
    filters.append(branch)

if area != "All":
    filters.append(area)

if customer != "All":
    filters.append(customer)

if industry != "All":
    filters.append(industry)

if not filters:
    filter_part = "All"
else:
    filter_part = "_".join(filters)

filter_part = re.sub(r"[^\w]+", "_", filter_part)
filename = f"Visit_Report_{today}_{filter_part}.pdf"

pdf_buffer = generate_visit_pdf(filtered_df, customer, area, branch)

st.download_button(
    label="📄 Download Visit Report (PDF)",
    data=pdf_buffer,
    file_name=filename,
    mime="application/pdf"
)

# -----------------------------
# 🧾 TEXT PANELS (BOTTOM)
# -----------------------------
if customer != "All":
    st.subheader("Customer Insights")

    colA, colB, colC = st.columns(3)
    with colA:
        st.markdown(f'<div class="insight-card"><div class="insight-header">Latest Company Updates</div><div class="insight-body">{measures["Latest Company Updates"] or "–"}</div></div>', unsafe_allow_html=True)
    with colB:
        st.markdown(f'<div class="insight-card"><div class="insight-header">Latest Competitor Info</div><div class="insight-body">{measures["Latest Competitor Info"] or "–"}</div></div>', unsafe_allow_html=True)
    with colC:
        st.markdown(f'<div class="insight-card"><div class="insight-header">Latest Follow-up Details</div><div class="insight-body">{measures["Latest Follow-up Details"] or "–"}</div></div>', unsafe_allow_html=True)

    colD, colE = st.columns(2)
    with colD:
        st.markdown(f'<div class="insight-card"><div class="insight-header">Latest Remarks</div><div class="insight-body">{measures["Latest Remarks"] or "–"}</div></div>', unsafe_allow_html=True)
    with colE:
        st.markdown(f'<div class="insight-card"><div class="insight-header">Latest Market Updates</div><div class="insight-body">{measures["Latest Market Updates"] or "–"}</div></div>', unsafe_allow_html=True)



