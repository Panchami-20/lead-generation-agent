import os
import pandas as pd
from dotenv import load_dotenv

from agent import qualify_leads


# Load environment variables
load_dotenv()


# Load lead data
leads = pd.read_csv("data/sample_leads.csv")


# Run the Lead Qualification Agent
print("\nStarting Lead Qualification Agent...\n")

results_df = qualify_leads(leads)


# Display ranked results
print("\n========================================")
print("       RANKED LEAD QUALIFICATION")
print("========================================\n")

if not results_df.empty:

    print(
        results_df[
            [
                "rank",
                "name",
                "company",
                "score",
                "tier"
            ]
        ].to_string(index=False)
    )

else:

    print("No leads were successfully qualified.")


# Display detailed recommendations
print("\n========================================")
print("       DETAILED RECOMMENDATIONS")
print("========================================\n")

for _, result in results_df.iterrows():

    print(f"Rank #{result['rank']}")
    print(f"Lead: {result['name']}")
    print(f"Company: {result['company']}")
    print(f"Score: {result['score']}/100")
    print(f"Tier: {result['tier']}")
    print(f"Reason: {result['reason']}")
    print(f"Next Action: {result['next_action']}")
    print("-" * 50)


# Create output directory
os.makedirs("output", exist_ok=True)


# Save CSV
csv_path = "output/qualified_leads.csv"

results_df.to_csv(
    csv_path,
    index=False
)


# Save JSON
json_path = "output/qualified_leads.json"

results_df.to_json(
    json_path,
    orient="records",
    indent=4
)


print("\n========================================")
print("             OUTPUT SAVED")
print("========================================")

print(f"\nCSV  : {csv_path}")
print(f"JSON : {json_path}")