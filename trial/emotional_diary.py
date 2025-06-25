from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import streamlit as st
from database import SupabaseClient
import time
import json


@st.cache_resource(show_spinner="Loading AI model...")
def initialize_llm():
    """Initialize and cache the language model"""
    return Ollama(model="tinyllama", temperature=0.5)


def get_prompt_template():
    """Get the chat prompt template for emotional diary"""
    return ChatPromptTemplate.from_messages([
        ("system", "You are an empathetic listener and emotional support AI. "
                   "Your goal is to help the user process their emotions by providing supportive, "
                   "non-judgmental responses. Acknowledge their feelings, offer gentle insights, "
                   "and suggest healthy coping mechanisms when appropriate. "
                   "Keep your responses warm and conversational. "
                   "Try to identify the user's emotional state from their entry."),
        ("user", "Previous conversation context: {conversation_context}. Diary entry: {entry}")
    ])


def analyze_emotion(llm, entry):
    """Analyze the emotion in the diary entry"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Analyze the following diary entry and identify the primary emotion expressed. "
                   "Respond with just one word that best describes the emotion (e.g., happy, sad, angry, "
                   "anxious, confused, hopeful, grateful, excited, worried, tired, frustrated, overwhelmed, "
                   "calm, peaceful, content, neutral, etc.). Be precise and avoid general terms."),
        ("user", "{entry}")
    ])
    chain = prompt | llm | StrOutputParser()
    try:
        emotion = chain.invoke({"entry": entry}).strip().lower()
        return emotion.split()[0] if emotion else "neutral"
    except Exception:
        return "neutral"


def get_conversation_context(conversation_history, max_context=3):
    """Format the recent conversation history as context"""
    if not conversation_history:
        return "No previous context"
    recent_history = conversation_history[-max_context:]
    return "\n".join([
        f"User entry: {e['entry']}\nAssistant response: {e['response']}\n"
        for e in recent_history
    ])


def process_diary_entry(entry, user_id):
    """Process the diary entry and get a response from the language model"""
    llm = initialize_llm()
    db = SupabaseClient()

    # Get past conversation context
    conversation_history = db.get_emotional_diary_history(user_id)
    conversation_context = get_conversation_context(conversation_history)

    # Set up the main response chain
    prompt = get_prompt_template()
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser

    # Generate the assistant response
    response = chain.invoke({
        "entry": entry,
        "conversation_context": conversation_context
    })

    # Analyze emotional tone
    mood = analyze_emotion(llm, entry)

    # Prepare and save the response
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    json_data = {
        "entry": entry,
        "response": response,
        "mood": mood,
        "timestamp": timestamp
    }

    db.save_emotional_diary_entry(user_id, entry, response, mood, json.dumps(json_data))

    # Update session state
    st.session_state.diary_messages.append({"role": "user", "content": entry})
    st.session_state.diary_messages.append({"role": "assistant", "content": response})

    return response, mood


def display_diary_interface():
    """Display the interactive diary interface"""
    if "diary_messages" not in st.session_state:
        st.session_state.diary_messages = []

    # Show chat history
    for msg in st.session_state.diary_messages:
        avatar = "📝" if msg["role"] == "user" else "🧠"
        st.chat_message(msg["role"], avatar=avatar).write(msg["content"])

    # User input
    if entry := st.chat_input("Write your thoughts and feelings here..."):
        st.chat_message("user", avatar="📝").write(entry)
        with st.chat_message("assistant", avatar="🧠"):
            thinking = st.empty()
            for i in range(3):
                thinking.write("Thinking" + "." * (i + 1))
                time.sleep(0.3)

            with st.spinner("Processing..."):
                response, mood = process_diary_entry(entry, st.session_state['user_id'])
            thinking.write(response)


def load_diary_history(user_id):
    """Load diary history from database into session state"""
    if "diary_messages" not in st.session_state:
        st.session_state.diary_messages = []

        db = SupabaseClient()
        history = db.get_emotional_diary_history(user_id)
        if history:
            for e in history:
                st.session_state.diary_messages.append({"role": "user", "content": e['entry']})
                st.session_state.diary_messages.append({"role": "assistant", "content": e['response']})


def display_diary_history(user_id):
    """Show diary entries grouped by date"""
    db = SupabaseClient()
    history = db.get_emotional_diary_history(user_id)

    if not history:
        st.info("No previous diary entries found.")
        return

    st.subheader("📘 Diary History")

    entries_by_date = {}
    for e in history:
        date_str = e.get('created_at', '').split('T')[0] or e.get('created_at', '').split(' ')[0]
        entries_by_date.setdefault(date_str, []).append(e)

    for date_str in sorted(entries_by_date.keys(), reverse=True):
        with st.expander(f"Entries from {date_str}", expanded=False):
            for e in entries_by_date[date_str]:
                time_str = e.get('created_at', '').split('T')[1].split('.')[0] if 'T' in e.get('created_at', '') else e.get('created_at', '').split(' ')[1]
                mood_emoji = get_mood_emoji(e.get('mood', ''))
                st.markdown(f"### {mood_emoji} Entry at {time_str}")
                st.markdown("*Your entry:*")
                st.write(e['entry'])
                st.markdown("*Response:*")
                st.write(e['response'])
                st.markdown("---")


def get_mood_emoji(mood):
    """Convert mood to emoji"""
    mood_map = {
        "happy": "😊", "sad": "😢", "angry": "😠", "anxious": "😰",
        "calm": "😌", "excited": "😃", "neutral": "😐", "confused": "😕",
        "stressed": "😫", "grateful": "🙏", "hopeful": "🌟", "tired": "😴",
        "worried": "😟", "content": "😌", "frustrated": "😤", "overwhelmed": "😩",
        "peaceful": "☮", "proud": "🥲", "disappointed": "😞", "lonely": "🥺"
    }
    return mood_map.get(mood.lower(), "📝")