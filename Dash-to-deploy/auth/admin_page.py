import streamlit as st
from auth.auth_functions import (
    get_pending_requests, get_all_users, get_denied_requests,
    approve_user, deny_request,
    remove_user, change_user_password,
    create_user_directly, restore_request,
    delete_request_permanently 
)

def show_admin_page():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IM+Fell+English:ital@0;1&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap');

    /* ── Page background ── */
    .stApp {
        background: #F5F1EA;
    }

    /* ── Section titles ── */
    .section-title {
        font-family: 'IM Fell English', serif;
        font-size: 22px;
        color: #1B2A4A;
        border-bottom: 2px solid #C9A84C;
        padding-bottom: 6px;
        margin: 32px 0 16px 0;
    }

    /* ── Name & email display ── */
    .user-name {
        font-family: 'Libre Baskerville', serif;
        font-size: 14px;
        font-weight: 700;
        color: #1B2A4A;
        margin-bottom: 2px;
        padding-top: 8px;
    }
    .user-email {
        font-family: 'Libre Baskerville', serif;
        font-size: 12px;
        color: #5A6A85;
        padding-bottom: 8px;
    }

    /* ── Status badges ── */
    .badge-pending {
        background: #FFF3CD;
        color: #856404;
        border: 1px solid #FFEAA7;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'Libre Baskerville', serif;
        letter-spacing: 0.5px;
        display: inline-block;
        margin-top: 10px;
    }
    .badge-approved {
        background: #D4EDDA;
        color: #155724;
        border: 1px solid #C3E6CB;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'Libre Baskerville', serif;
        display: inline-block;
        margin-top: 10px;
    }
    .badge-denied {
        background: #F8D7DA;
        color: #721C24;
        border: 1px solid #F5C6CB;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'Libre Baskerville', serif;
        display: inline-block;
        margin-top: 10px;
    }

    /* ── Column header labels ── */
    .col-header {
        font-family: 'Libre Baskerville', serif;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: #5A6A85;
        padding-bottom: 4px;
    }

    /* ── All buttons base ── */
    .stButton > button {
        font-family: 'Libre Baskerville', serif !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        border-radius: 6px !important;
        padding: 6px 12px !important;
        transition: all 0.2s ease !important;
        width: 100%;
    }

    /* ── Approve button — navy/gold ── */
    [data-testid="stVerticalBlock"] .stButton > button[kind="secondary"]:has(div:contains("✓")) {
        background: #1B2A4A !important;
        color: #E8C97A !important;
        border: 1.5px solid #C9A84C !important;
    }

    /* ── Default button style (approve/create/update) ── */
    .stButton > button {
        background: #1B2A4A !important;
        color: #E8C97A !important;
        border: 1.5px solid #C9A84C !important;
    }
    .stButton > button:hover {
        background: #C9A84C !important;
        color: #1B2A4A !important;
    }

    /* ── Inputs ── */
    .stTextInput input {
        font-family: 'Libre Baskerville', serif !important;
        font-size: 13px !important;
        border: 1px solid #D9D0BE !important;
        border-radius: 6px !important;
        padding: 6px 10px !important;
        background: #FFFFFF !important;
        color: #1B2A4A !important;
    }
    .stTextInput input:focus {
        border-color: #C9A84C !important;
        box-shadow: 0 0 0 2px rgba(201,168,76,0.15) !important;
    }
    .stTextInput label {
        font-family: 'Libre Baskerville', serif !important;
        font-size: 10px !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        color: #5A6A85 !important;
    }

    /* ── Expander (Denied Requests + Password) ── */
    [data-testid="stExpander"] {
        background: #FFFFFF !important;
        border: 1px solid #D9D0BE !important;
        border-left: 4px solid #F5C6CB !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(27,42,74,0.06) !important;
    }
    [data-testid="stExpander"] summary {
        font-family: 'Libre Baskerville', serif !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        color: #721C24 !important;
        padding: 12px 16px !important;
    }

    /* ── Create User expander — different accent ── */
    [data-testid="stExpander"]:has(summary:contains("Create")) {
        border-left: 4px solid #C9A84C !important;
    }
    [data-testid="stExpander"]:has(summary:contains("Create")) summary {
        color: #1B2A4A !important;
    }

    /* ── Info / warning / success alerts ── */
    .stAlert {
        border-radius: 8px !important;
        font-family: 'Libre Baskerville', serif !important;
        font-size: 13px !important;
    }

    /* ── Dividers ── */
    hr {
        border-color: #D9D0BE !important;
        margin: 6px 0 !important;
    }

    /* ── st.code (password display) ── */
    .stCode {
        font-size: 13px !important;
        border-radius: 6px !important;
        background: #F5F1EA !important;
    }

    /* ── Sidebar stays navy ── */
    section[data-testid="stSidebar"] {
        background: #1B2A4A !important;
        border-right: 3px solid #C9A84C;
    }
    section[data-testid="stSidebar"] * {
        color: #E8E4DC !important;
        font-family: 'Libre Baskerville', serif;
    }
    section[data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        color: #E8C97A !important;
        border: 1px solid #C9A84C !important;
        border-radius: 6px !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #C9A84C !important;
        color: #1B2A4A !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════
    # PENDING REQUESTS
    # ══════════════════════════════════════
    st.markdown('<div class="section-title">Pending Access Requests</div>',
                unsafe_allow_html=True)

    pending = get_pending_requests()
    active_pending = [p for p in pending if p.get("status") == "pending"]

    if not active_pending:
        st.info("No pending requests.")
    else:
        # Table header
        hc1, hc2, hc3, hc4, hc5 = st.columns([3, 3, 2, 1, 1])
        hc1.markdown("<span style='font-family:Libre Baskerville,serif; font-size:11px; font-weight:700; letter-spacing:1px; text-transform:uppercase; color:#5A6A85;'>Name</span>", unsafe_allow_html=True)
        hc2.markdown("<span style='font-family:Libre Baskerville,serif; font-size:11px; font-weight:700; letter-spacing:1px; text-transform:uppercase; color:#5A6A85;'>Email</span>", unsafe_allow_html=True)
        hc3.markdown("<span style='font-family:Libre Baskerville,serif; font-size:11px; font-weight:700; letter-spacing:1px; text-transform:uppercase; color:#5A6A85;'>Set Password</span>", unsafe_allow_html=True)
        hc4.markdown("<span style='font-family:Libre Baskerville,serif; font-size:11px; font-weight:700; letter-spacing:1px; text-transform:uppercase; color:#5A6A85;'>Approve</span>", unsafe_allow_html=True)
        hc5.markdown("<span style='font-family:Libre Baskerville,serif; font-size:11px; font-weight:700; letter-spacing:1px; text-transform:uppercase; color:#5A6A85;'>Deny</span>", unsafe_allow_html=True)

        st.markdown("<hr style='margin:4px 0 8px 0; border-color:#D9D0BE;'>", unsafe_allow_html=True)

        for req in active_pending:
            c1, c2, c3, c4, c5 = st.columns([3, 3, 2, 1, 1])

            with c1:
                st.markdown(f"""
                    <div class="user-name">{req['full_name']}</div>
                """, unsafe_allow_html=True)

            with c2:
                st.markdown(f"""
                    <div class="user-email">{req['email']}</div>
                """, unsafe_allow_html=True)

            with c3:
                new_pass = st.text_input(
                    "Password",
                    key=f"pass_{req['doc_id']}",
                    type="password",
                    placeholder="Min. 6 chars",
                    label_visibility="collapsed"
                )

            with c4:
                if st.button("✓ Approve", key=f"approve_{req['doc_id']}",
                             use_container_width=True):
                    if not new_pass:
                        st.error("Set a password first.")
                    else:
                        ok, msg = approve_user(
                            req['email'], req['full_name'],
                            req['doc_id'], new_pass
                        )
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

            with c5:
                if st.button("✗ Deny", key=f"deny_{req['doc_id']}",
                             use_container_width=True):
                    deny_request(req['doc_id'])
                    st.warning(f"Denied {req['full_name']}")
                    st.rerun()

            st.markdown("<hr style='margin:4px 0; border-color:#EDE8DF;'>",
                        unsafe_allow_html=True)
    # ══════════════════════════════════════
    # DENIED REQUESTS — hidden in expander
    # ══════════════════════════════════════
    denied = get_denied_requests()

    if denied:
        with st.expander(f"🚫  Denied Requests ({len(denied)})", expanded=False):
            
            dh1, dh2, dh3, dh4 = st.columns([3, 3, 2, 2])
            for col, label in zip(
                [dh1, dh2, dh3, dh4],
                ["Name", "Email", "Set Password", "Actions"]
            ):
                col.markdown(
                    f"<span style='font-family:Libre Baskerville,serif; font-size:11px;"
                    f"font-weight:700; letter-spacing:1px; text-transform:uppercase;"
                    f"color:#5A6A85;'>{label}</span>",
                    unsafe_allow_html=True
                )

            st.markdown("<hr style='margin:4px 0 8px 0; border-color:#D9D0BE;'>",
                        unsafe_allow_html=True)

            for req in denied:
                d1, d2, d3, d4 = st.columns([3, 3, 2, 2])

                with d1:
                    st.markdown(
                        f'<div class="user-name" style="color:#721C24;">'
                        f'{req["full_name"]}</div>',
                        unsafe_allow_html=True
                    )

                with d2:
                    st.markdown(
                        f'<div class="user-email">{req["email"]}</div>',
                        unsafe_allow_html=True
                    )

                with d3:
                    restore_pass = st.text_input(
                        "Password",
                        key=f"rpass_{req['doc_id']}",
                        type="password",
                        placeholder="To approve directly",
                        label_visibility="collapsed"
                    )

                with d4:
                    ca, cb, cc = st.columns(3)
                    with ca:
                        if st.button("↩", key=f"restore_{req['doc_id']}",
                                     use_container_width=True,
                                     help="Restore to pending"):
                            restore_request(req['doc_id'])
                            st.success(f"Restored {req['full_name']} to pending.")
                            st.rerun()
                    with cb:
                        if st.button("✓", key=f"dapprove_{req['doc_id']}",
                                     use_container_width=True,
                                     help="Approve directly"):
                            if not restore_pass:
                                st.error("Set a password first.")
                            else:
                                ok, msg = approve_user(
                                    req['email'], req['full_name'],
                                    req['doc_id'], restore_pass
                                )
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                    with cc:
                        if st.button("🗑", key=f"delete_{req['doc_id']}",
                                     use_container_width=True,
                                     help="Delete permanently"):
                            delete_request_permanently(req['doc_id'])
                            st.success(f"Deleted {req['full_name']} permanently.")
                            st.rerun()

                st.markdown("<hr style='margin:4px 0; border-color:#EDE8DF;'>",
                            unsafe_allow_html=True)
    # ══════════════════════════════════════
    # ALL USERS
    # ══════════════════════════════════════
    st.markdown('<div class="section-title">All Users</div>', unsafe_allow_html=True)

    all_users = get_all_users()

    if not all_users:
        st.info("No users yet.")
    else:
        # Table header
        uh1, uh2, uh3, uh4, uh5 = st.columns([3, 3, 1, 2, 1])
        for col, label in zip(
            [uh1, uh2, uh3, uh4, uh5],
            ["Name", "Email", "Status", "Password", "Action"]
        ):
            col.markdown(
                f"<span style='font-family:Libre Baskerville,serif; font-size:11px;"
                f"font-weight:700; letter-spacing:1px; text-transform:uppercase;"
                f"color:#5A6A85;'>{label}</span>",
                unsafe_allow_html=True
            )

        st.markdown("<hr style='margin:4px 0 8px 0; border-color:#D9D0BE;'>",
                    unsafe_allow_html=True)

        for user in all_users:
            u1, u2, u3, u4, u5 = st.columns([3, 3, 1, 2, 1])

            with u1:
                st.markdown(f'<div class="user-name">{user["full_name"]}</div>',
                            unsafe_allow_html=True)

            with u2:
                st.markdown(f'<div class="user-email">{user["email"]}</div>',
                            unsafe_allow_html=True)

            with u3:
                status = user.get("status", "approved")
                badge_class = f"badge-{status}"
                st.markdown(f'<span class="{badge_class}">{status.capitalize()}</span>',
                            unsafe_allow_html=True)

            with u4:
                with st.expander("View / Change"):
                    stored = user.get("password_plain", "–")
                    st.code(stored, language=None)
                    new_p = st.text_input(
                        "New password",
                        key=f"newp_{user['uid']}",
                        type="password",
                        placeholder="New password"
                    )
                    if st.button("Update", key=f"updp_{user['uid']}",
                                 use_container_width=True):
                        if new_p:
                            change_user_password(user['email'], new_p, user['uid'])
                            st.success("Updated!")
                            st.rerun()
                        else:
                            st.error("Enter a new password.")

            with u5:
                st.write("")
                if st.button("Remove", key=f"remove_{user['uid']}",
                             use_container_width=True):
                    remove_user(user['uid'], user['email'])
                    st.warning(f"Removed {user['full_name']}")
                    st.rerun()

            st.markdown("<hr style='margin:4px 0; border-color:#EDE8DF;'>",
                        unsafe_allow_html=True)
    # ══════════════════════════════════════
    # CREATE USER
    # ══════════════════════════════════════
    st.markdown('<div class="section-title">Create User</div>', unsafe_allow_html=True)

    with st.expander("➕  Create a new user directly", expanded=False):
        cc1, cc2, cc3, cc4 = st.columns([2, 2, 2, 1])

        with cc1:
            new_full_name = st.text_input("Full Name", key="create_full_name",
                                           placeholder="e.g. John Smith")
        with cc2:
            new_email = st.text_input("Email Address", key="create_email",
                                       placeholder="e.g. john@company.com")
        with cc3:
            new_password = st.text_input("Password", key="create_password",
                                          type="password", placeholder="Min. 6 chars")
        with cc4:
            st.write("")
            st.write("")
            create_clicked = st.button("Create User", key="create_user_btn",
                                        use_container_width=True)

        if create_clicked:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

            # ── Validation ──
            if not new_full_name or not new_email or not new_password:
                st.error("Please fill in all fields.")
            elif len(new_full_name.strip()) < 2:
                st.error("Please enter a valid full name.")
            elif any(char.isdigit() for char in new_full_name):
                st.error("Name should not contain numbers.")
            elif not re.match(email_pattern, new_email.strip()):
                st.error("Please enter a valid email address (e.g. name@example.com)")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                # Reuse approve_user but pass a fake doc_id since
                # there's no pending request to delete
                ok, msg = create_user_directly(
                    new_email.strip(), new_full_name.strip(), new_password
                )
                if ok:
                    st.success(f"✅ User {new_full_name} created successfully!")
                else:
                    st.error(msg)