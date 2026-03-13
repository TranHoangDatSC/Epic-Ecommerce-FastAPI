# OldShop E-commerce Platform

A full-stack e-commerce platform built with FastAPI (backend) and Angular (frontend), featuring PostgreSQL database and comprehensive moderator tools.

## 🚀 Quick Start

### Automated Setup (Recommended)

Run the automated setup script:

```bash
python setup_project.py
```

This will:
- Copy `.env.example` to `.env`
- Create Python virtual environment and install dependencies
- Install Node.js dependencies
- Start PostgreSQL database with Docker
- Provide next steps

### Manual Setup

1. **Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

2. **Database**
   ```bash
   docker-compose up -d
   # Adminer available at http://localhost:8080
   ```

3. **Backend**
   ```bash
   cd backend
   python -m venv venv
   # On Windows: venv\Scripts\activate
   # On Linux/Mac: source venv/bin/activate
   pip install -r requirements.txt
   python -m uvicorn app.main:app --reload
   ```

4. **Frontend**
   ```bash
   cd frontend
   npm install
   npm start
   ```

## 📁 Project Structure

```
oldshop-ecommerce/
├── backend/                 # FastAPI backend
│   ├── app/                # Application code
│   ├── requirements.txt    # Python dependencies
│   └── .env.example       # Environment template
├── frontend/               # Angular frontend
│   └── src/
├── database/               # Database setup scripts
├── docker-compose.yml      # PostgreSQL + Adminer
├── .env.example           # Root environment template
└── setup_project.py       # Automated setup script
```

## 🔧 Environment Variables

### Database Configuration
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/oldshop
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=oldshop
```

### Authentication
```env
SECRET_KEY=your-secret-key-change-this-in-production-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Server Settings
```env
DEBUG=True
LOG_LEVEL=INFO
API_V1_STR=/api/v1
PROJECT_NAME=OldShop API
PROJECT_VERSION=1.0.0
```

## 🗄️ Database

- **PostgreSQL**: Port 5432
- **Adminer**: http://localhost:8080 (Database UI)
- **Init Script**: Automatically runs on first startup

## 🛠️ Development

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Frontend**: http://localhost:4200
- **Database UI**: http://localhost:8080

## 📋 Requirements

- **Python**: 3.12+
- **Node.js**: 18+
- **Docker**: For database
- **PostgreSQL**: 15+ (via Docker)

## 🔐 Security Notes

- Change `SECRET_KEY` in production
- Update database credentials
- Use strong passwords
- Enable SSL in production

## 🤝 Contributing

1. Clone the repository
2. Run `python setup_project.py`
3. Edit `.env` with your settings
4. Start developing!

## 📚 Documentation

- [Backend API Docs](backend/README.md)
- [Database Setup](database/README.md)
- [Frontend Guide](frontend/README.md)