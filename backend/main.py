# backend/main.py

import io
import os
import uuid
from typing import Annotated, List

import easyocr
import fitz
import google.generativeai as genai
import numpy as np
import psycopg2
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from PIL import Image
from pydantic import BaseModel
from services.corpus_api import (
    finalize_record,
    get_all_records,
    get_categories,
    get_current_user_id,
    get_user_contributions,
    login_for_access_token,
    upload_chunk,
)
from services.vector_store import (
    add_text_to_store,
    initialize_vector_store,
    search_store,
)

load_dotenv()

# --- Database and AI Service Initialization ---
DATABASE_URL = os.getenv("DATABASE_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

reader = easyocr.Reader(["en", "te"])


# --- Pydantic Models ---
class StatusResponse(BaseModel):
    status: str
    message: str


class Category(BaseModel):
    id: str
    name: str
    title: str


class Token(BaseModel):
    access_token: str
    token_type: str


class Blog(BaseModel):
    id: int
    record_id: str
    title: str
    content: str  # <-- RESTORED


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]


# --- FastAPI App ---
app = FastAPI(
    title="దిక్సూచి (Diksoochi) API",
    description="The backend API for the Diksoochi project with RAG Chatbot.",
    version="1.6.1",  # Version bump for fix
)


# --- Database Functions (RESTORED) ---
def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None


def init_db():
    """Initializes the blogs table in the Supabase database."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS blogs (
                id SERIAL PRIMARY KEY,
                record_id TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """
        )
        conn.commit()
        cursor.close()
        conn.close()


@app.on_event("startup")
async def startup_event():
    init_db()
    initialize_vector_store()


# --- AUTHENTICATION ENDPOINT ---
@app.post("/token", response_model=Token, tags=["Authentication"])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    token_data = await login_for_access_token(
        {"username": form_data.username, "password": form_data.password}
    )
    return token_data


# --- CHATBOT ENDPOINT ---
@app.post("/chat/", response_model=ChatResponse, tags=["AI"])
async def handle_chat(request: ChatRequest):
    context_docs = search_store(request.query)
    if not context_docs:
        return {
            "answer": "I'm sorry, I couldn't find any relevant information to answer your question.",
            "sources": [],
        }
    prompt_template = """
    You are a helpful assistant. Answer the question as detailed as possible based on the provided context.
    If the answer is not in the context, say "I don't have enough information to answer that."
    Context: {context}
    Question: {question}
    Answer:
    """
    prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest", temperature=0.3, google_api_key=GEMINI_API_KEY
    )
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    response = await chain.ainvoke(
        {"input_documents": context_docs, "question": request.query}
    )
    sources = [doc.metadata for doc in context_docs]
    return {"answer": response.get("output_text", ""), "sources": sources}


# --- Upload Endpoint ---
@app.post("/upload/", tags=["Files"])
async def create_upload_file(
    file: Annotated[UploadFile, File()],
    title: Annotated[str, Form()],
    category_id: Annotated[str, Form()],
    release_rights: Annotated[str, Form()],
):
    user_id = await get_current_user_id()
    upload_uuid = str(uuid.uuid4())
    file_content = await file.read()
    await file.seek(0)
    await upload_chunk(file=file, upload_uuid=upload_uuid, filename=file.filename)
    final_result = await finalize_record(
        title=title,
        category_id=category_id,
        user_id=user_id,
        upload_uuid=upload_uuid,
        filename=file.filename,
        content_type=file.content_type,
        release_rights=release_rights,
    )
    record_id = final_result.get("id")

    # OCR, AI Cleanup, and Saving
    raw_text = ""
    if file.content_type == "application/pdf":
        pdf_document = fitz.open(stream=io.BytesIO(file_content), filetype="pdf")
        all_text_parts = []
        for page in pdf_document:
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            ocr_result = reader.readtext(img_bytes, detail=0, paragraph=True)
            all_text_parts.extend(ocr_result)
        raw_text = "\n".join(all_text_parts)
    else:
        image = Image.open(io.BytesIO(file_content))
        ocr_result = reader.readtext(np.array(image), detail=0, paragraph=True)
        raw_text = "\n".join(ocr_result)

    if GEMINI_API_KEY and raw_text:
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        prompt = f"Correct the following OCR text... Return only the corrected text.\n\nRAW TEXT:\n---\n{raw_text}"
        response = model.generate_content(prompt)
        cleaned_text = response.text

        if record_id and cleaned_text:
            metadata = {
                "record_id": record_id,
                "title": title,
                "filename": file.filename,
            }
            add_text_to_store(cleaned_text, metadata)

            # Save to Supabase
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO blogs (record_id, title, content) VALUES (%s, %s, %s) ON CONFLICT (record_id) DO NOTHING",
                        (record_id, title, cleaned_text),
                    )
                    conn.commit()
                finally:
                    cursor.close()
                    conn.close()
    return final_result


# --- Other Endpoints ---
@app.get("/", response_model=StatusResponse, tags=["Status"])
async def read_root():
    return {"status": "ok", "message": "Welcome to the Diksoochi API!"}


@app.get("/categories/", response_model=List[Category], tags=["Categories"])
async def list_categories():
    return await get_categories()


@app.get("/users/me/contributions", tags=["Users"])
async def read_user_me_contributions():
    user_id = await get_current_user_id()
    return await get_user_contributions(user_id)


@app.get("/records/", tags=["Records"])
async def read_all_records():
    return await get_all_records()


# --- BLOG ENDPOINT (RESTORED) ---
@app.get("/blogs/", response_model=List[Blog], tags=["Blog"])
def get_all_blogs():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed.")
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, record_id, title, content FROM blogs ORDER BY created_at DESC"
        )
        blogs_raw = cursor.fetchall()
        blogs = [
            {"id": r[0], "record_id": r[1], "title": r[2], "content": r[3]}
            for r in blogs_raw
        ]
        return blogs
    finally:
        cursor.close()
        conn.close()
