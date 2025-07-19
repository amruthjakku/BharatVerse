#!/bin/bash

# BharatVerse Production Deployment Script
# For Ubuntu 22.04 LTS servers (DigitalOcean, AWS, etc.)

set -e

echo "🚀 BharatVerse Production Deployment"
echo "===================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo "✅ Docker installed"
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
else
    echo "✅ Docker Compose already installed"
fi

# Install Git if not present
if ! command -v git &> /dev/null; then
    echo "📚 Installing Git..."
    apt install -y git
fi

# Install Nginx for reverse proxy
echo "🌐 Installing Nginx..."
apt install -y nginx

# Install Certbot for SSL
echo "🔒 Installing Certbot for SSL..."
apt install -y certbot python3-certbot-nginx

# Create application directory
APP_DIR="/opt/bharatverse"
echo "📁 Creating application directory: $APP_DIR"
mkdir -p $APP_DIR
cd $APP_DIR

# Clone repository (if not already present)
if [ ! -d ".git" ]; then
    echo "📥 Cloning BharatVerse repository..."
    echo "Please enter your GitHub repository URL:"
    read -p "Repository URL: " REPO_URL
    git clone $REPO_URL .
else
    echo "✅ Repository already cloned"
    git pull origin main
fi

# Create production environment file
echo "⚙️ Setting up production environment..."
if [ ! -f ".env.production" ]; then
    cat > .env.production << EOF
# Production Environment Configuration
POSTGRES_PASSWORD=$(openssl rand -base64 32)
MINIO_ACCESS_KEY=bharatverse-admin
MINIO_SECRET_KEY=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -base64 64)

# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=bharatverse_user
POSTGRES_DB=bharatverse

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# MinIO
MINIO_HOST=minio:9000

# AI Configuration
AI_MODE=production
ENABLE_HEAVY_MODELS=true
USE_LIGHTWEIGHT_MODELS=false

# Security
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF
    echo "✅ Production environment file created"
else
    echo "✅ Production environment file already exists"
fi

# Create Nginx configuration
echo "🌐 Setting up Nginx reverse proxy..."
cat > /etc/nginx/sites-available/bharatverse << EOF
server {
    listen 80;
    server_name _;
    
    client_max_body_size 200M;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 86400;
    }
}
EOF

# Enable Nginx site
ln -sf /etc/nginx/sites-available/bharatverse /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo "✅ Nginx configured"

# Create systemd service for auto-start
echo "🔄 Setting up auto-start service..."
cat > /etc/systemd/system/bharatverse.service << EOF
[Unit]
Description=BharatVerse Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$APP_DIR
ExecStart=/usr/local/bin/docker-compose -f docker-compose.production.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.production.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable bharatverse

# Start the application
echo "🚀 Starting BharatVerse application..."
docker-compose -f docker-compose.production.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
echo "🔍 Checking service status..."
if docker-compose -f docker-compose.production.yml ps | grep -q "Up"; then
    echo "✅ Services are running"
else
    echo "❌ Some services failed to start"
    docker-compose -f docker-compose.production.yml logs
    exit 1
fi

# Get server IP
SERVER_IP=$(curl -s ifconfig.me)

echo ""
echo "🎉 BharatVerse Deployment Complete!"
echo "=================================="
echo ""
echo "📍 Your application is now running at:"
echo "   http://$SERVER_IP"
echo ""
echo "🔧 Next Steps:"
echo "1. Point your domain to this server IP: $SERVER_IP"
echo "2. Set up SSL certificate:"
echo "   sudo certbot --nginx -d yourdomain.com"
echo ""
echo "📊 Monitor your application:"
echo "   docker-compose -f docker-compose.production.yml logs -f"
echo ""
echo "🔄 Manage the service:"
echo "   sudo systemctl start bharatverse    # Start"
echo "   sudo systemctl stop bharatverse     # Stop"
echo "   sudo systemctl restart bharatverse  # Restart"
echo ""
echo "📁 Application directory: $APP_DIR"
echo "⚙️ Environment file: $APP_DIR/.env.production"
echo ""
echo "🎯 Your BharatVerse platform is now live!"