from agent_config import ICP


# ==========================================
# FIT SCORE — 40 POINTS
# ==========================================

def calculate_fit_score(lead):
    """
    Calculate how well the lead fits the
    ideal customer profile.

    Maximum score: 40
    """

    score = 0

    # --------------------------------------
    # Industry — 10 points
    # --------------------------------------

    industry = str(
        lead.get("industry", "")
    ).strip()

    if industry in ICP["industries"]:
        score += 10

    # --------------------------------------
    # Company Size — 10 points
    # --------------------------------------

    try:
        company_size = int(
            lead.get("company_size", 0)
        )

        if (
            ICP["min_company_size"]
            <= company_size
            <= ICP["max_company_size"]
        ):
            score += 10

    except (ValueError, TypeError):
        pass

    # --------------------------------------
    # Requirement — 10 points
    # --------------------------------------

    requirement = str(
        lead.get("requirement", "")
    ).lower()

    target_requirements = [
        str(item).lower()
        for item in ICP["target_requirements"]
    ]

    if any(
        target in requirement
        for target in target_requirements
    ):
        score += 10

    # --------------------------------------
    # Decision Maker — 10 points
    # --------------------------------------

    job_title = str(
        lead.get("job_title", "")
    ).strip().lower()

    decision_maker_roles = [
        str(role).lower()
        for role in ICP["decision_maker_roles"]
    ]

    if job_title in decision_maker_roles:
        score += 10

    return score


# ==========================================
# INTENT SCORE — 40 POINTS
# ==========================================

def calculate_intent_score(qualification):
    """
    Calculate purchase intent.

    Maximum score: 40.
    """

    score = 0

    # --------------------------------------
    # Purchase Intent — 15 points
    # --------------------------------------

    purchase_intent = qualification.get(
        "purchase_intent",
        "unknown"
    )

    if purchase_intent == "high":
        score += 15

    elif purchase_intent == "medium":
        score += 8

    # --------------------------------------
    # Timeline Urgency — 10 points
    # --------------------------------------

    timeline_urgency = qualification.get(
        "timeline_urgency",
        "unknown"
    )

    if timeline_urgency == "high":
        score += 10

    elif timeline_urgency == "medium":
        score += 5

    # --------------------------------------
    # Demo Requested — 10 points
    # --------------------------------------

    if qualification.get(
        "demo_requested",
        False
    ) is True:
        score += 10

    # --------------------------------------
    # Engagement — 5 points
    # --------------------------------------

    engagement_level = qualification.get(
        "engagement_level",
        "unknown"
    )

    if engagement_level == "high":
        score += 5

    elif engagement_level == "medium":
        score += 3

    return score


# ==========================================
# COMMERCIAL SCORE — 20 POINTS
# ==========================================

def calculate_commercial_score(lead):
    """
    Calculate commercial quality.

    Maximum score: 20.
    """

    score = 0

    # --------------------------------------
    # Budget — 10 points
    # --------------------------------------

    budget = str(
        lead.get("budget", "")
    ).strip().lower()

    if budget not in [
        "",
        "nan",
        "unknown",
        "not specified"
    ]:
        score += 10

    # --------------------------------------
    # Lead Source — 10 points
    # --------------------------------------

    source_scores = {
        "website": 10,
        "referral": 10,
        "linkedin": 8,
        "google ads": 7,
        "instagram": 6
    }

    source = str(
        lead.get("source", "")
    ).strip().lower()

    score += source_scores.get(
        source,
        0
    )

    return score


# ==========================================
# COMPLETE SCORE BREAKDOWN
# ==========================================

def calculate_score_breakdown(
    lead,
    qualification
):
    """
    Calculate FIT, INTENT and COMMERCIAL
    scores and final score.
    """

    fit_score = calculate_fit_score(
        lead
    )

    intent_score = calculate_intent_score(
        qualification
    )

    commercial_score = calculate_commercial_score(
        lead
    )

    total_score = (
        fit_score
        + intent_score
        + commercial_score
    )

    # Keep score between 0 and 100
    total_score = max(
        0,
        min(
            total_score,
            100
        )
    )

    return {
        "fit_score": fit_score,
        "intent_score": intent_score,
        "commercial_score": commercial_score,
        "total_score": total_score
    }


# ==========================================
# CLASSIFY LEAD
# ==========================================

def classify_lead(score):
    """
    Convert numerical score into
    HOT / WARM / COLD.
    """

    if score >= 80:
        return "HOT"

    elif score >= 50:
        return "WARM"

    else:
        return "COLD"


# ==========================================
# DETERMINISTIC NEXT ACTION
# ==========================================

def determine_next_action(
    lead,
    qualification,
    tier
):
    """
    Determine the recommended next action
    using deterministic Python rules.

    The LLM does NOT generate the action.
    """

    # ======================================
    # CHECK MISSING INFORMATION FIRST
    # ======================================

    critical_fields = [
        "industry",
        "company_size",
        "job_title",
        "requirement",
        "budget",
        "timeline"
    ]

    missing_fields = 0

    for field in critical_fields:

        value = str(
            lead.get(field, "")
        ).strip().lower()

        if value in [
            "",
            "unknown",
            "not specified",
            "nan"
        ]:
            missing_fields += 1

    # If multiple important fields are
    # missing, request more information.
    #
    # This check happens BEFORE HOT/WARM/COLD
    # actions.

    if missing_fields >= 2:

        return (
            "Request additional information "
            "about the lead's requirements and timeline."
        )

    # ======================================
    # GET LLM SIGNALS
    # ======================================

    purchase_intent = qualification.get(
        "purchase_intent",
        "unknown"
    )

    demo_requested = qualification.get(
        "demo_requested",
        False
    )

    engagement_level = qualification.get(
        "engagement_level",
        "unknown"
    )

    # ======================================
    # HOT LEADS
    # ======================================

    if tier == "HOT":

        if demo_requested:

            return (
                "Schedule the requested demo "
                "and coordinate with the relevant team."
            )

        if purchase_intent == "high":

            return (
                "Contact the lead promptly "
                "and schedule a discovery call."
            )

        return (
            "Contact the lead promptly to understand "
            "requirements and next steps."
        )

    # ======================================
    # WARM LEADS
    # ======================================

    if tier == "WARM":

        if demo_requested:

            return (
                "Follow up on the demo request "
                "and schedule a suitable meeting."
            )

        if engagement_level == "high":

            return (
                "Send relevant information "
                "and schedule a discovery call."
            )

        return (
            "Send relevant information and follow up "
            "to understand the lead's requirements."
        )

    # ======================================
    # COLD LEADS
    # ======================================

    if tier == "COLD":

        return (
            "Nurture the lead with relevant information "
            "and follow up later."
        )

    # ======================================
    # FALLBACK
    # ======================================

    return (
        "Review the lead information and determine "
        "the appropriate follow-up."
    )