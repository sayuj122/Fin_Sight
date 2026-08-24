"""
==========================================================
Project:
A Hybrid Rule-Based and Explainable Machine Learning
Framework for Financial Statement Anomaly Detection

Module:
Rule Engine

File:
config.py

Purpose:
Configuration settings for the Rule-Based Audit Engine.
==========================================================
"""

from pathlib import Path

# ==========================================================
# PROJECT PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent

# ==========================================================
# CLIENT INPUT
# ==========================================================

CLIENT_DATA_DIR = PROJECT_ROOT.parent / "Preprocessor" / "output"

CLIENT_DATASET = CLIENT_DATA_DIR / "preprocessed_client_data.csv"

# ==========================================================
# RULES
# ==========================================================

RULES_DIR = PROJECT_ROOT / "audit_engine" / "rules"

# ==========================================================
# REPORT DIRECTORY
# ==========================================================

REPORT_DIR = PROJECT_ROOT / "reports"

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# ==========================================================
# OUTPUT REPORTS
# ==========================================================

RULE_VIOLATIONS = REPORT_DIR / "rule_violations.csv"

RULE_SCORES = REPORT_DIR / "rule_scores.csv"

AUDIT_REPORT = REPORT_DIR / "audit_report.csv"

RULE_EXECUTION_LOG = REPORT_DIR / "rule_execution_log.csv"

SYSTEM_ERROR_LOG = REPORT_DIR / "system_error_log.csv"

# ==========================================================
# ENGINE SETTINGS
# ==========================================================

ROUND_DECIMALS = 4

FLOAT_TOLERANCE = 1e-6

CSV_ENCODING = "utf-8"

# ==========================================================
# EXECUTION SETTINGS
# ==========================================================

PRINT_PROGRESS = True

VERBOSE = True

# ==========================================================
# SEVERITY WEIGHTS
# ==========================================================

SEVERITY_WEIGHTS = {

    "CRITICAL": 10,

    "HIGH": 7,

    "MEDIUM": 5,

    "LOW": 2,

    "INFO": 1

}

# ==========================================================
# DEFAULT TOLERANCES
# ==========================================================

DEFAULT_CONFIG = {

    "tolerance": 0.01,

    "minimum_history": 3,

    "z_score": 3.0

}
#Risk Score
# ==========================================================
# SEVERITY WEIGHTS
# ==========================================================

SEVERITY_WEIGHTS = {

    "Critical": 10,

    "High": 7,

    "Medium": 5,

    "Low": 2

}

# ==========================================================
# CATEGORY MULTIPLIERS
# ==========================================================

CATEGORY_WEIGHTS = {

    "integrity": 1.50,

    "fraud": 1.50,

    "compliance": 1.40,

    "solvency": 1.35,

    "liquidity": 1.30,

    "cash_flow": 1.25,

    "profitability": 1.20,

    "trend": 1.10,

    "efficiency": 1.10,

    "data_validation": 1.00

}

# ==========================================================
# RISK LEVELS
# ==========================================================

RISK_LEVELS = {

    (0,20):"Low",

    (21,40):"Moderate",

    (41,60):"Significant",

    (61,80):"High",

    (81,100):"Critical"

}