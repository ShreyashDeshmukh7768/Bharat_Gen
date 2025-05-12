# -- Users Table
# CREATE TABLE users (
#   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#   email VARCHAR NOT NULL UNIQUE,
#   password_hash VARCHAR NOT NULL,
#   full_name VARCHAR NOT NULL,
#   age INT NOT NULL,
#   gender VARCHAR NOT NULL,
#   contact_no VARCHAR NOT NULL,
#   created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
# );
#
# -- Medical Information Table
# CREATE TABLE medical_info (
#   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#   user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
#   condition_name VARCHAR NOT NULL,
#   condition_type VARCHAR NOT NULL, -- 'standard' or 'custom'
#   created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
# );
#
# -- Chat History Table
# CREATE TABLE chat_history (
#   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#   user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
#   question TEXT NOT NULL,
#   answer TEXT NOT NULL,
#   created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
# );
#
# -- Create indices for faster queries
# CREATE INDEX idx_medical_info_user_id ON medical_info(user_id);
# CREATE INDEX idx_chat_history_user_id ON chat_history(user_id);
# CREATE INDEX idx_chat_history_created_at ON chat_history(created_at);
#
# -- Row Level Security Policies (Optional but recommended)
# -- Enable RLS on tables
# ALTER TABLE users ENABLE ROW LEVEL SECURITY;
# ALTER TABLE medical_info ENABLE ROW LEVEL SECURITY;
# ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;
#
# -- Since your app handles authentication at the application level,
# -- you may not need complex RLS policies. Here are simple ones if needed:
#
# -- Users can only see their own data
# CREATE POLICY users_policy ON users
#   FOR ALL
#   USING (auth.uid() = id);
#
# -- Users can only see their own medical information
# CREATE POLICY medical_info_policy ON medical_info
#   FOR ALL
#   USING (auth.uid() = user_id);
#
# -- Users can only see their own chat history
# CREATE POLICY chat_history_policy ON chat_history
#   FOR ALL
#   USING (auth.uid() = user_id);
#
# -- Note: If you're not using Supabase Auth and handling authentication in your app,
# -- you may want to disable RLS or create service role policies instead.
# -- In that case, comment out the above policies and use:
#
# -- DISABLE RLS ALTERNATIVE:
# -- ALTER TABLE users DISABLE ROW LEVEL SECURITY;
# -- ALTER TABLE medical_info DISABLE ROW LEVEL SECURITY;
# -- ALTER TABLE chat_history DISABLE ROW LEVEL SECURITY;
#
#
# -- Disable Row Level Security on all tables
# ALTER TABLE users DISABLE ROW LEVEL SECURITY;
# ALTER TABLE medical_info DISABLE ROW LEVEL SECURITY;
# ALTER TABLE chat_history DISABLE ROW LEVEL SECURITY;
#
# -- Drop any existing policies if they exist
# DROP POLICY IF EXISTS users_policy ON users;
# DROP POLICY IF EXISTS medical_info_policy ON medical_info;
# DROP POLICY IF EXISTS chat_history_policy ON chat_history;
#
#
#
# SELECT * FROM user;