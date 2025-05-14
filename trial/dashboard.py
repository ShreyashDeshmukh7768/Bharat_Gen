# dashboard.py

import streamlit as st
from mood_visualizations import create_dashboard_mood_summary

# Inject CSS for hover effect
def add_hover_styles():
    st.markdown("""
    <style>
    .hover-tile {
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #ddd;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        background-color: #f8f9fa;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .hover-tile:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0,0,0,0.15);
    }

    .hover-tile h2, .hover-tile p {
        color: #212529;
    }
    </style>
    """, unsafe_allow_html=True)


def display_dashboard():
    """Display the main dashboard with tiles for different features"""
    st.title(f"Welcome, {st.session_state['user_name']}!")
    add_hover_styles()

    # Create dashboard layout
    left_col, right_col = st.columns([2, 1])

    with left_col:
        # First row of tiles
        col1, col2 = st.columns(2)

        # Chatbot tile
        with col1:
            st.markdown("""
            <div class="hover-tile">
                <h2>Chatbot</h2>
                <p>Get personalized health advice with our AI assistant</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Open Chatbot", key="open_chatbot", use_container_width=True):
                st.session_state['current_page'] = 'chatbot'
                st.rerun()

        # Emotional Diary tile
        with col2:
            st.markdown("""
            <div class="hover-tile">
                <h2>Emotional Diary</h2>
                <p>Express your feelings and receive supportive responses</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Open Diary", key="open_diary", use_container_width=True):
                st.session_state['current_page'] = 'emotional_diary'
                st.rerun()

        # Second row of tiles
        col3, col4 = st.columns(2)

        # Medical Profile tile
        with col3:
            st.markdown("""
            <div class="hover-tile">
                <h2>My Medical Profile</h2>
                <p>Update and view your medical information</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("View Profile", key="view_profile", use_container_width=True):
                st.session_state['current_page'] = 'profile'
                st.rerun()

        # NEW Document Upload tile (replacing Health Resources)
        with col4:
            st.markdown("""
            <div class="hover-tile">
                <h2>Document Upload</h2>
                <p>Upload and analyze medical documents and prescriptions</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Upload Documents", key="upload_documents", use_container_width=True):
                st.session_state['current_page'] = 'document_upload'
                st.rerun()

    with right_col:
        # Mood tracking summary
        st.markdown("""
        <div class="hover-tile">
            <h3>Mood Tracker</h3>
        </div>
        """, unsafe_allow_html=True)

        create_dashboard_mood_summary(st.session_state['user_id'])

        if st.button("View Detailed Analytics", key="view_analytics", use_container_width=True):
            st.session_state['current_page'] = 'emotional_diary'
            st.session_state['diary_view_mode'] = 'Mood Analytics'
            st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("""
    ### About Swasthya AI

    Swasthya AI is your personal health assistant, providing health advice tailored to your medical conditions. 
    Our AI-powered chatbot offers personalized guidance while respecting your privacy.

    *Note: This application is for informational purposes only and is not a substitute for professional medical advice.*
    """)