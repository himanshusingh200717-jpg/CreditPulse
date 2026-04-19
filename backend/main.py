from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
import json
import os
import shutil
import uuid
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Optional[Client] = None

if supabase_url and supabase_url != "your_supabase_url_here" and supabase_key and supabase_key != "your_supabase_service_role_key_here":
    try:
        supabase = create_client(supabase_url, supabase_key)
    except Exception as e:
        print("Failed to initialize Supabase:", e)

from orchestrator import run_orchestrator

app = FastAPI(title="CreditPulse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BorrowerRequest(BaseModel):
    name: str
    age: int
    profession: str
    city: str
    consent: bool
    document_paths: Optional[List[str]] = []

class ExportRequest(BaseModel):
    borrower_name: str
    profession: str
    score_data: Dict[str, Any]

def background_supabase_upload(file_path: str, local_path: str):
    if supabase:
        try:
            with open(local_path, "rb") as f:
                file_bytes = f.read()
            supabase.storage.from_("documents").upload(file_path, file_bytes)
        except Exception as e:
            print("Background Supabase upload failed:", e)

@app.post("/api/upload")
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # Always save locally first to guarantee fast response
    os.makedirs("uploads", exist_ok=True)
    local_path = f"uploads/{file.filename}"
    
    file_bytes = await file.read()
    with open(local_path, "wb") as buffer:
        buffer.write(file_bytes)
        
    file_path = f"{uuid.uuid4()}_{file.filename}"
    background_tasks.add_task(background_supabase_upload, file_path, local_path)
    
    return {"status": "success", "file_path": local_path, "filename": file.filename, "storage": "local"}

def background_supabase_db_insert(name, profession, city, result):
    if supabase:
        try:
            borrower_data = supabase.table("borrowers").insert({
                "name": name,
                "profession": profession,
                "city": city
            }).execute()
            
            if borrower_data.data:
                borrower_id = borrower_data.data[0]['id']
                supabase.table("credit_evaluations").insert({
                    "borrower_id": borrower_id,
                    "final_score": result["credit_score"]["score"],
                    "tier": result["credit_score"]["tier"],
                    "full_json_result": result
                }).execute()
        except Exception as e:
            print("Background Supabase DB insertion failed:", e)

@app.post("/api/score")
async def generate_score(request: BorrowerRequest, background_tasks: BackgroundTasks):
    if not request.consent:
        raise HTTPException(status_code=400, detail="Consent is required")
        
    try:
        # Load mock personas
        with open("data/personas.json", "r") as f:
            personas = json.load(f)
            
        profile_data = personas.get("default", {})
        for p_name, p_data in personas.items():
            if request.profession.lower() in p_name.lower():
                profile_data = p_data
                break
                
        result = await run_orchestrator(profile_data, request.document_paths)
        
        # Fire and forget DB insertion
        background_tasks.add_task(background_supabase_db_insert, request.name, request.profession, request.city, result)

        
        return {
            "status": "success",
            "borrower": {
                "name": request.name,
                "profession": request.profession,
                "city": request.city
            },
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def remove_file(path: str):
    try:
        os.remove(path)
    except:
        pass

@app.post("/api/export")
async def export_pdf(request: ExportRequest, background_tasks: BackgroundTasks):
    filename = f"uploads/report_{uuid.uuid4().hex[:8]}.pdf"
    
    # Generate PDF
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, 750, "CreditPulse Official Score Report")
    
    c.setFont("Helvetica", 14)
    c.drawString(50, 710, f"Borrower: {request.borrower_name}")
    c.drawString(50, 690, f"Profession: {request.profession}")
    
    score_info = request.score_data.get("credit_score", {})
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 650, f"Final Score: {score_info.get('score', 'N/A')}")
    c.drawString(250, 650, f"Tier: {score_info.get('tier', 'N/A')}")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, 620, f"Explanation:")
    c.setFont("Helvetica-Oblique", 11)
    
    # wrap text simply
    explanation = score_info.get("explanation_summary", "N/A")
    words = explanation.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) < 80:
            current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    
    y = 600
    for line in lines:
        c.drawString(50, y, line)
        y -= 20
        
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y - 20, "Agent Insights:")
    y -= 45
    
    c.setFont("Helvetica", 11)
    agents = request.score_data.get("agent_outputs", {})
    for agent_name, data in agents.items():
        c.drawString(50, y, f"- {agent_name.upper()} Agent: {data.get('explanation', '')[:80]}...")
        y -= 20
        
    c.save()
    
    # Clean up file after sending
    background_tasks.add_task(remove_file, filename)
    
    return FileResponse(filename, media_type="application/pdf", filename=f"CreditPulse_{request.borrower_name.replace(' ', '_')}.pdf")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
