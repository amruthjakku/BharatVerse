# 🚨 RENDER DEPLOYMENT QUICK FIX

## **Issue**: GitLab OAuth showing `None` values
**URL**: `https://bharatverse.onrender.com/None/oauth/authorize?client_id=None&redirect_uri=None...`

## ✅ **IMMEDIATE FIX (2 minutes)**

### **Option 1: Disable GitLab Auth Temporarily**
In Render dashboard → Environment Variables, add:
```
DISABLE_GITLAB_AUTH=true
```
This will make your app work immediately without OAuth.

### **Option 2: Set Up GitLab OAuth Properly**

#### **Step 1: Get GitLab Credentials**
1. Go to: https://code.swecha.org
2. Profile → Settings → Applications
3. Create new application:
   - **Name**: BharatVerse
   - **Redirect URIs**:
     ```
     http://localhost:8501/callback
     https://bharatverse.onrender.com/callback
     https://amruth-bharatverse.streamlit.app/callback
     ```
   - **Scopes**: api, read_user, profile, email
4. Copy Application ID and Secret

#### **Step 2: Set Render Environment Variables**
In Render dashboard → Your service → Environment:
```
GITLAB_CLIENT_ID=paste_your_application_id_here
GITLAB_CLIENT_SECRET=paste_your_secret_here
GITLAB_BASE_URL=https://code.swecha.org
GITLAB_SCOPES=api read_user profile email
APP_ENV=render
DISABLE_GITLAB_AUTH=false
```

#### **Step 3: Redeploy**
- Save environment variables
- Render will auto-redeploy
- OAuth should work in ~2 minutes

## 🎯 **Recommended: Use Option 1 First**

For immediate working app:
1. Add `DISABLE_GITLAB_AUTH=true` to Render environment
2. Your app will work without login
3. Set up proper OAuth later when you have time

## 🔍 **Debug Information**

The updated app will now show debug info when OAuth is misconfigured, helping you identify exactly what's missing.

---

**Choose Option 1 for immediate fix, Option 2 for full OAuth setup!**