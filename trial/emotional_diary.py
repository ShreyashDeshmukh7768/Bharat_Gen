# emotional_diary.py

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
import streamlit as st
from database import SupabaseClient
import time
import json


def initialize_llm():
    """Initialize the language model"""
    return Ollama(model="tinyllama")


def get_prompt_template():
    """Get the chat prompt template for emotional diary"""
    return ChatPromptTemplate.from_messages(
        [
            ("system", "You are an empathetic listener and emotional support AI. "
                      "Your goal is to help the user process their emotions by providing supportive, "
                      "non-judgmental responses. Acknowledge their feelings, offer gentle insights, "
                      "and suggest healthy coping mechanisms when appropriate. "
                      "Keep your responses warm and conversational. "
                      "Try to identify the user's emotional state from their entry."),
            ("user", "Previous conversation context: {conversation_context}. Diary entry: {entry}")
        ]
    )


def analyze_emotion(entry):
    """Analyze the emotion in the diary entry"""
    # Use the same LLM to analyze the emotion
    llm = initialize_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Analyze the following diary entry and identify the primary emotion expressed. "
                  "Respond with just one word that best describes the emotion (e.g., happy, sad, angry, "
                  "anxious, confused, hopeful, grateful, excited, worried, tired, frustrated, overwhelmed, "
                  "calm, peaceful, content, neutral, etc.). Be precise and avoid general terms."),
        ("user", f"{entry}")
    ])
    emotion_chain = prompt | llm | StrOutputParser()
    emotion = emotion_chain.invoke({})
    
    # Clean up the response (in case the LLM provides more than just the emotion word)
    emotion = emotion.strip().lower()
    # Get just the first word as the emotion
    emotion = emotion.split()[0] if emotion else "neutral"
    
    return emotion
    emotion = emotion.split()[0] if emotion else "unknown"
    
    return emotion


def get_conversation_context(conversation_history, max_context=3):
    """Format the recent conversation history as context"""
    if not conversation_history:
        return "No previous context"

    # Get last few interactions to use as context
    recent_history = conversation_history[-max_context:]
    context_text = ""

    for entry in recent_history:
        context_text += f"User entry: {entry['entry']}\nAssistant response: {entry['response']}\n\n"

    return context_text


def process_diary_entry(entry, user_id):
    """Process the diary entry and get a response from the language model"""
    # Initialize diary history in session state if not present
    if "diary_messages" not in st.session_state:
        st.session_state.diary_messages = []

    # Get conversation context from database
    db = SupabaseClient()
    conversation_history = db.get_emotional_diary_history(user_id)
    conversation_context = get_conversation_context(conversation_history)

    # Setup the language model chain
    llm = initialize_llm()
    prompt = get_prompt_template()
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser

    # Get response
    response = chain.invoke({
        "entry": entry,
        "conversation_context": conversation_context
    })
    
    # Analyze the emotion in the entry
    mood = analyze_emotion(entry)
    
    # Create JSON data (includes both entry and response)
    json_data = {
        "entry": entry,
        "response": response,
        "mood": mood,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    # Save the diary entry to the database
    db.save_emotional_diary_entry(user_id, entry, response, mood, json.dumps(json_data))

    # Add to session state for immediate display
    st.session_state.diary_messages.append({"role": "user", "content": entry})
    st.session_state.diary_messages.append({"role": "assistant", "content": response})

    return response, mood


def display_diary_interface():
    """Display an interactive emotional diary interface"""
    # Initialize diary history in session state if not present
    if "diary_messages" not in st.session_state:
        st.session_state.diary_messages = []

    # Display diary messages
    for message in st.session_state.diary_messages:
        if message["role"] == "user":
            st.chat_message("user", avatar="📝").write(message["content"])
        else:
            st.chat_message("assistant", avatar="🧠").write(message["content"])

    # Diary entry input
    if entry := st.chat_input("Write your thoughts and feelings here..."):
        # Add user message to chat
        st.chat_message("user", avatar="📝").write(entry)

        # Show thinking animation
        with st.chat_message("assistant", avatar="🧠"):
            thinking_placeholder = st.empty()
            for i in range(3):
                thinking_placeholder.write("Thinking" + "." * (i + 1))
                time.sleep(0.3)

            # Process the entry
            with st.spinner(""):
                response, mood = process_diary_entry(entry, st.session_state['user_id'])

            # Replace thinking animation with response
            thinking_placeholder.write(response)


def load_diary_history(user_id):
    """Load diary history from database into session state"""
    if "diary_messages" not in st.session_state:
        st.session_state.diary_messages = []

        # Get diary history from database
        db = SupabaseClient()
        diary_history = db.get_emotional_diary_history(user_id)

        if diary_history:
            for entry in diary_history:
                st.session_state.diary_messages.append({"role": "user", "content": entry['entry']})
                st.session_state.diary_messages.append({"role": "assistant", "content": entry['response']})


def display_diary_history(user_id):
    """Display the user's diary history as expandable sections"""
    db = SupabaseClient()
    diary_history = db.get_emotional_diary_history(user_id)

    if not diary_history:
        st.info("No previous diary entries found.")
        return

    st.subheader("Diary History")
    
    # Group by date (assuming created_at is in string format)
    entries_by_date = {}
    for entry in diary_history:
        # Extract date part from timestamp
        date_str = entry['created_at'].split('T')[0] if 'T' in entry['created_at'] else entry['created_at'].split(' ')[0]
        if date_str not in entries_by_date:
            entries_by_date[date_str] = []
        entries_by_date[date_str].append(entry)
    
    # Show entries grouped by date
    for date_str in sorted(entries_by_date.keys(), reverse=True):
        with st.expander(f"Entries from {date_str}", expanded=False):
            for entry in entries_by_date[date_str]:
                mood_emoji = get_mood_emoji(entry.get('mood', ''))
                st.markdown(f"### {mood_emoji} Entry at {entry['created_at'].split('T')[1].split('.')[0] if 'T' in entry['created_at'] else entry['created_at'].split(' ')[1]}")
                st.markdown("**Your entry:**")
                st.write(entry['entry'])
                st.markdown("**Response:**")
                st.write(entry['response'])
                st.markdown("---")


def get_mood_emoji(mood):
    """Return emoji based on mood"""
    mood_map = {
        "happy": "😊",
        "sad": "😢",
        "angry": "😠",
        "anxious": "😰",
        "calm": "😌",
        "excited": "😃",
        "neutral": "😐",
        "confused": "😕",
        "stressed": "😫",
        "grateful": "🙏",
        "hopeful": "🌟",
        "tired": "😴",
        "worried": "😟",
        "content": "😌",
        "frustrated": "😤",
        "overwhelmed": "😩",
        "peaceful": "☮️",
        "proud": "🥲",
        "disappointed": "😞",
        "lonely": "🥺"
    }
    
    # Default emoji if mood not found
    return mood_map.get(mood.lower(), "📝")