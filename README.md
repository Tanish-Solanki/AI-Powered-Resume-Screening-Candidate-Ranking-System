# AI-Powered Resume Screening & Candidate Ranking System

An intelligent resume screening platform that leverages NLP and machine learning to automate candidate evaluation, skill extraction, and ranking against job descriptions.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React.js + Tailwind CSS + Vite |
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| AI/NLP | Sentence Transformers + SpaCy + Scikit-learn |
| Deployment | Docker + Docker Compose |

## Project Structure

```
root/
├── frontend/          # React.js frontend application
├── backend/           # FastAPI backend application
├── docker/            # Docker configuration files
├── docs/              # Project documentation
├── docker-compose.yml # Multi-container orchestration
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Getting Started

### Prerequisites

- Node.js >= 18.x
- Python >= 3.11
- PostgreSQL >= 15
- Docker & Docker Compose

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd enginow1
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   uvicorn app.main:app --reload
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Docker Production Deployment (Full Stack)**
   The application is fully containerized bounding the React Nginx Frontend, FastAPI backend, and PostgreSQL database seamlessly scaling across networks natively.
   
   To boot up safely ensuring Alembic database migrations trigger seamlessly:
   ```bash
   docker-compose up --build -d
   ```
   
   Services will locally resolve at:
   - **Frontend UI**: `http://localhost:5173`
   - **Backend API Docs**: `http://localhost:8000/docs`
   - **Database**: `localhost:5432`

```bash
cp .env.example .env
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Features

- Resume parsing (PDF, DOCX, TXT)
- AI-powered skill extraction using SpaCy NER
- Semantic similarity matching with Sentence Transformers
- Candidate ranking and scoring with Scikit-learn
- Job description management
- Dashboard analytics
- Batch resume processing
- Export results (CSV, PDF)

## License

MIT License
