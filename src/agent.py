import json
import os

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

from scoring import (
    calculate_score_breakdown,
    classify_lead,
    determine_next_action
)


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()


# ==========================================
# CONNECT TO GROQ
# ==========================================

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


# ==========================================
# ANALYZE ONE LEAD
# ==========================================

def analyze_lead(lead):
    """
    Use the LLM to extract purchase-intent
    signals from one lead.

    The LLM does NOT calculate the final score
    and does NOT determine the next action.
    """

    lead_text = f"""
Name: {lead['name']}
Company: {lead['company']}
Job Title: {lead['job_title']}
Industry: {lead['industry']}
Company Size: {lead['company_size']}
Requirement: {lead['requirement']}
Budget: {lead['budget']}
Timeline: {lead['timeline']}
Source: {lead['source']}
Message: {lead['message']}
"""


    prompt = f"""
You are a Lead Qualification Agent.

Analyze the following inbound sales lead.

Your role is to extract ONLY purchase-intent
signals from the lead.

Evaluate:

1. Purchase intent
2. Timeline urgency
3. Whether a demo or sales contact was requested
4. Engagement level

IMPORTANT RULES:

- Use ONLY information explicitly provided.
- Do not invent information.
- Do not assume product pricing.
- Do not determine whether the budget is sufficient.
- Do not determine industry fit.
- Do not determine company-size fit.
- Do not determine lead-source quality.
- Do not calculate the final score.
- Do not recommend a sales action.
- The Python system will calculate the score.
- The Python system will determine the next action.
- If information is missing, use "unknown".
- Return ONLY valid JSON.
- Do not use markdown.
- Do not include text outside JSON.

Return exactly this structure:

{{
    "purchase_intent": "high/medium/low/unknown",
    "timeline_urgency": "high/medium/low/unknown",
    "demo_requested": true,
    "engagement_level": "high/medium/low/unknown",
    "reason": "brief explanation based only on the lead"
}}

Lead information:

{lead_text}
"""


    # ======================================
    # CALL LLM
    # ======================================

    response = client.responses.create(
        model="openai/gpt-oss-20b",
        input=prompt
    )


    ai_output = response.output_text


    # ======================================
    # PARSE JSON
    # ======================================

    try:

        qualification = json.loads(
            ai_output
        )


        return qualification


    except json.JSONDecodeError:

        print(
            f"\nCould not parse AI response "
            f"for {lead['name']}"
        )

        print(
            "\nRaw AI response:"
        )

        print(
            ai_output
        )

        return None


# ==========================================
# QUALIFY ALL LEADS
# ==========================================

def qualify_leads(leads):
    """
    Analyze, score, classify and rank
    all provided leads.
    """

    results = []


    # ======================================
    # PROCESS EACH LEAD
    # ======================================

    for _, lead in leads.iterrows():

        print(
            f"\nAnalyzing: "
            f"{lead['name']}..."
        )


        # ----------------------------------
        # AI ANALYSIS
        # ----------------------------------

        qualification = analyze_lead(
            lead
        )


        if qualification is None:

            continue


        # ----------------------------------
        # SCORE BREAKDOWN
        # ----------------------------------

        breakdown = calculate_score_breakdown(
            lead,
            qualification
        )


        score = breakdown[
            "total_score"
        ]


        # ----------------------------------
        # CLASSIFY
        # ----------------------------------

        tier = classify_lead(
            score
        )


        # ----------------------------------
        # NEXT ACTION
        # ----------------------------------

        next_action = determine_next_action(
            lead,
            qualification,
            tier
        )


        # ----------------------------------
        # STORE RESULT
        # ----------------------------------

        results.append({

            # Lead information
            "name": lead["name"],

            "company": lead["company"],

            "job_title": lead["job_title"],

            "industry": lead["industry"],

            "company_size": lead["company_size"],

            "requirement": lead["requirement"],

            "budget": lead["budget"],

            "timeline": lead["timeline"],

            "source": lead["source"],


            # Scores
            "score": score,

            "fit_score": breakdown[
                "fit_score"
            ],

            "intent_score": breakdown[
                "intent_score"
            ],

            "commercial_score": breakdown[
                "commercial_score"
            ],


            # Classification
            "tier": tier,


            # AI explanation
            "reason": qualification[
                "reason"
            ],


            # Python-generated action
            "next_action": next_action
        })


    # ======================================
    # CREATE RESULT DATAFRAME
    # ======================================

    results_df = pd.DataFrame(
        results
    )


    # ======================================
    # SORT RESULTS
    # ======================================

    if not results_df.empty:

        results_df = results_df.sort_values(
            by="score",
            ascending=False
        )


        # ----------------------------------
        # ADD RANK
        # ----------------------------------

        results_df.insert(
            0,
            "rank",
            range(
                1,
                len(results_df) + 1
            )
        )


    return results_df