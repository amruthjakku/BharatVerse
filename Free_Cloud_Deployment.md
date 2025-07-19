# 🌐 BharatVerse – Free-Tier Scalable AI Web App

> A production-ready architecture using **100% free-tier services** to deploy a powerful AI-powered Streamlit application backed by PostgreSQL, Redis, Object Storage, and Model Inference APIs.

            [🧑‍💻 User]
                |
        [🌐 Streamlit Cloud]
                |
     ┌────────────┬──────────────┬───────────────────┬───────────────────┐
     |            |              |                   |                   |
[🔮 Inference API]  [🐘 Supabase]   [⚡ Upstash Redis]     [🪣 R2 or MinIO]
(RunPod/HF Space)   (PostgreSQL)       (Cache)             (Storage)

✅ Tech Stack
Component	Service	Tier	Purpose
Frontend	Streamlit Cloud	Free	User interface & interaction
Inference API	Hugging Face Spaces / RunPod	Free	AI model inference via REST API
Database	Supabase	Free Tier (500MB)	Stores user data, logs, metadata
Cache	Upstash Redis	Free Tier (1GB)	Stores temporary/session data
Object Storage	Cloudflare R2	Free Tier (10GB)	Uploads, model outputs, media
🚀 Features
* ✅ Host large models via API (up to 47GB via RunPod or optimized HF Space)
* ✅ Scalable and modular backend
* ✅ Modern Streamlit frontend (cloud hosted)
* ✅ Full object upload/download from Cloudflare R2
* ✅ PostgreSQL support via Supabase (for structured data)
* ✅ Redis caching with Upstash
* ✅ Fully open source and serverless-friendly

🧱 Setup Instructions

## Prerequisites
1. **GitHub Account** (for code repository)
2. **Free service accounts**:
   - Streamlit Cloud (streamlit.io)
   - Supabase (supabase.com) 
   - Upstash Redis (upstash.com)
   - Cloudflare R2 (cloudflare.com)
   - Hugging Face (huggingface.co)

## 1. 🌐 Frontend Setup (Streamlit Cloud)

### Step 1.1: Prepare Repository
```bash
# Clone/fork the BharatVerse repository
git clone https://github.com/YOUR_USERNAME/bharatverse.git
cd bharatverse

# Run the setup script
python scripts/setup_free_cloud.py
```

### Step 1.2: Deploy to Streamlit Cloud
1. Push code to GitHub
2. Go to [https://share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app" → Select repository
5. Set **Main file path**: `Home.py`
6. Click "Advanced settings" → "Secrets"

### Step 1.3: Configure Secrets
Copy from `streamlit_secrets_template.toml` and update with your values:

```toml
[postgres]
host = "db.<your-project-id>.supabase.co"
port = "5432"
database = "postgres"
user = "postgres"
password = "your-supabase-password"

[redis]
url = "redis://:your-upstash-token@your-endpoint.upstash.io:port"

[r2]
endpoint_url = "https://<account-id>.r2.cloudflarestorage.com"
aws_access_key_id = "your-r2-access-key"
aws_secret_access_key = "your-r2-secret-key"
bucket_name = "bharatverse-files"

[inference]
huggingface_token = "hf_your_token_here"
whisper_api = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
text_analysis_api = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
image_analysis_api = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
translation_api = "https://api-inference.huggingface.co/models/facebook/nllb-200-distilled-600M"
```

## 2. 🔮 AI Inference Setup (Hugging Face)

### Step 2.1: Get Hugging Face Token
1. Go to [https://huggingface.co](https://huggingface.co)
2. Sign up/login → Settings → Access Tokens
3. Create new token with **Read** permissions
4. Copy token (starts with `hf_`)

### Step 2.2: Verify API Access
The app uses these free Hugging Face models:
- **Whisper Large-v3**: Audio transcription
- **RoBERTa Sentiment**: Text sentiment analysis  
- **BLIP Image Captioning**: Image understanding
- **NLLB Translation**: Multilingual translation

*Note: Free tier has rate limits. The app includes caching to optimize usage.*

## 3. 🐘 Supabase PostgreSQL Setup

### Step 3.1: Create Project
1. Go to [https://supabase.com](https://supabase.com)
2. Sign up → Create new project
3. Choose region closest to users
4. Set strong database password
5. Wait for setup completion (~2 minutes)

### Step 3.2: Get Connection Details
1. Project Settings → Database
2. Copy **Connection string** and **Direct connection details**
3. Note: Format is `db.<project-id>.supabase.co`

### Step 3.3: Database Schema
The app auto-creates required tables:
- `users` - User authentication
- `contributions` - User content
- `analytics` - Usage tracking
- `ai_processing_logs` - AI operation logs

## 4. ⚡ Upstash Redis Setup

### Step 4.1: Create Redis Instance
1. Go to [https://upstash.com](https://upstash.com)
2. Sign up → Create Redis Database
3. Choose **Global** region for best performance
4. Copy the **Redis URL** (includes auth token)

### Step 4.2: Verify Connection
Format: `redis://:token@endpoint:port`
- Used for caching AI results
- Session management
- Rate limiting

## 5. 🪣 Cloudflare R2 Storage Setup

### Step 5.1: Create R2 Bucket
1. Go to [https://dash.cloudflare.com](https://dash.cloudflare.com)
2. R2 Object Storage → Create bucket
3. Bucket name: `bharatverse-files` (or your choice)
4. Choose location close to users

### Step 5.2: Generate Access Keys
1. Manage R2 API Tokens → Create API token
2. Permissions: **Admin Read & Write**
3. Copy **Access Key ID** and **Secret Access Key**

### Step 5.3: Optional Custom Domain
1. Custom Domains → Connect Domain
2. Add DNS records as instructed
3. Provides clean URLs for uploaded files

📦 Folder Structure (Example)
project-root/
├── streamlit_app.py
├── requirements.txt
├── .streamlit/
│   └── config.toml
└── utils/
    ├── r2.py
    ├── db.py
    └── inference.py

🧪 Testing
Use:
* st.write() for debugging in UI
* Postman or curl to test inference API
* Supabase SQL console for DB tests
* Upstash dashboard to monitor Redis keys
* R2 dashboard to inspect uploaded files

🛡️ Security Notes
* Do not hardcode secrets; use st.secrets or environment variables
* Cloudflare R2 files are private by default — make public if needed
* Hugging Face Spaces may expose logs if not secured
* Supabase allows IP restriction and row-level security (RLS)

📚 Credits
* Streamlit
* Hugging Face Spaces
* Supabase
* Cloudflare R2
* Upstash Redis
* RunPod.io

💡 Future Enhancements
* Add BigBlueButton / video call integration
* Use RAG / Ollama / LangChain inference locally
* Add multilingual support via Translation API
* Connect to Telegram/WhatsApp for bot access
* Visual dashboards using Plotly or Chart.js

🧠 Maintained by: @amruthjakku
Have questions or want to collaborate? Open an issue or pull request!

