"""
==========================================================
Project:
A Hybrid Rule-Based and Explainable Machine Learning
Framework for Financial Statement Anomaly Detection

File:
preprocess_dataset.py

Purpose:
Preprocess the extracted financial dataset and prepare
it for feature engineering and machine learning.

Part 1
Imports
Configuration
Load Dataset
Inspection
Basic Cleaning
Helper Functions
==========================================================
"""

# ==========================================================
# IMPORTS
# ==========================================================

import os

import pandas as pd
import numpy as np

from config import (
    FINANCIAL_DATASET,
    ML_DATASET,
    DROP_COLUMNS,
    REQUIRED_COLUMNS,
    SORT_COLUMNS,
    ID_COLUMNS,
    ROUND_DECIMALS,
    MISSING_VALUE_STRATEGY,
    CSV_ENCODING,
    PRINT_PROGRESS,
    VERBOSE
)

# ==========================================================
# HELPER FUNCTION
# Logging
# ==========================================================

def log(message):

    if PRINT_PROGRESS:
        print(message)

# ==========================================================
# HELPER FUNCTION
# Safe Division
# ==========================================================

def safe_divide(numerator, denominator):

    denominator = denominator.replace(0, np.nan)

    result = numerator / denominator

    result = result.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # A ratio is left as NaN whenever it cannot be meaningfully
    # calculated: missing numerator, or a zero / missing denominator.
    return result

# ==========================================================
# LOAD DATASET
# ==========================================================

log("Loading financial dataset...")

df = pd.read_csv(

    FINANCIAL_DATASET,

    encoding=CSV_ENCODING

)

log("Dataset Loaded Successfully.")

# ==========================================================
# DATASET INSPECTION
# ==========================================================

if VERBOSE:

    print()

    print("=" * 60)

    print("DATASET INFORMATION")

    print("=" * 60)

    print(f"Shape : {df.shape}")

    print()

    print("Columns")

    for col in df.columns:

        print(f" - {col}")

    print()

    print("Data Types")

    print(df.dtypes)

    print()

# ==========================================================
# REMOVE DUPLICATE ROWS
# ==========================================================

before = len(df)

df.drop_duplicates(

    inplace=True

)

after = len(df)

duplicates_removed = before - after

log(f"Duplicate Rows Removed : {duplicates_removed}")

# ==========================================================
# REMOVE UNNECESSARY COLUMNS
# ==========================================================

df.drop(

    columns=DROP_COLUMNS,

    errors="ignore",

    inplace=True

)

log("Unused columns removed.")

# ==========================================================
# VALIDATE RAW INPUT DATASET
# ==========================================================

missing_identifier_columns = [

    column

    for column in SORT_COLUMNS

    if column not in df.columns

]

if len(missing_identifier_columns) > 0:

    raise ValueError(

        "The financial dataset is missing required identifier columns: "
        f"{missing_identifier_columns}. "
        "This usually means the extraction step did not produce the expected raw dataset. "
        f"Expected columns: {SORT_COLUMNS}. Found columns: {list(df.columns)}. "
        "Run extract_dataset.py to regenerate output/financial_dataset.csv."

    )

if df.empty:

    raise ValueError(

        "The financial dataset is empty. "
        "Run extract_dataset.py to regenerate output/financial_dataset.csv."

    )

# ==========================================================
# SORT DATASET
# ==========================================================

df.sort_values(

    by=SORT_COLUMNS,

    inplace=True

)

df.reset_index(

    drop=True,

    inplace=True

)

# ==========================================================
# CONVERT NUMERIC COLUMNS
# ==========================================================

numeric_columns = [

    col

    for col in df.columns

    if col not in ID_COLUMNS

]

for col in numeric_columns:

    df[col] = pd.to_numeric(

        df[col],

        errors="coerce"

    )

log("Numeric conversion completed.")

# ==========================================================
# HANDLE MISSING VALUES
# ==========================================================

missing_before = df.isna().sum().sum()

if MISSING_VALUE_STRATEGY == "fill_zero":

    # Backwards-compatible option: replace missing values with 0.
    df.fillna(

        0,

        inplace=True

    )

elif MISSING_VALUE_STRATEGY == "keep_nan":

    # Preserve genuinely missing / unavailable financial values as NaN.
    # They are not the same as a reported zero.
    log("Keeping missing values as NaN.")

else:

    raise ValueError(
        "Invalid MISSING_VALUE_STRATEGY: "
        f"'{MISSING_VALUE_STRATEGY}'. "
        "Expected 'fill_zero' or 'keep_nan'."
    )

missing_after = df.isna().sum().sum()

log(f"Missing Values Before : {missing_before}")

log(f"Missing Values After  : {missing_after}")

# ==========================================================
# REMOVE INFINITE VALUES
# ==========================================================

df.replace(

    [np.inf, -np.inf],

    0,

    inplace=True

)

# ==========================================================
# HELPER FUNCTION
# Print Dataset Summary
# ==========================================================

def print_summary(dataframe):

    if not VERBOSE:

        return

    print()

    print("=" * 60)

    print("DATASET SUMMARY")

    print("=" * 60)

    print(f"Rows    : {len(dataframe)}")

    print(f"Columns : {len(dataframe.columns)}")

    print()

    print(dataframe.head())

    print()

print_summary(df)

# ==========================================================
# Part 2 Starts Here
# Dataset Validation
# Numeric Validation
# Data Quality Checks
# ==========================================================
# ==========================================================
# DATASET VALIDATION
# ==========================================================

log("\nValidating dataset...")

# ==========================================================
# CHECK REQUIRED COLUMNS
# ==========================================================

missing_columns = [

    column

    for column in REQUIRED_COLUMNS

    if column not in df.columns

]

if "Operating Profit" in missing_columns or "Expenses" in missing_columns:

    expense_fields = [

        "Raw Material Cost",
        "Change in Inventory",
        "Power and Fuel",
        "Other Mfr. Exp",
        "Employee Cost",
        "Selling and admin",
        "Other Expenses",
        "Depreciation",
        "Interest"

    ]

    available_expense_fields = [

        field

        for field in expense_fields

        if field in df.columns

    ]

    if len(available_expense_fields) > 0:

        df["Expenses"] = df[available_expense_fields].sum(axis=1)

    if "Sales" in df.columns and "Expenses" in df.columns:

        df["Operating Profit"] = (
            df["Sales"]
            - df["Expenses"]
            + df["Other Income"].fillna(0)
            if "Other Income" in df.columns
            else df["Sales"] - df["Expenses"]
        )

    if "Operating Profit" in missing_columns:

        missing_columns.remove("Operating Profit")

    if "Expenses" in missing_columns:

        missing_columns.remove("Expenses")

if len(missing_columns) > 0:

    raise ValueError(

        f"Required columns missing:\n{missing_columns}"

    )

log("Required columns validation passed.")

# ==========================================================
# CHECK COMPANY NAMES
# ==========================================================

missing_company = df["Company"].isna().sum()

empty_company = (

    df["Company"]

    .astype(str)

    .str.strip()

    .eq("")

    .sum()

)

print(f"Missing Company Names : {missing_company}")

print(f"Empty Company Names   : {empty_company}")

# ==========================================================
# CHECK YEAR VALUES
# ==========================================================

invalid_years = df[

    (df["Year"] < 1990)

    |

    (df["Year"] > 2100)

]

print(f"Invalid Years : {len(invalid_years)}")

# ==========================================================
# CHECK DUPLICATE COMPANY-YEAR
# ==========================================================

duplicates = df.duplicated(

    subset=["Company", "Year"]

)

duplicate_count = duplicates.sum()

print(f"Duplicate Company-Year Records : {duplicate_count}")

# ==========================================================
# CHECK NEGATIVE VALUES
# ==========================================================

validation_columns = [

    "Sales",

    "Borrowings",

    "Equity Share Capital",

    "Reserves",

    "Total Assets"

]

for column in validation_columns:

    if column not in df.columns:

        continue

    negatives = (

        df[column] < 0

    ).sum()

    print(

        f"{column:<30}"

        f"Negative Values : {negatives}"

    )

# ==========================================================
# CHECK MISSING VALUES PER COLUMN
# ==========================================================

print()

print("=" * 60)

print("MISSING VALUES")

print("=" * 60)

missing_summary = (

    df.isnull()

      .sum()

      .sort_values(

          ascending=False

      )

)

print(

    missing_summary[

        missing_summary > 0

    ]

)

# ==========================================================
# CHECK ZERO VALUES
# ==========================================================

print()

print("=" * 60)

print("ZERO VALUE SUMMARY")

print("=" * 60)

for column in validation_columns:

    if column not in df.columns:

        continue

    zero_count = (

        df[column] == 0

    ).sum()

    print(

        f"{column:<30}"

        f"{zero_count}"

    )

# ==========================================================
# FINAL DATASET INFORMATION
# ==========================================================

print()

print("=" * 60)

print("VALIDATION SUMMARY")

print("=" * 60)

print(f"Rows    : {len(df)}")

print(f"Columns : {len(df.columns)}")

print()

print("Validation Completed Successfully.")

# ==========================================================
# Part 3 Starts Here
# Feature Engineering
# ==========================================================
# ==========================================================
# FEATURE ENGINEERING
# ==========================================================

log("\nCalculating financial ratios...")

# ==========================================================
# COMMON VARIABLES
# ==========================================================

equity = (
    df["Equity Share Capital"] +
    df["Reserves"]
)

total_assets = df["Total Assets"]

total_liabilities = df["Total Liabilities"]

sales = df["Sales"]

net_profit = df["Net profit"]

borrowings = df["Borrowings"]

interest = df["Interest"]

pbt = df["Profit before tax"]

operating_profit = df["Operating Profit"]

cash = df["Cash & Bank"]

receivables = df["Receivables"]

inventory = df["Inventory"]

other_assets = df["Other Assets"]

expenses = df["Expenses"]

depreciation = df["Depreciation"]

operating_cf = df["Cash from Operating Activity"]

# ==========================================================
# PROFITABILITY RATIOS
# ==========================================================

log("Calculating Profitability Ratios...")

df["Profit_Margin"] = safe_divide(
    net_profit,
    sales
)

df["Operating_Margin"] = safe_divide(
    operating_profit,
    sales
)

df["ROE"] = safe_divide(
    net_profit,
    equity
)

df["ROA"] = safe_divide(
    net_profit,
    total_assets
)

# ==========================================================
# SOLVENCY RATIOS
# ==========================================================

log("Calculating Solvency Ratios...")

# NOTE:
# In the Screener Balance Sheet export, the first "Total" row represents
# Total Liabilities + Equity, not true Total Liabilities. Because the source
# Excel does not expose a genuine liabilities-only total, debt-style ratios that
# divide by that total are not meaningful and are therefore excluded.

df["Debt_to_Equity"] = safe_divide(
    borrowings,
    equity
)

df["Interest_Coverage"] = safe_divide(
    pbt,
    interest + 1
)

# ==========================================================
# LIQUIDITY RATIOS
# ==========================================================

log("Calculating Liquidity Ratios...")

df["Working_Capital_Ratio"] = safe_divide(
    cash,
    total_liabilities + 1
)

# ==========================================================
# EFFICIENCY RATIOS
# ==========================================================

log("Calculating Efficiency Ratios...")

df["Asset_Utilization"] = safe_divide(
    sales,
    other_assets
)

df["Receivable_Ratio"] = safe_divide(
    receivables,
    sales
)

df["Inventory_Ratio"] = safe_divide(
    inventory,
    sales
)

df["Expense_Ratio"] = safe_divide(
    expenses,
    sales
)

df["Depreciation_Ratio"] = safe_divide(
    depreciation,
    total_assets
)

# ==========================================================
# CASH FLOW RATIOS
# ==========================================================

log("Calculating Cash Flow Ratios...")

df["Operating_CF_Ratio"] = safe_divide(
    operating_cf,
    sales
)

df["Cash_to_Debt"] = safe_divide(
    cash,
    borrowings + 1
)

df["Cash_Margin"] = safe_divide(
    operating_cf,
    net_profit
)

# ==========================================================
# ROUND ENGINEERED FEATURES
# ==========================================================

ratio_columns = [

    "Profit_Margin",

    "Operating_Margin",

    "ROE",

    "ROA",

    "Debt_to_Equity",

    "Interest_Coverage",

    "Working_Capital_Ratio",

    "Asset_Utilization",

    "Receivable_Ratio",

    "Inventory_Ratio",

    "Expense_Ratio",

    "Depreciation_Ratio",

    "Operating_CF_Ratio",

    "Cash_to_Debt",

    "Cash_Margin"

]

for column in ratio_columns:

    df[column] = df[column].round(
        ROUND_DECIMALS
    )

log("Ratio Feature Engineering Completed.")

print()

print("=" * 60)

print("ENGINEERED RATIO FEATURES")

print("=" * 60)

for feature in ratio_columns:

    print(feature)

print()

# ==========================================================
# Part 4 Starts Here
# Growth Features
# Trend Features
# Save Dataset
# ==========================================================
# ==========================================================
# PART 4
# Growth Features
# Trend Features
# Final Cleanup
# Save Dataset
# ==========================================================

log("\nCalculating Growth Features...")

# ==========================================================
# GROWTH FEATURES (Year-over-Year)
# ==========================================================

growth_columns = {

    "Sales": "Revenue_Growth",

    "Net profit": "Profit_Growth",

    "Borrowings": "Borrowing_Growth",

    "Total Assets": "Asset_Growth",

    "Reserves": "Reserve_Growth",

    "Cash from Operating Activity": "Operating_CF_Growth",

    "Receivables": "Receivable_Growth",

    "Inventory": "Inventory_Growth",

    "Cash & Bank": "Cash_Growth"

}

for source, target in growth_columns.items():

    if source in df.columns:

        df[target] = (

            df.groupby("Company")[source]

              .pct_change()

        )

# ==========================================================
# CAGR CALCULATION
# ==========================================================

log("Calculating CAGR Features...")

def calculate_cagr(series, years=3):

    result = np.zeros(len(series))

    values = series.values

    for i in range(years, len(values)):

        start = values[i - years]

        end = values[i]

        if start > 0 and end > 0:

            result[i] = (

                (end / start) ** (1 / years)

            ) - 1

        elif pd.isna(start) or pd.isna(end):

            # A missing endpoint cannot give a meaningful CAGR;
            # propagate NaN instead of a fabricated 0.
            result[i] = np.nan

        else:

            result[i] = 0

    return pd.Series(

        result,

        index=series.index

    )

df["Revenue_CAGR_3Y"] = (

    df.groupby("Company")["Sales"]

      .transform(calculate_cagr)

)

df["Profit_CAGR_3Y"] = (

    df.groupby("Company")["Net profit"]

      .transform(calculate_cagr)

)

# ==========================================================
# VOLATILITY FEATURES
# ==========================================================

log("Calculating Volatility Features...")

df["Revenue_Volatility"] = (

    df.groupby("Company")["Sales"]

      .transform(

          lambda x:

          x.rolling(

              window=3,

              min_periods=1

          ).std()

      )

)

df["Profit_Volatility"] = (

    df.groupby("Company")["Net profit"]

      .transform(

          lambda x:

          x.rolling(

              window=3,

              min_periods=1

          ).std()

      )

)

df["Operating_CF_Volatility"] = (

    df.groupby("Company")["Cash from Operating Activity"]

      .transform(

          lambda x:

          x.rolling(

              window=3,

              min_periods=1

          ).std()

      )

)

# ==========================================================
# REPLACE INFINITE VALUES (KEEP NaN AS MISSING)
# ==========================================================

log("Cleaning engineered features...")

# Infinite results of division are un-calculable and become NaN.
# Genuinely missing values (missing source metric, zero denominator,
# undefined growth/volatility) are deliberately preserved as NaN here.
df.replace(

    [np.inf, -np.inf],

    np.nan,

    inplace=True

)

# ==========================================================
# ROUND ALL ENGINEERED FEATURES
# ==========================================================

engineered_features = [

    "Revenue_Growth",

    "Profit_Growth",

    "Borrowing_Growth",

    "Asset_Growth",

    "Reserve_Growth",

    "Operating_CF_Growth",

    "Receivable_Growth",

    "Inventory_Growth",

    "Cash_Growth",

    "Revenue_CAGR_3Y",

    "Profit_CAGR_3Y",

    "Revenue_Volatility",

    "Profit_Volatility",

    "Operating_CF_Volatility"

]

for feature in engineered_features:

    if feature in df.columns:

        df[feature] = df[feature].round(

            ROUND_DECIMALS

        )

# ==========================================================
# FINAL DATASET SORTING
# ==========================================================

df.sort_values(

    by=SORT_COLUMNS,

    inplace=True

)

df.reset_index(

    drop=True,

    inplace=True

)

# ==========================================================
# FINAL VALIDATION
# ==========================================================

log("Running final validation...")

print()

print("=" * 70)

print("FINAL DATASET SUMMARY")

print("=" * 70)

print(f"Rows                : {len(df)}")

print(f"Columns             : {len(df.columns)}")

print(f"Missing Values      : {df.isnull().sum().sum()}")

print(f"Duplicate Rows      : {df.duplicated().sum()}")

print()

# ==========================================================
# SAVE ML DATASET
# ==========================================================

output_dir = os.path.dirname(ML_DATASET)

os.makedirs(
    output_dir,
    exist_ok=True
)

# Write to a temporary file first so a locked output file does not
# interrupt the whole pipeline. This also gives a clearer error if the
# destination is still open in another process.

temp_path = os.path.join(
    output_dir,
    f".{os.path.basename(ML_DATASET)}.{os.getpid()}.tmp"
)

try:

    df.to_csv(
        temp_path,
        index=False,
        encoding=CSV_ENCODING
    )

    if os.path.exists(ML_DATASET):

        os.remove(ML_DATASET)

    os.replace(
        temp_path,
        ML_DATASET
    )

except PermissionError as exc:

    if os.path.exists(temp_path):

        os.remove(temp_path)

    raise PermissionError(
        f"Could not write to {ML_DATASET}. Close the file if it is open in Excel, VS Code, or another program and try again."
    ) from exc

except Exception:

    if os.path.exists(temp_path):

        os.remove(temp_path)

    raise

# ==========================================================
# PRINT ENGINEERED FEATURES
# ==========================================================

print("Growth & Trend Features")

print("-----------------------")

for feature in engineered_features:

    print(f" - {feature}")

print()

print("Dataset Saved Successfully")

print(ML_DATASET)

print()

print("=" * 70)

print("PREPROCESSING COMPLETED SUCCESSFULLY")

print("=" * 70)

print()

print(df.head())

print()

print(df.info())
