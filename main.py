
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
    """Run rule-based and AI scoring on uploaded leads."""
    import os
    import openai
    results.clear()
    if not offers or not leads:
        return {"error": "No offer or leads uploaded."}
    offer = offers[-1]  # Use the latest offer
    icp = set([x.lower() for x in offer.ideal_use_cases])
    openai.api_key = os.getenv("OPENAI_API_KEY")
    for lead in leads:
        rule_score = 0
        # Role relevance
        role = lead.role.lower()
        if any(x in role for x in ["head", "chief", "vp", "director", "founder", "owner"]):
            rule_score += 20
        elif any(x in role for x in ["manager", "lead", "influencer"]):
            rule_score += 10
        # Industry match
        industry = lead.industry.lower()
        if any(x in industry for x in icp):
            rule_score += 20
        elif any(x in industry for x in ["saas", "software", "tech", "startup"]):
            rule_score += 10
        # Data completeness
        if all([lead.name, lead.role, lead.company, lead.industry, lead.location, lead.linkedin_bio]):
            rule_score += 10
        # AI Layer
        prompt = (
            f"Product/Offer: {offer.name}\n"
            f"Value Props: {', '.join(offer.value_props)}\n"
            f"Ideal Use Cases: {', '.join(offer.ideal_use_cases)}\n"
            f"Lead: {lead.name}, Role: {lead.role}, Company: {lead.company}, Industry: {lead.industry}, Location: {lead.location}, LinkedIn Bio: {lead.linkedin_bio}\n"
            "Classify intent (High/Medium/Low) and explain in 1–2 sentences."
        )
        ai_intent = "Low"
        ai_reasoning = "AI not available."
        ai_points = 10
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            ai_text = response.choices[0].message.content.strip()
            # Parse intent and reasoning
            if "high" in ai_text.lower():
                ai_intent = "High"
                ai_points = 50
            elif "medium" in ai_text.lower():
                ai_intent = "Medium"
                ai_points = 30
            else:
                ai_intent = "Low"
                ai_points = 10
            # Extract reasoning (after intent label)
            ai_reasoning = ai_text
        except Exception as e:
            ai_reasoning = f"AI error: {str(e)}"
        final_score = rule_score + ai_points
        results.append({
            "name": lead.name,
            "role": lead.role,
            "company": lead.company,
            "intent": ai_intent,
            "score": final_score,
            "reasoning": ai_reasoning
        })
    return {"message": "Scoring complete.", "count": len(results)}

@app.get("/results")
def get_results():
    """Return scored leads as JSON array."""
    return results

@app.get("/results/csv")
def export_results_csv():
    """Export scored leads as CSV file."""
    import pandas as pd
    from fastapi.responses import StreamingResponse
    if not results:
        return {"error": "No results to export."}
    df = pd.DataFrame(results)
    csv_data = df.to_csv(index=False)
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=results.csv"}
    )