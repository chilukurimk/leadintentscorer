from pydantic import BaseModel
from typing import Optional

class Lead(BaseModel):
    name: str
    role: str
    company: str
    industry: str
    location: str
    linkedin_bio: Optional[str]

def rule_score(lead, icp):
    # Only score if all fields are present
    if not all([lead.name, lead.role, lead.company, lead.industry, lead.location, lead.linkedin_bio]):
        return 0
    score = 0
    role = lead.role.lower()
    if any(x in role for x in ["head", "chief", "vp", "director", "founder", "owner"]):
        score += 20
    elif any(x in role for x in ["manager", "lead", "influencer"]):
        score += 10
    industry = lead.industry.lower()
    if any(x in industry for x in icp):
        score += 20
    elif any(x in industry for x in ["saas", "software", "tech", "startup"]):
        score += 10
    score += 10  # Data completeness
    return score
