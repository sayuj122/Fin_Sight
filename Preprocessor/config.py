"""
==========================================================
Project:
A Hybrid Rule-Based and Explainable Machine Learning
Framework for Financial Statement Anomaly Detection

File:
config.py

Purpose:
Central configuration file for the dataset creation pipeline.

Author:
Your Name

==========================================================
"""

import os

# ==========================================================
# PROJECT PATHS
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RAW_DATA_FOLDER = os.path.join(
    BASE_DIR,
    "input"
)

OUTPUT_FOLDER = os.path.join(
    BASE_DIR,
    "output"
)

FINANCIAL_DATASET = os.path.join(
    OUTPUT_FOLDER,
    "financial_dataset.csv"
)

ML_DATASET = os.path.join(
    OUTPUT_FOLDER,
    "preprocessed_client_data.csv"
)

# Automatically create output folder
os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)

# ==========================================================
# EXCEL CONFIGURATION
# ==========================================================

INPUT_SHEET_NAME = "Data Sheet"

# ==========================================================
# SECTION HEADERS
# ==========================================================

SECTION_HEADERS = {
    "PL": "PROFIT & LOSS",
    "QT": "QUARTERS",
    "BS": "BALANCE SHEET",
    "CF": "CASH FLOW"
}

# ==========================================================
# RAW METRICS TO EXTRACT
# ==========================================================

RAW_METRICS = {

    "Profit_Loss": [

    "Sales",

    "Expenses",

    "Operating Profit",

    "Raw Material Cost",

    "Change in Inventory",

    "Power and Fuel",

    "Other Mfr. Exp",

    "Employee Cost",

    "Selling and admin",

    "Other Expenses",

    "Other Income",

    "Depreciation",

    "Interest",

    "Profit before tax",

    "Tax",

    "Net profit",

    "Dividend Amount"

],

    "Balance_Sheet": [

        "Equity Share Capital",
        "Reserves",
        "Borrowings",
        "Other Liabilities",
        "Total",
        "Net Block",
        "Capital Work in Progress",
        "Investments",
        "Other Assets",
        "Receivables",
        "Inventory",
        "Cash & Bank"

    ],

    "Cash_Flow": [

        "Cash from Operating Activity",
        "Cash from Investing Activity",
        "Cash from Financing Activity",
        "Net Cash Flow"

    ]
}

# ==========================================================
# TOTAL ROW MAPPING
# ==========================================================

# Screener Excel contains two rows named "Total"
#
# First Total  -> Total Liabilities
# Second Total -> Total Assets

TOTAL_ROW_MAPPING = {

    1: "Total Liabilities",

    2: "Total Assets"

}

# ==========================================================
# IDENTIFIER COLUMNS
# ==========================================================

ID_COLUMNS = [

    "Company",
    "Year"

]

# ==========================================================
# SORT ORDER
# ==========================================================

SORT_COLUMNS = [

    "Company",
    "Year"

]

# ==========================================================
# REQUIRED COLUMNS
# ==========================================================

REQUIRED_COLUMNS = [

    "Company",
    "Year",

    "Sales",

    "Operating Profit",

    "Net profit",

    "Borrowings",

    "Equity Share Capital",

    "Reserves",

    "Other Assets",

    "Total Assets",

    "Cash from Operating Activity"

]

# ==========================================================
# COLUMNS TO REMOVE
# ==========================================================

DROP_COLUMNS = [

    "Report Date",
    "PRICE:",
    "Adjusted Equity Shares in Cr",
    "Face value",
    "New Bonus Shares",
    "No. of Equity Shares"

]


# ==========================================================
# REQUIRED RAW DATASET COLUMNS
# ==========================================================

REQUIRED_COLUMNS = [

    # Identifiers
    "Company",
    "Year",

    # Profit & Loss
    "Sales",
    "Operating Profit",
    "Profit before tax",
    "Net profit",

    # Balance Sheet
    "Equity Share Capital",
    "Reserves",
    "Borrowings",
    "Total Assets",
    "Total Liabilities",

    # Cash Flow
    "Cash from Operating Activity",
    "Cash from Investing Activity",
    "Cash from Financing Activity",
    "Net Cash Flow"

]
# ==========================================================
# FEATURE ENGINEERING
# ==========================================================

ENGINEERED_FEATURES = [

    # Profitability

    "Profit_Margin",
    "Operating_Margin",
    "ROE",
    "ROA",

    # Solvency

    "Debt_to_Equity",
    "Debt_Ratio",
    "Equity_Ratio",
    "Interest_Coverage",
    "Borrowing_Dependency",

    # Liquidity

    "Working_Capital_Ratio",

    # Efficiency

    "Asset_Utilization",
    "Receivable_Ratio",
    "Inventory_Ratio",
    "Expense_Ratio",
    "Depreciation_Ratio",

    # Cash Flow

    "Operating_CF_Ratio",
    "Cash_to_Debt",
    "Cash_Margin",

    # Growth

    "Revenue_Growth",
    "Profit_Growth",
    "Borrowing_Growth",
    "Asset_Growth",
    "Reserve_Growth",
    "Operating_CF_Growth",
    "Receivable_Growth",
    "Inventory_Growth",
    "Cash_Growth",

    # Trend

    "Revenue_CAGR_3Y",
    "Profit_CAGR_3Y",
    "Revenue_Volatility",
    "Profit_Volatility",
    "Operating_CF_Volatility"

]

# ==========================================================
# TREND CONFIGURATION
# ==========================================================

TREND_WINDOW = 3

# ==========================================================
# PREPROCESSING
# ==========================================================

# Missing-value strategy.
#
# "keep_nan" preserves genuinely missing / unavailable financial values
# as NaN throughout preprocessing and in the final exported dataset.
# Genuine reported zero values are untouched.
MISSING_VALUE_STRATEGY = "keep_nan"

ROUND_DECIMALS = 4

# ==========================================================
# MACHINE LEARNING CONFIGURATION
# ==========================================================

RANDOM_STATE = 42

SCALER = "RobustScaler"

# Available options:
# "RobustScaler"
# "StandardScaler"
# "MinMaxScaler"

# ==========================================================
# CSV CONFIGURATION
# ==========================================================

CSV_ENCODING = "utf-8"

# ==========================================================
# LOGGING
# ==========================================================

PRINT_PROGRESS = True

VERBOSE = True