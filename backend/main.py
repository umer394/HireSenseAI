from dotenv import load_dotenv
import os
from agents import Agent, OpenAIChatCompletionsModel, AsyncOpenAI,RunConfig
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from uuid import uuid4
from fastapi import Body
from screener import evaluate_cv
from pydantic import BaseModel
import PyPDF2
import io


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


async def extract_text_from_pdf(content: bytes) -> str:
    try:
        # Create a PDF reader object
        pdf_file = io.BytesIO(content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from each page
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return ""

@app.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...), job_title: str = Form(...)):
    content = await file.read()
    doc_id = str(uuid4())
    
    # Extract text based on file type
    if file.filename.lower().endswith('.pdf'):
        extracted_text = await extract_text_from_pdf(content)
    else:
        # For non-PDF files, try to decode as text
        try:
            extracted_text = content.decode("utf-8", errors="ignore")
        except:
            extracted_text = str(content)
    
    cv_collection.insert_one({
        "id": doc_id,
        "filename": file.filename,
        "job_title": job_title,
        "content": extracted_text,
        "score": "",
        "ai_summary": ""
    })

    return {"status": "uploaded successfully"}

class JobPrompt(BaseModel):
    job_prompt: str

@app.post("/screen-cvs")
async def screen(job_prompt: JobPrompt):
    cvs = list(cv_collection.find({}))
    results = []

    for cv in cvs:
        try:
            ai_response = await evaluate_cv(cv["content"], job_prompt.job_prompt)

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