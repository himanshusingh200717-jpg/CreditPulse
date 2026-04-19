import asyncio
import random

async def resolve_conflicts(agent_outputs: dict):
    await asyncio.sleep(random.uniform(1, 2))
    
    upi_income = agent_outputs["upi"]["average_income"]
    gst_income = agent_outputs["gst"]["declared_revenue"]
    
    conflict = abs(upi_income - gst_income) > 10000
    reconciled = (upi_income * 0.7) + (gst_income * 0.3)
    
    return {
        "conflict_detected": conflict,
        "reconciled_income": int(reconciled),
        "reliability_weight": random.randint(70, 95),
        "reasoning": f"Weighted reconciliation applied. UPI shows ₹{upi_income} vs GST ₹{gst_income}. Higher weight given to actual bank inflows (UPI) due to common under-reporting in GST for this segment." if conflict else "No major conflicts detected between data sources."
    }
