"""
==========================================================
Project:
Hybrid Rule-Based and Explainable Financial Statement
Anomaly Detection Framework

Module:
Rule Engine

File:
risk_score.py

Purpose:
Calculate Rule-Based Risk Score for each
Company-Year combination.
==========================================================
"""

import pandas as pd

from config import (
    RULE_EXECUTION_LOG,
    RULE_SCORES,
    SEVERITY_WEIGHTS,
    CATEGORY_WEIGHTS,
    RISK_LEVELS
)


# ==========================================================
# LOAD RULE EXECUTION LOG
# ==========================================================

print("Loading rule execution log...")

df = pd.read_csv(RULE_EXECUTION_LOG)

print("Rule execution log loaded.")

# ==========================================================
# CALCULATE SCORE OF EACH RULE
# ==========================================================

def calculate_rule_score(row):

    if row["Status"] != "fail":
        return 0.0

    severity_weight = SEVERITY_WEIGHTS.get(

        row["Severity"],

        0

    )

    category_weight = CATEGORY_WEIGHTS.get(

        str(row["Category"]).lower(),

        1.0

    )

    return severity_weight * category_weight


df["Rule Score"] = df.apply(

    calculate_rule_score,

    axis=1

)

# ==========================================================
# MAXIMUM POSSIBLE SCORE
# ==========================================================

maximum_score = 0

unique_rules = df[

    ["Rule ID", "Severity", "Category"]

].drop_duplicates()

for _, row in unique_rules.iterrows():

    maximum_score += (

        SEVERITY_WEIGHTS.get(

            row["Severity"],

            0

        )

        *

        CATEGORY_WEIGHTS.get(

            str(row["Category"]).lower(),

            1.0

        )

    )

print(f"Maximum Possible Score : {maximum_score:.2f}")

# ==========================================================
# GROUP BY COMPANY + YEAR
# ==========================================================

summary = []

grouped = df.groupby(

    ["Company", "Year"]

)

# ==========================================================
# CALCULATE COMPANY RISK
# ==========================================================

for (company, year), data in grouped:

    obtained_score = data["Rule Score"].sum()

    risk_score = (

        obtained_score

        /

        maximum_score

    ) * 100

    risk_score = round(

        risk_score,

        2

    )

    failed = len(

        data[

            data["Status"] == "fail"

        ]

    )

    passed = len(

        data[

            data["Status"] == "pass"

        ]

    )

    skipped = len(

        data[

            data["Status"] == "skipped"

        ]

    )

    critical = len(

        data[

            (data["Status"] == "fail")

            &

            (data["Severity"] == "Critical")

        ]

    )

    high = len(

        data[

            (data["Status"] == "fail")

            &

            (data["Severity"] == "High")

        ]

    )

    medium = len(

        data[

            (data["Status"] == "fail")

            &

            (data["Severity"] == "Medium")

        ]

    )

    low = len(

        data[

            (data["Status"] == "fail")

            &

            (data["Severity"] == "Low")

        ]

    )

    # ===========================================
    # RISK LEVEL
    # ===========================================

    if risk_score <= 20:

        level = "Low"

    elif risk_score <= 40:

        level = "Moderate"

    elif risk_score <= 60:

        level = "Significant"

    elif risk_score <= 80:

        level = "High"

    else:

        level = "Critical"

    summary.append({

        "Company": company,

        "Year": year,

        "Passed Rules": passed,

        "Failed Rules": failed,

        "Skipped Rules": skipped,

        "Critical Failures": critical,

        "High Failures": high,

        "Medium Failures": medium,

        "Low Failures": low,

        "Obtained Score": round(

            obtained_score,

            2

        ),

        "Maximum Score": round(

            maximum_score,

            2

        ),

        "Risk Score": risk_score,

        "Risk Level": level

    })

# ==========================================================
# SAVE REPORT
# ==========================================================

risk_df = pd.DataFrame(summary)

risk_df.to_csv(

    RULE_SCORES,

    index=False

)

print()

print("=" * 60)

print("RULE RISK SCORE SUMMARY")

print("=" * 60)

print(risk_df)

print()

print(

    f"Risk report saved to : {RULE_SCORES}"

)

print()

print("Risk score calculation completed.")