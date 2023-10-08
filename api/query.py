from fastapi import APIRouter, HTTPException, Request
from api import client
from dotenv import load_dotenv
import os
import openai

load_dotenv()
router = APIRouter()


@router.post("/api/prompt/{fingerprint}")
async def create_prompt(fingerprint: str):
    db = client.get_db()
    prompt_collections = db["prompts"]

    prompt = prompt_collections.find_one({"fingerprint": fingerprint})

    if prompt is not None:
        return HTTPException(status_code=400, detail="Prompt already exists")

    first_prompt = "Hey, what do you need me to find?"
    prompt_collections.insert_one(
        {
            "fingerprint": fingerprint,
            "messages": [
                {
                    "role": "assistant",
                    "content": first_prompt,
                }
            ],
        }
    )

    return {"status": "success", "status_code": 200}


@router.post("/api/prompt/{fingerprint}/insert")
async def insert_prompt(request: Request, fingerprint: str):
    db = client.get_db()
    prompt_collections = db["prompts"]

    data = await request.json()

    if "message" not in data:
        return HTTPException(status_code=400, detail="Invalid request body")

    message = data["message"]

    if not isinstance(message, str):
        return HTTPException(status_code=400, detail="Invalid request body")

    prompt = prompt_collections.find_one({"fingerprint": fingerprint})

    if prompt is None:
        return HTTPException(status_code=400, detail="Prompt does not exist")

    prompt_collections.update_one(
        {"fingerprint": fingerprint},
        {"$push": {"messages": {"role": "user", "content": message}}},
    )

    return {"status": "success", "status_code": 200}
