# site-rw2 (Site rewrite 2)

## Overview

Site for training stuff.

---

## Prerequisites

- Python 3.13+  
- `pip` package manager  
- Redis server (optional, for rate limiting in production)  
- Gunicorn  
- Nginx (optional, for production reverse proxy)  
- Ngrok (optional, for tunneling)

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/rikemannen/site-rw2.git
cd site-rw2
````

### 2. Create and activate virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Running Locally (Development)

Run Flask app with built-in server (not for production):

```bash
export FLASK_APP=app
export FLASK_ENV=development
flask run
```

---

## Running with Gunicorn (Production)

### Basic Gunicorn command:

```bash
gunicorn -k eventlet -w 1 -b 0.0.0.0:8000 app:app
```

* `-k eventlet`: async worker for Socket.IO support
* `-w 1`: number of worker processes
* `-b 0.0.0.0:8000`: bind to all interfaces on port 8000
* `app:app`: import `app` instance from `app/__init__.py`

---

## Using Ngrok for External Access

1. [Download and install ngrok](https://ngrok.com/download).

2. Run ngrok to tunnel port 8000:

```bash
ngrok http 8000
```

3. Copy the generated public URL (e.g., `https://abc123.ngrok.io`) and open it in your browser.

---

## Production Setup with Nginx (Optional)

### 1. Install Nginx

```bash
sudo apt update
sudo apt install nginx
```

### 2. Configure Nginx to reverse proxy to Gunicorn

Create `/etc/nginx/sites-available/yourproject`:

```nginx
server {
    listen 80;
    server_name your_domain_or_IP;

    location /static/ {
        alias /path/to/your/project/app/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support for Socket.IO
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 3. Enable the site and restart Nginx

```bash
sudo ln -s /etc/nginx/sites-available/yourproject /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Notes

* Make sure your Flask app config sets `SECRET_KEY` and session security settings.
* Use Redis or another backend for Flask-Limiter in production (configure `RATELIMIT_STORAGE_URI`).
* Serve static files via Nginx, not Flask, in production.
* Use HTTPS in production (set up certificates with Let's Encrypt or other CA).

---

## Troubleshooting

* If you can't access via LAN IP, ensure Gunicorn binds to `0.0.0.0`.
* For Socket.IO issues, ensure Gunicorn uses `eventlet` or `gevent` worker class.
* Check firewall and router settings if external access fails.

---