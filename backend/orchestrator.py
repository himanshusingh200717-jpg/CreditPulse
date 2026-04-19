import asyncio
import PyPDF2
import os
import io
from supabase import create_client, Client
from agents.upi_agent import run_upi_agent
from agents.gst_agent import run_gst_agent
from agents.rent_agent import run_rent_agent
from agents.social_agent import run_social_agent
from agents.conflict_resolver import resolve_conflicts

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client | None = None
if supabase_url and supabase_key and supabase_url != "your_supabase_url_here":
    try:
        supabase = create_client(supabase_url, supabase_key)
    except:
        pass

def extract_text_from_pdfs(document_paths):
    text = ""
    for path in document_paths:
        try:
            # We always have a local path now
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error reading {path}: {e}")
    return text

async def run_orchestrator(profile_data: dict, document_paths: list = None):
    document_text = ""
    if document_paths:
        document_text = extract_text_from_pdfs(document_paths)

    # Execute all 4 agents in parallel, passing the document text
    upi_task = asyncio.create_task(run_upi_agent(profile_data, document_text))
    gst_task = asyncio.create_task(run_gst_agent(profile_data, document_text))
    rent_task = asyncio.create_task(run_rent_agent(profile_data, document_text))
    social_task = asyncio.create_task(run_social_agent(profile_data)) # Social might still be mock or need text
    
    results = await asyncio.gather(upi_task, gst_task, rent_task, social_task)
    
    agent_outputs = {
        "upi": results[0],
        "gst": results[1],
        "rent": results[2],
        "social": results[3]
    }
    
    # Pass to Conflict Resolver
    resolution = await resolve_conflicts(agent_outputs)
    
    # Calculate Score
    # Example logic: base score 300, max 900
    # Add weights based on resolved income, stability, compliance
    score = 300
    
    # 1. Income score (up to 200 pts)
    resolved_income = resolution["reconciled_income"]
    income_pts = min(200, (resolved_income / 100000) * 200) 
    
    # 2. Stability score (up to 200 pts)
    stability = agent_outputs["social"]["job_stability"] + agent_outputs["rent"]["stability_score"]
    stability_pts = min(200, stability * 20)
    
    # 3. Compliance & Discipline (up to 200 pts)
    compliance = agent_outputs["gst"]["compliance_score"] + agent_outputs["upi"]["spending_discipline"]
    compliance_pts = min(200, compliance * 10)
    
    final_score = int(score + income_pts + stability_pts + compliance_pts)
    final_score = min(900, max(300, final_score))
    
    # Determine Tier
    tier = "E"
    if final_score >= 800: tier = "A"
    elif final_score >= 700: tier = "B"
    elif final_score >= 600: tier = "C"
    elif final_score >= 500: tier = "D"
    
    return {
        "agent_outputs": agent_outputs,
        "conflict_resolution": resolution,
        "credit_score": {
            "score": final_score,
            "tier": tier,
            "confidence_band": "High" if resolution["reliability_weight"] > 80 else "Medium",
            "explanation_summary": "Score based on strong UPI transaction history and stable rent payments, despite minor discrepancies in declared GST."
        }
    }
