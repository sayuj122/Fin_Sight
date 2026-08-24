"""
==========================================================
Prediction Module Configuration
==========================================================
"""

import os


# ==========================================================
# BASE DIRECTORIES
# ==========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

PREDICTION_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# ==========================================================
# TRAINED MODEL FILES
# ==========================================================

MODEL_FILE = os.path.join(
    PREDICTION_DIR,
    "isolation_forest.pkl"
)

SCALER_FILE = os.path.join(
    PREDICTION_DIR,
    "robust_scaler.pkl"
)

FEATURE_FILE = os.path.join(
    PREDICTION_DIR,
    "feature_columns.pkl"
)

IMPUTER_FILE = os.path.join(
    PREDICTION_DIR,
    "imputer.pkl"
)


# ==========================================================
# CLIENT INPUT
# ==========================================================

# The preprocessed client financial dataset from the Preprocessor module.
CLIENT_DATASET = os.path.join(
    BASE_DIR,
    "Preprocessor",
    "output",
    "preprocessed_client_data.csv"
)


# ==========================================================
# OUTPUT
# ==========================================================

OUTPUT_DIR = os.path.join(
    PREDICTION_DIR,
    "output"
)

PREDICTION_FILE = os.path.join(
    OUTPUT_DIR,
    "prediction_results.csv"
)


# ==========================================================
# IDENTIFIER COLUMNS
# ==========================================================

ID_COLUMNS = [
    "Company",
    "Year"
]


# ==========================================================
# SCALING
# ==========================================================

SCALER = "RobustScaler"


# ==========================================================
# PREDICTION LABELS
# ==========================================================

NORMAL_LABEL = "Normal"

ANOMALY_LABEL = "Anomaly"


# ==========================================================
# ANOMALY SCORE
# ==========================================================

# Isolation Forest's decision_function returns
# larger values for more normal observations.
# We retain the original model score and also
# calculate an easier-to-read anomaly score.

ANOMALY_SCORE_MULTIPLIER = -1


# ==========================================================
# FILE ENCODING
# ==========================================================

CSV_ENCODING = "utf-8"


# ==========================================================
# DISPLAY SETTINGS
# ==========================================================

VERBOSE = True
PRINT_PROGRESS = True