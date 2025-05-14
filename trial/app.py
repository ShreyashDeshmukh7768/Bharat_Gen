# app.py
import streamlit as st
import os
from dotenv import load_dotenv
from auth import initialize_session_state, login_page, register_page, show_user_info, logout
from chat import display_chat_interface, load_chat_history, display_chat_history
from dashboard import display_dashboard
from my_profile import display_profile_update
from emotional_diary_page import display_emotional_diary
from document_upload import display_document_upload

# Load environment variables
load_dotenv()

# Setup LangChain tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

def main():
    # Initialize session state
    initialize_session_state()
    
    # Set up the page
    st.set_page_config(
        page_title="Swasthya AI",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Display user info in sidebar
    show_user_info()
    
    # Main content
    if not st.session_state['logged_in']:
        # Show tabs for login and registration
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            login_page()
        with tab2:
            register_page()
    else:
        # Determine which page to show based on session state
        if 'current_page' not in st.session_state:
            st.session_state['current_page'] = 'dashboard'
        
        # Add navigation to sidebar for logged-in users
        with st.sidebar:
            st.markdown("---")
            st.subheader("Navigation")
                    
            if st.button("Dashboard", use_container_width=True):
                st.session_state['current_page'] = 'dashboard'
                st.rerun()
                        
            if st.button("Update Profile", use_container_width=True):
                st.session_state['current_page'] = 'profile'
                st.rerun()
                        
            if st.button("Logout", use_container_width=True):
                logout()
                st.rerun()
        
        # Display the appropriate page based on session state
        if st.session_state['current_page'] == 'dashboard':
            display_dashboard()
        elif st.session_state['current_page'] == 'profile':
            display_profile_update()
        elif st.session_state['current_page'] == 'chatbot':
            st.title('Swasthya AI Chatbot')
                    
            # Button to navigate back to dashboard
            col1, col2 = st.columns([5, 1])
            with col2:
                if st.button("Back to Dashboard", use_container_width=True):
                    st.session_state['current_page'] = 'dashboard'
                    st.rerun()
                    
            # Add chatbot sidebar options
            with st.sidebar:
                st.markdown("---")
                st.subheader("Chatbot Options")
                view_mode = st.radio(
                    "View Mode:",
                    ["Chat Interface", "Chat History"],
                    key="view_mode"
                )
                if st.button("Clear Current Chat", use_container_width=True):
                    st.session_state.chat_messages = []
                    st.rerun()
            
            # Load chat history if not already loaded
            load_chat_history(st.session_state['user_id'])
            
            # Display either chat interface or chat history based on selection
            if view_mode == "Chat Interface":
                display_chat_interface()
            else:
                display_chat_history(st.session_state['user_id'])
        elif st.session_state['current_page'] == 'emotional_diary':
            # Display the emotional diary page
            display_emotional_diary()
        elif st.session_state['current_page'] == 'document_upload':
            # NEW: Display document upload page
            # Button to navigate back to dashboard
            col1, col2 = st.columns([5, 1])
            with col2:
                if st.button("Back to Dashboard", use_container_width=True):
                    st.session_state['current_page'] = 'dashboard'
                    st.rerun()
                    
            # Display document upload interface
            display_document_upload()

if __name__ == "__main__":
    main()

# Database Schema
# -- Users Table
# CREATE TABLE users (
#   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#   email varchar NOT NULL UNIQUE,
#   password_hash varchar NOT NULL,
#   full_name varchar NOT NULL,
#   age INT NOT NULL,
#   gender varchar NOT NULL,
#   contact_no varchar NOT NULL,
#   created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
# );
#
# -- Medical Information Table
# CREATE TABLE medical_info (
#   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#   user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
#   condition_name VARCHAR NOT NULL,
#   condition_type VARCHAR NOT NULL, -- 'standard' or 'custom'
#   created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
# );
#
# -- Chat History Table
# CREATE TABLE chat_history (
#   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#   user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
#   question TEXT NOT NULL,
#   answer TEXT NOT NULL,
#   created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
# );
#
# -- Emotional Diary Table
# CREATE TABLE emotional_diary (
#   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#   user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
#   entry TEXT NOT NULL,
#   response TEXT NOT NULL,
#   mood VARCHAR NOT NULL,
#   json_data JSONB,
#   created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
# );
#
# -- NEW: User Documents Table
# CREATE TABLE user_documents (
#   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#   user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
#   file_name VARCHAR NOT NULL,
#   extracted_text TEXT NOT NULL,
#   summary TEXT NOT NULL,
#   medicines TEXT[], -- Array of medicine names found in the document
#   created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
# );
#
# -- Create indices for faster queries
# CREATE INDEX idx_medical_info_user_id ON medical_info(user_id);
# CREATE INDEX idx_chat_history_user_id ON chat_history(user_id);
# CREATE INDEX idx_emotional_diary_user_id ON emotional_diary(user_id);
# CREATE INDEX idx_user_documents_user_id ON user_documents(user_id);
# CREATE INDEX idx_user_documents_created_at ON user_documents(created_at);
#
# -- Disable Row Level Security on all tables
# ALTER TABLE users DISABLE ROW LEVEL SECURITY;
# ALTER TABLE medical_info DISABLE ROW LEVEL SECURITY;
# ALTER TABLE chat_history DISABLE ROW LEVEL SECURITY;
# ALTER TABLE emotional_diary DISABLE ROW LEVEL SECURITY;
# ALTER TABLE user_documents DISABLE ROW LEVEL SECURITY;