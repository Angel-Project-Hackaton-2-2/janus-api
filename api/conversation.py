from api import *


@router.post("/api/conversation/{fingerprint}/{conversation_type}")
async def create_message(request: Request, fingerprint: str, conversation_type):
    db = client.get_db()
    conversation_collections = db["conversations"]

    data = await request.json()
    if "message" not in data:
        return HTTPException(status_code=400, detail="Invalid request body")
