import streamlit as st
import os
from dotenv import load_dotenv
from auth import initialize_session_state, login_page, register_page, show_user_info
from chat import display_chat_interface, load_chat_history, display_chat_history

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
        page_title="Medical Assistant Chatbot",
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
        # Main application interface for logged-in users
        st.title('Medical Assistant Chatbot')

        # Add sidebar options
        with st.sidebar:
            st.markdown("---")
            st.subheader("Options")
            view_mode = st.radio(
                "View Mode:",
                ["Chat Interface", "Chat History"],
                key="view_mode"
            )

            if st.button("Clear Current Chat"):
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