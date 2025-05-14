import streamlit as st
import bcrypt
from database import SupabaseClient


def hash_password(password):
    """Hash a password for storing."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))


def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = None
    if 'user_email' not in st.session_state:
        st.session_state['user_email'] = None
    if 'user_name' not in st.session_state:
        st.session_state['user_name'] = None
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'dashboard'


def login_page():
    """Display the login page and handle login attempts"""
    st.header("Login to your account")

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", use_container_width=True):
        if not email or not password:
            st.error("Please enter both email and password")
            return

        # Attempt to log in the user
        db = SupabaseClient()
        user = db.get_user_by_email(email)

        if user and verify_password(user['password_hash'], password):
            # Set session state
            st.session_state['logged_in'] = True
            st.session_state['user_id'] = user['id']
            st.session_state['user_email'] = user['email']
            st.session_state['user_name'] = user['full_name']
            st.session_state['current_page'] = 'dashboard'  # Set to dashboard after login

            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid email or password")


def register_page():
    """Display the registration page and handle registration attempts"""
    st.header("Create a new account")

    with st.form(key="registration_form"):
        col1, col2 = st.columns(2)

        with col1:
            full_name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")

        with col2:
            age = st.number_input("Age", min_value=1, max_value=120, step=1)
            gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
            contact_no = st.text_input("Contact Number")

        # Medical conditions
        st.subheader("Medical Conditions")
        col1, col2 = st.columns(2)

        with col1:
            st.write("Standard conditions:")
            diabetes = st.checkbox("Diabetes")
            hypertension = st.checkbox("Hypertension")
            asthma = st.checkbox("Asthma")
            heart_disease = st.checkbox("Heart Disease")

        with col2:
            st.write("Custom conditions:")
            custom_conditions = st.text_area("Enter any other medical conditions (one per line)")

        submit_button = st.form_submit_button(label="Register")

        if submit_button:
            # Validate form fields
            if not all([full_name, email, password, confirm_password, age, gender, contact_no]):
                st.error("Please fill in all required fields.")
                return

            if password != confirm_password:
                st.error("Passwords do not match.")
                return

            # Hash the password
            password_hash = hash_password(password)

            # Prepare user data
            user_data = {
                'email': email,
                'password_hash': password_hash,
                'full_name': full_name,
                'age': age,
                'gender': gender,
                'contact_no': contact_no
            }

            # Prepare medical conditions
            medical_conditions = {
                'standard': {
                    'diabetes': diabetes,
                    'hypertension': hypertension,
                    'asthma': asthma,
                    'heart_disease': heart_disease
                },
                'custom': custom_conditions.strip().split('\n') if custom_conditions else []
            }

            # Create user in database
            db = SupabaseClient()
            existing_user = db.get_user_by_email(email)

            if existing_user:
                st.error("Email already registered. Please use a different email.")
                return

            user = db.create_user(user_data)

            if user:
                # Add medical info
                db.create_medical_info(user['id'], medical_conditions)

                st.success("Registration successful! You can now log in.")
                
                # Switch to login tab
                st.session_state['show_login'] = True
                st.rerun()
            else:
                st.error("Registration failed. Please try again.")


def logout():
    """Log out the current user"""
    st.session_state['logged_in'] = False
    st.session_state['user_id'] = None
    st.session_state['user_email'] = None
    st.session_state['user_name'] = None
    st.session_state['current_page'] = 'login'
    if 'chat_messages' in st.session_state:
        del st.session_state['chat_messages']


def show_user_info():
    """Display user information in the sidebar"""
    if st.session_state['logged_in']:
        col1, col2 = st.sidebar.columns([1, 3])
        
        with col1:
            st.sidebar.markdown("👤")  # User icon
        
        with col2:
            st.sidebar.markdown(f"**{st.session_state['user_name']}**")
            st.sidebar.markdown(f"*{st.session_state['user_email']}*")

        # Get user medical info
        db = SupabaseClient()
        medical_info = db.get_user_medical_info(st.session_state['user_id'])

        if medical_info:
            with st.sidebar.expander("Medical Conditions"):
                conditions = [info['condition_name'] for info in medical_info]
                st.write(", ".join(conditions))
    else:
        st.sidebar.info("Please login to access the application")