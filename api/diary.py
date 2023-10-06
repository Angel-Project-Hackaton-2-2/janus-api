from fastapi import APIRouter, HTTPException, Request
from api import client
from datetime import date

router = APIRouter()


@router.post("/api/diary/{fingerprint}")
async def create_diary(request: Request, fingerprint: str):
    db = client.get_db()
    diary_collections = db["diaries"]

    data = await request.json()

    if "content" not in data:
        return HTTPException(status_code=400, detail="Invalid request body")

    content = data["content"]

    if not isinstance(content, str):
        return HTTPException(status_code=400, detail="Invalid request body")

    diary = diary_collections.find_one({"fingerprint": fingerprint})

    if diary is not None:
        return HTTPException(status_code=400, detail="Diary already exists")

    diary_collections.insert_one(
        {
            "fingerprint": fingerprint,
            "diaries": [
                {"content": content, "timestamp": date.today().strftime("%Y-%m-%d")}
            ],
        }
    )
    return {"status": "success", "status_code": 200}


@router.post("/api/diary/{fingerprint}/insert")
async def insert_diary(request: Request, fingerprint: str):
    db = client.get_db()
    diary_collections = db["diaries"]

    data = await request.json()

    if "content" not in data:
        return HTTPException(status_code=400, detail="Invalid request body")

    content = data["content"]

    if not isinstance(content, str):
        return HTTPException(status_code=400, detail="Invalid request body")

    diary = diary_collections.find_one({"fingerprint": fingerprint})

    if diary is None:
        return HTTPException(status_code=400, detail="Diary does not exist")

    diary_collections.update_one(
        {"fingerprint": fingerprint},
        {
            "$push": {
                "diaries": {
                    "content": content,
                    "timestamp": date.today().strftime("%Y-%m-%d"),
                }
            },
        },
    )
    return {"status": "success", "status_code": 200}
