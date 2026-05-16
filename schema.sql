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
