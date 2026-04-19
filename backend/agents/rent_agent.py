import asyncio
import random
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

async def run_rent_agent(profile_data: dict, document_text: str = ""):
    if document_text and "GEMINI_API_KEY" in os.environ and os.environ["GEMINI_API_KEY"] != "your_api_key_here":
        try:
            loop = asyncio.get_event_loop()
            model = genai.GenerativeModel('gemini-2.5-flash')
            prompt = f"""
            You are a real estate analyst. Read the following text extracted from user documents (likely containing a rent agreement or utility bill).
            Extract the 'payment_streak_months' (how many months continuous residence/payment, guess if needed based on date) and evaluate a 'stability_score' from 1 to 10 (10 being highly stable).
            Also estimate 'tenancy_duration_months'. Provide a short 'explanation'.
            Return ONLY a valid JSON object with keys: "payment_streak_months", "stability_score", "tenancy_duration_months", "explanation".
            Text: {document_text[:3000]}
            """
            
            def get_gemini_response():
                response = model.generate_content(prompt)
                return response.text.strip("```json").strip("```").strip()
                
            response_text = await loop.run_in_executor(None, get_gemini_response)
            return json.loads(response_text)
        except Exception as e:
            print("Gemini API error in Rent Agent:", e)
            # Fallback to mock if API fails

    await asyncio.sleep(random.uniform(1, 2))
    streak = profile_data.get("rent_streak", random.randint(6, 24))
    return {
        "payment_streak_months": streak,
        "stability_score": random.randint(6, 10),
        "tenancy_duration_months": streak + random.randint(0, 12),
        "explanation": f"Strong indicators of stability with a {streak}-month continuous on-time rent payment streak."
    }
