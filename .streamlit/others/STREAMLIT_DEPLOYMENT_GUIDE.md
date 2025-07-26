# 🚀 Streamlit Cloud Production Deployment Guide

## **Step 1: Create GitLab OAuth Application (5 minutes)**

### **1.1 Go to GitLab**
- Visit: `https://code.swecha.org`
- Login with your account
- Click your profile picture → **Settings**

### **1.2 Create OAuth Application**
- In left sidebar → **Applications**
- Click **New Application**
- Fill in these **EXACT** values:

```
Name: BharatVerse Production
Redirect URIs: https://amruth-bharatverse.streamlit.app/callback
Scopes: ✅ api ✅ read_user ✅ profile ✅ email
Confidential: ✅ Yes
```

### **1.3 Save and Copy Credentials**
- Click **Save application**
- **COPY** the **Application ID** (looks like: `a1b2c3d4e5f6...`)
- **COPY** the **Secret** (looks like: `gloas-xyz123...`)
- **Keep these safe** - you'll need them in Step 2

---

## **Step 2: Configure Streamlit Cloud Secrets (3 minutes)**

### **2.1 Access Streamlit Cloud**
- Go to: `https://share.streamlit.io`
- Find your **BharatVerse** app
- Click **Settings** (⚙️ icon)
- Click **Secrets** tab

### **2.2 Add Production Secrets**
Copy this template and **replace the placeholder values**:

```toml
[gitlab]
client_id = "PASTE_YOUR_APPLICATION_ID_HERE"
client_secret = "PASTE_YOUR_SECRET_HERE"
base_url = "https://code.swecha.org"
scopes = "api read_user profile email"

[general]
APP_ENV = "streamlit"
DEPLOYMENT_MODE = "cloud"
AI_MODE = "cloud"
DISABLE_GITLAB_AUTH = "false"

[security]
SECRET_KEY = "bharatverse-prod-2025-secure-key"
SESSION_TIMEOUT = "3600"

[features]
ENABLE_AUDIO_CAPTURE = "true"
ENABLE_TEXT_STORIES = "true"
ENABLE_VISUAL_HERITAGE = "true"
ENABLE_AI_INSIGHTS = "true"
ENABLE_COMMUNITY_FEATURES = "true"
```

### **2.3 Save Secrets**
- Paste the configuration (with your real values)
- Click **Save**
- Streamlit will automatically redeploy

---

## **Step 3: Verify Deployment (2 minutes)**

### **3.1 Wait for Deployment**
- Watch the deployment logs
- Should complete in ~2-3 minutes
- Look for "Your app is live!" message

### **3.2 Test Your App**
- Visit: `https://amruth-bharatverse.streamlit.app`
- Should see beautiful BharatVerse homepage
- Click **GitLab Login** to test OAuth
- Should redirect to GitLab → back to your app

### **3.3 Test Features**
- ✅ Homepage loads
- ✅ Navigation works
- ✅ GitLab OAuth works
- ✅ All pages accessible
- ✅ No error messages

---

## **🎯 Production Checklist**

### **Before Going Live:**
- [ ] GitLab OAuth app created with correct redirect URI
- [ ] Streamlit secrets configured with real credentials
- [ ] App deploys without errors
- [ ] OAuth login/logout works
- [ ] All main features accessible
- [ ] No sensitive data in public repository

### **Security Best Practices:**
- [ ] Never commit secrets to Git
- [ ] Use strong, unique SECRET_KEY
- [ ] Regularly rotate OAuth credentials
- [ ] Monitor app usage and errors
- [ ] Set up proper error handling

---

## **🚨 Troubleshooting**

### **Issue: "OAuth redirect URI mismatch"**
**Solution:** Verify GitLab app has exact URI: `https://amruth-bharatverse.streamlit.app/callback`

### **Issue: "Invalid client credentials"**
**Solution:** Double-check client_id and client_secret in Streamlit secrets

### **Issue: "App won't start"**
**Solution:** Check Streamlit Cloud logs for specific error messages

### **Issue: "Features not working"**
**Solution:** Verify all required secrets are set and formatted correctly

---

## **📊 Expected Results**

### **✅ Working Production App:**
- **URL**: `https://amruth-bharatverse.streamlit.app`
- **Features**: All pages and navigation working
- **Authentication**: GitLab OAuth login/logout
- **Performance**: Fast loading, responsive UI
- **Security**: Proper secret management

### **✅ User Experience:**
- Beautiful homepage with BharatVerse branding
- Working navigation to all features
- Seamless GitLab authentication
- Cultural heritage documentation tools
- Community features and collaboration

---

## **🎉 Success Indicators**

When everything is working correctly, you should see:

1. **Homepage**: Beautiful BharatVerse landing page
2. **Navigation**: All page buttons work
3. **OAuth**: "Login with GitLab" redirects properly
4. **Features**: Audio, Text, Visual heritage pages load
5. **No Errors**: Clean logs, no error messages

---

## **📞 Need Help?**

If you encounter issues:

1. **Check Streamlit Cloud logs** for specific errors
2. **Verify GitLab OAuth settings** match exactly
3. **Double-check secrets format** (no extra spaces/quotes)
4. **Test OAuth flow** step by step
5. **Monitor deployment status** in Streamlit dashboard

---

## **🚀 Ready to Deploy?**

Follow the 3 steps above, and your BharatVerse app will be live in production with full GitLab OAuth integration!

**Total time: ~10 minutes**  
**Result: Professional cultural heritage platform** 🏛️✨

---

*Last Updated: January 2025*  
*Version: Production Ready*