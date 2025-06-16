from dotenv import load_dotenv
import os
from agents import Agent, OpenAIChatCompletionsModel, AsyncOpenAI,RunConfig
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from uuid import uuid4
from fastapi import Body
from screener import evaluate_cv


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



@app.post("/upload-cv")
async def upload_cv(file:UploadFile = File(...),job_title: str = Form(...)):
    content = await file.read()
    doc_id = str(uuid4())
    print(job_title)
    cv_collection.insert_one({
        "id":doc_id,
        "filename":file.filename,
        "job_title":job_title,
        "content" : content.decode("utf-8",errors="ignore"),
        "score": "",
        "ai_summary": ""

    })

    return {"status" : "uploaded successfull"}

@app.post("/screen-cvs")
async def screen(job_prompt: str = Body(...)):
    cvs = list(cv_collection.find({}))
    results = []

    for cv in cvs:
        try:
            ai_response = await evaluate_cv(cv["content"], job_prompt)

            # You can parse score if your AI response format is fixed
            result = {
                "id": cv["id"],
                "filename": cv["filename"],
                "job_title": cv["job_title"],
                "score_and_reason": ai_response
            }

            results.append(result)
        except Exception as e:
            results.append({"id": cv["id"], "error": str(e)})
    
    return {"ranked_cvs": results}