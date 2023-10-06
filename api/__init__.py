from fastapi import APIRouter, HTTPException, Request
from db import MongoDBClient

router = APIRouter()
client = MongoDBClient()