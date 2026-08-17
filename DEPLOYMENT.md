# Complete Deployment Guide - GlobalExportHub

This document provides step-by-step instructions to deploy your **GlobalExportHub** platform online to production cloud environments (Render, Railway, Docker, or a Linux VPS).

---

## Option A: Free Cloud Deployment via Render.com (Recommended for MVPs)

Render provides free hosting for Web Services and Managed MySQL databases.

### Step 1: Push Code to GitHub / GitLab
1. Create a new repository on GitHub (e.g. `exportweb-platform`).
2. Initialize git and push your project:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of Exporter B2B platform"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/exportweb-platform.git
   git push -u origin main
   ```

### Step 2: Create Managed Database on Render
1. Sign up on [Render.com](https://render.com).
2. Click **New +** -> **MySQL Database**.
3. Set Name: `exportweb-db` and select Free tier.
4. Once created, copy the **Internal Database URL** or **External Database URL**.

### Step 3: Create Web Service on Render
1. Click **New +** -> **Web Service**.
2. Connect your GitHub repository (`exportweb-platform`).
3. Set configuration:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python seed.py`
   - **Start Command**: `gunicorn wsgi:app`
4. Add **Environment Variables**:
   - `SECRET_KEY` = `your-secure-production-random-key`
   - `DATABASE_URL` = *(Paste the MySQL URL from Step 2)*
   - `USE_SQLITE_FALLBACK` = `False`
   - `CLOUDINARY_CLOUD_NAME` = *(Your Cloudinary Cloud Name)*
   - `CLOUDINARY_API_KEY` = *(Your Cloudinary API Key)*
   - `CLOUDINARY_API_SECRET` = *(Your Cloudinary API Secret)*
5. Click **Create Web Service**.
6. Render will build and deploy your live platform at `https://your-app-name.onrender.com`!

---

## Option B: Railway.app Deployment

1. Sign up on [Railway.app](https://railway.app).
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select your repository.
4. Click **+ New** -> **Database** -> **Add MySQL**.
5. In your web service settings, add environment variable `DATABASE_URL=${MySQL.MYSQL_URL}`.
6. Add `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`.
7. Railway auto-detects `Procfile` (`gunicorn wsgi:app`) and deploys your live site with HTTPS!

---

## Option C: Ubuntu Linux VPS (AWS EC2 / DigitalOcean / Hetzner)

If you are hosting on your own Linux server (Ubuntu 22.04 / 24.04):

### 1. System Packages & MySQL Setup
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv nginx mysql-server -y

# Secure MySQL setup
sudo mysql -e "CREATE DATABASE exportweb_db;"
sudo mysql -e "CREATE USER 'exportuser'@'localhost' IDENTIFIED BY 'YourStrongPassword123!';"
sudo mysql -e "GRANT ALL PRIVILEGES ON exportweb_db.* TO 'exportuser'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"
```

### 2. Clone Code & Virtual Environment
```bash
cd /var/www
sudo git clone https://github.com/YOUR_USERNAME/exportweb-platform.git exportweb
cd exportweb

sudo python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python seed.py
```

### 3. Create Systemd Service (`/etc/systemd/system/exportweb.service`)
```ini
[Unit]
Description=Gunicorn instance for GlobalExportHub B2B Platform
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/exportweb
Environment="PATH=/var/www/exportweb/venv/bin"
Environment="DATABASE_URL=mysql+pymysql://exportuser:YourStrongPassword123!@localhost:3306/exportweb_db"
Environment="SECRET_KEY=production_random_secret_key"
ExecStart=/var/www/exportweb/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 wsgi:app

[Install]
WantedBy=multi-user.target
```

Enable & start service:
```bash
sudo systemctl daemon-reload
sudo systemctl start exportweb
sudo systemctl enable exportweb
```

### 4. Configure Nginx Reverse Proxy (`/etc/nginx/sites-available/exportweb`)
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/exportweb/static/;
    }
}
```

Enable site & restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/exportweb /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Free SSL Certificate with Certbot
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## Option D: Docker Compose Deployment

If you prefer running via Docker Compose:

1. Create a `.env` file on your server with your Cloudinary keys.
2. Run:
   ```bash
   docker-compose up -d --build
   ```
3. Your platform will be running in Docker at `http://YOUR_SERVER_IP:5000`.

---

## Production Checklist

- [ ] Set `FLASK_ENV=production` and `DEBUG=False` in environment variables.
- [ ] Ensure a strong `SECRET_KEY` is specified.
- [ ] Add your actual Cloudinary API credentials (`CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`) in `.env`.
- [ ] Configure real SMTP email server settings (`MAIL_USERNAME`, `MAIL_PASSWORD`) for real email lead delivery.
