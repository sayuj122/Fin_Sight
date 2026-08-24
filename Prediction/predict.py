
"""
======================================================================
PROJECT:
A Hybrid Rule-Based and Explainable Machine Learning
Framework for Financial Statement Anomaly Detection

FILE:
predict.py

PURPOSE:
Apply the already-trained Isolation Forest model to the
ALREADY PREPROCESSED client financial dataset.

IMPORTANT:
This module DOES NOT:
    - extract financial metrics
    - standardize raw metric names
    - calculate financial ratios
    - calculate growth features
    - calculate trend features
    - calculate operating profit
    - calculate expenses

Those responsibilities belong ONLY to the Preprocessor.

INPUT:
    Preprocessed client CSV

MODEL ARTIFACTS:
    isolation_forest.pkl
    scaler.pkl
    feature_columns.pkl

OUTPUT:
    prediction_results.csv

EXPECTED CLIENT:
    One company
    Multiple financial years
======================================================================
"""

from __future__ import annotations

import os
import sys

import joblib
import numpy as np
import pandas as pd


# ======================================================================
# CONFIGURATION
# ======================================================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)


from config import (
    MODEL_FILE,
    SCALER_FILE,
    FEATURE_FILE,
    IMPUTER_FILE,
    CLIENT_DATASET,
    OUTPUT_DIR,
    PREDICTION_FILE,
    ID_COLUMNS,
    NORMAL_LABEL,
    ANOMALY_LABEL,
    ANOMALY_SCORE_MULTIPLIER,
    CSV_ENCODING,
    VERBOSE,
)


# ======================================================================
# LOGGING
# ======================================================================

def log(message: str) -> None:

    if VERBOSE:
        print(message)


# ======================================================================
# LOAD PREPROCESSED CLIENT DATA
# ======================================================================

def load_client_dataset() -> pd.DataFrame:

    log("=" * 70)
    log("LOADING PREPROCESSED CLIENT DATA")
    log("=" * 70)

    if not os.path.exists(CLIENT_DATASET):

        raise FileNotFoundError(
            "Preprocessed client dataset not found:\n"
            f"{CLIENT_DATASET}\n\n"
            "Run the Preprocessor first."
        )

    extension = (
        os.path.splitext(
            CLIENT_DATASET
        )[1]
        .lower()
    )

    if extension == ".csv":

        df = pd.read_csv(
            CLIENT_DATASET,
            encoding=CSV_ENCODING
        )

    elif extension in [".xlsx", ".xls"]:

        df = pd.read_excel(
            CLIENT_DATASET
        )

    else:

        raise ValueError(
            "Prediction input must be a "
            "preprocessed CSV or Excel file."
        )

    if df.empty:

        raise ValueError(
            "Preprocessed client dataset is empty."
        )

    print()
    print(
        f"File      : "
        f"{os.path.basename(CLIENT_DATASET)}"
    )

    print(
        f"Rows      : {len(df)}"
    )

    print(
        f"Columns   : {len(df.columns)}"
    )

    print()

    print(
        "Preprocessed client dataset "
        "loaded successfully."
    )

    return df


# ======================================================================
# VALIDATE CLIENT DATASET
# ======================================================================

def validate_client_dataset(
    df: pd.DataFrame
) -> pd.DataFrame:

    print()
    print("=" * 70)
    print("VALIDATING PREPROCESSED CLIENT DATA")
    print("=" * 70)

    # --------------------------------------------------------------
    # IDENTIFIERS
    # --------------------------------------------------------------

    required_identifiers = [
        "Company",
        "Year",
    ]

    missing_identifiers = [
        column
        for column in required_identifiers
        if column not in df.columns
    ]

    if missing_identifiers:

        raise ValueError(
            "Missing identifier columns:\n"
            f"{missing_identifiers}"
        )

    # --------------------------------------------------------------
    # COMPANY
    # --------------------------------------------------------------

    if df["Company"].isna().all():

        raise ValueError(
            "Company column contains no valid "
            "company information."
        )

    # --------------------------------------------------------------
    # YEAR
    # --------------------------------------------------------------

    df["Year"] = pd.to_numeric(
        df["Year"],
        errors="coerce"
    )

    if df["Year"].isna().any():

        raise ValueError(
            "Invalid Year values found in "
            "preprocessed client data."
        )

    # --------------------------------------------------------------
    # ONE COMPANY ONLY
    # --------------------------------------------------------------

    companies = (
        df["Company"]
        .astype(str)
        .str.strip()
        .unique()
    )

    if len(companies) != 1:

        raise ValueError(
            "Prediction input must contain "
            "ONE client company only.\n\n"
            f"Companies found: {list(companies)}"
        )

    # --------------------------------------------------------------
    # DUPLICATE COMPANY-YEAR
    # --------------------------------------------------------------

    duplicate_count = (
        df.duplicated(
            subset=[
                "Company",
                "Year",
            ]
        )
        .sum()
    )

    if duplicate_count > 0:

        raise ValueError(
            "Duplicate Company-Year records "
            f"found: {duplicate_count}"
        )

    # --------------------------------------------------------------
    # SORT
    # --------------------------------------------------------------

    df.sort_values(
        by=[
            "Company",
            "Year",
        ],
        inplace=True
    )

    df.reset_index(
        drop=True,
        inplace=True
    )

    print(
        "Identifier validation passed."
    )

    print(
        f"Company : {companies[0]}"
    )

    print(
        f"Years   : "
        f"{df['Year'].min()} - "
        f"{df['Year'].max()}"
    )

    return df


# ======================================================================
# LOAD TRAINED MODEL ARTIFACTS
# ======================================================================

def load_model_artifacts():

    print()
    print("=" * 70)
    print("LOADING TRAINED MODEL ARTIFACTS")
    print("=" * 70)

    # --------------------------------------------------------------
    # MODEL
    # --------------------------------------------------------------

    if not os.path.exists(MODEL_FILE):

        raise FileNotFoundError(
            "Isolation Forest model not found:\n"
            f"{MODEL_FILE}"
        )

    # --------------------------------------------------------------
    # SCALER
    # --------------------------------------------------------------

    if not os.path.exists(SCALER_FILE):

        raise FileNotFoundError(
            "Scaler not found:\n"
            f"{SCALER_FILE}"
        )

    # --------------------------------------------------------------
    # FEATURE LIST
    # --------------------------------------------------------------

    if not os.path.exists(FEATURE_FILE):

        raise FileNotFoundError(
            "Feature list not found:\n"
            f"{FEATURE_FILE}"
        )

    # --------------------------------------------------------------
    # IMPUTER
    # --------------------------------------------------------------

    if not os.path.exists(IMPUTER_FILE):

        raise FileNotFoundError(
            "Imputer not found:\n"
            f"{IMPUTER_FILE}"
        )

    # --------------------------------------------------------------
    # LOAD
    # --------------------------------------------------------------

    model = joblib.load(
        MODEL_FILE
    )

    scaler = joblib.load(
        SCALER_FILE
    )

    feature_columns = joblib.load(
        FEATURE_FILE
    )

    imputer = joblib.load(
        IMPUTER_FILE
    )

    # --------------------------------------------------------------
    # VALIDATE FEATURE LIST
    # --------------------------------------------------------------

    if not isinstance(
        feature_columns,
        (list, tuple)
    ):

        raise TypeError(
            "Saved feature list must be "
            "a list or tuple."
        )

    feature_columns = list(
        feature_columns
    )

    if len(feature_columns) == 0:

        raise ValueError(
            "Saved feature list is empty."
        )

    # --------------------------------------------------------------
    # VALIDATE IMPUTER
    # --------------------------------------------------------------

    if not hasattr(imputer, 'transform'):

        raise TypeError(
            "Loaded imputer must have a 'transform' method."
        )

    print(
        "Isolation Forest loaded."
    )

    print(
        f"Scaler loaded."
    )

    print(
        f"Feature list loaded."
    )

    print(
        f"Imputer loaded."
    )

    print(
        f"Expected ML Features : "
        f"{len(feature_columns)}"
    )

    return (
        model,
        scaler,
        feature_columns,
        imputer,
    )


# ======================================================================
# VALIDATE FEATURE SCHEMA
# ======================================================================

def validate_feature_schema(
    df: pd.DataFrame,
    feature_columns: list
) -> None:

    print()
    print("=" * 70)
    print("VALIDATING FEATURE SCHEMA")
    print("=" * 70)

    # --------------------------------------------------------------
    # MISSING FEATURES
    # --------------------------------------------------------------

    missing_features = [
        feature
        for feature in feature_columns
        if feature not in df.columns
    ]

    if missing_features:

        print()
        print(
            "MISSING FEATURES:"
        )

        for feature in missing_features:

            print(
                f" - {feature}"
            )

        raise ValueError(
            "Preprocessed client data does not "
            "contain all features required by "
            "the trained model."
        )

    # --------------------------------------------------------------
    # EXTRA FEATURES
    # --------------------------------------------------------------

    extra_features = [
        column
        for column in df.columns
        if column not in feature_columns
        and column not in ID_COLUMNS
    ]

    if extra_features:

        print()
        print(
            "Extra columns detected."
        )

        print(
            "These columns will be ignored "
            "by the ML model:"
        )

        for feature in extra_features:

            print(
                f" - {feature}"
            )

    # --------------------------------------------------------------
    # FEATURE COUNT
    # --------------------------------------------------------------

    print()
    print(
        f"Required ML Features : "
        f"{len(feature_columns)}"
    )

    print(
        "Feature schema validation passed."
    )


# ======================================================================
# PREPARE MODEL FEATURES
# ======================================================================

def prepare_features(
    df: pd.DataFrame,
    feature_columns: list,
    imputer
) -> pd.DataFrame:

    print()
    print("=" * 70)
    print("PREPARING MODEL FEATURES")
    print("=" * 70)

    # --------------------------------------------------------------
    # SELECT EXACT TRAINING FEATURES
    # --------------------------------------------------------------

    X = df[
        feature_columns
    ].copy()

    # --------------------------------------------------------------
    # CONVERT TO NUMERIC
    # --------------------------------------------------------------

    for column in X.columns:

        X[column] = pd.to_numeric(
            X[column],
            errors="coerce"
        )

    # --------------------------------------------------------------
    # INFINITE VALUES
    # --------------------------------------------------------------

    X.replace(
        [
            np.inf,
            -np.inf,
        ],
        np.nan,
        inplace=True
    )

    # --------------------------------------------------------------
    # MISSING VALUES - IMPUTATION
    # --------------------------------------------------------------
    #
    # The imputer was fitted on the TRAINING dataset during
    # ML Training and contains the median value per feature.
    #
    # Prediction must ONLY call imputer.transform() to apply
    # those learned medians. It must NOT call fit() or
    # fit_transform() on client data.
    # --------------------------------------------------------------

    missing_before = (
        X.isna()
        .sum()
        .sum()
    )

    if missing_before > 0:

        print()
        print(
            f"Missing feature values detected : "
            f"{missing_before}"
        )

        print(
            "Applying trained imputer (median strategy)..."
        )

        X_imputed = imputer.transform(X)

        # Convert back to DataFrame to preserve column names
        X = pd.DataFrame(
            X_imputed,
            columns=X.columns,
            index=X.index
        )

        missing_after = (
            X.isna()
            .sum()
            .sum()
        )

        print(
            f"Missing values after imputation : "
            f"{missing_after}"
        )

        if missing_after > 0:
            raise ValueError(
                "NaN values remain after imputation."
            )
    else:
        print(
            "No missing values detected. Imputation skipped."
        )

    # --------------------------------------------------------------
    # FINAL VALIDATION
    # --------------------------------------------------------------

    if not np.isfinite(
        X.to_numpy()
    ).all():

        raise ValueError(
            "Infinite values remain in "
            "the model feature matrix."
        )

    # --------------------------------------------------------------
    # NUMERIC VALIDATION
    # --------------------------------------------------------------

    non_numeric = [
        column
        for column in X.columns
        if not pd.api.types.is_numeric_dtype(
            X[column]
        )
    ]

    if non_numeric:

        raise ValueError(
            "Non-numeric ML features found:\n"
            f"{non_numeric}"
        )

    print(
        f"Feature Matrix Shape : "
        f"{X.shape}"
    )

    print(
        "Model feature preparation "
        "completed."
    )

    return X


# ======================================================================
# APPLY TRAINED SCALER
# ======================================================================

def scale_features(
    X: pd.DataFrame,
    scaler
):

    print()
    print("=" * 70)
    print("APPLYING TRAINED SCALER")
    print("=" * 70)

    X_scaled = scaler.transform(
        X
    )

    # --------------------------------------------------------------
    # RESTORE FEATURE NAMES
    #
    # scaler.transform() returns an unnamed NumPy array,
    # but the trained Isolation Forest was fitted with
    # feature names. Rebuild the DataFrame so the model
    # receives named features in the exact training order.
    # --------------------------------------------------------------

    X_scaled = pd.DataFrame(
        X_scaled,
        columns=X.columns,
        index=X.index
    )

    if not np.isfinite(
        X_scaled.to_numpy()
    ).all():

        raise ValueError(
            "Scaled feature matrix contains "
            "NaN or infinite values."
        )

    print(
        "Trained RobustScaler applied successfully."
    )

    print(
        f"Scaled Matrix Shape : "
        f"{X_scaled.shape}"
    )

    return X_scaled


# ======================================================================
# GENERATE ISOLATION FOREST PREDICTIONS
# ======================================================================

def generate_predictions(
    model,
    X_scaled
):

    print()
    print("=" * 70)
    print("GENERATING ISOLATION FOREST PREDICTIONS")
    print("=" * 70)

    # --------------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------------

    predictions = model.predict(
        X_scaled
    )

    # --------------------------------------------------------------
    # DECISION FUNCTION
    # --------------------------------------------------------------

    decision_scores = (
        model.decision_function(
            X_scaled
        )
    )

    # --------------------------------------------------------------
    # LABELS
    #
    # Isolation Forest:
    #     1  = Normal
    #    -1  = Anomaly
    # --------------------------------------------------------------

    labels = [
        ANOMALY_LABEL
        if prediction == -1
        else NORMAL_LABEL

        for prediction in predictions
    ]

    # --------------------------------------------------------------
    # ANOMALY SCORE
    # --------------------------------------------------------------

    anomaly_scores = (
        decision_scores
        * ANOMALY_SCORE_MULTIPLIER
    )

    print(
        "Predictions generated successfully."
    )

    return (
        labels,
        decision_scores,
        anomaly_scores,
    )


# ======================================================================
# CREATE RESULT DATAFRAME
# ======================================================================

def create_results(
    df: pd.DataFrame,
    labels,
    decision_scores,
    anomaly_scores
) -> pd.DataFrame:

    results = df[
        ID_COLUMNS
    ].copy()

    results[
        "Prediction"
    ] = labels

    results[
        "Decision Score"
    ] = np.round(
        decision_scores,
        6
    )

    results[
        "Anomaly Score"
    ] = np.round(
        anomaly_scores,
        6
    )

    return results


# ======================================================================
# SAVE RESULTS
# ======================================================================

def save_results(
    results: pd.DataFrame
) -> None:

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    results.to_csv(
        PREDICTION_FILE,
        index=False,
        encoding=CSV_ENCODING
    )

    print()
    print("=" * 70)
    print("PREDICTION RESULTS SAVED")
    print("=" * 70)

    print(
        PREDICTION_FILE
    )


# ======================================================================
# PRINT SUMMARY
# ======================================================================

def print_summary(
    results: pd.DataFrame
) -> None:

    total = len(
        results
    )

    anomalies = (
        results["Prediction"]
        == ANOMALY_LABEL
    ).sum()

    normal = (
        results["Prediction"]
        == NORMAL_LABEL
    ).sum()

    print()
    print("=" * 70)
    print("PREDICTION SUMMARY")
    print("=" * 70)

    print(
        f"Client Company  : "
        f"{results['Company'].iloc[0]}"
    )

    print(
        f"Financial Years  : "
        f"{results['Year'].min()} - "
        f"{results['Year'].max()}"
    )

    print(
        f"Total Records    : "
        f"{total}"
    )

    print(
        f"Normal Records   : "
        f"{normal}"
    )

    print(
        f"Anomalies        : "
        f"{anomalies}"
    )

    print()

    print(
        "Predictions:"
    )

    print()

    print(
        results.to_string(
            index=False
        )
    )

    print()


# ======================================================================
# MAIN
# ======================================================================

def main():

    print()
    print("=" * 70)
    print("FINANCIAL ANOMALY PREDICTION")
    print("=" * 70)

    print()
    print(
        "INPUT MODE : PREPROCESSED CLIENT DATA"
    )

    # ==============================================================
    # STEP 1
    # ==============================================================

    df = load_client_dataset()

    # ==============================================================
    # STEP 2
    # ==============================================================

    df = validate_client_dataset(
        df
    )

    # ==============================================================
    # STEP 3
    # ==============================================================

    (
        model,
        scaler,
        feature_columns,
        imputer,
    ) = load_model_artifacts()

    # ==============================================================
    # STEP 4
    # ==============================================================

    validate_feature_schema(
        df,
        feature_columns
    )

    # ==============================================================
    # STEP 5
    # ==============================================================

    X = prepare_features(
        df,
        feature_columns,
        imputer
    )

    # ==============================================================
    # STEP 6
    # ==============================================================

    X_scaled = scale_features(
        X,
        scaler
    )

    # ==============================================================
    # STEP 7
    # ==============================================================

    (
        labels,
        decision_scores,
        anomaly_scores,
    ) = generate_predictions(
        model,
        X_scaled
    )

    # ==============================================================
    # STEP 8
    # ==============================================================

    results = create_results(
        df,
        labels,
        decision_scores,
        anomaly_scores
    )

    # ==============================================================
    # STEP 9
    # ==============================================================

    save_results(
        results
    )

    # ==============================================================
    # STEP 10
    # ==============================================================

    print_summary(
        results
    )

    print("=" * 70)
    print("PREDICTION COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print()


# ======================================================================
# PROGRAM ENTRY POINT
# ======================================================================

if __name__ == "__main__":

    try:

        main()

    except Exception as exc:

        print()
        print("=" * 70)
        print("PREDICTION FAILED")
        print("=" * 70)

        print()
        print(
            f"Error : {exc}"
        )

        print()

        raise
