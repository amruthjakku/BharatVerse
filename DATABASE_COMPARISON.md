# Database Comparison for BharatVerse

## Overview
Comparison of free, open-source databases for storing audio, video, and text data at scale.

## Key Requirements
- ✅ Handle multimedia files (audio, video, text)
- ✅ Free and open-source
- ✅ Scalable for large datasets
- ✅ Efficient performance
- ✅ Good community support

## Database Comparison Table

| Database | Storage Limit | Best For | Pros | Cons | Multimedia Support |
|----------|--------------|----------|------|------|-------------------|
| **PostgreSQL** | No limit (disk space) | Structured data + BLOB | • ACID compliant<br>• JSON support<br>• Full-text search<br>• Extensions (PostGIS) | • Requires more setup<br>• BLOB handling can be complex | Store file paths + metadata, or use Large Objects |
| **MongoDB** | No limit (disk space) | Unstructured/semi-structured | • GridFS for large files<br>• Flexible schema<br>• Horizontal scaling<br>• Native binary storage | • More RAM usage<br>• No ACID by default | Excellent - GridFS handles files >16MB |
| **SQLite** | 281 TB theoretical | Development/small projects | • Zero configuration<br>• Serverless<br>• Single file database | • Single writer<br>• Not for concurrent users | Limited - stores BLOBs but not optimal |
| **CouchDB** | No limit (disk space) | Document storage + sync | • Built-in sync<br>• HTTP/JSON API<br>• Attachments support | • Slower queries<br>• Less flexible querying | Good - native attachment support |
| **MinIO** | No limit (disk space) | Object storage (S3-compatible) | • S3 API compatible<br>• Built for large files<br>• Distributed storage | • Not a database<br>• Needs separate metadata DB | Excellent - designed for multimedia |
| **Cassandra** | No limit (disk space) | Time-series, high write | • Linear scalability<br>• No single point of failure | • Complex setup<br>• Eventually consistent | Via file paths + external storage |

## Recommended Architecture for BharatVerse

### 🏆 Best Solution: Hybrid Approach

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                         │
│                 (Streamlit/FastAPI)                      │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────┐
│                    Application Layer                      │
├─────────────────────────┬───────────────────────────────┤
│                         │                                 │
│   ┌─────────────────┐   │   ┌────────────────────────┐ │
│   │   PostgreSQL    │   │   │    MinIO/S3           │ │
│   │                 │   │   │  (Object Storage)      │ │
│   │ • Metadata      │   │   │                        │ │
│   │ • Search index  │   │   │ • Audio files         │ │
│   │ • User data     │   │   │ • Video files         │ │
│   │ • Relationships │   │   │ • Images              │ │
│   └─────────────────┘   │   └────────────────────────┘ │
│                         │                                 │
│   ┌─────────────────┐   │   ┌────────────────────────┐ │
│   │     Redis       │   │   │   MongoDB (Optional)   │ │
│   │   (Cache)       │   │   │  (Transcriptions)     │ │
│   └─────────────────┘   │   └────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Option 1: PostgreSQL + File System (Simple & Effective)
**Best for**: Small to medium scale (up to 10TB)

```python
# Implementation approach
class MultimediaStorage:
    def __init__(self):
        self.db = PostgreSQL()
        self.storage_path = "/data/bharatverse"
    
    def save_audio(self, file, metadata):
        # Save file to disk
        file_path = f"{self.storage_path}/audio/{uuid}.mp3"
        save_file(file, file_path)
        
        # Save metadata to PostgreSQL
        self.db.insert('audio_files', {
            'id': uuid,
            'path': file_path,
            'title': metadata['title'],
            'language': metadata['language'],
            'transcription': metadata['transcription'],
            'tags': metadata['tags']  # PostgreSQL array
        })
```

**Storage**: Limited by disk space
**Cost**: Free (self-hosted)

### Option 2: MongoDB with GridFS (Scalable)
**Best for**: Medium to large scale (up to 100TB+)

```python
from pymongo import MongoClient
import gridfs

client = MongoClient('mongodb://localhost:27017/')
db = client['bharatverse']
fs = gridfs.GridFS(db)

# Store large audio file
with open("audio.mp3", "rb") as f:
    file_id = fs.put(f, filename="folk_song.mp3", 
                     metadata={
                         "language": "Telugu",
                         "region": "Andhra Pradesh",
                         "tags": ["folk", "traditional"]
                     })

# Retrieve file
audio_file = fs.get(file_id)
```

**Storage**: Unlimited (add nodes as needed)
**Cost**: Free (self-hosted)

### Option 3: MinIO + PostgreSQL (Professional)
**Best for**: Large scale, production (100TB+)

```python
from minio import Minio
import psycopg2

# MinIO for files
minio_client = Minio('localhost:9000',
                     access_key='minioadmin',
                     secret_key='minioadmin',
                     secure=False)

# PostgreSQL for metadata
conn = psycopg2.connect("dbname=bharatverse")

# Upload file to MinIO
minio_client.fput_object('audio-bucket', 'folk-song.mp3', '/path/to/audio.mp3')

# Store metadata in PostgreSQL
cursor = conn.cursor()
cursor.execute("""
    INSERT INTO audio_metadata (filename, url, language, tags)
    VALUES (%s, %s, %s, %s)
""", ('folk-song.mp3', 'http://localhost:9000/audio-bucket/folk-song.mp3', 
      'Telugu', ['folk', 'traditional']))
```

**Storage**: Unlimited (distributed)
**Cost**: Free (self-hosted)

## Free Cloud Storage Options

### 1. **Supabase** (PostgreSQL)
- **Free Tier**: 500MB database + 1GB file storage
- **Good for**: MVP/Demo
- **Limits**: 2GB file upload limit

### 2. **MongoDB Atlas**
- **Free Tier**: 512MB storage
- **Good for**: Development
- **Limits**: Shared cluster, limited performance

### 3. **Firebase** (Google)
- **Free Tier**: 1GB Firestore + 5GB Storage
- **Good for**: Small projects
- **Limits**: Vendor lock-in

### 4. **Cloudflare R2**
- **Free Tier**: 10GB storage/month
- **Good for**: Static assets
- **Limits**: Egress fees may apply

### 5. **Backblaze B2**
- **Free Tier**: 10GB storage
- **Good for**: Backup/Archive
- **Limits**: API call limits

## 🎯 Recommendation for BharatVerse

### For Development/MVP:
```bash
# Quick setup
docker-compose up -d postgres redis
```

Use **PostgreSQL + File System**:
- Simple to implement
- Handles metadata efficiently
- Files stored on disk
- Can migrate later

### For Production:
Use **MinIO + PostgreSQL + Redis**:
- MinIO for multimedia files (S3-compatible)
- PostgreSQL for metadata and search
- Redis for caching
- Scalable to petabytes

### Implementation Plan:

1. **Phase 1**: Start with PostgreSQL + File System
2. **Phase 2**: Add Redis for caching
3. **Phase 3**: Migrate files to MinIO/S3
4. **Phase 4**: Add MongoDB for transcriptions (optional)

## Sample Docker Compose Setup

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: bharatverse
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  minio:
    image: minio/minio
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

## Storage Calculation

For BharatVerse with multimedia content:

### Estimated Storage Needs:
- **Audio files**: ~10MB per file (3-5 min recordings)
- **Video files**: ~100MB per file (5-10 min videos)
- **Images**: ~2MB per file
- **Text**: Negligible

### Scale Estimation:
| Contributions | Audio (GB) | Video (GB) | Images (GB) | Total (GB) |
|--------------|------------|------------|-------------|------------|
| 1,000 | 10 | 100 | 2 | 112 |
| 10,000 | 100 | 1,000 | 20 | 1,120 |
| 100,000 | 1,000 | 10,000 | 200 | 11,200 |

## Final Recommendation

**For BharatVerse, use this stack:**

1. **PostgreSQL** - Metadata, search, user data
2. **MinIO** - Audio/video/image files (or local filesystem initially)
3. **Redis** - Caching layer
4. **Optional: MongoDB** - For flexible document storage

This provides:
- ✅ Unlimited storage (self-hosted)
- ✅ High performance
- ✅ Easy scaling
- ✅ S3 compatibility (MinIO)
- ✅ Full-text search (PostgreSQL)
- ✅ 100% free and open-source
