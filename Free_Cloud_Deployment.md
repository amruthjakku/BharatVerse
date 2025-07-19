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
1. 🌐 Frontend (Streamlit Cloud)
* Push your app to GitHub (e.g., streamlit_app.py, requirements.txt)
* Deploy via https://streamlit.io/cloud
* Add environment secrets:
# .streamlit/secrets.toml
[r2]
endpoint_url = "https://<r2-url>"
aws_access_key_id = "your-key"
aws_secret_access_key = "your-secret"
bucket_name = "bharatverse-files"

[postgres]
host = "db.<supabase>.supabase.co"
port = "5432"
database = "postgres"
user = "postgres"
password = "your-password"

[redis]
url = "redis://:<token>@<upstash-host>:<port>"

[inference]
api_url = "https://your-model-space/api/predict"

2. 🔮 Model Inference API
Use either:
* Hugging Face Spaces: Deploy model via Gradio or FastAPI
* RunPod.io: Deploy GPU-based inference container and expose it via REST
Your Streamlit app will send POST requests to the model endpoint.
import requests
res = requests.post(st.secrets["inference"]["api_url"], json={"input": "your_input"})
prediction = res.json()["result"]

3. 🐘 Supabase PostgreSQL Setup
* Go to https://supabase.com
* Create a new project → Use SQL Editor to set up tables
* Use psycopg2 or SQLAlchemy in Streamlit
import psycopg2
conn = psycopg2.connect(
    dbname=st.secrets["postgres"]["database"],
    user=st.secrets["postgres"]["user"],
    password=st.secrets["postgres"]["password"],
    host=st.secrets["postgres"]["host"],
    port=st.secrets["postgres"]["port"]
)

4. ⚡ Upstash Redis Setup
* Visit https://upstash.com
* Create a Redis instance → Copy URL & Token
import redis
r = redis.from_url(st.secrets["redis"]["url"])
r.set("key", "value")

5. 🪣 Cloudflare R2 Object Storage
* Go to https://dash.cloudflare.com
* Create R2 bucket → Generate Access Key & Secret
import boto3
s3 = boto3.client("s3",
    endpoint_url=st.secrets["r2"]["endpoint_url"],
    aws_access_key_id=st.secrets["r2"]["aws_access_key_id"],
    aws_secret_access_key=st.secrets["r2"]["aws_secret_access_key"],
)

# Upload a file
s3.upload_fileobj(file, st.secrets["r2"]["bucket_name"], "uploads/myfile.jpg")

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

