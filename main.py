
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class Offer(BaseModel):
    name: str
    value_props: List[str]
    ideal_use_cases: List[str]

class Lead(BaseModel):
    name: str
    role: str
    company: str
    industry: str
    location: str
    linkedin_bio: Optional[str]

class ScoredLead(BaseModel):
    name: str
    role: str
    company: str
    intent: str
    score: int
    reasoning: str

offers = []
leads = []
results = []

@app.get("/")
def read_root():
    """Root endpoint to verify API is running."""
    return {"message": "Lead Intent Scorer API is running."}

@app.post("/offer")
def create_offer(offer: Offer):
    """Accept product/offer details as JSON."""
    offers.append(offer)
    return {"message": "Offer received.", "offer": offer}

@app.post("/leads/upload")
async def upload_leads(file: UploadFile = File(...)):
    """Accept a CSV file with lead details and parse it into Lead objects."""
    import pandas as pd
    from io import StringIO
    leads.clear()
    content = await file.read()
    df = pd.read_csv(StringIO(content.decode()))
    for _, row in df.iterrows():
        lead = Lead(
            name=row.get("name", ""),
            role=row.get("role", ""),
            company=row.get("company", ""),
            industry=row.get("industry", ""),
            location=row.get("location", ""),
            linkedin_bio=row.get("linkedin_bio", "")
        )
        leads.append(lead)
    return {"message": f"{len(leads)} leads uploaded.", "count": len(leads)}

@app.post("/score")
def score_leads():
    """Run rule-based scoring on uploaded leads."""
    results.clear()
    if not offers or not leads:
        return {"error": "No offer or leads uploaded."}
    offer = offers[-1]  # Use the latest offer
    icp = set([x.lower() for x in offer.ideal_use_cases])
    for lead in leads:
        rule_score = 0
        # Role relevance
        role = lead.role.lower()
        if any(x in role for x in ["head", "chief", "vp", "director", "founder", "owner"]):
            rule_score += 20  # Decision maker
        elif any(x in role for x in ["manager", "lead", "influencer"]):
            rule_score += 10  # Influencer
        # Industry match
        industry = lead.industry.lower()
        if any(x in industry for x in icp):
            rule_score += 20  # Exact ICP
        elif any(x in industry for x in ["saas", "software", "tech", "startup"]):
            rule_score += 10  # Adjacent
        # Data completeness
        if all([lead.name, lead.role, lead.company, lead.industry, lead.location, lead.linkedin_bio]):
            rule_score += 10
        results.append({
            "name": lead.name,
            "role": lead.role,
            "company": lead.company,
            "intent": "Pending",
            "score": rule_score,
            "reasoning": "Rule-based score only. AI reasoning not yet applied."
        })
    return {"message": "Rule-based scoring complete.", "count": len(results)}

@app.get("/results")
def get_results():
    """Return scored leads as JSON array."""
    return results
