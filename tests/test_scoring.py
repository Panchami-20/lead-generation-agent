import sys
import os


# ==========================================
# FIND SRC FOLDER
# ==========================================

SRC_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "src"
    )
)

sys.path.insert(
    0,
    SRC_PATH
)


# ==========================================
# IMPORT SCORING FUNCTIONS
# ==========================================

from scoring import (
    calculate_fit_score,
    calculate_intent_score,
    calculate_commercial_score,
    calculate_score_breakdown,
    classify_lead,
    determine_next_action
)


# ==========================================
# HELPER FUNCTION
# ==========================================

def make_lead(
    industry="SaaS",
    company_size=300,
    requirement="AI customer support automation",
    job_title="CTO",
    budget="800000",
    timeline="2 weeks",
    source="Website"
):
    """
    Create a sample lead for testing.
    """

    return {
        "industry": industry,
        "company_size": company_size,
        "requirement": requirement,
        "job_title": job_title,
        "budget": budget,
        "timeline": timeline,
        "source": source
    }


# ==========================================
# CLASSIFICATION TESTS
# ==========================================

def test_hot_classification():

    assert classify_lead(80) == "HOT"
    assert classify_lead(100) == "HOT"


def test_warm_classification():

    assert classify_lead(50) == "WARM"
    assert classify_lead(79) == "WARM"


def test_cold_classification():

    assert classify_lead(0) == "COLD"
    assert classify_lead(49) == "COLD"


# ==========================================
# FIT TESTS
# ==========================================

def test_fit_score():

    lead = make_lead()

    score = calculate_fit_score(
        lead
    )

    assert score == 40


def test_missing_company_size():

    lead = make_lead(
        company_size="Unknown"
    )

    score = calculate_fit_score(
        lead
    )

    assert isinstance(
        score,
        int
    )


# ==========================================
# INTENT TESTS
# ==========================================

def test_high_intent_score():

    qualification = {
        "purchase_intent": "high",
        "timeline_urgency": "high",
        "demo_requested": True,
        "engagement_level": "high"
    }

    score = calculate_intent_score(
        qualification
    )

    assert score == 40


def test_low_intent_score():

    qualification = {
        "purchase_intent": "low",
        "timeline_urgency": "unknown",
        "demo_requested": False,
        "engagement_level": "low"
    }

    score = calculate_intent_score(
        qualification
    )

    assert score == 0


# ==========================================
# COMMERCIAL TEST
# ==========================================

def test_commercial_score():

    lead = make_lead()

    score = calculate_commercial_score(
        lead
    )

    assert score == 20


# ==========================================
# TOTAL SCORE TEST
# ==========================================

def test_total_score_range():

    lead = make_lead()

    qualification = {
        "purchase_intent": "high",
        "timeline_urgency": "high",
        "demo_requested": True,
        "engagement_level": "high"
    }

    breakdown = calculate_score_breakdown(
        lead,
        qualification
    )

    assert (
        0
        <= breakdown["total_score"]
        <= 100
    )


# ==========================================
# SCORE BREAKDOWN TEST
# ==========================================

def test_score_breakdown():

    lead = make_lead()

    qualification = {
        "purchase_intent": "high",
        "timeline_urgency": "high",
        "demo_requested": True,
        "engagement_level": "high"
    }

    breakdown = calculate_score_breakdown(
        lead,
        qualification
    )

    assert "fit_score" in breakdown
    assert "intent_score" in breakdown
    assert "commercial_score" in breakdown
    assert "total_score" in breakdown


# ==========================================
# NEXT ACTION — HOT
# ==========================================

def test_hot_next_action():

    lead = make_lead()

    qualification = {
        "purchase_intent": "high",
        "timeline_urgency": "high",
        "demo_requested": True,
        "engagement_level": "high"
    }

    action = determine_next_action(
        lead,
        qualification,
        "HOT"
    )

    assert "demo" in action.lower()


# ==========================================
# NEXT ACTION — WARM
# ==========================================

def test_warm_next_action():

    lead = make_lead()

    qualification = {
        "purchase_intent": "medium",
        "timeline_urgency": "medium",
        "demo_requested": False,
        "engagement_level": "high"
    }

    action = determine_next_action(
        lead,
        qualification,
        "WARM"
    )

    assert (
        "information" in action.lower()
        or "discovery" in action.lower()
    )


# ==========================================
# NEXT ACTION — COLD
# ==========================================

def test_cold_next_action():

    lead = make_lead()

    qualification = {
        "purchase_intent": "low",
        "timeline_urgency": "low",
        "demo_requested": False,
        "engagement_level": "low"
    }

    action = determine_next_action(
        lead,
        qualification,
        "COLD"
    )

    assert "nurture" in action.lower()


# ==========================================
# MISSING INFORMATION — SCORE
# ==========================================

def test_missing_information():

    lead = make_lead(
        industry="Unknown",
        company_size="Unknown",
        requirement="General AI solutions",
        job_title="Unknown",
        budget="Not specified",
        timeline="Not specified",
        source="Unknown"
    )

    qualification = {
        "purchase_intent": "unknown",
        "timeline_urgency": "unknown",
        "demo_requested": False,
        "engagement_level": "unknown"
    }

    breakdown = calculate_score_breakdown(
        lead,
        qualification
    )

    assert (
        0
        <= breakdown["total_score"]
        <= 100
    )


# ==========================================
# MISSING INFORMATION — ACTION
# ==========================================

def test_missing_information_action():

    lead = make_lead(
        industry="Unknown",
        company_size="Unknown",
        requirement="General AI solutions",
        job_title="Unknown",
        budget="Not specified",
        timeline="Not specified",
        source="Unknown"
    )

    qualification = {
        "purchase_intent": "unknown",
        "timeline_urgency": "unknown",
        "demo_requested": False,
        "engagement_level": "unknown"
    }

    action = determine_next_action(
        lead,
        qualification,
        "COLD"
    )

    assert (
        "request" in action.lower()
        or "information" in action.lower()
    )


# ==========================================
# MISSING BUDGET TEST
# ==========================================

def test_missing_budget():

    lead = make_lead(
        budget="Not specified"
    )

    score = calculate_commercial_score(
        lead
    )

    assert score >= 0
    assert score <= 20


# ==========================================
# UNKNOWN LEAD SOURCE TEST
# ==========================================

def test_unknown_source():

    lead = make_lead(
        source="Unknown"
    )

    score = calculate_commercial_score(
        lead
    )

    assert score >= 0
    assert score <= 20