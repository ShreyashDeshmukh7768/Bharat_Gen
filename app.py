import streamlit as st
import os
from dotenv import load_dotenv
from auth import initialize_session_state, login_page, register_page, show_user_info
from chat import process_query, display_chat_history

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
    st.set_page_config(page_title="Medical Assistant Chatbot", layout="wide")

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

        # Chat interface
        st.header("Ask a Question")

        input_text = st.text_area("Type your health-related question here", height=100)

        if st.button("Get Answer"):
            if input_text:
                with st.spinner("Processing your query..."):
                    response = process_query(input_text, st.session_state['user_id'])

                st.markdown("### Answer:")
                st.write(response)
            else:
                st.warning("Please enter a question.")

        # Display chat history
        st.markdown("---")
        display_chat_history(st.session_state['user_id'])


if __name__ == "__main__":
    main()