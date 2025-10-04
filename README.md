# Flask CRM System 🚀

**Enterprise-grade Customer Relationship Management system** built with Flask, featuring modern UI/UX inspired by Salesforce and LeadSquared.

## ✨ Features

### Core CRM Functionality
- 📊 **Dashboard Analytics** - Real-time metrics and KPIs
- 👥 **Contact Management** - Comprehensive contact database
- 🎯 **Lead Management** - Lead capture, scoring, and nurturing
- 💼 **Deal Pipeline** - Visual sales pipeline with drag-and-drop
- 📈 **Activity Tracking** - Complete activity timeline
- 📝 **Notes & Logs** - Rich text notes with attachments

### Communication Features
- 📧 **Email Integration** - SendGrid/SMTP integration
- 📱 **SMS Notifications** - Twilio SMS integration
- 🔔 **Push Notifications** - Firebase Cloud Messaging
- 💬 **Internal Chat** - Real-time team communication
- 📞 **Call Logging** - Track all customer interactions

### Automation & Intelligence
- ⏰ **Reminders & Tasks** - Smart task management
- 🤖 **Lead Scoring** - Automated lead qualification
- 📊 **Reports & Analytics** - Customizable reports
- 🔄 **Workflow Automation** - Custom workflows
- 📤 **Data Export** - CSV/Excel export functionality

### Security & Access
- 🔐 **Role-based Access Control** - Admin, Manager, User roles
- 🔒 **Secure Authentication** - Password hashing and JWT tokens
- 👤 **User Management** - Team member administration

## 🛠️ Technology Stack

- **Backend**: Flask (Python 3.9+)
- **Database**: PostgreSQL / SQLite
- **Real-time**: Flask-SocketIO
- **Task Queue**: Celery + Redis
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **UI Framework**: Custom CSS with modern design patterns
- **Icons**: Font Awesome

## 📋 Prerequisites

- Python 3.9 or higher
- PostgreSQL 12+ (or SQLite for development)
- Redis (for Celery tasks)
- Node.js (optional, for frontend build tools)

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/vikkysarswat/flask-crm-system.git
cd flask-crm-system
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the root directory:
```env
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///crm.db
# For PostgreSQL: postgresql://username:password@localhost/crm_db

# Email Configuration (SendGrid)
MAIL_API_KEY=your-sendgrid-api-key
MAIL_DEFAULT_SENDER=noreply@yourcompany.com

# SMS Configuration (Twilio)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Push Notifications (Firebase)
FCM_SERVER_KEY=your-firebase-server-key

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0

# Application Settings
APP_NAME=CRM System
APP_URL=http://localhost:5000
```

### 5. Initialize database
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. Create admin user
```bash
python create_admin.py
```

### 7. Run the application
```bash
# Development
python run.py

# Production with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### 8. Start Celery worker (in separate terminal)
```bash
celery -A app.celery worker --loglevel=info
```

Access the application at: `http://localhost:5000`

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

## 🌐 Nginx Configuration

Create `/etc/nginx/sites-available/crm`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:5000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /static {
        alias /path/to/flask-crm-system/app/static;
        expires 30d;
    }
}
```

Enable and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/crm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 📁 Project Structure

```
flask-crm-system/
├── app/
│   ├── __init__.py           # App factory
│   ├── models/               # Database models
│   ├── routes/               # Route blueprints
│   ├── services/             # Business logic
│   ├── utils/                # Helper functions
│   ├── static/               # CSS, JS, images
│   └── templates/            # Jinja2 templates
├── migrations/               # Database migrations
├── tests/                    # Unit tests
├── config.py                 # Configuration
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
└── README.md
```

## 🔧 Configuration

Edit `config.py` to customize:
- Database settings
- Email/SMS providers
- Security settings
- Feature flags

## 🧪 Testing

```bash
pytest tests/
```

## 📊 Default Login

After running `create_admin.py`:
- **Email**: admin@crm.com
- **Password**: admin123 (change immediately!)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 Code Style

- Follows PEP 8 guidelines
- Docstrings in English and Hinglish
- Type hints where applicable
- Comprehensive comments

## 🔒 Security

- All passwords are hashed using bcrypt
- CSRF protection enabled
- SQL injection protection via SQLAlchemy ORM
- XSS protection in templates
- Rate limiting on sensitive endpoints

## 📄 License

MIT License - feel free to use for personal and commercial projects!

## 🙏 Acknowledgments

Inspired by leading CRM platforms:
- Salesforce
- LeadSquared
- HubSpot
- Zoho CRM

## 📧 Support

For issues and questions, please open a GitHub issue.

---

**Built with ❤️ using Flask**