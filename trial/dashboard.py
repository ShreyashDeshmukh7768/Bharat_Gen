import streamlit as st


def display_dashboard():
    """Display the main dashboard with tiles for different features"""
    st.title(f"Welcome, {st.session_state['user_name']}!")
    
    # Create two columns for the dashboard tiles
    col1, col2 = st.columns(2)
    
    # Chatbot tile
    with col1:
        st.markdown("""
        <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; text-align: center;">
            <h2>Chatbot</h2>
            <p>Get personalized health advice with our AI assistant</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Open Chatbot", key="open_chatbot", use_container_width=True):
            st.session_state['current_page'] = 'chatbot'
            st.rerun()
    
    # Health Resources tile (placeholder for future features)
    with col2:
        st.markdown("""
        <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; text-align: center;">
            <h2>Health Resources</h2>
            <p>Access helpful health information and resources</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Explore Resources", key="explore_resources", use_container_width=True):
            st.info("Health resources feature coming soon!")
    
    # Second row of tiles
    col3, col4 = st.columns(2)
    
    # Medical Records tile
    with col3:
        st.markdown("""
        <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; text-align: center;">
            <h2>My Medical Profile</h2>
            <p>Update and view your medical information</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("View Profile", key="view_profile", use_container_width=True):
            st.session_state['current_page'] = 'profile'
            st.rerun()
    
    # Appointment tile
    with col4:
        st.markdown("""
        <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; text-align: center;">
            <h2>Appointments</h2>
            <p>Schedule and manage your medical appointments</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Manage Appointments", key="manage_appointments", use_container_width=True):
            st.info("Appointment management feature coming soon!")
    
    # App information
    st.markdown("---")
    st.markdown("""
    ### About Swasthya AI
    
    Swasthya AI is your personal health assistant, providing health advice tailored to your medical conditions. 
    Our AI-powered chatbot offers personalized guidance while respecting your privacy.
    
    *Note: This application is for informational purposes only and is not a substitute for professional medical advice.*
    """)