import hmac
import hashlib
import os
import json
from fastapi import APIRouter, Request, HTTPException


router = APIRouter()

SECRET = os.getenv("GITLAB_SECRET")

@router.post("/webhook")
async def handle_webhook(request: Request):
    signature = request.headers.get("X-Gitlab-Token")
    body = await request.body()

    if signature != SECRET:
        raise HTTPException(403, "Invalid GitLab Token")

    payload = json.loads(body)
    return await process_webhook(payload)

async def process_webhook(payload: dict):
    event = payload.get("object_kind")
    if event == "push":
        user_id = extract_user_from_payload(payload)
        repo_url = payload['repository']['git_http_url']
        return {"status": "Triggering deployment", "repo_url": repo_url}
