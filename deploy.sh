#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting deployment of Meme Generator...${NC}"

# Update system
echo -e "${GREEN}Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# Install required packages
echo -e "${GREEN}Installing required packages...${NC}"
sudo apt install -y docker.io docker-compose curl nginx certbot python3-certbot-nginx

# Start and enable Docker
echo -e "${GREEN}Setting up Docker...${NC}"
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Create directory structure
echo -e "${GREEN}Creating directory structure...${NC}"
mkdir -p ~/meme-generator/{nginx/conf.d,ssl,logs/nginx,data/{media,static}}

# Move to project directory
cd ~/meme-generator

# Create docker-compose.yml
echo -e "${GREEN}Creating docker-compose.yml...${NC}"
cat > docker-compose.yml << 'EOL'
version: '3.8'

services:
  web:
    image: dadidelux/mcp-meme-generator:latest
    command: gunicorn mysite.wsgi:application --bind 0.0.0.0:8000 --workers=4 --threads=2 --worker-class=gthread --worker-tmp-dir=/dev/shm --timeout=30
    volumes:
      - ./data/static:/app/staticfiles
      - ./data/media:/app/media
    expose:
      - 8000
    env_file:
      - .env.prod
    depends_on:
      - db
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD} --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:1.25-alpine
    volumes:
      - ./data/static:/app/staticfiles
      - ./data/media:/app/media
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./ssl:/etc/nginx/ssl
      - ./logs/nginx:/var/log/nginx
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
EOL

# Create Nginx configuration
echo -e "${GREEN}Creating Nginx configuration...${NC}"
cat > nginx/conf.d/app.conf << 'EOL'
upstream web {
    server web:8000;
}

server {
    listen 80;
    listen [::]:80;
    server_name YOUR_DOMAIN;  # Replace with your domain

    location / {
        proxy_pass http://web;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
        client_max_body_size 100M;
    }

    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    location /media/ {
        alias /app/media/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
EOL

# Create environment file template
echo -e "${GREEN}Creating environment file template...${NC}"
cat > .env.prod.template << 'EOL'
DJANGO_SECRET_KEY=your_secret_key_here
DJANGO_ALLOWED_HOSTS=your_domain
DEBUG=0
DB_NAME=django_db
DB_USER=django_user
DB_PASSWORD=your_secure_db_password
DB_HOST=db
REDIS_HOST=redis
REDIS_PASSWORD=your_secure_redis_password
GOOGLE_API_KEY=your_google_api_key
IMGFLIP_USERNAME=your_imgflip_username
IMGFLIP_PASSWORD=your_imgflip_password
EOL

# Create maintenance scripts
echo -e "${GREEN}Creating maintenance scripts...${NC}"

# Update script
cat > update.sh << 'EOL'
#!/bin/bash
docker-compose pull
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --no-input
EOL

# Backup script
cat > backup.sh << 'EOL'
#!/bin/bash
BACKUP_DIR="./backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T db pg_dump -U $DB_USER $DB_NAME > "$BACKUP_DIR/database.sql"

# Backup media files
tar -czf "$BACKUP_DIR/media.tar.gz" -C data/media .

# Cleanup old backups (keep last 7 days)
find ./backups -type d -mtime +7 -exec rm -rf {} +
EOL

chmod +x update.sh backup.sh

echo -e "${BLUE}Installation files prepared!${NC}"
echo -e "${BLUE}Next steps:${NC}"
echo "1. Copy .env.prod.template to .env.prod and fill in your values"
echo "2. Update nginx/conf.d/app.conf with your domain name"
echo "3. Run: docker-compose pull"
echo "4. Run: docker-compose up -d"
echo "5. Optional: Setup SSL with: sudo certbot --nginx -d your_domain"
echo -e "${BLUE}For SSL setup, make sure your domain is pointing to this server first!${NC}" 