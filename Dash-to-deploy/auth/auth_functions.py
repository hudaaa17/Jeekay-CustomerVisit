from firebase_admin import auth
from auth.firebase_config import get_db
import streamlit as st
import requests
from firebase_admin import auth
import re



def login_user(email, password):
    """Verify user via Firebase Auth REST API"""
    api_key = st.secrets["keys"]["firebase_web_api_key"]
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    r = requests.post(url, json=payload)
    return r.json()

def validate_full_name(full_name):
    full_name = full_name.strip()
    
    if len(full_name) < 4:
        return False, "Please enter a valid full name."
    
    if any(char.isdigit() for char in full_name):
        return False, "Name should not contain numbers."
    
    if not re.match(r"^[a-zA-Z\s\-\']+$", full_name):
        return False, "Name contains invalid special characters."
    
    if " " not in full_name:
        return False, "Please enter both your first and last name."

    if "  " in full_name:
        return False, "Name contains unnecessary spaces."

    return True, None

def validate_email(email):
    email = email.strip()

    if len(email) < 5:
        return False, "Email is too short."

    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(email_regex, email):
        return False, "Please enter a valid email address (e.g., name@example.com)."

    if ".." in email:
        return False, "Email contains invalid consecutive dots."

    return True, None  # Consistent return

def register_request(email, full_name):
    
    #Validate Name
    is_name_valid, name_error = validate_full_name(full_name)
    if not is_name_valid:
        return False, name_error

    # 2. Validate Email
    is_email_valid, email_error = validate_email(email)
    if not is_email_valid:
        return False, email_error
    

    db = get_db()

    # Check if request already exists    
    pending_docs = db.collection("pending_requests").where("email", "==", email).get()
    if pending_docs:
        return False, "A request with this email is already pending approval."

    # Check if email is already registered
    existing = db.collection("users").where("email", "==", email).get()
    if existing:
        return False, "A request with this email already exists."
    
    # Case: Email is not registered or in pending requests
    db.collection("pending_requests").add({
        "email": email,
        "full_name": full_name,
        "status": "pending",
    })
    return True, "Request sent! Admin will set up your account."

def get_user_record(uid):
    db = get_db()
    doc = db.collection("users").document(uid).get()
    if doc.exists:
        return doc.to_dict()
    return None

def get_all_requests():
    db = get_db()
    return [doc.to_dict() for doc in db.collection("users").stream()]

def update_user_status(uid, status):
    db = get_db()
    db.collection("users").document(uid).update({"status": status})

def approve_user(email, full_name, doc_id, password):
    api_key = st.secrets["keys"]["firebase_web_api_key"]

    # Create user in Firebase Auth
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    r = requests.post(url, json=payload)
    data = r.json()

    if "error" in data:
        return False, data["error"]["message"]

    uid = data["localId"]
    db = get_db()

    # Add to users collection
    db.collection("users").document(uid).set({
        "uid": uid,
        "email": email,
        "full_name": full_name,
        "role": "user",
        "status": "approved",
        "password_plain": password,  # stored so admin can view it
    })

    # Delete from pending
    db.collection("pending_requests").document(doc_id).delete()
    return True, f"User {email} created successfully!"

def deny_request(doc_id):
    db = get_db()
    db.collection("pending_requests").document(doc_id).update({"status": "denied"})

def get_pending_requests():
    db = get_db()
    docs = db.collection("pending_requests").stream()
    return [{"doc_id": d.id, **d.to_dict()} for d in docs]

def get_all_users():
    db = get_db()
    docs = db.collection("users").stream()
    return [d.to_dict() for d in docs]

def remove_user(uid, email):
    # Delete from Firebase Auth
    from auth.firebase_config import init_firebase  # ← add this
    from firebase_admin import auth
    init_firebase() 
    try:
        auth.delete_user(uid)
    except Exception:
        pass
    # Delete from Firestore
    db = get_db()
    db.collection("users").document(uid).delete()


def change_user_password(email, new_password, uid):
    from firebase_admin import auth
    auth.update_user(uid, password=new_password)
    db = get_db()
    db.collection("users").document(uid).update({"password_plain": new_password})

def create_user_directly(email, full_name, password):
    import requests
    api_key = st.secrets["keys"]["firebase_web_api_key"]
    db = get_db()

    # Check duplicates in users only
    existing = db.collection("users").where("email", "==", email).get()
    if existing:
        return False, "A user with this email already exists."

    # Create in Firebase Auth
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    r = requests.post(url, json=payload)
    data = r.json()

    if "error" in data:
        return False, data["error"]["message"]

    uid = data["localId"]

    # If a pending request exists for this email, clean it up
    pending = db.collection("pending_requests").where("email", "==", email).get()
    for doc in pending:
        db.collection("pending_requests").document(doc.id).delete()

    # Save to Firestore
    db.collection("users").document(uid).set({
        "uid": uid,
        "email": email,
        "full_name": full_name,
        "role": "user",
        "status": "approved",
        "password_plain": password,
    })
    return True, f"User {full_name} created!"

def get_denied_requests():
    db = get_db()
    docs = db.collection("pending_requests").where("status", "==", "denied").stream()
    return [{"doc_id": d.id, **d.to_dict()} for d in docs]

def restore_request(doc_id):
    db = get_db()
    db.collection("pending_requests").document(doc_id).update({"status": "pending"})

def delete_request_permanently(doc_id):
    db = get_db()
    db.collection("pending_requests").document(doc_id).delete()