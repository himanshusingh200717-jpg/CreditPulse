import asyncio
import random

async def run_social_agent(profile_data: dict):
    await asyncio.sleep(random.uniform(1.5, 3.5))
    
    stability = profile_data.get("job_stability", random.randint(5, 10))
    return {
        "job_stability": stability,
        "professional_network_credibility": random.randint(4, 9),
        "work_continuity_score": random.randint(5, 10),
        "explanation": f"Professional networks indicate steady engagement within the gig economy ecosystem."
    }
