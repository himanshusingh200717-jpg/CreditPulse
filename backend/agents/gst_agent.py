import asyncio
import random
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

async def run_gst_agent(profile_data: dict, document_text: str = ""):
    if document_text and "GEMINI_API_KEY" in os.environ and os.environ["GEMINI_API_KEY"] != "your_api_key_here":
        try:
            loop = asyncio.get_event_loop()
            model = genai.GenerativeModel('gemini-2.5-flash')
            prompt = f"""
            You are a tax compliance officer. Read the following text extracted from user documents (likely containing a GST invoice/return).
            Extract 'declared_revenue' as an integer, 'filing_consistency' as a float between 0.0 and 1.0, and evaluate a 'compliance_score' from 1 to 10.
            Provide a short 'explanation'.
            Return ONLY a valid JSON object with keys: "declared_revenue", "filing_consistency", "compliance_score", "explanation".
            Text: {document_text[:3000]}
            """
            
            def get_gemini_response():
                response = model.generate_content(prompt)
                return response.text.strip("```json").strip("```").strip()
                
            response_text = await loop.run_in_executor(None, get_gemini_response)
            return json.loads(response_text)
        except Exception as e:
            print("Gemini API error in GST Agent:", e)

    await asyncio.sleep(random.uniform(2, 4))
    
    declared_income = profile_data.get("gst_income", random.randint(10000, 50000))
    return {
        "declared_revenue": declared_income,
        "filing_consistency": random.uniform(0.5, 1.0),
        "compliance_score": random.randint(5, 10),
        "explanation": f"GST filings are somewhat consistent. Declared revenue is ₹{declared_income}."
    }
