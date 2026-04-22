import streamlit as st
from auth.auth_functions import login_user, register_request, get_user_record
import base64
from streamlit_cookies_controller import CookieController


if "cookie_controller" not in st.session_state:
    st.session_state["cookie_controller"] = CookieController()

cookie = st.session_state["cookie_controller"]

ADMIN_EMAIL = st.secrets["admin"]["ADMIN_EMAIL"]

def show_login_page():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IM+Fell+English:ital@0;1&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap');

    .stApp {
        background: linear-gradient(135deg, #1B2A4A 0%, #243556 50%, #1B2A4A 100%) !important;
    }
    #MainMenu, footer, header { visibility: hidden; }
    section[data-testid="stSidebar"] { display: none !important; }

    .block-container {
        max-width: 600px !important;
        margin: 40px auto 0 auto !important;
        padding: 50px !important;
        background: #FFFFFF !important;
        border-radius: 12px !important;
        border-top: 5px solid #C9A84C !important;
        box-shadow: 0 24px 64px rgba(0,0,0,0.35) !important;
        position: absolute !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: #F5F1EA !important;
        border-radius: 8px !important;
        padding: 4px !important;
        border: 1px solid #D9D0BE !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px !important;
        font-family: 'Libre Baskerville', serif !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        color: #5A6A85 !important;
        padding: 8px 28px !important;
        border: none !important;
        background: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        background: #1B2A4A !important;
        color: #E8C97A !important;
    }
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] { display: none !important; }

    .stTextInput label {
        font-family: 'Libre Baskerville', serif !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        letter-spacing: 1.2px !important;
        text-transform: uppercase !important;
        color: #5A6A85 !important;
    }
    .stTextInput input {
        font-family: 'Libre Baskerville', serif !important;
        font-size: 17px !important;
        color: #1B2A4A !important;
        border: 1px solid #D9D0BE !important;
        border-radius: 6px !important;
        padding: 12px 14px !important; 
        background: #FDFBF7 !important;
    }
    .stTextInput input:focus {
        border-color: #C9A84C !important;
        box-shadow: 0 0 0 2px rgba(201,168,76,0.15) !important;
    }

    .stButton > button {
        background: #1B2A4A !important;
        color: #E8C97A !important;
        border: 2px solid #C9A84C !important;
        border-radius: 8px !important;
        font-family: 'Libre Baskerville', serif !important;
        font-size: 17px !important;
        font-weight: 700 !important;
        letter-spacing: 0.8px !important;
        padding: 14px 0 !important;
        margin-top: 8px;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: #C9A84C !important;
        color: #1B2A4A !important;
    }
    .stAlert {
        border-radius: 8px !important;
        font-family: 'Libre Baskerville', serif !important;
        font-size: 13px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    def get_base64(img_path):
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode()  

    logo = get_base64("logo.png") 

    # Branding
    st.markdown(f"""
        <div style="text-align:center; margin-bottom:10px;">
        <img src="data:image/png;base64,{logo}" width="400"  height="200"
        style="border-radius:8px;">
           </div>
        <div style="font-family:'IM Fell English',serif; font-size:26px;
                    color:#1B2A4A; text-align:center; margin-bottom:4px;">
            Customer Visit Report
        </div>
        <div style="font-family:'Libre Baskerville',serif; font-size:11px;
                    color:#5A6A85; text-align:center; letter-spacing:1.8px;
                    text-transform:uppercase; margin-bottom:6px;">
            Sales Intelligence Dashboard
        </div>
        <div style="width:48px; height:3px; background:#C9A84C;
                    margin: 0 auto 28px auto; border-radius:2px;"></div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["  Login  ", "  Request Access  "])

    with tab1:
        email = st.text_input("Email Address", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Sign In", key="login_btn", use_container_width=True):
            if not email or not password:
                st.error("Please fill in all fields.")
            else:
                result = login_user(email, password)
                if "error" in result:
                    st.error("Invalid email or password.")
                else:
                    uid = result["localId"]
                    if email == ADMIN_EMAIL:
                        # ── Step 1 passed — now ask for 2FA ──
                        st.session_state["awaiting_2fa"] = True
                        st.session_state["pending_uid"]  = uid
                        st.session_state["pending_email"] = email
                        st.rerun()
                    
                    else:
                    
                        user_record = get_user_record(uid)
                        if not user_record:
                            st.error("No access request found. Please request access first.")
                        elif user_record["status"] == "pending":
                            st.warning("⏳ Your request is pending admin approval.")
                        elif user_record["status"] == "denied":
                            st.error("Access denied. Contact your administrator.")
                        elif user_record["status"] == "approved":
                            st.session_state["logged_in"] = True
                            st.session_state["role"]      = "user"
                            st.session_state["uid"]       = uid
                            st.session_state["email"]     = email
                            cookie.set("uid",   uid)    # ← add
                            cookie.set("email", email)  # ← add
                            cookie.set("role",  "user") # ← add
                            st.rerun()



    with tab2:
        st.markdown("""
            <p style="font-family:'Libre Baskerville',serif; font-size:13px;
               color:#5A6A85; margin-bottom:8px; line-height:1.7;">
               Submit your details below. The administrator will review your
               request and set up your account credentials.
            </p>
        """, unsafe_allow_html=True)
        full_name = st.text_input("Full Name", key="reg_name")
        email_reg = st.text_input("Email Address", key="reg_email")

        if st.button("Submit Request", key="reg_btn", use_container_width=True):
            if not full_name or not email_reg:
                st.error("Please fill in all fields.")
            else:
                success, msg = register_request(email_reg, full_name)
                if success:
                    st.success("✅ Request submitted! You will be notified once approved.")
                else:
                    st.error(msg)

    st.markdown("""
        <hr style="border:none; border-top:1px solid #EDE8DF; margin:28px 0 16px 0;">
        <div style="font-family:'Libre Baskerville',serif; font-size:11px;
                    color:#A0A8B8; text-align:center;">
            Samira Chemicals &nbsp;·&nbsp; Confidential Access Only
        </div>
    """, unsafe_allow_html=True)