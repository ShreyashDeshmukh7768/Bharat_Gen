import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SupabaseClient:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("Missing Supabase URL or key. Add them to your .env file.")
        self.client = create_client(url, key)

    def create_user(self, user_data):
        """Insert user personal info into the users table"""
        try:
            response = self.client.table('users').insert({
                'email': user_data['email'],
                'password_hash': user_data['password_hash'],
                'full_name': user_data['full_name'],
                'age': user_data['age'],
                'gender': user_data['gender'],
                'contact_no': user_data['contact_no']
            }).execute()

            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    def create_medical_info(self, user_id, conditions):
        """Insert user medical conditions into the medical_info table"""
        try:
            # Insert standard conditions
            for condition_name, has_condition in conditions['standard'].items():
                if has_condition:
                    self.client.table('medical_info').insert({
                        'user_id': user_id,
                        'condition_name': condition_name,
                        'condition_type': 'standard'
                    }).execute()

            # Insert custom conditions
            for condition in conditions['custom']:
                if condition.strip():  # Only insert non-empty conditions
                    self.client.table('medical_info').insert({
                        'user_id': user_id,
                        'condition_name': condition,
                        'condition_type': 'custom'
                    }).execute()

            return True
        except Exception as e:
            print(f"Error creating medical info: {e}")
            return False

    def get_user_by_email(self, email):
        """Retrieve user by email for login"""
        try:
            response = self.client.table('users').select('*').eq('email', email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None

    def get_user_by_id(self, user_id):
        """Retrieve user by ID for profile display/update"""
        try:
            response = self.client.table('users').select('*').eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None

    def update_user(self, user_id, update_data):
        """Update user information"""
        try:
            response = self.client.table('users').update(update_data).eq('id', user_id).execute()
            return True if response.data else False
        except Exception as e:
            print(f"Error updating user: {e}")
            return False

    def update_medical_info(self, user_id, conditions):
        """Update user medical conditions"""
        try:
            # First delete all existing conditions
            self.client.table('medical_info').delete().eq('user_id', user_id).execute()
            
            # Then create new ones
            self.create_medical_info(user_id, conditions)
            return True
        except Exception as e:
            print(f"Error updating medical info: {e}")
            return False

    def get_user_medical_info(self, user_id):
        """Retrieve user medical conditions"""
        try:
            response = self.client.table('medical_info').select('*').eq('user_id', user_id).execute()
            return response.data
        except Exception as e:
            print(f"Error getting medical info: {e}")
            return []

    def save_chat(self, user_id, question, answer):
        """Save chat history for a user"""
        try:
            response = self.client.table('chat_history').insert({
                'user_id': user_id,
                'question': question,
                'answer': answer,
            }).execute()
            return True
        except Exception as e:
            print(f"Error saving chat: {e}")
            return False

    def get_chat_history(self, user_id):
        """Retrieve chat history for a user"""
        try:
            response = self.client.table('chat_history').select('*').eq('user_id', user_id).order('created_at',
                                                                                                  desc=False).execute()
            return response.data
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []