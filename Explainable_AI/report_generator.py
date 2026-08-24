"""
Report Generator Module

Constructs the final explainable audit report DataFrame and saves to CSV.
"""

import pandas as pd
from pathlib import Path
from config import OUTPUT_FILE, OUTPUT_DIR


# Desired column order for the final report
REPORT_COLUMNS = [
    'Company',
    'Year',
    'Rule Risk Score',
    'Rule Risk Level',
    'Passed Rules',
    'Failed Rules',
    'Skipped Rules',
    'Critical Failures',
    'High Failures',
    'Medium Failures',
    'Low Failures',
    'ML Prediction',
    'Decision Score',
    'Anomaly Score',
    'Violation Count',
    'Violation Categories',
    'Highest Severity',
    'Rule-Based Explanation',
    'ML Explanation',
    'Overall Explanation',
    'Audit Recommendation'
]


def construct_report_dataframe(explanation_records: list) -> pd.DataFrame:
    """
    Construct the final report DataFrame from explanation records.

    Args:
        explanation_records: List of dictionaries containing explanation data

    Returns:
        DataFrame with standardized columns
    """
    if not explanation_records:
        return pd.DataFrame(columns=REPORT_COLUMNS)

    df = pd.DataFrame(explanation_records)

    # Ensure all expected columns exist
    for col in REPORT_COLUMNS:
        if col not in df.columns:
            df[col] = None

    # Reorder columns
    df = df[REPORT_COLUMNS]

    return df


def save_report(df: pd.DataFrame, output_path: Path = OUTPUT_FILE) -> bool:
    """
    Save the report to CSV.

    Args:
        df: Report DataFrame
        output_path: Output file path

    Returns:
        True if successful
    """
    try:
        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save to CSV
        df.to_csv(output_path, index=False)
        return True
    except Exception as e:
        print(f"Error saving report: {e}")
        return False


def print_report_statistics(df: pd.DataFrame) -> None:
    """Print summary statistics of the generated report."""
    print("\n" + "="*60)
    print("EXPLAINABLE AUDIT REPORT - GENERATION SUMMARY")
    print("="*60)
    print(f"Total records: {len(df)}")
    print(f"Companies: {df['Company'].nunique()}")
    print(f"Years covered: {sorted(df['Year'].dropna().unique().tolist())}")

    # Rule risk level distribution
    if 'Rule Risk Level' in df.columns:
        print(f"\nRule Risk Level Distribution:")
        print(df['Rule Risk Level'].value_counts().to_string())

    # ML Prediction distribution
    if 'ML Prediction' in df.columns:
        print(f"\nML Prediction Distribution:")
        print(df['ML Prediction'].value_counts().to_string())

    # Violation statistics
    if 'Violation Count' in df.columns:
        total_violations = df['Violation Count'].sum()
        avg_violations = df['Violation Count'].mean()
        max_violations = df['Violation Count'].max()
        print(f"\nViolation Statistics:")
        print(f"  Total violations: {total_violations}")
        print(f"  Average per Company-Year: {avg_violations:.1f}")
        print(f"  Maximum per Company-Year: {max_violations}")

    # Highest severity distribution
    if 'Highest Severity' in df.columns:
        print(f"\nHighest Severity Distribution:")
        print(df['Highest Severity'].value_counts().to_string())

    # Output file
    print(f"\nOutput file: {OUTPUT_FILE}")
    print("="*60)


def generate_report(explanation_records: list) -> pd.DataFrame:
    """
    Main function to generate and save the report.

    Args:
        explanation_records: List of explanation dictionaries

    Returns:
        Generated DataFrame
    """
    print("Constructing report DataFrame...")
    df = construct_report_dataframe(explanation_records)

    print(f"Report shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    print("Saving report...")
    success = save_report(df)

    if success:
        print(f"Report successfully saved to: {OUTPUT_FILE}")
    else:
        print("ERROR: Failed to save report")

    print_report_statistics(df)

    return df