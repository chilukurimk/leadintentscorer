
import pytest
from leadintentscorer.scoring import Lead, rule_score

def test_decision_maker_exact_icp():
    lead = Lead(name="Ava Patel", role="Head of Growth", company="FlowMetrics", industry="B2B SaaS mid-market", location="NY", linkedin_bio="Bio")
    icp = ["b2b saas mid-market"]
    assert rule_score(lead, icp) == 50

def test_influencer_adjacent():
    lead = Lead(name="Ben Lee", role="Marketing Manager", company="TechFlow", industry="SaaS", location="SF", linkedin_bio="Bio")
    icp = ["b2b saas mid-market"]
    assert rule_score(lead, icp) == 30

def test_missing_fields():
    lead = Lead(name="", role="Analyst", company="FlowMetrics", industry="Finance", location="NY", linkedin_bio="")
    icp = ["finance"]
    assert rule_score(lead, icp) == 0
