from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / 'input'
OUTPUT_DIR = BASE_DIR / 'output'

# Input filenames
PREPROCESSED_DATA_FILE = INPUT_DIR / 'preprocessed_client_data.csv'
RULE_LOG_FILE = INPUT_DIR / 'rule_execution_log.csv'
RULE_VIOLATIONS_FILE = INPUT_DIR / 'rule_violations.csv'
RULE_SCORES_FILE = INPUT_DIR / 'rule_scores.csv'
PREDICTION_RESULTS_FILE = INPUT_DIR / 'prediction_results.csv'

# Output filename
OUTPUT_FILE = OUTPUT_DIR / 'explainable_audit_report.csv'

# Join keys
JOIN_KEYS = ['Company', 'Year']

# Severity priority (higher number = higher priority)
SEVERITY_PRIORITY = {
    'Critical': 4,
    'High': 3,
    'Medium': 2,
    'Low': 1
}

# Required columns for reports (example set, will be adjusted based on available data)
# These are mapped from the actual files inspected
VIOLATION_COLUMNS = ['Company', 'Year', 'Rule ID', 'Rule Name', 'Category', 'Severity', 'Message', 'Observed']
SCORE_COLUMNS = ['Company', 'Year', 'Passed Rules', 'Failed Rules', 'Skipped Rules', 'Critical Failures', 'High Failures', 'Medium Failures', 'Low Failures', 'Obtained Score', 'Maximum Score', 'Risk Score', 'Risk Level']
PREDICTION_COLUMNS = ['Company', 'Year', 'Prediction', 'Decision Score', 'Anomaly Score']