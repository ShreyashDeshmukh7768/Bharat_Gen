# Medical Assistant Chatbot

A personalized medical assistant built with Streamlit, LangChain, and Supabase. This application provides users with health-related information based on their medical conditions and stores chat history for future reference.

## Features

- *User Authentication*: Registration and login system
- *Medical Profile*: Users can store standard and custom medical conditions
- *Personalized AI Responses*: Tailors answers based on user's medical information
- *Chat History*: Saves conversations for future reference
- *Session Management*: Retains user data across sessions

## Demo

![Medical Assistant Chatbot Demo](https://via.placeholder.com/800x450.png?text=Medical+Assistant+Chatbot)

## Technology Stack

- *Frontend & Backend*: Streamlit
- *AI/ML*: LangChain with Mistral model
- *Database*: Supabase
- *Authentication*: Custom implementation with bcrypt
- *Environment Management*: python-dotenv

## Installation

### Prerequisites

- Python 3.8+
- Supabase account
- LangChain API key

### Setup

1. *Clone the repository*

bash
git clone https://github.com/yourusername/medical-assistant-chatbot.git
cd medical-assistant-chatbot


2. *Create a virtual environment and install dependencies*

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt


3. *Set up environment variables*

Copy the example environment file and fill in your credentials:

bash
cp .env-example .env


Edit .env with your Supabase URL, key, and LangChain API key:


LANGCHAIN_API_KEY="your_langchain_api_key"
LANGCHAIN_PROJECT="Project1"
SUPABASE_URL="your_supabase_url"
SUPABASE_KEY="your_supabase_key"


4. *Set up Supabase database*

Execute the SQL script in your Supabase SQL Editor:

sql
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

-- Create indices for faster queries
CREATE INDEX idx_medical_info_user_id ON medical_info(user_id);
CREATE INDEX idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX idx_chat_history_created_at ON chat_history(created_at);

-- Disable Row Level Security if using app authentication
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE medical_info DISABLE ROW LEVEL SECURITY;
ALTER TABLE chat_history DISABLE ROW LEVEL SECURITY;


## Usage

1. *Run the application*

bash
streamlit run app.py


2. *Register a new account* with your personal and medical information

3. *Login* with your email and password

4. *Ask health-related questions* and get personalized responses

5. *View your chat history* for future reference

## Project Structure


medical-assistant-chatbot/
├── app.py                 # Main Streamlit application
├── auth.py                # Authentication functions
├── chat.py                # LLM chat functionality
├── database.py            # Supabase database operations
├── debug_view_tables.py   # Debug utility for database
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .env-example           # Example environment variables
└── README.md              # This file


## Customization

### Changing the Language Model

To use a different language model:

1. Open chat.py
2. Modify the initialize_llm() function:

python
def initialize_llm():
    # Use OpenAI instead of Ollama
    return ChatOpenAI(model_name="gpt-3.5-turbo")


### Adding More Medical Conditions

To add more standard medical conditions:

1. Update the form in auth.py with additional checkboxes
2. Update the medical conditions dictionary in the registration function

## Troubleshooting

### Database Connection Issues

If you experience connection issues with Supabase:

1. Check that your environment variables are correctly set
2. Ensure your Supabase project is active
3. Verify that the tables were created correctly
4. Try enabling the debug view with the checkbox in the sidebar

### Authentication Problems

If users can't register or log in:

1. Make sure RLS is disabled on the tables
2. Check the console for error messages
3. Verify that bcrypt is installed correctly

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Streamlit](https://streamlit.io/) for the web framework
- [LangChain](https://langchain.com/) for the language model interface
- [Supabase](https://supabase.com/) for the database backend
- [Mistral AI](https://mistral.ai/) for the language model