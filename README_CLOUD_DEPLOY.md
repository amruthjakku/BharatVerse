# 🏛️ BharatVerse - Free Cloud Deployment

A scalable cultural heritage platform using **100% free cloud services**.

## 🌐 Architecture

```
[🧑‍💻 User] → [🌐 Streamlit Cloud] → [🔮 HF Spaces] + [🐘 Supabase] + [⚡ Upstash] + [🪣 MinIO]
```

## 🚀 Free Services Used

- **Frontend**: Streamlit Cloud (Free)
- **AI Processing**: Hugging Face Inference API (Free tier)
- **Database**: Supabase PostgreSQL (500MB free)
- **Cache**: Upstash Redis (10k commands/day free)
- **Storage**: MinIO on Render (1GB free)

## 📦 Deployment Steps

1. **Fork this repository**
2. **Set up free services**:
   - Create Supabase project
   - Create Upstash Redis instance
   - Deploy MinIO on Render
   - Get Hugging Face token
3. **Deploy to Streamlit Cloud**:
   - Connect GitHub repository
   - Add secrets from `streamlit_secrets_template.toml`
   - Deploy!

## 🔧 Configuration

Copy `streamlit_secrets_template.toml` to Streamlit Cloud secrets and fill in your values.

## 💰 Cost

**$0/month** - Everything runs on free tiers!

## 📚 Documentation

See `Free_Cloud_Deployment.md` for detailed setup instructions.

## 🎯 Features

- Real AI-powered audio transcription
- Intelligent text analysis with cultural context
- Advanced image processing and captioning
- Multi-language translation support
- Real-time analytics and monitoring
- User authentication and profiles
- Community features and collaboration

---

Built with ❤️ for preserving cultural heritage
