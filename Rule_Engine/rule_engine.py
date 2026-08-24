"""
==========================================================
Project:
A Hybrid Rule-Based and Explainable Machine Learning
Framework for Financial Statement Anomaly Detection

Module:
Rule Engine

File:
rule_engine.py

Purpose:
Execute audit rules on client financial statements.

Part 1
Imports
Configuration
Load Client Dataset
Load Audit Rules
Dataset Validation
Engine Initialization
==========================================================
"""

# ==========================================================
# IMPORTS
# ==========================================================

import pandas as pd

from config import (
    CLIENT_DATASET,
    DEFAULT_CONFIG,
    PRINT_PROGRESS,
    VERBOSE,
    CSV_ENCODING
)

from audit_rules import get_all_rules

from utils import log

# ==========================================================
# LOAD CLIENT DATASET
# ==========================================================

log("Loading client financial dataset...")

df = pd.read_csv(

    CLIENT_DATASET,

    encoding=CSV_ENCODING

)

log("Client dataset loaded successfully.")

# ==========================================================
# LOAD AUDIT RULES
# ==========================================================

log("Loading audit rules...")

RULES = get_all_rules()

log(f"Audit Rules Loaded : {len(RULES)}")

# ==========================================================
# REQUIRED COLUMNS
# ==========================================================

REQUIRED_COLUMNS = [

    "Company",

    "Year"

]

# ==========================================================
# VALIDATE REQUIRED COLUMNS
# ==========================================================

missing_columns = [

    column

    for column in REQUIRED_COLUMNS

    if column not in df.columns

]

if len(missing_columns) > 0:

    raise ValueError(

        f"Missing Required Columns : {missing_columns}"

    )

log("Required column validation passed.")

# ==========================================================
# BASIC DATASET CLEANING
# ==========================================================

df.drop_duplicates(

    inplace=True

)

df.reset_index(

    drop=True,

    inplace=True

)

# ==========================================================
# SORT DATASET
# ==========================================================

if "Company" in df.columns and "Year" in df.columns:

    df.sort_values(

        by=["Company", "Year"],

        inplace=True

    )

    df.reset_index(

        drop=True,

        inplace=True

    )

# ==========================================================
# ENGINE CONFIGURATION
# ==========================================================

ENGINE_CONFIG = DEFAULT_CONFIG.copy()

# ==========================================================
# DATASET INFORMATION
# ==========================================================

if VERBOSE:

    print()

    print("=" * 60)

    print("CLIENT DATASET INFORMATION")

    print("=" * 60)

    print(f"Rows    : {len(df)}")

    print(f"Columns : {len(df.columns)}")

    print()

    print("Columns")

    for column in df.columns:

        print(f" - {column}")

    print()

# ==========================================================
# RULE INFORMATION
# ==========================================================

if VERBOSE:

    print("=" * 60)

    print("AUDIT RULE INFORMATION")

    print("=" * 60)

    print(f"Total Rules : {len(RULES)}")

    print()

    print("First 10 Rules")

    for rule in RULES[:10]:

        print(

            f"{rule.spec.rule_id:<10}"

            f"{rule.spec.name}"

        )

    print()

# ==========================================================
# INITIALIZATION SUMMARY
# ==========================================================

print("=" * 60)

print("RULE ENGINE INITIALIZED")

print("=" * 60)

print(f"Client Records : {len(df)}")

print(f"Audit Rules    : {len(RULES)}")

print()

log("Rule Engine Ready.")

# ==========================================================
# Part 2 Starts Here
# Execute Audit Rules
# Generate Rule Results
# ==========================================================
# ==========================================================
# PART 2
# Execute Audit Rules
# Collect Rule Results
# ==========================================================

log("Executing audit rules...")

results = []

total_records = len(df)

total_rules = len(RULES)

execution_count = 0

# ==========================================================
# EXECUTE RULES
# ==========================================================

for index in df.index:

    if PRINT_PROGRESS:

        print(

            f"\nProcessing Record "

            f"{index + 1}/{total_records}"

        )

    for rule in RULES:

        execution_count += 1

        try:

            result = rule.evaluate(

                frame=df,

                index=index,

                config=ENGINE_CONFIG

            )

            results.append({

                "Company": result.company,

                "Year": result.year,

                "Rule ID": result.rule_id,

                "Rule Name": rule.spec.name,

                "Group": rule.spec.group,

                "Category": rule.spec.category,

                "Severity": result.severity.value,

                "Status": result.status.value,

                "Message": result.message,

                "Observed": str(result.observed)

            })

        except Exception as e:

            row = df.iloc[index]

            results.append({

                "Company": row.get("Company", ""),

                "Year": row.get("Year", ""),

                "Rule ID": rule.spec.rule_id,

                "Rule Name": rule.spec.name,

                "Group": rule.spec.group,

                "Category": rule.spec.category,

                "Severity": rule.spec.severity.value,

                "Status": "error",

                "Message": str(e),

                "Observed": ""

            })

# ==========================================================
# CREATE RESULTS DATAFRAME
# ==========================================================

results_df = pd.DataFrame(results)

log("Rule execution completed.")

# ==========================================================
# EXECUTION SUMMARY
# ==========================================================

print()

print("=" * 60)

print("RULE EXECUTION SUMMARY")

print("=" * 60)

print(f"Client Records      : {total_records}")

print(f"Audit Rules         : {total_rules}")

print(f"Executions          : {execution_count}")

print(f"Results Generated   : {len(results_df)}")

print()

print("STATUS DISTRIBUTION")

print("-------------------")

print(

    results_df["Status"]

    .value_counts()

)

print()

print("SEVERITY DISTRIBUTION")

print("---------------------")

print(

    results_df["Severity"]

    .value_counts()

)

print()

# ==========================================================
# PART 3 STARTS HERE
# Save Reports
# Risk Score
# ==========================================================
# ==========================================================
# PART 3
# Generate Reports
# ==========================================================

from config import (
    RULE_EXECUTION_LOG,
    RULE_VIOLATIONS,
    SYSTEM_ERROR_LOG
)

log("Generating audit reports...")

# ==========================================================
# RULE EXECUTION LOG
# ==========================================================

results_df.to_csv(

    RULE_EXECUTION_LOG,

    index=False,

    encoding=CSV_ENCODING

)

log("Rule execution log generated.")

# ==========================================================
# RULE VIOLATIONS
# ==========================================================

violations_df = results_df[

    results_df["Status"] == "fail"

].copy()

violations_df.to_csv(

    RULE_VIOLATIONS,

    index=False,

    encoding=CSV_ENCODING

)

log("Rule violations report generated.")

# ==========================================================
# SYSTEM ERROR LOG
# ==========================================================

system_error_df = results_df[

    results_df["Status"] == "error"

].copy()

system_error_df.to_csv(

    SYSTEM_ERROR_LOG,

    index=False,

    encoding=CSV_ENCODING

)

log("System error log generated.")

# ==========================================================
# SUMMARY COUNTS
# ==========================================================

passed_count = len(

    results_df[

        results_df["Status"] == "pass"

    ]

)

failed_count = len(

    violations_df

)

skipped_count = len(

    results_df[

        results_df["Status"] == "skipped"

    ]

)

error_count = len(

    system_error_df

)

total_rules = len(results_df)

# ==========================================================
# CLIENT AUDIT SUMMARY
# ==========================================================

print()

print("=" * 60)

print("CLIENT AUDIT SUMMARY")

print("=" * 60)

print(f"Rules Executed : {total_rules}")

print(f"Passed         : {passed_count}")

print(f"Failed         : {failed_count}")

print(f"Skipped        : {skipped_count}")

print()

if skipped_count > 0:

    print("Skipped rules require additional")

    print("financial information.")

    print()

if error_count > 0:

    print(

        f"Internal System Errors : "

        f"{error_count}"

    )

    print(

        "Refer system_error_log.csv"

    )

    print()

# ==========================================================
# REPORT SUMMARY
# ==========================================================

print("=" * 60)

print("REPORTS GENERATED")

print("=" * 60)

print(f"Rule Execution Log : {RULE_EXECUTION_LOG.name}")

print(f"Rule Violations    : {RULE_VIOLATIONS.name}")

print(f"System Error Log   : {SYSTEM_ERROR_LOG.name}")

print()

log("Report generation completed.")

# ==========================================================
# PART 4 STARTS HERE
# Risk Score
# Explainability
# ==========================================================