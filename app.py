from fastapi import FastAPI
from api.user import router as user_router
from api.conversation import router as conversation_router
from api.diary import router as diary_router, get_diaries
from api.query import router as prompt_router
from dotenv import load_dotenv
from utils import vectorize_diary
from models.semantic import calculate_embedding

load_dotenv()

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/test/{fingerprint}")
async def test(fingerprint: str):
    diary = await get_diaries(fingerprint)
    diary = vectorize_diary(diary)
    response = calculate_embedding(diary, "What did i get for my 18th birthday?")
    return {"response": response}


app.include_router(user_router)
app.include_router(conversation_router)
app.include_router(diary_router)
app.include_router(prompt_router)
