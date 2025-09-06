# 🩺 Swasthya-AI

A comprehensive **Medical Assistant** application built with **Streamlit**, **LangChain**, and **Supabase** that provides personalized health information, manages medical profiles, and offers emotional support through AI-powered conversations.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-latest-red.svg)
![LangChain](https://img.shields.io/badge/langchain-latest-green.svg)
![Supabase](https://img.shields.io/badge/supabase-latest-orange.svg)


## 🚀 Features

### 🤖 Medical Assistant Chatbot
- 🔐 **User Authentication** – Registration and login system  
- 🧾 **Medical Profile** – Store standard and custom medical conditions  
- 💬 **Personalized AI Responses** – Tailors answers based on your health profile  
- 💾 **Chat History** – Save and revisit past conversations  
- 🔄 **Session Management** – Retains user data across sessions  

### 📝 Emotional Support Diary
- 🧠 **Mood Tracking** – Record emotions and daily thoughts  
- 🤝 **Empathetic AI Responses** – Provides supportive and therapeutic guidance  
- 💬 **Conversation History** – Save diary entries for future reference  

### 📜 Prescription OCR
- 📷 **Prescription Digitization** – Extract medicines and details from handwritten prescriptions  
- 💊 **Generic Alternatives** – Suggest affordable substitutes for prescribed medicines  
- ✅ **Validation** – Verify extracted data against a structured database  

---

## 🎥 Demo

👉 *Coming soon: Swasthya-AI Demo*

---
## 🎥 Demo

*Demo video and screenshots coming soon*

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Frontend & Backend** | Streamlit |
| **AI/ML Framework** | LangChain with Mistral AI |
| **Database** | Supabase (PostgreSQL) |
| **Authentication** | bcrypt + custom implementation |
| **OCR Engine** | Tesseract OCR |
| **Environment Management** | python-dotenv |

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Supabase account and project
- LangChain API key
- Tesseract OCR installed on your system

### Step-by-Step Setup

#### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/medical-assistant-chatbot.git
cd medical-assistant-chatbot
```

#### 2️⃣ Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3️⃣ Environment Configuration
```bash
# Copy example environment file
cp .env-example .env
```

Edit the `.env` file with your credentials:
```env
LANGCHAIN_API_KEY="your_langchain_api_key_here"
LANGCHAIN_PROJECT="Medical_Assistant_Project"
SUPABASE_URL="your_supabase_project_url"
SUPABASE_KEY="your_supabase_anon_key"
```

#### 4️⃣ Database Setup
Run the following SQL commands in your Supabase SQL Editor:

```sql
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

-- Create Performance Indexes
CREATE INDEX idx_medical_info_user_id ON medical_info(user_id);
CREATE INDEX idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX idx_chat_history_created_at ON chat_history(created_at);

-- Disable Row Level Security (for app-level authentication)
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE medical_info DISABLE ROW LEVEL SECURITY;
ALTER TABLE chat_history DISABLE ROW LEVEL SECURITY;
```

#### 5️⃣ Install Tesseract OCR
**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Add installation path to system PATH

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install tesseract-ocr
```

## 🚀 Usage

### Running the Application
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

### Getting Started
1. **Registration**: Create a new account with personal and medical information
2. **Login**: Access your personalized dashboard
3. **Medical Consultation**: Ask health-related questions for tailored responses
4. **Prescription OCR**: Upload prescription images to extract medication details
5. **Emotional Diary**: Write diary entries and receive supportive AI feedback
6. **History Review**: Access your previous conversations and insights

## 📁 Project Structure

```
medical-assistant-chatbot/
├── 📄 app.py                   # Main Streamlit application
├── 🔐 auth.py                  # User authentication & registration
├── 💬 chat.py                  # LLM integration & chat logic
├── 🗄️  database.py             # Supabase database operations
├── 📷 ocr.py                   # OCR & NER for prescriptions
├── 📝 diary.py                 # Emotional support diary
├── 🔧 debug_view_tables.py     # Database debugging utility
├── 📋 requirements.txt         # Python dependencies
├── ⚙️  .env                    # Environment variables (create from example)
├── 📄 .env-example             # Environment template
└── 📖 README.md                # Project documentation
```

## 🎯 Customization

### Changing the Language Model
Edit `chat.py` to use different LLM providers:
```python
def initialize_llm():
    # OpenAI Example
    return ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
    
    # Anthropic Claude Example
    return ChatAnthropic(model_name="claude-3-sonnet-20240229")
```

### Adding Medical Conditions
Update the conditions in `auth.py`:
```python
conditions = {
    "Heart Disease": st.checkbox("Heart Disease"),
    "Diabetes": st.checkbox("Diabetes"),
    "Your New Condition": st.checkbox("Your New Condition"),
    # Add more conditions here
}
```

### Customizing UI Theme
Add custom CSS in `app.py`:
```python
st.markdown("""
<style>
    .main-header {
        color: #2E86AB;
        text-align: center;
        padding: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)
```

## 🐛 Troubleshooting

### Common Issues

**Database Connection Problems**
- ✅ Verify Supabase URL and key in `.env`
- ✅ Check if Supabase project is active
- ✅ Ensure all tables are created
- ✅ Run `python debug_view_tables.py` to verify data

**Authentication Errors**
- ✅ Confirm Row Level Security is disabled
- ✅ Check bcrypt installation: `pip install bcrypt`
- ✅ Verify password hashing in registration

**OCR Not Working**
- ✅ Install Tesseract OCR system-wide
- ✅ Add Tesseract to system PATH
- ✅ Test with: `tesseract --version`

### Getting Help
If you encounter issues:
1. Check the console output for error messages
2. Verify all environment variables are set correctly
3. Test database connectivity using the debug script
4. Open an issue with detailed error information

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute
- 🐛 **Bug Reports**: Report issues with detailed reproduction steps
- ✨ **Feature Requests**: Suggest new functionality
- 🔧 **Code Contributions**: Submit pull requests for improvements
- 📚 **Documentation**: Help improve documentation and examples
- 🧪 **Testing**: Add test cases and improve test coverage

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `python -m pytest`
5. Submit a pull request with a clear description

### Coding Guidelines
- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include unit tests for new features
- Update documentation as needed



*Empowering healthcare through AI-powered assistance*
