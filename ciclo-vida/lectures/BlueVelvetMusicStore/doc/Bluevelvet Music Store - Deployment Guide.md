# Bluevelvet Music Store - Deployment Guide

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Database Management](#database-management)
6. [Monitoring and Logging](#monitoring-and-logging)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Operating System:** Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **Java:** OpenJDK 21 or higher
- **Maven:** 3.9 or higher
- **Docker:** 20.10 or higher
- **Docker Compose:** 2.0 or higher
- **MySQL:** 8.0 or higher (for local development)
- **Git:** 2.30 or higher

### Google OAuth2 Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google+ API
4. Create OAuth 2.0 credentials (Web Application)
5. Add authorized redirect URIs:
   - `http://localhost:8080/login/oauth2/code/google`
   - `http://localhost:8080/oauth2/callback`
   - `https://yourdomain.com/login/oauth2/code/google`
6. Copy Client ID and Client Secret

---

## Local Development

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/bluevelvet-music-store-enterprise.git
cd bluevelvet-music-store-enterprise
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env .env

# Edit with your values
nano .env
```

**Required environment variables:**

```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=bluevelvet_db
DB_USER=bluevelvet
DB_PASSWORD=your_secure_password

# OAuth2
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret

# Server
SERVER_PORT=8080
SPRING_PROFILES_ACTIVE=dev
```

### 3. Start MySQL (Docker)

```bash
docker run -d \
  --name bluevelvet-mysql \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -e MYSQL_DATABASE=bluevelvet_db \
  -e MYSQL_USER=bluevelvet \
  -e MYSQL_PASSWORD=your_secure_password \
  -p 3306:3306 \
  -v mysql_data:/var/lib/mysql \
  mysql:8.0
```

### 4. Initialize Database

```bash
# Connect to MySQL
mysql -h localhost -u bluevelvet -p bluevelvet_db < init-db.sql
```

### 5. Build and Run

```bash
# Build the project
mvn clean install

# Run the application
mvn spring-boot:run
```

### 6. Access the Application

- **Home:** http://localhost:8080
- **Categories:** http://localhost:8080/categories
- **Login:** http://localhost:8080/login
- **Swagger API:** http://localhost:8080/swagger-ui.html

---

## Docker Deployment

### 1. Build Docker Image

```bash
# Build the image
docker build -t bluevelvet-music-store:1.0.0 .

# Tag for registry
docker tag bluevelvet-music-store:1.0.0 your-registry/bluevelvet:1.0.0
```

### 2. Push to Registry

```bash
# Login to registry
docker login your-registry

# Push image
docker push your-registry/bluevelvet:1.0.0
```

### 3. Deploy with Docker Compose

```bash
# Create .env file
cp .env .env
nano .env

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app
```

### 4. Verify Deployment

```bash
# Health check
curl http://localhost:8080/actuator/health

# API test
curl http://localhost:8080/api/v1/categories/root
```

### 5. Stop Services

```bash
docker-compose down

# Remove volumes (careful!)
docker-compose down -v
```

---

## Production Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create app directory
sudo mkdir -p /opt/bluevelvet
sudo chown $USER:$USER /opt/bluevelvet
```

### 2. SSL/TLS Certificate

```bash
# Using Let's Encrypt with Certbot
sudo apt install certbot python3-certbot-nginx -y

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Certificate location
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

### 3. Nginx Configuration

Create `/etc/nginx/sites-available/bluevelvet`:

```nginx
upstream bluevelvet_app {
    server app:8080;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy Configuration
    location / {
        proxy_pass http://bluevelvet_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        proxy_pass http://bluevelvet_app;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
    gzip_vary on;
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/bluevelvet /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Deploy Application

```bash
cd /opt/bluevelvet

# Copy docker-compose.yml
cp /path/to/docker-compose.yml .

# Create .env
cat > .env << EOF
DB_HOST=mysql
DB_PORT=3306
DB_NAME=bluevelvet_db
DB_USER=bluevelvet
DB_PASSWORD=$(openssl rand -base64 32)
GOOGLE_CLIENT_ID=your_production_client_id
GOOGLE_CLIENT_SECRET=your_production_client_secret
SPRING_PROFILES_ACTIVE=prod
EOF

# Start services
docker-compose up -d

# Verify
docker-compose ps
```

### 5. Backup Strategy

```bash
# Daily MySQL backup
0 2 * * * /usr/local/bin/backup-mysql.sh

# Create backup script
cat > /usr/local/bin/backup-mysql.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
CONTAINER_ID=$(docker ps -q -f name=bluevelvet-mysql)

mkdir -p $BACKUP_DIR

docker exec $CONTAINER_ID mysqldump -u bluevelvet -ppassword bluevelvet_db | \
  gzip > $BACKUP_DIR/bluevelvet_db_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
EOF

chmod +x /usr/local/bin/backup-mysql.sh
```

### 6. Auto-renewal of SSL Certificate

```bash
# Certbot auto-renewal (runs twice daily)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Test renewal
sudo certbot renew --dry-run
```

---

## Database Management

### 1. Connect to Database

```bash
# From host
mysql -h localhost -u bluevelvet -p bluevelvet_db

# From Docker container
docker exec -it bluevelvet-mysql mysql -u bluevelvet -p bluevelvet_db
```

### 2. Database Migrations

```bash
# View current schema
SHOW TABLES;

# Add new table
ALTER TABLE categories ADD COLUMN new_column VARCHAR(255);

# Create index
CREATE INDEX idx_category_name ON categories(name);
```

### 3. Data Export/Import

```bash
# Export data
docker exec bluevelvet-mysql mysqldump -u bluevelvet -p bluevelvet_db > backup.sql

# Import data
docker exec -i bluevelvet-mysql mysql -u bluevelvet -p bluevelvet_db < backup.sql
```

---

## Monitoring and Logging

### 1. Application Logs

```bash
# View logs
docker-compose logs -f app

# View specific service
docker-compose logs -f mysql

# Last 100 lines
docker-compose logs --tail=100 app
```

### 2. Health Checks

```bash
# Application health
curl http://localhost:8080/actuator/health

# Database health
curl http://localhost:8080/actuator/health/db

# Metrics
curl http://localhost:8080/actuator/metrics
```

### 3. Performance Monitoring

```bash
# CPU and Memory usage
docker stats bluevelvet-app bluevelvet-mysql

# Disk usage
docker exec bluevelvet-mysql du -sh /var/lib/mysql
```

### 4. Log Aggregation (Optional)

Setup ELK Stack (Elasticsearch, Logstash, Kibana):

```yaml
# Add to docker-compose.yml
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
  environment:
    - discovery.type=single-node
  ports:
    - "9200:9200"

kibana:
  image: docker.elastic.co/kibana/kibana:8.0.0
  ports:
    - "5601:5601"
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed

```bash
# Check MySQL container
docker-compose ps mysql

# Check logs
docker-compose logs mysql

# Verify connection
docker exec bluevelvet-app curl mysql:3306

# Restart MySQL
docker-compose restart mysql
```

#### 2. OAuth2 Authentication Error

```bash
# Verify credentials in .env
cat .env | grep GOOGLE

# Check logs for error details
docker-compose logs app | grep -i oauth

# Verify redirect URI in Google Console
```

#### 3. Port Already in Use

```bash
# Find process using port 8080
lsof -i :8080

# Kill process
kill -9 <PID>

# Or use different port in docker-compose.yml
```

#### 4. Out of Memory

```bash
# Increase Docker memory limit
# Edit /etc/docker/daemon.json
{
  "memory": "4g",
  "memory-swap": "4g"
}

# Restart Docker
sudo systemctl restart docker
```

#### 5. SSL Certificate Error

```bash
# Check certificate validity
openssl x509 -in /etc/letsencrypt/live/yourdomain.com/fullchain.pem -text -noout

# Renew certificate
sudo certbot renew --force-renewal

# Restart Nginx
sudo systemctl restart nginx
```

### Debug Mode

```bash
# Enable debug logging
SPRING_PROFILES_ACTIVE=debug docker-compose up

# View detailed logs
docker-compose logs -f --tail=500 app
```

### Performance Tuning

```bash
# MySQL optimization
docker exec bluevelvet-mysql mysql -u root -p -e "
  SET GLOBAL max_connections = 1000;
  SET GLOBAL innodb_buffer_pool_size = 2G;
"

# Java heap size
# Edit docker-compose.yml
environment:
  - JAVA_OPTS=-Xmx2g -Xms1g
```

---

## Security Checklist

- [ ] Change default database password
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set strong OAuth2 credentials
- [ ] Enable database backups
- [ ] Configure log rotation
- [ ] Update Docker images regularly
- [ ] Use environment variables for secrets
- [ ] Enable audit logging
- [ ] Set up monitoring alerts

---

## Support and Resources

- [Spring Boot Documentation](https://spring.io/projects/spring-boot)
- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
- [MySQL Documentation](https://dev.mysql.com/doc/)

---

**Last Updated:** January 2025  
**Author:** Rafael Passos Domingues
