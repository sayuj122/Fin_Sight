"""
Explainable AI Module - Main Orchestration

Combines Rule Engine outputs, Risk Scores, and ML Predictions
to generate auditor-readable explanations.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

from config import (
    BASE_DIR, INPUT_DIR, OUTPUT_DIR,
    RULE_VIOLATIONS_FILE, RULE_SCORES_FILE, PREDICTION_RESULTS_FILE,
    PREPROCESSED_DATA_FILE, JOIN_KEYS
)
from explanation_generator import build_explanation_record
from report_generator import generate_report


def load_csv(filepath: Path, description: str) -> pd.DataFrame:
    """Load a CSV file with validation."""
    print(f"Loading {description} from {filepath}...")
    try:
        df = pd.read_csv(filepath)
        print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")
        return df
    except FileNotFoundError:
        print(f"  ERROR: File not found: {filepath}")
        return pd.DataFrame()
    except Exception as e:
        print(f"  ERROR loading {description}: {e}")
        return pd.DataFrame()


def normalize_company_year(df: pd.DataFrame, company_col: str = 'Company', year_col: str = 'Year') -> pd.DataFrame:
    """Normalize Company and Year columns for consistent joining."""
    if df.empty:
        return df

    df = df.copy()

    if company_col in df.columns:
        df[company_col] = df[company_col].astype(str).str.strip()

    if year_col in df.columns:
        df[year_col] = pd.to_numeric(df[year_col], errors='coerce').astype('Int64')

    return df


def validate_required_columns(df: pd.DataFrame, required_cols: list, name: str) -> bool:
    """Validate that required columns exist in DataFrame."""
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        print(f"  WARNING: {name} missing columns: {missing}")
        return False
    return True


def get_violations_for_company_year(violations_df: pd.DataFrame, company: str, year: int) -> pd.DataFrame:
    """Filter violations for specific Company-Year."""
    if violations_df.empty:
        return pd.DataFrame()

    mask = (violations_df['Company'] == company) & (violations_df['Year'] == year)
    return violations_df[mask].copy()


def get_rule_scores_for_company_year(scores_df: pd.DataFrame, company: str, year: int) -> pd.Series:
    """Get rule scores for specific Company-Year."""
    if scores_df.empty:
        return pd.Series(dtype=object)

    mask = (scores_df['Company'] == company) & (scores_df['Year'] == year)
    result = scores_df[mask]
    if result.empty:
        return pd.Series(dtype=object)
    return result.iloc[0]


def get_prediction_for_company_year(pred_df: pd.DataFrame, company: str, year: int) -> pd.Series:
    """Get ML prediction for specific Company-Year."""
    if pred_df.empty:
        return pd.Series(dtype=object)

    mask = (pred_df['Company'] == company) & (pred_df['Year'] == year)
    result = pred_df[mask]
    if result.empty:
        return pd.Series(dtype=object)
    return result.iloc[0]


def get_preprocessed_for_company_year(preprocessed_df: pd.DataFrame, company: str, year: int) -> pd.Series:
    """Get preprocessed data for specific Company-Year."""
    if preprocessed_df.empty:
        return pd.Series(dtype=object)

    mask = (preprocessed_df['Company'] == company) & (preprocessed_df['Year'] == year)
    result = preprocessed_df[mask]
    if result.empty:
        return pd.Series(dtype=object)
    return result.iloc[0]


def main():
    """Main orchestration function."""
    print("="*60)
    print("EXPLAINABLE AI MODULE - FINANCIAL STATEMENT ANOMALY DETECTION")
    print("="*60)

    # 1. Load all input files
    print("\n[1/6] Loading input files...")
    violations_df = load_csv(RULE_VIOLATIONS_FILE, "Rule Violations")
    scores_df = load_csv(RULE_SCORES_FILE, "Rule Scores")
    predictions_df = load_csv(PREDICTION_RESULTS_FILE, "ML Predictions")
    preprocessed_df = load_csv(PREPROCESSED_DATA_FILE, "Preprocessed Client Data")

    # Check for missing critical files
    if violations_df.empty:
        print("ERROR: Rule violations file is empty or missing. Cannot proceed.")
        return 1

    # 2. Normalize join keys
    print("\n[2/6] Normalizing join keys (Company, Year)...")
    violations_df = normalize_company_year(violations_df)
    scores_df = normalize_company_year(scores_df)
    predictions_df = normalize_company_year(predictions_df)
    preprocessed_df = normalize_company_year(preprocessed_df)

    # 3. Validate required columns
    print("\n[3/6] Validating required columns...")
    validate_required_columns(violations_df, JOIN_KEYS + ['Rule ID', 'Rule Name', 'Severity', 'Message'], "Violations")
    validate_required_columns(scores_df, JOIN_KEYS + ['Risk Score', 'Risk Level'], "Scores")
    validate_required_columns(predictions_df, JOIN_KEYS + ['Prediction', 'Decision Score', 'Anomaly Score'], "Predictions")

    # 4. Determine unique Company-Year pairs from violations (primary source)
    print("\n[4/6] Identifying Company-Year pairs...")
    company_years = violations_df[JOIN_KEYS].drop_duplicates().sort_values(JOIN_KEYS)
    print(f"  Found {len(company_years)} unique Company-Year pairs from violations")

    # Also include Company-Years from scores and predictions that might not have violations
    if not scores_df.empty:
        score_pairs = scores_df[JOIN_KEYS].drop_duplicates()
        company_years = pd.concat([company_years, score_pairs]).drop_duplicates().sort_values(JOIN_KEYS)

    if not predictions_df.empty:
        pred_pairs = predictions_df[JOIN_KEYS].drop_duplicates()
        company_years = pd.concat([company_years, pred_pairs]).drop_duplicates().sort_values(JOIN_KEYS)

    print(f"  Total unique Company-Year pairs to process: {len(company_years)}")

    # 5. Generate explanations for each Company-Year
    print("\n[5/6] Generating explanations...")
    explanation_records = []

    for idx, row in company_years.iterrows():
        company = row['Company']
        year = row['Year']

        print(f"  Processing: {company} - {year}")

        # Get violations for this Company-Year
        company_violations = get_violations_for_company_year(violations_df, company, year)

        # Get rule scores for this Company-Year
        company_scores = get_rule_scores_for_company_year(scores_df, company, year)

        # Get ML prediction for this Company-Year
        company_prediction = get_prediction_for_company_year(predictions_df, company, year)

        # Get preprocessed data (optional, for context)
        company_preprocessed = get_preprocessed_for_company_year(preprocessed_df, company, year)

        # Build explanation record
        record = build_explanation_record(
            company=company,
            year=year,
            violations=company_violations,
            rule_scores=company_scores if not company_scores.empty else None,
            prediction=company_prediction if not company_prediction.empty else None,
            preprocessed_data=company_preprocessed if not company_preprocessed.empty else None
        )

        explanation_records.append(record)

    print(f"  Generated {len(explanation_records)} explanation records")

    # 6. Generate and save report
    print("\n[6/6] Generating final report...")
    report_df = generate_report(explanation_records)

    print("\n" + "="*60)
    print("EXPLAINABLE AI MODULE - COMPLETED SUCCESSFULLY")
    print("="*60)

    return 0


if __name__ == '__main__':
    sys.exit(main())