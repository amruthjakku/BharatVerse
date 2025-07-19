# 🔐 BharatVerse Authentication System

Complete GitLab OAuth authentication with user isolation, personal profiles, and admin dashboard.

## ✅ What's Implemented

### 🔑 Authentication Features
- **GitLab OAuth 2.0 Integration** with `https://code.swecha.org`
- **Secure Token Management** with automatic refresh
- **Session Persistence** across browser sessions
- **CSRF Protection** with state parameter validation
- **User Profile Sync** from GitLab to local database

### 👤 User Management
- **User Isolation** - Each user has their own data space
- **Role-Based Access Control** (Admin, Moderator, User)
- **Personal Profiles** with customizable settings
- **Activity Tracking** and audit logs
- **Contribution Management** per user

### 🛡️ Admin Dashboard
- **User Management** - View, edit, and manage all users
- **Content Moderation** - Review and manage contributions
- **System Analytics** - User growth, activity metrics
- **Role Management** - Assign admin/moderator roles
- **System Health** monitoring

## 🚀 Getting Started

### 1. Prerequisites
- PostgreSQL running locally
- GitLab OAuth app configured at `https://code.swecha.org`
- Python environment with required packages

### 2. Database Setup
```bash
# Start PostgreSQL
brew services start postgresql@14

# Database is automatically created when app starts
# Tables are created via user_manager.py
```

### 3. Environment Configuration
The system uses `.env.local` for local development:

```bash
# GitLab OAuth Configuration
GITLAB_CLIENT_ID=3a7ccf98f197e891fc2fbff9f4841e4d54c6f069f901bed75b86f1bebf123f95
GITLAB_CLIENT_SECRET=gloas-f837cd1a91e884e8d8dd56203c689ecf730996c79c20fa6aae46a32a4459e574
GITLAB_REDIRECT_URI=http://localhost:8501/callback
GITLAB_BASE_URL=https://code.swecha.org
GITLAB_SCOPES=api read_api read_user k8s_proxy read_repository read_observability write_observability ai_features profile email

# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=bharatverse
POSTGRES_USER=bharatverse_user
POSTGRES_PASSWORD=secretpassword
```

### 4. Start the Application
```bash
# Activate virtual environment
source venv/bin/activate

# Start Streamlit app
streamlit run streamlit_app/app.py --server.port 8501
```

### 5. Test the System
```bash
# Run authentication test
python test_auth_simple.py
```

## 🔐 Authentication Flow

### User Login Process
1. **User clicks "Login with GitLab"** in sidebar
2. **Redirected to GitLab OAuth** at `https://code.swecha.org/oauth/authorize`
3. **User authorizes application** with requested scopes
4. **GitLab redirects back** with authorization code
5. **App exchanges code for access token**
6. **User profile fetched** from GitLab API
7. **User created/updated** in local database
8. **Session established** with user data

### Correct OAuth URL
```
https://code.swecha.org/oauth/authorize?client_id=3a7ccf98f197e891fc2fbff9f4841e4d54c6f069f901bed75b86f1bebf123f95&redirect_uri=http%3A%2F%2Flocalhost%3A8501%2Fcallback&response_type=code&scope=api+read_api+read_user+k8s_proxy+read_repository+read_observability+write_observability+ai_features+profile+email&state=SECURE_RANDOM_STATE
```

## 👤 User Features

### Personal Profile (`👤 My Profile`)
- **Dashboard** with contribution statistics
- **My Contributions** management interface
- **Settings** for privacy and preferences
- **Activity Log** showing user actions
- **GitLab Profile** sync and display

### User Isolation
- Each user's contributions are isolated
- Personal dashboard shows only their data
- Privacy settings control data visibility
- Secure access to user-specific features

## 🛡️ Admin Features

### Admin Dashboard (`🛡️ Admin Dashboard`)
- **System Overview** with user statistics
- **User Management** - view, edit, promote users
- **Content Management** - moderate contributions
- **Analytics** - user growth and activity metrics
- **System Settings** - configuration management

### Setting Up First Admin
```bash
# After first user logs in via GitLab
python setup_admin.py

# Or list all users
python setup_admin.py list
```

## 🔧 Technical Implementation

### Recent Updates
- **✅ Fixed Streamlit API Deprecation** - Updated to use `st.query_params` instead of deprecated `st.experimental_get_query_params`
- **✅ Streamlined Query Parameter Handling** - Simplified code to use only the new Streamlit API
- **✅ Removed API Compatibility Layer** - No more fallback code for older Streamlit versions

### Database Schema
```sql
-- Users table
users (
    id, gitlab_id, username, email, name, avatar_url,
    bio, location, organization, job_title, web_url,
    role, is_active, created_at, updated_at, last_login,
    profile_data, preferences
)

-- User contributions
user_contributions (
    id, user_id, contribution_type, title, description,
    file_path, metadata, tags, language, region,
    is_public, created_at, updated_at
)

-- User sessions
user_sessions (
    id, user_id, session_token, gitlab_access_token,
    gitlab_refresh_token, token_expires_at, created_at,
    last_activity, is_active
)

-- Activity log
user_activity (
    id, user_id, activity_type, activity_data,
    ip_address, user_agent, created_at
)
```

### Key Components
- **`streamlit_app/utils/auth.py`** - OAuth authentication logic
- **`streamlit_app/utils/user_manager.py`** - User database management
- **`streamlit_app/user_profile.py`** - Personal profile interface
- **`streamlit_app/admin_dashboard.py`** - Admin control panel

### Security Features
- **State Parameter** prevents CSRF attacks
- **Token Encryption** in session storage
- **Role-Based Access** with decorators
- **Activity Logging** for audit trails
- **Input Validation** and sanitization

## 🎯 Usage Examples

### Check Authentication
```python
from streamlit_app.utils.auth import GitLabAuth

auth = GitLabAuth()
if auth.is_authenticated():
    user = auth.get_current_user()
    st.write(f"Welcome, {user['name']}!")
```

### Require Authentication
```python
from streamlit_app.utils.auth import require_auth

@require_auth
def protected_function():
    st.write("This requires login")
```

### Admin Only Features
```python
from streamlit_app.utils.auth import GitLabAuth

auth = GitLabAuth()
if auth.is_admin():
    st.write("Admin panel")
else:
    st.error("Admin access required")
```

### Make API Calls
```python
from streamlit_app.utils.auth import make_gitlab_api_request

# Get user's projects
projects = make_gitlab_api_request("projects?owned=true")

# Get user info
user_info = make_gitlab_api_request("user")
```

### Add User Contribution
```python
from streamlit_app.utils.user_manager import user_manager
from streamlit_app.utils.auth import GitLabAuth

auth = GitLabAuth()
db_user = auth.get_current_db_user()

contribution_data = {
    'type': 'audio',
    'title': 'Folk Song',
    'description': 'Traditional song',
    'language': 'Hindi',
    'region': 'Rajasthan',
    'tags': ['folk', 'traditional'],
    'is_public': True
}

contribution_id = user_manager.add_user_contribution(
    db_user['id'], 
    contribution_data
)
```

## 🔍 Testing & Debugging

### Test Authentication
```bash
# Test system components
python test_auth_simple.py

# Check database
python -c "from streamlit_app.utils.user_manager import user_manager; print(user_manager.get_user_stats())"

# List users
python setup_admin.py list
```

### Debug OAuth Issues
1. **Check environment variables** are loaded correctly
2. **Verify callback URL** matches GitLab app settings
3. **Check GitLab instance** is accessible
4. **Review browser console** for JavaScript errors
5. **Check Streamlit logs** for detailed error messages

### Common Issues
- **"Invalid state parameter"** - Clear browser cache/cookies
- **"Authentication failed"** - Check GitLab credentials
- **"Database connection failed"** - Ensure PostgreSQL is running
- **"Admin access required"** - Run `setup_admin.py` first

## 🚀 Production Deployment

### Environment Updates
```bash
# Update for production domain
GITLAB_REDIRECT_URI=https://your-domain.com/callback

# Use secure secrets
APP_SECRET_KEY=your-secure-random-key
SESSION_SECRET_KEY=another-secure-random-key

# Production database
POSTGRES_HOST=your-db-host
POSTGRES_PASSWORD=secure-password
```

### Security Checklist
- [ ] Use HTTPS for all URLs
- [ ] Secure environment variables
- [ ] Enable database SSL
- [ ] Set up proper CORS
- [ ] Configure rate limiting
- [ ] Enable audit logging
- [ ] Regular security updates

## 📊 Current Status

✅ **Completed Features:**
- GitLab OAuth 2.0 integration
- User database with isolation
- Personal profile pages
- Admin dashboard
- Role-based access control
- Activity logging
- Contribution management

🔄 **In Progress:**
- Enhanced content moderation
- Advanced analytics
- Email notifications
- API rate limiting

🎯 **Next Steps:**
1. Test authentication flow
2. Create first admin user
3. Add user contributions
4. Explore admin features
5. Customize user profiles

---

**🎉 The authentication system is fully functional and ready for use!**

Visit http://localhost:8501 and click "Login with GitLab" to get started.