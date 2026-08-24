"""
==========================================================
Project:
Hybrid Rule-Based and Explainable Financial Statement
Anomaly Detection Framework

File:
utils.py

Purpose:
Common helper functions used by the Rule Engine.
==========================================================
"""

from pathlib import Path
import pandas as pd


# ==========================================================
# LOGGING
# ==========================================================

def log(message, enabled=True):

    if enabled:
        print(message)


# ==========================================================
# LOAD DATASET
# ==========================================================

def load_dataset(path):

    return pd.read_csv(path)


# ==========================================================
# ENSURE REPORT DIRECTORY
# ==========================================================

def ensure_directory(path):

    Path(path).mkdir(
        parents=True,
        exist_ok=True
    )


# ==========================================================
# SAVE DATAFRAME
# ==========================================================

def save_dataframe(df, path):

    df.to_csv(
        path,
        index=False
    )


# ==========================================================
# SAFE FLOAT
# ==========================================================

def safe_float(value):

    try:
        return float(value)
    except Exception:
        return 0.0


# ==========================================================
# COMPANY INFORMATION
# ==========================================================

def get_company(row):

    return str(row.get("Company", ""))


def get_year(row):

    try:
        return int(row.get("Year", 0))
    except Exception:
        return 0