# BharatVerse - Streamlit Cloud Deployment Guide

## 🚀 Quick Deploy to Streamlit Cloud

### Prerequisites
1. A GitHub account
2. A Streamlit Cloud account (free at share.streamlit.io)
3. Fork or clone this repository

### Step 1: Prepare Your Repository
1. Fork this repository to your GitHub account
2. Ensure the following files are present:
   - `Home.py` (main app file)
   - `requirements.txt` (dependencies)
   - `packages.txt` (system dependencies)
   - `.streamlit/config.toml` (configuration)
   - `runtime.txt` (Python version)

### Step 2: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your repository
4. Set the following:
   - **Repository:** `your-username/bharatverse`
   - **Branch:** `main` (or your default branch)
   - **Main file path:** `Home.py`
5. Click "Deploy"

### Step 3: Configure Secrets

1. In Streamlit Cloud dashboard, go to your app settings
2. Click on "Secrets" in the left sidebar
3. Copy the contents from `.streamlit/secrets.toml.example`
4. Fill in your actual values:

```toml
# Database Configuration
[database]
host = "your-actual-database-host"
port = 5432
database = "bharatverse"
user = "your-database-user"
password = "your-database-password"

# Add other configurations as needed...
```

### Step 4: Environment Variables (Optional)

If you're using external services, configure these in the secrets:

- **PostgreSQL Database:** Use Supabase, Neon, or Railway
- **Redis:** Use Upstash Redis or Redis Cloud
- **Storage:** Use MinIO Cloud or AWS S3
- **GitLab OAuth:** Register app at gitlab.com

## 📦 Dependencies Management

The `requirements.txt` file contains all necessary dependencies. Streamlit Cloud will automatically install these.

### Core Dependencies:
- Streamlit and UI components
- Authentication and security
- Database and storage
- AI/ML models
- Audio and vision processing

## 🔧 Configuration

The `.streamlit/config.toml` file contains:
- Theme settings
- Server optimizations
- Security configurations
- Performance settings

## 🌐 Free Hosting Options

### Recommended Services:
1. **Database:** [Supabase](https://supabase.com) (Free tier)
2. **Redis:** [Upstash](https://upstash.com) (Free tier)
3. **Storage:** [Cloudinary](https://cloudinary.com) or [MinIO](https://min.io)
4. **Deployment:** [Streamlit Cloud](https://streamlit.io/cloud) (Free tier)

## 🐛 Troubleshooting

### Common Issues:

1. **Module Import Errors:**
   - Check that all dependencies are in `requirements.txt`
   - Verify Python version compatibility (3.8+)

2. **Database Connection Issues:**
   - Verify database credentials in secrets
   - Check if database allows external connections

3. **Memory Issues:**
   - Streamlit Cloud free tier has 1GB RAM limit
   - Consider optimizing AI models or using cloud APIs

4. **File Upload Issues:**
   - Maximum upload size is set to 100MB
   - Can be adjusted in `.streamlit/config.toml`

## 📊 Monitoring

Once deployed, monitor your app:
1. Check the Streamlit Cloud dashboard for logs
2. View metrics and usage statistics
3. Set up error alerts (optional)

## 🔄 Updates

To update your deployed app:
1. Push changes to your GitHub repository
2. Streamlit Cloud automatically redeploys on push
3. Check the dashboard for deployment status

## 🔒 Security

Important security considerations:
- Never commit secrets to the repository
- Use environment variables for sensitive data
- Enable CORS and XSRF protection
- Keep dependencies updated

## 📞 Support

For issues or questions:
- Check [Streamlit documentation](https://docs.streamlit.io)
- Visit [Streamlit community forum](https://discuss.streamlit.io)
- Open an issue in the repository

---

## Local Development

For local development:
```bash
# Install dependencies
pip install -r requirements.txt

# Create secrets file
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit and add your secrets

# Run the app
streamlit run Home.py
```

Or use the provided script:
```bash
chmod +x start_app.sh
./start_app.sh
```
