# Streamlit Cloud Deployment Guide

## 🚨 **IMMEDIATE FIXES NEEDED**

### **1. Fix packages.txt** ✅ DONE
- **Issue**: Comments in packages.txt caused deployment failure
- **Fix**: Removed comment line, now contains only package names

### **2. Change Main File in Streamlit Cloud**
- **Current**: `scripts/run_app.py` ❌
- **Change to**: `Home.py` ✅
- **Action**: Go to your Streamlit Cloud app settings and change the main file

### **3. Lightweight Requirements** ✅ DONE
- **Issue**: Too many heavy dependencies
- **Fix**: Created ultra-lightweight requirements.txt

---

## 🔧 **Step-by-Step Deployment Fix**

### **Step 1: Update Streamlit Cloud Settings**
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Find your app: `bharatverse-45hkxngrfvxrehjujp2ttj`
3. Click **Settings** (gear icon)
4. Change **Main file path** from `scripts/run_app.py` to `Home.py`
5. Click **Save**

### **Step 2: Push Current Fixes**
```bash
git add .
git commit -m "Fix deployment: clean packages.txt and lightweight requirements"
git push origin main
```

### **Step 3: Restart Deployment**
- Streamlit Cloud will automatically redeploy after the push
- Or manually restart from the app dashboard

---

## 📁 **Files Fixed**

### **packages.txt** ✅
```
libsndfile1
ffmpeg
libsm6
libxext6
libxrender-dev
libgomp1
```

### **requirements.txt** ✅
```
# Streamlit Cloud Requirements - Ultra Lightweight
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
requests>=2.31.0
python-dotenv>=1.0.0
plotly>=5.15.0
pillow>=10.0.0
python-dateutil>=2.8.0
pytz>=2023.3
pydantic>=2.0.0
bcrypt>=4.0.0
langdetect>=1.0.9
diskcache>=5.6.0
soundfile>=0.12.0
```

### **Entry Point** ✅
- **File**: `Home.py` (exists and ready)
- **Type**: Simple Streamlit app (not complex runner script)

---

## 🎯 **Expected Results After Fix**

### **Deployment Should Work Because:**
1. ✅ **No comments in packages.txt**
2. ✅ **Lightweight requirements** (< 1GB memory)
3. ✅ **Simple entry point** (Home.py)
4. ✅ **No complex startup scripts**
5. ✅ **Cloud-optimized dependencies**

### **App Features That Will Work:**
- ✅ **Basic Streamlit interface**
- ✅ **Home page and navigation**
- ✅ **Text and basic features**
- ✅ **Simple audio upload**
- ✅ **Basic image processing**
- ⚠️ **AI features** (limited by free tier memory)

---

## 🚀 **Deployment Commands**

### **If you need to redeploy manually:**
```bash
# 1. Commit current fixes
git add packages.txt requirements.txt
git commit -m "Fix Streamlit Cloud deployment issues"
git push origin main

# 2. The app will auto-redeploy
# 3. Check logs at: https://share.streamlit.io
```

---

## 🔍 **Troubleshooting**

### **If deployment still fails:**

1. **Check the main file setting**:
   - Must be `Home.py`, not `scripts/run_app.py`

2. **Memory issues**:
   - Current requirements are ultra-lightweight
   - If still issues, remove more packages

3. **Import errors**:
   - Check Home.py imports only available packages
   - May need to add try/except for optional imports

4. **Environment variables**:
   - Set `DISABLE_GITLAB_AUTH=true` in Streamlit Cloud secrets
   - Add other required environment variables

---

## 📝 **Streamlit Cloud Secrets**

Add these to your Streamlit Cloud app secrets:

```toml
# Basic configuration
DISABLE_GITLAB_AUTH = "true"
AI_MODE = "cloud"
DEPLOYMENT_MODE = "cloud"

# Database (if using)
# DATABASE_URL = "your_database_url"

# Optional: HuggingFace for AI features
# HUGGINGFACE_TOKEN = "your_token"
```

---

## ✅ **Quick Checklist**

- [x] **packages.txt**: No comments, only package names
- [x] **requirements.txt**: Ultra-lightweight version
- [ ] **Main file**: Change to `Home.py` in Streamlit Cloud settings
- [ ] **Push changes**: Commit and push to trigger redeploy
- [ ] **Check logs**: Monitor deployment in Streamlit Cloud dashboard

---

## 🎉 **After Successful Deployment**

Your app should be available at:
`https://bharatverse-45hkxngrfvxrehjujp2ttj.streamlit.app/`

### **Features Available:**
- ✅ Home page with navigation
- ✅ Basic audio capture
- ✅ Text stories
- ✅ Visual heritage (basic)
- ✅ Community features
- ⚠️ AI features (limited by memory)

---

## 🚨 **CRITICAL ACTION REQUIRED**

**You MUST change the main file in Streamlit Cloud settings from `scripts/run_app.py` to `Home.py`**

This is the most important fix - the deployment will keep failing until you make this change in the Streamlit Cloud dashboard.