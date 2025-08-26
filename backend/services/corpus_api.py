# backend/services/corpus_api.py

import httpx
from core.settings import settings
from fastapi import HTTPException, UploadFile

# --- API Endpoints ---
BASE_URL = settings.CORPUS_API_BASE_URL
FINALIZE_UPLOAD_URL = f"{BASE_URL}/api/v1/records/upload"
CHUNK_UPLOAD_URL = f"{BASE_URL}/api/v1/records/upload/chunk"
CATEGORIES_URL = f"{BASE_URL}/api/v1/categories/"
ME_URL = f"{BASE_URL}/api/v1/auth/me"
TOKEN_URL = f"{BASE_URL}/api/v1/auth/login"
CONTRIBUTIONS_URL = f"{BASE_URL}/api/v1/users/{{user_id}}/contributions"
RECORDS_URL = f"{BASE_URL}/api/v1/records/"


# --- (All other functions like login, get_categories, etc. remain the same) ---
async def login_for_access_token(form_data: dict) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            api_payload = {
                "phone": form_data["username"],
                "password": form_data["password"],
            }
            response = await client.post(TOKEN_URL, json=api_payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Login failed: {e.response.text}",
            ) from e


def get_media_type(content_type: str) -> str:
    if content_type.startswith("audio/"):
        return "audio"
    if content_type.startswith("video/"):
        return "video"
    if content_type.startswith("image/") or "pdf" in content_type:
        return "image"
    return "text"


async def get_current_user_id() -> str:
    async with httpx.AsyncClient() as client:
        try:
            if not settings.CORPUS_API_TOKEN:
                raise ValueError("CORPUS_API_TOKEN is not set.")
            headers = {"Authorization": f"Bearer {settings.CORPUS_API_TOKEN}"}
            response = await client.get(ME_URL, headers=headers)
            response.raise_for_status()
            return response.json().get("id")
        except Exception as e:
            raise HTTPException(
                status_code=401, detail="Could not verify current user."
            ) from e


async def get_categories() -> list:
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {settings.CORPUS_API_TOKEN}"}
            response = await client.get(CATEGORIES_URL, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise HTTPException(
                status_code=502, detail="Could not fetch categories."
            ) from e


async def get_user_contributions(user_id: str) -> list:
    async with httpx.AsyncClient() as client:
        try:
            if not settings.CORPUS_API_TOKEN:
                raise ValueError("CORPUS_API_TOKEN is not set.")
            headers = {"Authorization": f"Bearer {settings.CORPUS_API_TOKEN}"}
            url = CONTRIBUTIONS_URL.format(user_id=user_id)
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=502, detail="Failed to fetch user contributions."
            ) from e


async def get_all_records() -> list:
    async with httpx.AsyncClient() as client:
        try:
            if not settings.CORPUS_API_TOKEN:
                raise ValueError("CORPUS_API_TOKEN is not set.")
            headers = {"Authorization": f"Bearer {settings.CORPUS_API_TOKEN}"}
            response = await client.get(RECORDS_URL, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=502, detail="Failed to fetch public records."
            ) from e


async def upload_chunk(file: UploadFile, upload_uuid: str, filename: str):
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            data = {
                "upload_uuid": upload_uuid,
                "chunk_index": "0",
                "total_chunks": "1",
                "filename": filename,
            }
            files = {"chunk": (filename, file.file, file.content_type)}
            headers = {"Authorization": f"Bearer {settings.CORPUS_API_TOKEN}"}
            response = await client.post(
                CHUNK_UPLOAD_URL, data=data, files=files, headers=headers
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=502, detail=f"Chunk upload failed: {e.response.text}"
            ) from e


async def finalize_record(
    title: str,
    category_id: str,
    user_id: str,
    upload_uuid: str,
    filename: str,
    content_type: str,
    release_rights: str,
) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            payload = {
                "title": title,
                "category_id": category_id,
                "user_id": user_id,
                "media_type": get_media_type(content_type),
                "upload_uuid": upload_uuid,
                "filename": filename,
                "total_chunks": "1",
                "release_rights": release_rights,
            }
            headers = {"Authorization": f"Bearer {settings.CORPUS_API_TOKEN}"}
            response = await client.post(
                FINALIZE_UPLOAD_URL, data=payload, headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=502, detail=f"Finalization failed: {e.response.text}"
            ) from e
