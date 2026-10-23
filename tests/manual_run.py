import pandas as pd
import sys

# Allow Python to find the src folder
sys.path.append("src")

from agent import qualify_leads


# Load test leads
leads = pd.read_csv(
    "tests/test_leads.csv"
)


print("\n========================================")
print("       LEAD AGENT TEST")
print("========================================\n")


# Run the agent
results = qualify_leads(
    leads
)


# Display results
if results.empty:

    print("ERROR: No leads were qualified.")

else:

    print(
        results[
            [
                "rank",
                "name",
                "company",
                "score",
                "tier"
            ]
        ].to_string(
            index=False
        )
    )


print("\n========================================")
print("       TEST DETAILS")
print("========================================\n")


for _, lead in results.iterrows():

    print(
        f"{lead['name']} "
        f"→ {lead['score']}/100 "
        f"→ {lead['tier']}"
    )

    print(
        f"Reason: {lead['reason']}"
    )

    print(
        f"Next Action: {lead['next_action']}"
    )

    print("-" * 60)