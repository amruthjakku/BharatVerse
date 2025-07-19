# 🔐 GitLab OAuth Authentication Setup for BharatVerse

## 🎯 **Current Status**

**✅ Demo Authentication Removed**: All demo authentication has been removed  
**✅ GitLab OAuth Implemented**: Proper GitLab OAuth authentication is now in place  
**⚠️ OAuth Configuration Required**: You need to set up GitLab OAuth credentials  

This document explains how to set up and use GitLab OAuth authentication in BharatVerse.

## 🔧 Configuration

### Environment Variables

Add the following variables to your `.env` or `.env.local` file:

```bash
# GitLab OAuth Configuration
GITLAB_CLIENT_ID=3a7ccf98f197e891fc2fbff9f4841e4d54c6f069f901bed75b86f1bebf123f95
GITLAB_CLIENT_SECRET=gloas-f837cd1a91e884e8d8dd56203c689ecf730996c79c20fa6aae46a32a4459e574
GITLAB_REDIRECT_URI=http://localhost:8501/callback
GITLAB_BASE_URL=https://code.swecha.org
GITLAB_SCOPES=api read_api read_user k8s_proxy read_repository read_observability write_observability ai_features profile email
```

### GitLab Application Settings

The OAuth application is configured on GitLab instance `https://code.swecha.org` with:

- **Application ID**: `3a7ccf98f197e891fc2fbff9f4841e4d54c6f069f901bed75b86f1bebf123f95`
- **Callback URL**: `http://localhost:8501/callback` (update port as needed)
- **Scopes**: 
  - `api` - Access the API on your behalf
  - `read_api` - Read API
  - `read_user` - Read your personal information
  - `k8s_proxy` - Kubernetes API calls
  - `read_repository` - Read-only repository access
  - `read_observability` - Read-only GitLab Observability access
  - `write_observability` - Read-write GitLab Observability access
  - `ai_features` - GitLab Duo features
  - `profile` - OpenID Connect profile access
  - `email` - OpenID Connect email access

## 🚀 Installation

1. **Install Dependencies**:
   ```bash
   pip install authlib httpx 'python-jose[cryptography]'
   ```

2. **Update Requirements** (already done):
   ```bash
   # OAuth and Authentication
   authlib>=1.2.1
   httpx>=0.25.0
   python-jose[cryptography]>=3.3.0
   ```

## 📁 File Structure

The authentication system consists of:

```
streamlit_app/
├── utils/
│   └── auth.py              # Main authentication module
├── gitlab_module.py         # GitLab integration page
└── app.py                   # Updated main app with auth
test_auth.py                 # Standalone authentication test
```

## 🔐 Authentication Flow

1. **User clicks "Login with GitLab"**
2. **Redirect to GitLab OAuth**:
   - URL: `https://code.swecha.org/oauth/authorize`
   - Parameters: client_id, redirect_uri, response_type, scope, state
3. **User authorizes on GitLab**
4. **GitLab redirects back** with authorization code
5. **Exchange code for access token**
6. **Fetch user information** from GitLab API
7. **Store in Streamlit session**

## 🛠️ Usage

### Basic Authentication Check

```python
from streamlit_app.utils.auth import GitLabAuth

auth = GitLabAuth()
if auth.is_authenticated():
    user_info = auth.get_current_user()
    st.write(f"Welcome, {user_info['name']}!")
else:
    st.write("Please login")
```

### Protected Pages

```python
from streamlit_app.utils.auth import require_auth

@require_auth
def protected_function():
    st.write("This requires authentication")
```

### API Requests

```python
from streamlit_app.utils.auth import make_gitlab_api_request

# Get user projects
projects = make_gitlab_api_request("projects?owned=true")

# Get user info
user_info = make_gitlab_api_request("user")
```

### Login/Logout UI

```python
from streamlit_app.utils.auth import render_login_button, render_user_info

auth = GitLabAuth()
if auth.is_authenticated():
    render_user_info()  # Shows user profile and logout button
else:
    render_login_button()  # Shows login button
```

## 🧪 Testing

### Standalone Test

Run the authentication test:

```bash
streamlit run test_auth.py --server.port 8503
```

This provides:
- ✅ Authentication status
- 👤 User profile display
- 🛠️ API testing interface
- ⚙️ Configuration verification

### Integration Test

The authentication is integrated into the main app:

```bash
streamlit run streamlit_app/app.py
```

Look for:
- 🔐 Login button in sidebar (when not authenticated)
- 👤 User profile in sidebar (when authenticated)
- 🦊 GitLab integration page in navigation

## 🔧 API Integration

### Available Endpoints

The authentication provides access to GitLab API v4:

- `GET /user` - Current user information
- `GET /projects` - User projects
- `GET /groups` - User groups
- `GET /user/activities` - User activities
- `GET /projects?starred=true` - Starred projects
- `GET /user/keys` - SSH keys

### Example API Usage

```python
# Get user's projects
projects = make_gitlab_api_request("projects?owned=true&per_page=10")

# Get user's groups
groups = make_gitlab_api_request("groups")

# Get specific project
project = make_gitlab_api_request("projects/123")
```

## 🔒 Security Features

- **State Parameter**: CSRF protection using secure random state
- **Token Storage**: Secure session-based token storage
- **Token Expiration**: Automatic token expiration handling
- **Scope Validation**: Proper OAuth scope management
- **Error Handling**: Comprehensive error handling and user feedback

## 🐛 Troubleshooting

### Common Issues

1. **"Invalid state parameter"**
   - Clear browser cache and cookies
   - Restart Streamlit app

2. **"Authentication failed"**
   - Check GitLab instance is accessible
   - Verify client ID and secret
   - Check callback URL matches exactly

3. **"API request failed"**
   - Verify token hasn't expired
   - Check API endpoint exists
   - Ensure proper scopes are granted

### Debug Mode

Enable debug logging by setting:

```bash
DEBUG=True
LOG_LEVEL=DEBUG
```

### Port Configuration

If using different ports, update:

1. **Environment variable**:
   ```bash
   GITLAB_REDIRECT_URI=http://localhost:YOUR_PORT/callback
   ```

2. **GitLab application settings** (if you have admin access)

## 🚀 Production Deployment

For production deployment:

1. **Update callback URL** to production domain
2. **Use HTTPS** for security
3. **Set secure environment variables**
4. **Configure proper CORS settings**
5. **Use production-grade secret management**

Example production config:

```bash
GITLAB_REDIRECT_URI=https://your-domain.com/callback
GITLAB_BASE_URL=https://code.swecha.org
APP_SECRET_KEY=your-secure-random-key
SESSION_SECRET_KEY=another-secure-random-key
```

## 📚 Additional Resources

- [GitLab OAuth Documentation](https://docs.gitlab.com/ee/api/oauth2.html)
- [Streamlit Authentication Patterns](https://docs.streamlit.io/knowledge-base/deploy/authentication-without-sso)
- [OAuth 2.0 Security Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)

## 🤝 Contributing

To extend the authentication system:

1. **Add new OAuth providers** in `auth.py`
2. **Extend API integration** in `gitlab_module.py`
3. **Add new protected features** using `@require_auth`
4. **Update tests** in `test_auth.py`

---

**Note**: This authentication system is specifically configured for the BharatVerse GitLab instance at `https://code.swecha.org`. For other GitLab instances, update the `GITLAB_BASE_URL` accordingly.