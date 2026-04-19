import asyncio
import random
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

async def run_upi_agent(profile_data: dict, document_text: str = ""):
    if document_text and "GEMINI_API_KEY" in os.environ and os.environ["GEMINI_API_KEY"] != "your_api_key_here":
        try:
            # We use an async wrapper or run_in_executor for the blocking API call
            loop = asyncio.get_event_loop()
            model = genai.GenerativeModel('gemini-2.5-flash')
            prompt = f"""
            You are a financial analyst. Read the following text extracted from user documents (likely containing a bank statement).
            Extract the 'average monthly income' as an integer and evaluate a 'spending discipline' score from 1 to 10 (10 being best).
            Provide a short 'explanation' for the score.
            Return ONLY a valid JSON object with keys: "average_income", "variance_score", "spending_discipline", "explanation".
            Text: {document_text[:3000]}
            """
            
            def get_gemini_response():
                response = model.generate_content(prompt)
                return response.text.strip("```json").strip("```").strip()
                
            response_text = await loop.run_in_executor(None, get_gemini_response)
            return json.loads(response_text)
        except Exception as e:
            print("Gemini API error in UPI Agent:", e)
            # Fallback to mock if API fails

    # Mock analysis of UPI data
    await asyncio.sleep(random.uniform(1, 2))
    income = profile_data.get("upi_income", random.randint(15000, 60000))
    return {
        "average_income": income,
        "variance_score": random.randint(1, 10),
        "spending_discipline": random.randint(1, 10),
        "explanation": f"Consistent daily inflow indicating healthy business activity. Estimated monthly average is ₹{income}."
    }
