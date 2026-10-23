import streamlit as st
import pandas as pd
import os
import sys


# ============================================================
# PROJECT PATH
# ============================================================

SRC_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "src"
    )
)

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)


from agent import qualify_leads


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="LeadIQ | Lead Qualification",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PROFESSIONAL UI STYLE
# ============================================================

st.markdown(
    """
    <style>

    /* Main application */

    .stApp {
        background-color: #0f1117;
    }

    /* Content width */

    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Sidebar */

    section[data-testid="stSidebar"] {
        background-color: #151922;
        border-right: 1px solid #2a2f3a;
    }

    /* Headings */

    h1 {
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    h2 {
        font-weight: 650 !important;
    }

    h3 {
        font-weight: 600 !important;
    }

    /* Buttons */

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        min-height: 42px;
    }

    /* File uploader */

    [data-testid="stFileUploader"] {
        border-radius: 10px;
    }

    /* Divider */

    hr {
        border-color: #2a2f3a !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🎯 LeadIQ")

    st.caption(
        "AI Lead Qualification System"
    )

    st.divider()

    st.subheader("Lead Input")

    uploaded_file = st.file_uploader(
        "Upload Lead CSV",
        type=["csv"],
        help="Upload a CSV containing your lead information."
    )


    # ========================================================
    # LOAD UPLOADED LEADS
    # ========================================================

    if uploaded_file is not None:

        try:

            leads = pd.read_csv(
                uploaded_file
            )

            st.success(
                f"{len(leads)} leads loaded"
            )

        except pd.errors.EmptyDataError:

            st.error(
                "The uploaded CSV is empty."
            )

            st.stop()

        except Exception as error:

            st.error(
                f"Unable to read CSV: {error}"
            )

            st.stop()


    # ========================================================
    # SAMPLE LEADS
    # ========================================================

    else:

        sample_path = (
            "data/sample_leads.csv"
        )

        if os.path.exists(
            sample_path
        ):

            try:

                leads = pd.read_csv(
                    sample_path
                )

                st.info(
                    f"Using sample leads • {len(leads)} records"
                )

            except pd.errors.EmptyDataError:

                st.error(
                    "sample_leads.csv is empty."
                )

                st.stop()

        else:

            st.warning(
                "Upload a CSV to begin."
            )

            st.stop()


    st.divider()

    # ========================================================
    # AGENT INFORMATION
    # ========================================================

    st.subheader("Agent")

    run_agent = st.button(
        "🚀 Qualify Leads",
        width="stretch"
    )


    st.divider()

    st.caption("AI Engine")

    st.write(
        "GPT-OSS-20B via Groq"
    )

    st.caption("Decision Engine")

    st.write(
        "Deterministic Python scoring"
    )

    st.caption("Score Range")

    st.write(
        "0 – 100"
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.title(
    "🎯 Lead Qualification Agent"
)

st.write(
    "AI-powered analysis, scoring, ranking and "
    "prioritization of inbound sales leads."
)

st.caption(
    "LLM-based intent analysis combined with "
    "deterministic business rules."
)

st.divider()


# ============================================================
# RUN AGENT
# ============================================================

if run_agent:

    with st.spinner(
        "Analyzing leads with AI..."
    ):

        try:

            results_df = qualify_leads(
                leads
            )

        except Exception as error:

            st.error(
                f"Agent execution failed: {error}"
            )

            st.stop()


    if results_df.empty:

        st.error(
            "No leads could be qualified."
        )

        st.stop()


    # ========================================================
    # SAVE OUTPUT
    # ========================================================

    os.makedirs(
        "output",
        exist_ok=True
    )


    results_df.to_csv(
        "output/qualified_leads.csv",
        index=False
    )


    results_df.to_json(
        "output/qualified_leads.json",
        orient="records",
        indent=4
    )


    st.session_state[
        "results"
    ] = results_df


    st.success(
        "Lead qualification completed successfully."
    )


# ============================================================
# LOAD RESULTS
# ============================================================

if "results" in st.session_state:

    df = st.session_state[
        "results"
    ]

else:

    output_path = (
        "output/qualified_leads.csv"
    )

    if not os.path.exists(
        output_path
    ):

        st.info(
            "Upload your lead CSV and click "
            "'Qualify Leads' to begin."
        )

        st.stop()


    try:

        df = pd.read_csv(
            output_path
        )

    except pd.errors.EmptyDataError:

        st.info(
            "Upload your lead CSV and click "
            "'Qualify Leads' to begin."
        )

        st.stop()


# ============================================================
# REQUIRED RESULT COLUMNS
# ============================================================

required_columns = [

    "rank",
    "name",
    "company",
    "job_title",
    "industry",
    "company_size",
    "requirement",
    "budget",
    "timeline",
    "source",
    "score",
    "fit_score",
    "intent_score",
    "commercial_score",
    "tier",
    "reason",
    "next_action"

]


missing_columns = [

    column
    for column in required_columns
    if column not in df.columns

]


if missing_columns:

    st.error(
        "Results are missing: "
        + ", ".join(missing_columns)
    )

    st.info(
        "Click 'Qualify Leads' to regenerate the results."
    )

    st.stop()


# ============================================================
# QUALIFICATION OVERVIEW
# ============================================================

st.header(
    "📊 Qualification Overview"
)

st.caption(
    "Summary of the current lead portfolio."
)


total_leads = len(df)

hot_leads = len(
    df[
        df["tier"] == "HOT"
    ]
)

warm_leads = len(
    df[
        df["tier"] == "WARM"
    ]
)

cold_leads = len(
    df[
        df["tier"] == "COLD"
    ]
)


col1, col2, col3, col4 = st.columns(
    4
)


with col1:

    st.metric(
        "Total Leads",
        total_leads
    )


with col2:

    st.metric(
        "🔥 Hot Leads",
        hot_leads
    )


with col3:

    st.metric(
        "🟡 Warm Leads",
        warm_leads
    )


with col4:

    st.metric(
        "🔵 Cold Leads",
        cold_leads
    )


st.divider()


# ============================================================
# LEAD RANKING
# ============================================================

st.header(
    "🏆 Lead Ranking"
)

st.caption(
    "Leads are ordered by their final qualification score."
)


# ============================================================
# FILTER
# ============================================================

filter_option = st.selectbox(
    "Filter by qualification",
    [
        "All Leads",
        "HOT",
        "WARM",
        "COLD"
    ]
)


if filter_option == "All Leads":

    filtered_df = df.copy()

else:

    filtered_df = df[
        df["tier"] == filter_option
    ].copy()


# ============================================================
# RANKING TABLE
# ============================================================

ranking_df = filtered_df[
    [
        "rank",
        "name",
        "company",
        "score",
        "tier"
    ]
].copy()


# ============================================================
# TIER COLOR FUNCTION
# ============================================================

def color_tier(value):

    if value == "HOT":

        return (
            "background-color: #7f1d1d;"
            "color: #fecaca;"
            "font-weight: 700;"
            "text-align: center;"
        )

    elif value == "WARM":

        return (
            "background-color: #78350f;"
            "color: #fde68a;"
            "font-weight: 700;"
            "text-align: center;"
        )

    elif value == "COLD":

        return (
            "background-color: #1e3a8a;"
            "color: #bfdbfe;"
            "font-weight: 700;"
            "text-align: center;"
        )

    return ""


# ============================================================
# APPLY COLORS
# ============================================================

styled_ranking = (
    ranking_df
    .style
    .map(
        color_tier,
        subset=["tier"]
    )
    .format(
        {
            "score": "{:.0f}"
        }
    )
)


st.dataframe(
    styled_ranking,
    width="stretch",
    hide_index=True
)


st.caption(
    "🔥 HOT = immediate attention   |   "
    "🟡 WARM = follow-up required   |   "
    "🔵 COLD = nurture later"
)


st.divider()


# ============================================================
# LEAD INTELLIGENCE
# ============================================================

st.header(
    "🔎 Lead Intelligence"
)

st.caption(
    "Select a lead to inspect its qualification details."
)


if not filtered_df.empty:

    selected_lead = st.selectbox(
        "Select a lead",
        filtered_df[
            "name"
        ].tolist()
    )


    selected_row = filtered_df[
        filtered_df[
            "name"
        ] == selected_lead
    ].iloc[0]


    # ========================================================
    # LEAD HEADER
    # ========================================================

    st.subheader(
        f"{selected_row['name']} — "
        f"{selected_row['company']}"
    )


    # ========================================================
    # BASIC INFORMATION
    # ========================================================

    col1, col2, col3, col4 = st.columns(
        4
    )


    with col1:

        st.write("**Job Title**")

        st.write(
            selected_row["job_title"]
        )


    with col2:

        st.write("**Industry**")

        st.write(
            selected_row["industry"]
        )


    with col3:

        st.write("**Company Size**")

        st.write(
            selected_row["company_size"]
        )


    with col4:

        st.write("**Lead Source**")

        st.write(
            selected_row["source"]
        )


    st.divider()


    # ========================================================
    # BUSINESS INFORMATION
    # ========================================================

    st.subheader(
        "💼 Business Information"
    )


    col1, col2, col3 = st.columns(
        3
    )


    with col1:

        st.write("**Requirement**")

        st.write(
            selected_row["requirement"]
        )


    with col2:

        st.write("**Budget**")

        st.write(
            selected_row["budget"]
        )


    with col3:

        st.write("**Timeline**")

        st.write(
            selected_row["timeline"]
        )


    st.divider()


    # ========================================================
    # QUALIFICATION SCORE
    # ========================================================

    st.subheader(
        "📈 Qualification Score"
    )


    score1, score2, score3, score4 = st.columns(
        4
    )


    with score1:

        st.metric(
            "FIT",
            f"{selected_row['fit_score']}/40"
        )


    with score2:

        st.metric(
            "INTENT",
            f"{selected_row['intent_score']}/40"
        )


    with score3:

        st.metric(
            "COMMERCIAL",
            f"{selected_row['commercial_score']}/20"
        )


    with score4:

        st.metric(
            "TOTAL",
            f"{selected_row['score']}/100"
        )


    # ========================================================
    # QUALIFICATION STATUS
    # ========================================================

    st.write(
        "**Qualification Status**"
    )


    tier = selected_row["tier"]


    if tier == "HOT":

        st.error(
            "🔥 HOT — Immediate sales attention"
        )

    elif tier == "WARM":

        st.warning(
            "🟡 WARM — Follow-up opportunity"
        )

    else:

        st.info(
            "🔵 COLD — Nurture opportunity"
        )


    st.divider()


    # ========================================================
    # AI INSIGHT
    # ========================================================

    st.subheader(
        "🤖 AI Qualification Insight"
    )


    st.info(
        selected_row["reason"]
    )


    # ========================================================
    # NEXT ACTION
    # ========================================================

    st.subheader(
        "🎯 Recommended Next Action"
    )


    st.success(
        selected_row["next_action"]
    )


# ============================================================
# EXPORT
# ============================================================

st.divider()


st.header(
    "📥 Export Results"
)

st.caption(
    "Download the complete qualification results "
    "for your sales workflow."
)


csv_data = df.to_csv(
    index=False
)


st.download_button(
    label="⬇️ Download Qualified Leads CSV",
    data=csv_data,
    file_name="qualified_leads.csv",
    mime="text/csv",
    width="stretch"
)


# ============================================================
# FOOTER
# ============================================================

st.divider()


st.caption(
    "LeadIQ • AI Lead Qualification Agent • "
    "GPT-OSS-20B via Groq • "
    "Deterministic Python Scoring • "
    "Pandas • Streamlit"
)