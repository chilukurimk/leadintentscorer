
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
    """Accept a CSV file with lead details."""
    # Placeholder: parse CSV in next step
    leads.clear()
    return {"message": "Leads file uploaded."}

@app.post("/score")
def score_leads():
    """Run scoring pipeline on uploaded leads."""
    # Placeholder: implement scoring in next step
    results.clear()
    return {"message": "Scoring complete."}

@app.get("/results")
def get_results():
    """Return scored leads as JSON array."""
    return results
