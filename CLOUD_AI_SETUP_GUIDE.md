# 🤖 Cloud AI Setup Guide for BharatVerse

## 🎯 **Why Your AI Services Show as Offline**

Your cloud AI services are showing as ❌ offline because:
1. **HuggingFace API token needs to be refreshed**
2. **Secrets not configured in Streamlit Cloud**
3. **API endpoints need proper configuration**

## 🔧 **Fix Steps**

### **Step 1: Get Fresh HuggingFace Token**

1. **Go to HuggingFace**: https://huggingface.co/settings/tokens
2. **Login** to your account (or create free account)
3. **Create New Token**:
   - Name: `BharatVerse-AI`
   - Type: `Read` (free tier)
   - Click **Create token**
4. **Copy the token** (starts with `hf_`)

### **Step 2: Update Local Configuration**

Update your `.streamlit/secrets.toml`:

```toml
[inference]
huggingface_token = "hf_YOUR_NEW_TOKEN_HERE"
base_url = "https://api-inference.huggingface.co"

# AI Model Endpoints (Free HuggingFace Inference API)
whisper_api = "https://api-inference.huggingface.co/models/openai/whisper-small"
text_analysis_api = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
image_analysis_api = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
translation_api = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-hi-en"
runpod_token = ""

[rate_limits]
api_calls_per_minute = 60
```

### **Step 3: Configure Streamlit Cloud Secrets**

1. **Go to your Streamlit Cloud app**
2. **Click "Manage app"** (bottom right)
3. **Go to "Secrets"** tab
4. **Copy your entire `.streamlit/secrets.toml` content**
5. **Paste into the secrets editor**
6. **Save** and **redeploy**

## 🧪 **Test Your Configuration**

Run the test locally:
```bash
python test_cloud_ai.py
```

**Expected output:**
```
🤖 BharatVerse Cloud AI Test
========================================
✅ Found HuggingFace token: hf_...
✅ Text Analysis: Working
✅ Translation: Working  
⏳ Whisper: Model loading (try again in a minute)
✅ Redis: Connected

🎉 Cloud AI services are configured correctly!
```

## 🚀 **Alternative: Use Free AI Services**

If HuggingFace doesn't work, here are other free options:

### **Option 1: OpenAI Free Tier**
```toml
[inference]
openai_api_key = "sk-your-key-here"
openai_base_url = "https://api.openai.com/v1"
```

### **Option 2: Groq Free API**
```toml
[inference]
groq_api_key = "gsk_your-key-here"
groq_base_url = "https://api.groq.com/openai/v1"
```

### **Option 3: Together AI Free Tier**
```toml
[inference]
together_api_key = "your-key-here"
together_base_url = "https://api.together.xyz/v1"
```

## 🔄 **Fallback Configuration**

I've also improved your app to work even when AI services are offline:

### **When AI Services Work** ✅:
- 🎤 Real-time audio transcription
- 🔤 Advanced text analysis
- 🖼️ Image recognition
- 🌍 Multi-language translation

### **When AI Services Offline** ⚠️:
- 📁 File upload still works
- 📝 Manual text entry available
- 🎯 All other features functional
- 💡 Clear guidance for users

## 🎯 **Quick Fix for Deployment**

**Immediate solution:**

1. **Get new HuggingFace token** (5 minutes)
2. **Update Streamlit Cloud secrets** (2 minutes)  
3. **Redeploy** (1 minute)
4. **AI services will show as ✅ online**

## 📋 **Complete Secrets Template**

Copy this to your Streamlit Cloud secrets:

```toml
# 🤗 HuggingFace AI Configuration
[inference]
huggingface_token = "hf_YOUR_NEW_TOKEN_HERE"
base_url = "https://api-inference.huggingface.co"
whisper_api = "https://api-inference.huggingface.co/models/openai/whisper-small"
text_analysis_api = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
image_analysis_api = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
translation_api = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-hi-en"

[rate_limits]
api_calls_per_minute = 60

[app]
enable_caching = true
cache_ttl_hours = 24

# Your existing Redis, Database, and GitLab configs...
# (Copy from your current secrets.toml)
```

## 🎉 **Result**

After following these steps, your BharatVerse dashboard will show:

```
🔧 Cloud AI Services Status
🔮 Inference APIs
Whisper API: ✅
Text Analysis: ✅  
Image Analysis: ✅
Translation: ✅
```

**Your AI-powered cultural heritage platform will be fully operational!** 🇮🇳✨