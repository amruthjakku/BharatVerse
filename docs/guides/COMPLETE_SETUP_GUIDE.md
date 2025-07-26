# 🚀 BharatVerse Complete Setup Guide

## 📋 **What We'll Set Up**

| Service | Purpose | Free Tier | Setup Time |
|:---:|:---|:---:|:---:|
| 🤗 **HuggingFace** | AI/ML APIs | Unlimited free API calls | 2 mins |
| 🐘 **Supabase** | PostgreSQL Database | 500MB + 2GB bandwidth | 3 mins |
| ⚡ **Upstash** | Redis Cache | 10K requests/day | 2 mins |
| 🪣 **Cloudflare R2** | Object Storage | 10GB storage + 1M requests | 3 mins |
| 🌐 **Streamlit Cloud** | Frontend Hosting | Unlimited public apps | 2 mins |

**🎯 Total Setup Time: ~12 minutes**
**💰 Total Cost: $0/month**

---

## 1️⃣ **HuggingFace Setup (AI/ML APIs)**

### Step 1: Create Account
1. Go to [huggingface.co](https://huggingface.co)
2. Click **"Sign Up"**
3. Create account with email/GitHub

### Step 2: Get API Token
1. Click your profile picture → **"Settings"**
2. Click **"Access Tokens"** in left sidebar
3. Click **"New token"**
4. **Name**: `bharatverse-api`
5. **Role**: Select **"Read"**
6. Click **"Generate a token"**
7. **📝 COPY & SAVE**: `hf_xxxxxxxxxxxxxxxxxxxx`

✅ **Test the API:**
```bash
curl -X POST \
  "https://api-inference.huggingface.co/models/openai/whisper-base" \
  -H "Authorization: Bearer hf_your_token_here" \
  -H "Content-Type: application/json" \
  -d '{"inputs": "test"}'
```

---

## 2️⃣ **Supabase Setup (Database)**

### Step 1: Create Project
1. Go to [supabase.com](https://supabase.com)
2. Click **"Start your project"**
3. Sign up with GitHub (recommended)
4. Click **"New Project"**
5. **Name**: `bharatverse`
6. **Password**: Create strong password (save it!)
7. **Region**: Choose nearest to you
8. Click **"Create new project"** (takes ~2 mins)

### Step 2: Get Connection Details
1. In your project dashboard, click **"Settings"** (gear icon)
2. Click **"API"** in left sidebar
3. **📝 SAVE THESE VALUES**:
   ```
   Project URL: https://your-project-id.supabase.co
   API Key (anon/public): eyJhbGciOiJIUzI1NiIs...
   Service Role Key: eyJhbGciOiJIUzI1NiIs...
   ```

### Step 3: Get Database URL
1. Still in Settings, click **"Database"** 
2. Scroll to **"Connection string"**
3. Select **"URI"** tab
4. **📝 SAVE**: `postgresql://postgres:[password]@db.your-project-id.supabase.co:5432/postgres`
5. Replace `[password]` with the password you created

### Step 4: Create Tables
1. Click **"SQL Editor"** in left sidebar
2. Paste this SQL:
```sql
-- Create contributions table
CREATE TABLE contributions (
    id SERIAL PRIMARY KEY,
    user_id TEXT,
    content_type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    file_url TEXT,
    language TEXT,
    region TEXT,
    tags TEXT[],
    sentiment_score FLOAT,
    ai_analysis JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create analytics table
CREATE TABLE analytics (
    id SERIAL PRIMARY KEY,
    event_type TEXT NOT NULL,
    event_data JSONB,
    user_id TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_contributions_content_type ON contributions(content_type);
CREATE INDEX idx_contributions_language ON contributions(language);
CREATE INDEX idx_contributions_region ON contributions(region);
CREATE INDEX idx_contributions_created_at ON contributions(created_at);
CREATE INDEX idx_analytics_event_type ON analytics(event_type);
CREATE INDEX idx_analytics_timestamp ON analytics(timestamp);
```
3. Click **"Run"**

✅ **Test Connection:**
```bash
curl "https://your-project-id.supabase.co/rest/v1/contributions" \
  -H "apikey: your-anon-key" \
  -H "Content-Type: application/json"
```

---

## 3️⃣ **Upstash Setup (Redis Cache)**

### Step 1: Create Account
1. Go to [upstash.com](https://upstash.com)
2. Click **"Get Started for Free"**
3. Sign up with GitHub/Google

### Step 2: Create Database
1. Click **"Create database"**
2. **Name**: `bharatverse-cache`
3. **Type**: **Regional**
4. **Region**: Choose nearest to you
5. **Eviction**: **allkeys-lru** (recommended)
6. Click **"Create"**

### Step 3: Get Connection Details
1. Click on your database name
2. Scroll to **"REST API"** section
3. **📝 SAVE THESE VALUES**:
   ```
   UPSTASH_REDIS_REST_URL: https://your-db-id.upstash.io
   UPSTASH_REDIS_REST_TOKEN: your-rest-token-here
   ```

✅ **Test Connection:**
```bash
curl https://your-db-id.upstash.io/set/test/hello \
  -H "Authorization: Bearer your-rest-token"
```

---

## 4️⃣ **Cloudflare R2 Setup (Object Storage)**

### Step 1: Create Account
1. Go to [cloudflare.com](https://cloudflare.com)
2. Click **"Sign up"**
3. Create account with email

### Step 2: Create R2 Bucket
1. In dashboard, click **"R2 Object Storage"** in left sidebar
2. Click **"Create bucket"**
3. **Name**: `bharatverse-files` (must be unique)
4. **Location**: Choose nearest to you
5. Click **"Create bucket"**

### Step 3: Create API Token
1. Click **"Manage R2 API tokens"**
2. Click **"Create API token"**
3. **Token name**: `bharatverse-api`
4. **Permissions**: 
   - ✅ **Object Read**
   - ✅ **Object Write**
5. **Bucket**: Select your bucket or **All buckets**
6. Click **"Create API token"**
7. **📝 SAVE THESE VALUES**:
   ```
   Access Key ID: your-access-key-id
   Secret Access Key: your-secret-key
   Endpoint URL: https://your-account-id.r2.cloudflarestorage.com
   ```

### Step 4: Configure Bucket Settings
1. Go back to your bucket
2. Click **"Settings"** tab
3. Under **"Public access"**, click **"Allow access"** (for public file serving)
4. **📝 SAVE**: `Public URL: https://pub-your-id.r2.dev`

✅ **Test Upload:**
```bash
# Using AWS CLI (install: pip install awscli)
aws s3 cp test.txt s3://bharatverse-files/ \
  --endpoint-url https://your-account-id.r2.cloudflarestorage.com \
  --profile r2
```

---

## 5️⃣ **GitHub Setup (Code Repository)**

### Step 1: Create Repository
1. Go to [github.com](https://github.com)
2. Click **"+"** → **"New repository"**
3. **Name**: `bharatverse`
4. **Description**: `AI-Powered Cultural Heritage Platform`
5. ✅ **Public**
6. ✅ **Add README**
7. Click **"Create repository"**

### Step 2: Push Your Code
```bash
cd /Users/jakkuamruth/Documents/hackathon/bharatverse

# Initialize git (if not already done)
git init
git remote add origin https://github.com/YOUR_USERNAME/bharatverse.git

# Add all files
git add .
git commit -m "Initial commit: BharatVerse AI-Powered Cultural Platform"

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## 6️⃣ **Configure Secrets File**

Create your local secrets file with all the credentials you collected: