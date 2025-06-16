from dotenv import load_dotenv
import os
from agents import Agent, OpenAIChatCompletionsModel, AsyncOpenAI,RunConfig
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from uuid import uuid4
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client.hiresense
cv_collection = db.cvs


client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

config = RunConfig(
    model="gemini-1.5-flash",
    model_provider=client,
    tracing_disabled=True,
)

@app.post("/upload-cv")
async def upload_cv(file:UploadFile = File(...),job_title: str = Form(...)):
    content = await file.read()
    doc_id = str(uuid4())
    print(job_title)
    cv_collection.insert_one({
        "id":doc_id,
        "filename":file.filename,
        "job_title":job_title,
        "content" : content.decode("utf-8",errors="ignore")
    })

    return {"status" : "uploaded successfull"}