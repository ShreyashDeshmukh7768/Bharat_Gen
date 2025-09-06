Swasthya-AI

An AI-powered healthcare platform that combines medical guidance, emotional support, and prescription digitization into one unified system.

Project Overview

Swasthya-AI addresses critical gaps in healthcare accessibility and support through three integrated services:

🤖 Medical Assistant Chatbot

Personalized health guidance built with Streamlit, LangChain, and Supabase

Tailored responses based on stored medical conditions

Secure chat history for future reference

💬 Emotional Support Diary

Sentiment analysis using NLP models

Tracks user mood and provides empathetic, therapeutic responses

Supports text-based journaling with optional voice interaction

📜 Prescription OCR System

Digitizes handwritten prescriptions using Tesseract + OpenCV + PyMuPDF

Extracts medicine names and suggests generic, affordable alternatives

Validates prescriptions against a stored medicine database

Features

User Authentication: Registration & login system with bcrypt

Medical Profile: Store standard and custom medical conditions

Personalized AI Responses: Tailored answers based on user’s medical information

Chat History: Save and retrieve past conversations

Session Management: Retain user data across sessions

Emotional Diary: Real-time sentiment analysis & mood tracking

Prescription OCR: Extracts and validates medicines from handwritten prescriptions

Demo

📺 [Coming Soon] – Medical Assistant Chatbot & Emotional Diary Demo

Technology Stack

Frontend & Backend: Streamlit

AI/ML: LangChain with Mistral / GPT models

Database: Supabase

Authentication: Custom implementation with bcrypt

Environment Management: python-dotenv

Sentiment Analysis: PyTorch NLP model (GoEmotions-based)

OCR: Tesseract, OpenCV, PyMuPDF

Installation
Prerequisites

Python 3.8+

Supabase account

LangChain / OpenAI API key

Setup

Clone the repository

git clone https://github.com/yourusername/SwasthyaAi.git
cd SwasthyaAi


Create a virtual environment and install dependencies

python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt


Set up environment variables

cp .env-example .env


Edit .env with your credentials:

LANGCHAIN_API_KEY="your_langchain_api_key"
SUPABASE_URL="your_supabase_url"
SUPABASE_KEY="your_supabase_key"

Set up Supabase database

Execute the following SQL in your Supabase SQL Editor:

-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR NOT NULL UNIQUE,
    password_hash VARCHAR NOT NULL,
    full_name VARCHAR NOT NULL,
    age INT NOT NULL,
    gender VARCHAR NOT NULL,
    contact_no VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Medical Information Table
CREATE TABLE medical_info (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    condition_name VARCHAR NOT NULL,
    condition_type VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chat History Table
CREATE TABLE chat_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indices
CREATE INDEX idx_medical_info_user_id ON medical_info(user_id);
CREATE INDEX idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX idx_chat_history_created_at ON chat_history(created_at);

-- Disable RLS
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE medical_info DISABLE ROW LEVEL SECURITY;
ALTER TABLE chat_history DISABLE ROW LEVEL SECURITY;

Usage

Run the application:

streamlit run app.py


Register a new account with your medical & personal details

Log in with your credentials

Access the chatbot for health queries

Use the emotional diary for journaling & mood support

Upload prescriptions to digitize and check medicines

Project Structure
SwasthyaAi/
├── app.py                # Main Streamlit application
├── auth.py               # Authentication functions
├── chat.py               # Chatbot (LangChain + LLMs)
├── diary.py              # Emotional diary sentiment analysis
├── ocr.py                # Prescription OCR pipeline
├── database.py           # Supabase operations
├── debug_view_tables.py  # Debug utility
├── requirements.txt      # Dependencies
├── .env                  # Environment variables (ignored by git)
├── .env-example          # Example env file
└── README.md             # This file

Customization

Change LLM model → Edit initialize_llm() in chat.py

Add medical conditions → Update form in auth.py and dictionary in registration

Troubleshooting

Database Connection Issues

Check environment variables

Ensure Supabase project is running

Confirm SQL tables exist

Authentication Problems

Disable RLS on tables

Verify bcrypt installation

OCR Not Working

Ensure Tesseract is installed & added to PATH

Use clear, well-scanned prescription images

Contributing

Contributions are welcome! Please open a Pull Request.

License

This project is licensed under the MIT License.

Acknowledgements

Streamlit for the framework

LangChain & GPT/Mistral for LLMs

Supabase for database backend

Tesseract OCR & OpenCV for prescription recognition

PyTorch GoEmotions for sentiment analysis

🌿 Swasthya-AI: Making healthcare accessible, affordable, and supportive.
