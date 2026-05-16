import os
import json
import uuid
import requests

from fastapi import (
    FastAPI,
    Request,
    UploadFile,
    File,
    Form
)

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy import text

from .db import SessionLocal
from .parser import parse_pdf, parse_docx
from .embedding import generate_embedding
from .chunker import chunk_resume

app = FastAPI()
import os

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

templates = Jinja2Templates(
         directory=os.path.join(
        BASE_DIR,
        "templates"
    )
)

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


@app.get(
    "/",
    response_class=HTMLResponse
)
async def home(request: Request):

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request
        }
    )


@app.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...)
):

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(file_path, "wb") as f:
        f.write(await file.read())

    if file.filename.endswith(".pdf"):

        content = parse_pdf(file_path)

    elif file.filename.endswith(".docx"):

        content = parse_docx(file_path)

    else:
        return {
            "error": "Only PDF/DOCX supported"
        }

    chunks = chunk_resume(content)

    resume_id = str(uuid.uuid4())

    db = SessionLocal()

    for chunk in chunks:

        embedding = generate_embedding(
            chunk["chunk_text"]
        )

        query = text("""
            INSERT INTO resume_chunks(
                resume_id,
                file_name,
                chunk_type,
                chunk_text,
                embedding
            )
            VALUES (
                :resume_id,
                :file_name,
                :chunk_type,
                :chunk_text,
                :embedding
            )
        """)

        db.execute(query, {
            "resume_id": resume_id,
            "file_name": file.filename,
            "chunk_type": chunk["chunk_type"],
            "chunk_text": chunk["chunk_text"],
            "embedding": str(embedding)
        })

    db.commit()

    return {
        "message": "Resume uploaded successfully",
        "chunks_stored": len(chunks)
    }


@app.post("/match-job")
async def match_job(
    request: Request,
    job_description: str = Form(...)
):
    #import pdb;pdb.set_trace()
    jd_embedding = generate_embedding(
        job_description
    )

    db = SessionLocal()

    query = text("""
        SELECT
            file_name,
            chunk_type,
            chunk_text,
            1 - (
                embedding <=>
                CAST(:embedding AS vector)
            ) AS similarity
        FROM resume_chunks
        ORDER BY embedding <=>
                 CAST(:embedding AS vector)
        LIMIT 5
    """)

    rows = db.execute(query, {
        "embedding": str(jd_embedding)
    }).fetchall()

    if not rows:

        return templates.TemplateResponse(
                request,
            "index.html",
            {
                "request": request,
                "error": "No resumes found"
            }
        )

    retrieved_context = ""

    matched_chunks = []

    for row in rows:

        score = round(
            row.similarity * 100,
            2
        )

        retrieved_context += f"""

        Section:
        {row.chunk_type}

        Content:
        {row.chunk_text}

        Similarity:
        {score}

        """

        matched_chunks.append({
            "chunk_type": row.chunk_type,
            "chunk_text": row.chunk_text,
            "score": score
        })

    llm_prompt = f"""
    You are an expert AI recruiter.

    Analyze the candidate based on
    the resume context and job description.

    JOB DESCRIPTION:
    {job_description}

    RETRIEVED RESUME CONTEXT:
    {retrieved_context}

    Provide:
    1. Match score out of 100
    2. Candidate strengths
    3. Missing qualifications
    4. Hiring recommendation
    5. Final summary

    Keep the response professional.
    """

    #import pdb;pdb.set_trace()
    print("coming to ollama")
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi3",
            "prompt": llm_prompt,
            "stream": True,
            "keep_alive": "1h"
        }
        
    )

    #llm_response = response.json()["response"]
    llm_response = ""
    for line in response.iter_lines():
        print(line)
        if line:
            data = json.loads(line)
            if "response" in data:
                llm_response += data["response"]
    #print(llm_response)

    return templates.TemplateResponse(
            request, 
        "index.html",
        {
            "request": request,
            "matched_chunks": matched_chunks,
            "llm_response": llm_response
        }
    )
