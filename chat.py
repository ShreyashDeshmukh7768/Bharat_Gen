from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
import streamlit as st
from database import SupabaseClient


def initialize_llm():
    """Initialize the language model"""
    return Ollama(model="mistral")


def get_prompt_template():
    """Get the chat prompt template"""
    return ChatPromptTemplate.from_messages(
        [
            ("system", "Provide a detailed answer to the question, mention the steps in points. "
                       "Consider the user's medical conditions when relevant."),
            ("user", "User has the following medical conditions: {medical_conditions}. Question: {question}")
        ]
    )


def format_medical_conditions(user_id):
    """Get user's medical conditions as a formatted string"""
    db = SupabaseClient()
    medical_info = db.get_user_medical_info(user_id)

    if not medical_info:
        return "None specified"

    conditions = [info['condition_name'] for info in medical_info]
    return ", ".join(conditions)


def process_query(question, user_id):
    """Process the user query and get a response from the language model"""
    # Get user's medical conditions
    medical_conditions = format_medical_conditions(user_id)

    # Setup the language model chain
    llm = initialize_llm()
    prompt = get_prompt_template()
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser

    # Get response
    response = chain.invoke({
        "question": question,
        "medical_conditions": medical_conditions
    })

    # Save the chat to the database
    db = SupabaseClient()
    db.save_chat(user_id, question, response)

    return response


def display_chat_history(user_id):
    """Display the user's chat history"""
    db = SupabaseClient()
    chat_history = db.get_chat_history(user_id)

    if not chat_history:
        st.info("No previous chats found.")
        return

    st.subheader("Chat History")

    for chat in chat_history:
        with st.expander(f"Q: {chat['question'][:50]}...", expanded=False):
            st.write("*Question:*")
            st.write(chat['question'])
            st.write("*Answer:*")
            st.write(chat['answer'])