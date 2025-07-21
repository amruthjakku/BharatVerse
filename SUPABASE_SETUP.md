# 🗄️ Supabase Database Setup for BharatVerse

## 📋 Quick Setup Guide

### Step 1: Get Your Supabase Credentials

1. **Go to your Supabase project dashboard**
2. **Navigate to**: Settings → Database
3. **Copy the following information**:
   - **Host**: `your-project-ref.supabase.co`
   - **Database**: `postgres`
   - **User**: `postgres`
   - **Password**: Your database password

### Step 2: Add Configuration to Secrets

Add this to your `.streamlit/secrets.toml` file:

```toml
# 🗄️ Supabase Database Configuration
[postgres]
host = "your-project-ref.supabase.co"
port = 5432
database = "postgres"
user = "postgres"
password = "your-database-password"
```

### Step 3: Create Tables

Run one of these commands:

```bash
# Option 1: Interactive setup
python setup_supabase_config.py

# Option 2: Direct table creation (after adding config)
python create_supabase_tables.py
```

## 🏗️ Tables That Will Be Created

### 1. **users** - User accounts and profiles
```sql
- id (Primary Key)
- username (Unique)
- email (Unique)
- full_name
- avatar_url
- provider (gitlab, email, etc.)
- role (user, admin)
- created_at, updated_at
```

### 2. **contributions** - All user contributions
```sql
- id (Primary Key)
- user_id (Foreign Key)
- title
- content (Text stories, proverbs, etc.)
- content_type (text, proverb, audio, etc.)
- language
- region
- tags (Array)
- metadata (JSON)
- ai_analysis (JSON)
- created_at, updated_at
```

### 3. **analytics** - User activity tracking
```sql
- id (Primary Key)
- user_id (Foreign Key)
- event_type
- event_data (JSON)
- created_at
```

### 4. **community_interactions** - Likes, comments, etc.
```sql
- id (Primary Key)
- user_id (Foreign Key)
- contribution_id (Foreign Key)
- interaction_type
- content
- created_at
```

## 🔍 Verification

After setup, you should see these tables in your Supabase dashboard:
- ✅ users
- ✅ contributions  
- ✅ analytics
- ✅ community_interactions

## 🚀 What Happens Next

Once tables are created:

1. **Text submissions** → Stored directly in `contributions` table
2. **User registration** → Stored in `users` table
3. **Activity tracking** → Logged in `analytics` table
4. **Community features** → Tracked in `community_interactions` table

## 🔧 Troubleshooting

### Connection Issues
- ✅ Check your project URL is correct
- ✅ Verify database password
- ✅ Ensure Supabase project is active
- ✅ Check firewall/network settings

### Table Creation Issues
- ✅ Verify you have database permissions
- ✅ Check for syntax errors in SQL
- ✅ Ensure psycopg2 is installed: `pip install psycopg2-binary`

### App Integration Issues
- ✅ Restart Streamlit app after adding secrets
- ✅ Check secrets.toml syntax
- ✅ Verify import paths in code

## 📱 Testing

After setup, test by:

1. **Running your Streamlit app**
2. **Logging in with GitLab**
3. **Submitting a text story**
4. **Checking Supabase dashboard** for new data

## 🎯 Expected Results

- **Text stories** appear in `contributions` table
- **User data** appears in `users` table  
- **Activity logs** appear in `analytics` table
- **Browse page** shows contributions from Supabase
- **Analytics** display real-time data from cloud

## 🆘 Need Help?

If you encounter issues:

1. **Check the console** for error messages
2. **Verify your secrets.toml** configuration
3. **Test connection** with the setup script
4. **Check Supabase logs** in your dashboard

---

**Once setup is complete, all text operations will use Supabase directly!** 🚀