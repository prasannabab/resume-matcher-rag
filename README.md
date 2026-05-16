# resume-matcher-rag
Developed an AI Resume Matcher using RAG that lets users upload a resume once and dynamically test it against various job descriptions. The system generates a precise compatibility score alongside a comprehensive AI Recruiter Analysis detailing key skill alignment, candidate strengths, and targeted areas for improvement.

# Resume RAG Matcher

A fully local AI-powered Resume RAG (Retrieval-Augmented Generation) system using:

- FastAPI
- PostgreSQL + pgvector
- FAISS (optional vector store)
- Ollama
- nomic-embed-text embeddings
- Local LLMs like llama3 / phi3

This project:

- Uploads resumes
- Splits resumes into chunks
- Generates embeddings
- Stores vectors in pgvector or FAISS
- Retrieves top matching resume chunks
- Matches resumes against Job Descriptions
- Uses local Ollama LLMs for recruiter-style analysis
- Runs completely offline

---

# Features

## Resume Upload

Supports:

- PDF
- DOCX

---

## Semantic Resume Search

- Resume chunking
- Embedding generation
- Vector similarity search
- Top-k chunk retrieval

---

## AI Recruiter Analysis

The local LLM analyzes:

- Resume relevance
- Experience match
- Skill alignment
- Missing qualifications
- Hiring recommendation
- Match score

---

## Fully Local AI Stack

No OpenAI APIs.

Everything runs locally using Ollama.

---

# Architecture

```text
Resume Upload
    ↓
PDF/DOCX Parsing
    ↓
Resume Chunking
    ↓
Ollama Embeddings
    ↓
Vector Storage
(pgvector / FAISS)
    ↓
Job Description Embedding
    ↓
Top-k Retrieval
    ↓
Prompt Augmentation
    ↓
Local LLM Analysis
    ↓
Final Recruiter Report
```

---

# Tech Stack

| Component | Technology |
|---|---|
| Backend | FastAPI |
| Vector DB | PostgreSQL + pgvector |
| Optional Vector Store | FAISS |
| Embeddings | nomic-embed-text |
| LLM Runtime | Ollama |
| LLMs | llama3 / phi3 |
| Frontend | Jinja2 HTML |
| Database ORM | SQLAlchemy |

---

# Project Structure

```text
resume-rag/
│
├── app/
│   ├── main.py
│   ├── db.py
│   ├── parser.py
│   ├── embedding.py
│   ├── chunker.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│
├── uploads/
├── requirements.txt
└── schema.sql
```

---

# Prerequisites

Install:

- Python 3.10+
- PostgreSQL
- pgvector extension
- Ollama

---

# Install Ollama

Official website:

https://ollama.com

---

# Pull Ollama Models

## Embedding Model

```bash
ollama pull nomic-embed-text
```

---

## LLM Models

### Option 1 — phi3 (Recommended for low RAM systems)

```bash
ollama pull phi3:mini
```

Best for:

- 8 GB RAM laptops
- Faster inference
- CPU-only systems
- Development environments

---

### Option 2 — llama3

```bash
ollama pull llama3
```

Best for:

- 16 GB+ RAM systems
- Better reasoning quality
- More accurate recruiter analysis

---

# Model Recommendation Based on System

| System RAM | Recommended Model |
|---|---|
| 8 GB | phi3:mini |
| 16 GB | llama3 |
| 32 GB+ | llama3 / qwen2.5 |
|
GPU Available | llama3 / mistral |

---

# Start Ollama

```bash
ollama serve
```

Verify models:

```bash
ollama list
```

---

# Install Python Dependencies

## requirements.txt

```txt
fastapi
uvicorn
jinja2
python-multipart
sqlalchemy
psycopg2-binary
requests
PyPDF2
python-docx
numpy
faiss-cpu
```

Install:

```bash
pip install -r requirements.txt
```

---

# PostgreSQL Setup

Create database:

```sql
CREATE DATABASE resumes;
```

Connect:

```bash
psql -U postgres -d resumes
```

---

# Enable pgvector

## schema.sql

```sql
CREATE EXTENSION IF NOT EXISTS vector;

DROP TABLE IF EXISTS resume_chunks;

CREATE TABLE resume_chunks (
    id SERIAL PRIMARY KEY,
    resume_id UUID,
    file_name TEXT,
    chunk_type TEXT,
    chunk_text TEXT,
    embedding vector(768)
);

CREATE INDEX resume_chunks_embedding_idx
ON resume_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

ANALYZE resume_chunks;
```

Run:

```bash
psql -U postgres -d resumes -f schema.sql
```

---

# Configure Database

## app/db.py

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/resumes"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
```

Update username/password if needed.

---

# Resume Chunking

The application:

- Splits resumes into sections
- Creates semantic chunks
- Generates embeddings for each chunk
- Stores chunk embeddings independently

This improves retrieval quality.

---

# Why Chunking Matters

Instead of embedding the full resume:

```text
One large embedding
```

We store:

```text
Skills chunk
Experience chunk
Projects chunk
Education chunk
```

This allows:

- Better semantic retrieval
- Smaller prompts
- Faster LLM analysis
- Higher match accuracy

---

# Ollama Embedding Configuration

## app/embedding.py

```python
import requests

OLLAMA_URL = "http://localhost:11434/api/embeddings"

MODEL_NAME = "nomic-embed-text"


def generate_embedding(text: str):

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": text,
            "keep_alive": "30m"
        }
    )

    response.raise_for_status()

    return response.json()["embedding"]
```

---

# Performance Optimization

Recommended settings:

| Setting | Recommended |
|---|---|
| top_k | 3 |
| chunk size | 300-500 chars |
| num_ctx | 1024 |
| keep_alive | 30m |
| model | phi3:mini |

---

# Why Use Top 3 Chunks

Using:

```text
LIMIT 3
```

improves:

- Speed
- Relevance
- Lower hallucinations
- Smaller prompt size

---

# Streaming Responses

Use streaming for faster UI response:

```python
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "phi3:mini",
        "prompt": llm_prompt,
        "stream": True,
        "keep_alive": "30m",
        "options": {
            "num_ctx": 1024
        }
    },
    stream=True
)
```

---

# Why keep_alive Is Important

Without:

```text
keep_alive
```

Ollama unloads models frequently.

This causes:

- Model reload delays
- Slow inference
- Higher RAM thrashing

Recommended:

```python
"keep_alive": "30m"
```

---

# FAISS Support (Optional)

You can optionally replace pgvector with FAISS.

Benefits:

- Faster local vector search
- No PostgreSQL dependency
- Simple local indexing

---

# Install FAISS

```bash
pip install faiss-cpu
```

---

# Example FAISS Usage

```python
import faiss
import numpy as np

index = faiss.IndexFlatL2(768)

vectors = np.array(embeddings).astype('float32')

index.add(vectors)
```

Search:

```python
D, I = index.search(query_vector, 3)
```

---

# pgvector vs FAISS

| Feature | pgvector | FAISS |
|---|---|---|
| Persistence | Yes | Manual |
| SQL Support | Yes | No |
| Distributed Support | Better | Limited |
| Performance | Good | Excellent |
| Setup | Medium | Simple |

---

# Run FastAPI Application

From project root:

```bash
uvicorn app.main:app --reload
```

---

# Open Browser

```text
http://localhost:8000
```

---

# UI Preview

![Resume RAG Matcher UI](Screenshot from 2026-05-16 22-18-51.png)

---

# Application Workflow

The application provides a simple recruiter-style AI workflow.

## Step 1 — Upload Resume

The user uploads the resume one time using:

- PDF
- DOCX

Once uploaded:

- Resume text gets extracted
- Resume is chunked semantically
- Embeddings are generated using Ollama
- Embeddings are stored in pgvector or FAISS

This becomes the searchable semantic resume database.

---

## Step 2 — Enter Job Description

The user can paste any job description into the Job Description textarea.

The application:

- Generates embedding for the Job Description
- Retrieves top matching resume chunks
- Sends retrieved resume context to the local LLM

---

## Step 3 — AI Recruiter Analysis

The system generates:

- Match score
- Resume relevance
- Skill alignment
- Missing qualifications
- Hiring recommendation
- AI recruiter analysis between Resume and Job Description

---

## Example User Flow

```text
Upload Resume (One-Time Activity)
        ↓
Store Resume Embeddings
        ↓
Paste Job Description
        ↓
Retrieve Best Resume Chunks
        ↓
AI Recruiter Analysis
        ↓
Match Score + Recommendation
```

---

# Example Flow

## Upload Resume

- Upload PDF/DOCX
- Resume gets chunked
- Embeddings generated
- Stored in pgvector

---

## Match Job Description

- Paste job description
- JD embedding generated
- Top matching chunks retrieved
- LLM generates recruiter analysis

---

# Example Recruiter Analysis

```text
Match Score: 82/100

Strengths:
- Strong backend development experience
- Kafka and microservices expertise
- FastAPI and PostgreSQL knowledge

Missing Qualifications:
- Limited cloud exposure
- No Kubernetes production experience

Recommendation:
Good Match
```

---

# Troubleshooting

## Template Not Found

Ensure structure:

```text
app/templates/index.html
```

---

## Ollama Slow Loading

Use:

```python
"keep_alive": "30m"
```

and:

```python
"num_ctx": 1024
```

---

## JSONDecodeError with Streaming

If using:

```python
"stream": True
```

Do NOT use:

```python
response.json()
```

Use:

```python
response.iter_lines()
```

---

## Low RAM Systems

Use:

```text
phi3:mini
```

instead of:

```text
llama3
```

---

# Future Improvements

Possible enhancements:

- Multi-resume support
- Resume ranking dashboard
- Candidate comparison
- Redis caching
- LangChain integration
- Hybrid search
- Metadata filtering
- Async embedding generation
- Streaming UI updates
- Docker support
- Kubernetes deployment
- JWT authentication
- Admin dashboard

---

# Production Recommendations

## Small Laptop

| Component | Recommendation |
|---|---|
| Model | phi3:mini |
| Context | 1024 |
| top_k | 3 |
| Chunk size | 300 |

---

## Powerful Machine

| Component | Recommendation |
|---|---|
| Model | llama3 |
| Context | 4096 |
| top_k | 5 |
| Chunk size | 500 |

---

# Summary

This project demonstrates a complete local AI Resume RAG system using:

- FastAPI
- Ollama
- pgvector
- FAISS
- nomic-embed-text
- llama3 / phi3

It provides:

- Semantic resume search
- Recruiter-style AI analysis
- Retrieval-Augmented Generation
- Fully local execution
- No cloud dependency
- No OpenAI cost

This architecture is close to production-grade semantic recruiting systems.

# Example:
job description: Python Software Developer
Larsen & Toubro (L&T)
3.923.9K Reviews
left wingmiddle wingEmployees' choiceright wing
Company Logo
5 - 7 years
Not Disclosed
Bengaluru, Mysuru
Send me jobs like this
Posted: 3 days ago
Openings: 1
Applicants: 100+
Save
Apply
Follow Larsen & Toubro (L&T) as you apply to stay updated
Company Logo
Python Software Developer
Larsen & Toubro (L&T)
3.923.9K Reviews
left wingmiddle wingEmployees' choiceright wing
Send me jobs like thisApply
Job highlights
Experience in Python development with expertise in Django, Flask, or FastAPI frameworks
Design, develop, test, and maintain Python applications and RESTful APIs; build data pipelines; collaborate with cross-functional teams; support CI/CD pipelines
Job match score
Early Applicant
Keyskills
Location
Work Experience
Job description
Role & responsibilities


Design, develop, test, and maintain applications using Python
Build RESTful APIs and backend services using frameworks such as Flask / FastAPI / Django
Develop data processing, automation, or ETL pipelines using Python
Write clean, efficient, reusable, and welldocumented code
Perform unit testing, debugging, and performance optimization
Work with databases and data storage systems for efficient data handling
Collaborate with architects, QA, DevOps, and product teams
Participate in code reviews, sprint planning, and technical discussions
Support deployments and CI/CD pipelines

Role: Back End Developer
Industry Type: Engineering & Construction
Department: Engineering - Software & QA
Employment Type: Full Time, Permanent
Role Category: Software Development
Education
UG: B.Tech / B.E. in Any Specialization
PG: MCA in Any Specialization
Key Skills
Skills highlighted with ‘‘ are preferred keyskills
DjangoFast ApiReact.JsPythonFlask
Python FrameworkSQL

RAG Response:
<img width="1842" height="1003" alt="Screenshot from 2026-05-16 22-42-53" src="https://github.com/user-attachments/assets/706926ce-b9bc-4140-9ea1-ffb70791a0d9" />

Over All UI:
<img width="1591" height="1000" alt="Screenshot from 2026-05-16 22-42-31" src="https://github.com/user-attachments/assets/3e75cdfb-3491-4a36-b820-2d96345f2259" />

