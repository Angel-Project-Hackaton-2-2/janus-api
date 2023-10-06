from fastapi import FastAPI
from api.user import router as user_router
from api.conversation import router as conversation_router

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(user_router)
app.include_router(conversation_router)
