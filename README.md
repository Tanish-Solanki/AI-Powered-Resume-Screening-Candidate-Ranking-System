# AI-Powered Resume Screening & Candidate Ranking System

## Overview

An intelligent Resume Screening and Candidate Ranking platform that leverages Natural Language Processing (NLP), Semantic Search, and Machine Learning to automate candidate evaluation against job descriptions.

The system extracts skills from resumes, generates semantic embeddings using Sentence Transformers, computes candidate-job similarity scores, and ranks applicants based on relevance to hiring requirements.

This project aims to reduce manual screening effort and improve recruitment efficiency by providing data-driven candidate recommendations.

---

## Features

### Resume Processing

* Parse resumes in PDF, DOCX, and TXT formats
* Extract textual content automatically
* Batch resume processing support

### Skill Extraction

* Named Entity Recognition (NER) using SpaCy
* Technical skill identification
* Experience and qualification extraction

### Semantic Matching

* Sentence Transformer-based embeddings
* Context-aware resume-job comparison
* Semantic similarity scoring

### Candidate Ranking

* Automated candidate ranking
* Relevance-based scoring
* Top candidate recommendations

### Analytics Dashboard

* Job description management
* Candidate ranking visualization
* Recruitment insights dashboard

### Export Support

* CSV export
* PDF report generation

---

## System Architecture

```text
Resume Upload
      │
      ▼
Resume Parsing
(PDF/DOCX/TXT)
      │
      ▼
Skill Extraction
(SpaCy NER)
      │
      ▼
Sentence Embeddings
(all-MiniLM-L6-v2)
      │
      ▼
Semantic Similarity
(Cosine Similarity)
      │
      ▼
Candidate Ranking
      │
      ▼
Dashboard & Reports
```

---

## Tech Stack

### Frontend

* React.js
* Vite
* Tailwind CSS

### Backend

* FastAPI
* Python

### Database

* PostgreSQL

### Machine Learning & NLP

* Sentence Transformers
* SpaCy
* Scikit-learn
* NumPy
* Pandas

### Deployment

* Docker
* Docker Compose

---

## Project Structure

```text
root/
├── frontend/
│   ├── src/
│   └── public/
│
├── backend/
│   ├── app/
│   ├── evaluation/
│   ├── models/
│   └── services/
│
├── docs/
├── docker/
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## Machine Learning Pipeline

### 1. Resume Parsing

Resumes are extracted from uploaded documents and converted into structured text.

### 2. Skill Extraction

SpaCy Named Entity Recognition is used to identify:

* Technical Skills
* Programming Languages
* Frameworks
* Tools
* Qualifications

### 3. Semantic Embedding Generation

The system uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

to generate dense vector representations of:

* Resumes
* Job Descriptions

### 4. Similarity Computation

Cosine Similarity is calculated between resume and job embeddings.

```text
Similarity Score = Cosine(Resume Embedding, Job Embedding)
```

### 5. Candidate Ranking

Candidates are ranked in descending order based on semantic similarity scores.

---

## Evaluation Methodology

The ranking engine was evaluated using manually labeled relevance judgments.

### Relevance Scale

| Grade | Meaning             |
| ----- | ------------------- |
| 0     | Not Relevant        |
| 1     | Marginally Relevant |
| 2     | Relevant            |
| 3     | Highly Relevant     |

Human evaluators compared resumes against job descriptions and assigned relevance scores independently of model predictions.

---

## Evaluation Dataset

| Item              | Count |
| ----------------- | ----- |
| Job Descriptions  | 3     |
| Candidate Resumes | 10    |
| Resume-Job Pairs  | 30    |

Domains evaluated:

* Backend Python Development
* NLP & Machine Learning
* Full Stack Web Development

---

## Evaluation Metrics

Industry-standard Information Retrieval (IR) metrics were used:

### Precision@K

Measures how many candidates in the top-K recommendations are relevant.

### Recall@K

Measures how many relevant candidates were successfully retrieved.

### MAP (Mean Average Precision)

Measures overall ranking quality across all queries.

### MRR (Mean Reciprocal Rank)

Measures how quickly the first relevant candidate appears.

### NDCG@K

Measures ranking quality while considering the ordering of candidates.

---

## Results

### Aggregate Evaluation Results

| Metric      | Score       |
| ----------- | ----------- |
| Precision@5 | **86.67%**  |
| Recall@5    | **94.44%**  |
| NDCG@5      | **99.07%**  |
| MAP         | **99.21%**  |
| MRR         | **100.00%** |

### Key Findings

* Successfully retrieved nearly all relevant candidates.
* Ranked highly relevant candidates near the top positions.
* Achieved strong semantic matching performance across multiple job domains.

---

## Installation

### Prerequisites

* Python 3.11+
* Node.js 18+
* PostgreSQL 15+
* Docker

---

### Clone Repository

```bash
git clone <repository-url>
cd AI-Powered-Resume-Screening-Candidate-Ranking-System
```

---

### Backend Setup

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

python -m spacy download en_core_web_sm

uvicorn app.main:app --reload
```

---

### Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

---

## Docker Deployment

```bash
docker-compose up --build -d
```

Services:

| Service  | URL                        |
| -------- | -------------------------- |
| Frontend | http://localhost:5173      |
| API Docs | http://localhost:8000/docs |
| Database | localhost:5432             |

---

## API Documentation

Swagger UI:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

---

## Future Improvements

* Hybrid ranking model
* LLM-powered resume analysis
* Interview recommendation engine
* Skill gap analysis
* Candidate-job explainability
* Multi-language resume support
* Cloud deployment on AWS

---

## Applications

* Recruitment Automation
* Talent Acquisition
* Applicant Tracking Systems (ATS)
* Candidate Recommendation Engines
* HR Analytics Platforms

---

## License

MIT License

---

## Author

Tanish Solanki

Computer Science & Engineering Student

Machine Learning | NLP | Software Development
