import streamlit as st
import os
from dotenv import load_dotenv
from auth import initialize_session_state, login_page, register_page, show_user_info, logout
from chat import display_chat_interface, load_chat_history, display_chat_history
from dashboard import display_dashboard
from profile import display_profile_update

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


if __name__ == "__main__":
    main()