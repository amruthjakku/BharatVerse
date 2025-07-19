# 🪣 Deploy MinIO on Render - Step by Step

## 🚀 Quick Deploy Instructions

### Method 1: Manual Web Service Creation

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +" → "Web Service"**
3. **Select "Deploy an existing image from a registry"**

### Configuration:

| Setting | Value |
|---------|--------|
| **Image URL** | `minio/minio:latest` |
| **Service Name** | `bharatverse-minio` |
| **Region** | `Oregon (US West)` |
| **Branch** | `main` |
| **Root Directory** | `.` |
| **Runtime** | `Docker` |
| **Build Command** | `(leave empty)` |
| **Start Command** | `minio server /data --address :9000 --console-address :9001` |
| **Plan** | **Free** |
| **Port** | `9000` |

### Environment Variables:

Add these in the "Advanced" section:

```bash
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin  
MINIO_ADDRESS=:9000
MINIO_CONSOLE_ADDRESS=:9001
```

### Expected Result:

- **MinIO API**: `https://your-service-name.onrender.com` (port 9000)
- **MinIO Console**: Access via API URL + console path

---

## Method 2: Deploy Button URL

Use this direct deploy URL (opens pre-configured):

```
https://dashboard.render.com/select-repo?type=web&repo=https://github.com/render-examples/minio&envVars[MINIO_ROOT_USER]=minioadmin&envVars[MINIO_ROOT_PASSWORD]=minioadmin&envVars[MINIO_ADDRESS]=:9000
```

---

## 🧪 After Deployment

1. **Wait 3-5 minutes** for deployment to complete
2. **Copy your service URL** (e.g., `https://bharatverse-minio-abc.onrender.com`)
3. **Test the deployment**:
   - Visit your MinIO URL
   - Login with `minioadmin` / `minioadmin`
   - Create bucket named `bharatverse-bucket`

4. **Update your BharatVerse config**:
   - Run: `python setup_accounts.py`
   - Enter your MinIO endpoint URL when prompted
   - The script will test the connection and create the bucket

---

## ⚠️  Troubleshooting

### If deployment fails:
- Check logs in Render dashboard
- Ensure port 9000 is configured
- Verify environment variables are set

### If can't access MinIO console:
- MinIO console runs on internal port 9001
- Access via the main service URL
- Login: `minioadmin` / `minioadmin`

### If bucket creation fails:
- Create bucket manually in MinIO console
- Set bucket name to `bharatverse-bucket`
- Make sure bucket policy allows read/write