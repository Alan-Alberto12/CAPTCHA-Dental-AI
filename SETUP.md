# Setup Instructions

## Prerequisites

- Docker and Docker Compose installed
- Git installed
- (Optional for local development) Node.js 18+ and Python 3.11+

## Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CAPTCHA-Dental-AI
   ```

2. **Build and start all services**
   ```bash
   docker-compose up --build
   ```

3. **Access the applications**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Database: localhost:5432

4. **Stop the services**
   ```bash
   docker-compose down
   ```

## Local Development Setup

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the backend**
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Run the frontend**
   ```bash
   npm start
   ```

## Database Setup

The PostgreSQL database is automatically configured when using Docker Compose.

For manual setup:
- Create a PostgreSQL database with credentials matching your `.env` file
- Update `DATABASE_URL` in your environment variables

## Development Workflow

### Making Changes

1. **Backend changes**: Edit files in `backend/`, the server will auto-reload
2. **Frontend changes**: Edit files in `frontend/src/`, React will hot-reload
3. **Database changes**: Use Alembic for migrations (to be configured)

### Running Tests

**Backend tests:**
```bash
cd backend
pytest
```

**Frontend tests:**
```bash
cd frontend
npm test
```

## Project Structure

```
CAPTCHA-Dental-AI/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile          # Backend container configuration
│   └── .env.example        # Environment variables template
├── frontend/
│   ├── src/                # React source code
│   ├── public/             # Static assets
│   ├── package.json        # Node dependencies
│   └── Dockerfile          # Frontend container configuration
├── docker-compose.yml      # Multi-container Docker configuration
└── .env.example           # Root environment variables
```

## Troubleshooting

### Port conflicts
If ports 3000, 8000, or 5432 are already in use, modify the port mappings in `docker-compose.yml`

### Permission issues on Linux
```bash
sudo chown -R $USER:$USER .
```

### Database connection issues
Ensure PostgreSQL service is healthy:
```bash
docker-compose ps
```

### Frontend can't reach backend
Check that CORS origins are configured correctly in `backend/main.py`

## Next Steps

- Configure database models and migrations
- Add authentication system
- Implement dental image upload and processing
- Set up CI/CD pipeline
- Deploy to production environment
