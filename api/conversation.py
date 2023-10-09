from fastapi import APIRouter, HTTPException, Request
from api import client
from dotenv import load_dotenv
import os
import openai
from models.semantic import calculate_embedding
from api.diary import get_diaries
from utils import vectorize_diary

load_dotenv()
openai.api_key = os.getenv("OPENAI_KEY")

router = APIRouter()


@router.post("/api/conversation/{fingerprint}/{type}")
async def create_conversation(request: Request, fingerprint: str, type: str):
    db = client.get_db()
    if type == "conversation":
        conversation_collections = db["conversations"]

        data = await request.json()
        if "conversation_type" not in data:
            return HTTPException(status_code=400, detail="Invalid request body")

        conversation_type = data["conversation_type"]

        if conversation_type not in ["friend", "counselor"]:
            return HTTPException(status_code=400, detail="Invalid request body")

        conversation = conversation_collections.find_one(
            {"fingerprint": fingerprint, "type": conversation_type}
        )

        if conversation is not None:
            return HTTPException(status_code=400, detail="Conversation already exists")

        first_conversation = "Hello! What brings you here today?"
        if conversation_type == "friend":
            first_conversation = "Hi, How are you?"

        conversation_collections.insert_one(
            {
                "fingerprint": fingerprint,
                "conversation_type": conversation_type,
                "messages": [{"role": "assistant", "content": first_conversation}],
            }
        )
    elif type == "diary":
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


@router.post("/api/conversation/{fingerprint}/{conversation_type}/{type}")
async def create_message(
    request: Request, fingerprint: str, conversation_type: str, type: str
):
    db = client.get_db()
    if type == "conversation":
        conversation_collections = db["conversations"]

        # validation for text messages
        data = await request.json()
        if "message" not in data:
            return HTTPException(status_code=400, detail="Invalid request body")
        message = data["message"]

        if not isinstance(message, str):
            return HTTPException(status_code=400, detail="Invalid request body")

        conversation = conversation_collections.find_one(
            {"fingerprint": fingerprint, "conversation_type": conversation_type}
        )

        if conversation is None:
            # create conversation if not exists
            conversation_collections.insert_one(
                {
                    "fingerprint": fingerprint,
                    "conversation_type": conversation_type,
                    "messages": [
                        {
                            "role": "assistant",
                            "content": "Hello! What brings you here today?",
                        }
                    ],
                }
            )

        conversation = conversation_collections.find_one(
            {"fingerprint": fingerprint, "conversation_type": conversation_type}
        )

        new_message = {"role": "user", "content": message}
        # insert the message into mongodb
        messages = conversation["messages"]
        messages.append(new_message)

        if conversation_type == "friend":
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a bestfriend, and someone who is always there to support you, can understand and feel what you're going through, and you are active listener",
                    }
                ]
                + messages,
            )
        else:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a very good counselor, friendly and full of empathy. You have a great ability to easily understand someone's emotions and you are active listener",
                    }
                ]
                + messages,
            )

        new_message = {
            "role": "assistant",
            "content": response["choices"][0]["message"]["content"],
        }

        # insert the message into mongodb
        messages = conversation["messages"]
        messages.append(new_message)

        conversation_collections.update_one(
            {"_id": conversation["_id"]}, {"$set": {"messages": messages}}
        )
    elif type == "diary":
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

        diary = await get_diaries(fingerprint)
        diary = vectorize_diary(diary)
        response = calculate_embedding(diary, message)

        prompt_collections.update_one(
            {"fingerprint": fingerprint},
            {
                "$push": {
                    "messages": {"role": "assistant", "content": response["content"]}
                }
            },
        )
    return {
        "status": "success",
        "status_code": 200,
        "data": {"role": "assistant", "content": response["content"]},
    }


@router.get("/api/conversation/{fingerprint}/{conversation_type}")
async def get_conversastion(fingerprint: str, conversation_type: str):
    db = client.get_db()
    conversation_collections = db["conversations"]

    conversation = conversation_collections.find_one(
        {"fingerprint": fingerprint, "conversation_type": conversation_type}
    )

    if conversation is None:
        return HTTPException(status_code=400, detail="Conversation not found")

    conversation["_id"] = str(conversation["_id"])
    return {"status": "success", "status_code": 200, "data": conversation}
