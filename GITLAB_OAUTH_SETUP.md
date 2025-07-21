# GitLab OAuth Setup Guide for Multiple Environments

## 🔧 **Step 1: Configure Multiple Redirect URIs in GitLab**

### **Access GitLab OAuth Settings:**
1. Go to: `https://code.swecha.org`
2. Click your profile picture → **Settings**
3. In left sidebar → **Applications**
4. Find your BharatVerse application or create new one

### **Set Multiple Redirect URIs:**
In the **Redirect URI** field, add each URL on a separate line:

```
http://localhost:8501/callback
https://bharatverse.onrender.com/callback
https://amruth-bharatverse.streamlit.app/callback
```

### **Application Settings:**
- **Name**: `BharatVerse`
- **Redirect URI**: (multiple lines as above)
- **Scopes**: Check these boxes:
  - ✅ `api` - Access the authenticated user's API
  - ✅ `read_user` - Read the authenticated user's personal information
  - ✅ `profile` - Access the authenticated user's profile information
  - ✅ `email` - Access the authenticated user's email addresses

### **Save and Get Credentials:**
- Click **Save application**
- Copy the **Application ID** (Client ID)
- Copy the **Secret** (Client Secret)

---

## 🔧 **Step 2: Environment Configuration**

### **For Local Development:**
Create `.env` file in project root:
```bash
# GitLab OAuth Configuration
GITLAB_CLIENT_ID=your_application_id_here
GITLAB_CLIENT_SECRET=your_secret_here
GITLAB_BASE_URL=https://code.swecha.org
GITLAB_SCOPES=api read_user profile email
APP_ENV=local

# Disable auth for testing (optional)
DISABLE_GITLAB_AUTH=false
```

### **For Render Deployment:**
In Render dashboard → Environment Variables:
```bash
GITLAB_CLIENT_ID=your_application_id_here
GITLAB_CLIENT_SECRET=your_secret_here
GITLAB_BASE_URL=https://code.swecha.org
GITLAB_SCOPES=api read_user profile email
APP_ENV=render
DISABLE_GITLAB_AUTH=false
```

### **For Streamlit Cloud:**
In Streamlit Cloud → App Settings → Secrets:
```toml
[gitlab]
client_id = "your_application_id_here"
client_secret = "your_secret_here"
base_url = "https://code.swecha.org"
scopes = "api read_user profile email"

[general]
APP_ENV = "streamlit"
DISABLE_GITLAB_AUTH = "false"
```

---

## 🚀 **Step 3: Automatic Environment Detection**

The updated `auth.py` now automatically detects the environment and uses the correct redirect URI:

### **Detection Logic:**
1. **APP_ENV environment variable** (most reliable)
   - `local` → `http://localhost:8501/callback`
   - `render` → `https://bharatverse.onrender.com/callback`
   - `streamlit` → `https://amruth-bharatverse.streamlit.app/callback`

2. **Platform-specific environment variables**
   - `RENDER` → Render deployment
   - `STREAMLIT_SHARING` → Streamlit Cloud

3. **Fallback** → `http://localhost:8501/callback`

### **Manual Override:**
You can still manually set `GITLAB_REDIRECT_URI` to override auto-detection.

---

## 🔍 **Step 4: Testing OAuth Flow**

### **Test Each Environment:**

#### **Local (localhost:8501):**
```bash
# Set environment
export APP_ENV=local

# Run app
streamlit run Home.py
```

#### **Render (bharatverse.onrender.com):**
- Environment variable `APP_ENV=render` should be set
- OAuth should redirect to `https://bharatverse.onrender.com/callback`

#### **Streamlit Cloud (amruth-bharatverse.streamlit.app):**
- Secret `APP_ENV = "streamlit"` should be set
- OAuth should redirect to `https://amruth-bharatverse.streamlit.app/callback`

---

## 🛠️ **Step 5: Troubleshooting**

### **Common Issues:**

#### **Issue: "Redirect URI mismatch"**
**Solution:**
1. Check GitLab application has all 3 redirect URIs
2. Verify `APP_ENV` is set correctly
3. Check logs to see which redirect URI is being used

#### **Issue: "Invalid client"**
**Solution:**
1. Verify `GITLAB_CLIENT_ID` matches GitLab Application ID
2. Check `GITLAB_CLIENT_SECRET` is correct
3. Ensure GitLab application is not disabled

#### **Issue: "Scope error"**
**Solution:**
1. Check GitLab application has required scopes enabled
2. Verify `GITLAB_SCOPES` matches enabled scopes

### **Debug Information:**
Add this to your app to see detected environment:
```python
if st.button("Debug OAuth Config"):
    auth = GitLabAuth()
    st.write(f"Detected Redirect URI: {auth.redirect_uri}")
    st.write(f"APP_ENV: {os.getenv('APP_ENV', 'Not set')}")
    st.write(f"Base URL: {auth.base_url}")
```

---

## 📋 **Step 6: Deployment Checklist**

### **Before Deploying:**
- [ ] GitLab application configured with all 3 redirect URIs
- [ ] Environment variables set for each platform
- [ ] `APP_ENV` variable set correctly
- [ ] OAuth credentials are valid and not expired

### **After Deploying:**
- [ ] Test OAuth login on each platform
- [ ] Verify redirect URIs work correctly
- [ ] Check user authentication persists
- [ ] Test logout functionality

---

## 🔐 **Security Best Practices**

### **Environment Variables:**
- ✅ Never commit secrets to Git
- ✅ Use different secrets for different environments
- ✅ Rotate secrets regularly
- ✅ Use platform-specific secret management

### **OAuth Security:**
- ✅ Always validate state parameter
- ✅ Use HTTPS for all redirect URIs (except localhost)
- ✅ Implement proper session management
- ✅ Handle token expiration gracefully

---

## 🎯 **Quick Setup Commands**

### **For Local Development:**
```bash
# Create .env file
cat > .env << EOF
GITLAB_CLIENT_ID=your_app_id_here
GITLAB_CLIENT_SECRET=your_secret_here
GITLAB_BASE_URL=https://code.swecha.org
APP_ENV=local
DISABLE_GITLAB_AUTH=false
EOF

# Run locally
streamlit run Home.py
```

### **For Production Deployment:**
```bash
# Render - set these environment variables:
GITLAB_CLIENT_ID=your_app_id_here
GITLAB_CLIENT_SECRET=your_secret_here
APP_ENV=render

# Streamlit Cloud - add to secrets:
[gitlab]
client_id = "your_app_id_here"
client_secret = "your_secret_here"

[general]
APP_ENV = "streamlit"
```

---

## ✅ **Verification**

After setup, your OAuth should work seamlessly across all environments:

- 🏠 **Local**: `http://localhost:8501` → GitLab → `http://localhost:8501/callback`
- 🚀 **Render**: `https://bharatverse.onrender.com` → GitLab → `https://bharatverse.onrender.com/callback`
- ☁️ **Streamlit**: `https://amruth-bharatverse.streamlit.app` → GitLab → `https://amruth-bharatverse.streamlit.app/callback`

**All three environments will use the same GitLab OAuth application with multiple redirect URIs!** 🎉

---

*Last Updated: January 2025*  
*Version: 1.0*