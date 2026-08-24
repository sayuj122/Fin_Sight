"""
==============================================================
Project:
A Hybrid Rule-Based and Explainable Machine Learning Framework
for Financial Statement Anomaly Detection

File:
extract_dataset.py

Purpose:
Extract financial metrics from Screener.in Excel workbooks
and create a standardized financial dataset.

Author:
Your Name
==============================================================
"""

# ==========================================================
# IMPORTS
# ==========================================================

import os
import warnings
import pandas as pd
import numpy as np

from config import (
    RAW_DATA_FOLDER,
    FINANCIAL_DATASET,
    INPUT_SHEET_NAME,
    PRINT_PROGRESS,
    VERBOSE,
    CSV_ENCODING
)

warnings.filterwarnings("ignore")

# ==========================================================
# GLOBAL DATASET
# ==========================================================

dataset = []

# ==========================================================
# SHEET NAMES
# ==========================================================

SHEETS = {
    "PL": "Profit & Loss",
    "BS": "Balance Sheet",
    "CF": "Cash Flow"
}

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def print_separator(length=70):
    """Print separator line."""

    print("=" * length)


def print_company_header(company_name):
    """Print company heading."""

    print_separator()
    print(company_name.upper())
    print_separator()


def safe_string(value):
    """
    Convert value to clean string.
    """

    if pd.isna(value):
        return ""

    return str(value).strip()


def is_blank(value):
    """
    Check whether cell is blank.
    """

    if pd.isna(value):
        return True

    if str(value).strip() == "":
        return True

    return False


def is_year(value):
    """
    Check whether a cell represents a financial year/date.
    """

    try:

        pd.to_datetime(value)

        return True

    except Exception:

        return False


def to_year(value):
    """
    Convert datetime/date to year.
    """

    try:

        return pd.to_datetime(value).year

    except Exception:

        return None


# ==========================================================
# EXCEL READING
# ==========================================================

def load_sheet(file_path, sheet_name):
    """
    Read a worksheet from Excel.

    Returns
    -------
    pandas.DataFrame
    """

    return pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        header=None
    )


# ==========================================================
# COMPANY NAME
# ==========================================================

def get_company_name(file_path):
    """
    Read company name from Data Sheet.

    Returns
    -------
    str
    """

    try:

        meta = pd.read_excel(
            file_path,
            sheet_name=INPUT_SHEET_NAME,
            header=None
        )

        company = safe_string(meta.iloc[0, 1])

        if company == "":
            company = os.path.splitext(
                os.path.basename(file_path)
            )[0].upper()

        return company

    except Exception:

        return os.path.splitext(
            os.path.basename(file_path)
        )[0].upper()


# ==========================================================
# FIND NARRATION ROW
# ==========================================================

def find_narration_row(df):
    """
    Locate the row containing 'Narration'.

    Returns
    -------
    int
    """

    for idx in range(len(df)):

        value = safe_string(df.iloc[idx, 0]).lower()

        if value == "narration":

            return idx

    raise ValueError("Narration row not found.")


# ==========================================================
# FIND YEAR COLUMNS
# ==========================================================

def get_year_columns(df, narration_row):
    """
    Detect financial year columns.

    Returns
    -------
    list

    Example

    [
        (1,2017),
        (2,2018),
        ...
    ]
    """

    year_columns = []

    for col in range(1, df.shape[1]):

        value = df.iloc[narration_row, col]

        if is_year(value):

            year_columns.append(
                (
                    col,
                    to_year(value)
                )
            )

    return year_columns


# ==========================================================
# LAST METRIC ROW
# ==========================================================

def last_metric_row(df, narration_row):
    """
    Find where financial metrics end.

    Stops when a long sequence of blank rows begins.
    """

    blank_counter = 0

    for row in range(narration_row + 1, len(df)):

        metric = df.iloc[row, 0]

        if is_blank(metric):

            blank_counter += 1

        else:

            blank_counter = 0

        if blank_counter >= 5:

            return row - blank_counter

    return len(df) - 1


# ==========================================================
# START MESSAGE
# ==========================================================

if PRINT_PROGRESS:

    print_separator()

    print("FINANCIAL DATASET EXTRACTION")

    print_separator()

    print(f"Raw Data Folder : {RAW_DATA_FOLDER}")

    print(f"Output Dataset  : {FINANCIAL_DATASET}")

    print()
#Part 2
# ==========================================================
# GENERIC WORKSHEET PARSER
# ==========================================================

def extract_sheet(df, sheet_name):
    """
    Generic worksheet parser.

    Works for:
        • Profit & Loss
        • Balance Sheet
        • Cash Flow

    Parameters
    ----------
    df : pandas.DataFrame
        Worksheet DataFrame.

    sheet_name : str
        Sheet name.

    Returns
    -------
    list
        List of yearly dictionaries.
    """

    narration_row = find_narration_row(df)

    year_columns = get_year_columns(
        df,
        narration_row
    )

    if len(year_columns) == 0:

        raise Exception(
            f"No financial years found in {sheet_name}"
        )

    end_row = last_metric_row(
        df,
        narration_row
    )

    records = []

    total_counter = 0

    # ------------------------------------------------------
    # Iterate through every financial year
    # ------------------------------------------------------

    for col_index, year in year_columns:

        row_data = {

            "Year": year

        }

        # ----------------------------------------------
        # Iterate through every metric
        # ----------------------------------------------

        total_counter = 0

        for row in range(
            narration_row + 1,
            end_row + 1
        ):

            metric = safe_string(
                df.iloc[row, 0]
            )

            if metric == "":
                continue

            value = df.iloc[
                row,
                col_index
            ]

            # ------------------------------------------
            # Balance Sheet contains two "Total" rows
            # Rename them explicitly.
            # ------------------------------------------

            if (
                sheet_name == "Balance Sheet"
                and metric == "Total"
            ):

                total_counter += 1

                if total_counter == 1:

                    metric = "Total Liabilities"

                elif total_counter == 2:

                    metric = "Total Assets"

            row_data[metric] = value

        records.append(row_data)

    # ------------------------------------------------------
    # Logging
    # ------------------------------------------------------

    if VERBOSE:

        print(
            f"{sheet_name:<18} : "
            f"{len(records)} Years"
        )

    return records


# ==========================================================
# MERGE THREE FINANCIAL STATEMENTS
# ==========================================================

def merge_financial_statements(
    profit_loss,
    balance_sheet,
    cash_flow
):
    """
    Merge yearly Profit & Loss,
    Balance Sheet and Cash Flow.

    Parameters
    ----------
    profit_loss : list

    balance_sheet : list

    cash_flow : list

    Returns
    -------
    list
    """

    merged = {}

    # ---------------------------------------------
    # Merge all statements
    # ---------------------------------------------

    for statement in [

        profit_loss,
        balance_sheet,
        cash_flow

    ]:

        for row in statement:

            year = row["Year"]

            if year not in merged:

                merged[year] = {

                    "Year": year

                }

            merged[year].update(row)

    return list(merged.values())


# ==========================================================
# VALIDATE YEAR COUNTS
# ==========================================================

def validate_extraction(
    profit_loss,
    balance_sheet,
    cash_flow
):
    """
    Validate extracted year counts.
    """

    if VERBOSE:

        print()

        print(
            f"Profit & Loss Years : "
            f"{len(profit_loss)}"
        )

        print(
            f"Balance Sheet Years : "
            f"{len(balance_sheet)}"
        )

        print(
            f"Cash Flow Years     : "
            f"{len(cash_flow)}"
        )

        print()

    years = [

        len(profit_loss),
        len(balance_sheet),
        len(cash_flow)

    ]

    if len(set(years)) != 1:

        print(
            "WARNING : Year count mismatch."
        )

# ==========================================================
# DATA SHEET PARSER (FALLBACK FOR CURRENT SCREENER FORMAT)
# ==========================================================

def extract_data_sheet_records(file_path):
    """
    Parse the current Screener export layout where the actual values live
    in the Data Sheet rather than in the individual statement tabs.
    """

    data_df = pd.read_excel(
        file_path,
        sheet_name=INPUT_SHEET_NAME,
        header=None
    )

    company = get_company_name(file_path)

    section_map = {
        "PROFIT & LOSS": "Profit & Loss",
        "BALANCE SHEET": "Balance Sheet",
        "CASH FLOW": "Cash Flow",
        "QUARTERS": "Quarters"
    }

    section_order = [
        "Profit & Loss",
        "Balance Sheet",
        "Cash Flow"
    ]

    extracted = {}

    for label, statement_name in section_map.items():

        start_row = None

        for idx in range(len(data_df)):

            if safe_string(data_df.iloc[idx, 0]).upper() == label:

                start_row = idx

                break

        if start_row is None:

            continue

        report_row = None

        for idx in range(start_row + 1, min(len(data_df), start_row + 30)):

            if safe_string(data_df.iloc[idx, 0]).lower() == "report date":

                report_row = idx

                break

        if report_row is None:

            continue

        year_columns = []

        for col in range(1, data_df.shape[1]):

            value = data_df.iloc[report_row, col]

            if pd.isna(value):

                continue

            try:

                year = pd.to_datetime(value).year

            except Exception:

                continue

            year_columns.append((col, year))

        if len(year_columns) == 0:

            continue

        section_records = []

        for col_index, year in year_columns:

            total_counter = 0

            row_data = {
                "Year": year
            }

            for row in range(report_row + 1, len(data_df)):

                metric = safe_string(data_df.iloc[row, 0])

                if metric == "":

                    continue

                if (
                    metric.upper() in section_map
                    or metric.upper() == "QUARTERS"
                ):

                    break

                if (
                    statement_name == "Balance Sheet"
                    and metric == "Total"
                ):

                    total_counter += 1

                    if total_counter == 1:

                        metric = "Total Liabilities"

                    elif total_counter == 2:

                        metric = "Total Assets"

                value = data_df.iloc[row, col_index]

                if pd.isna(value):

                    continue

                row_data[metric] = value

            section_records.append(row_data)

        extracted[statement_name] = section_records

    if not extracted:

        raise ValueError(
            f"Unable to parse Data Sheet for {company}."
        )

    profit_loss = extracted.get("Profit & Loss", [])
    balance_sheet = extracted.get("Balance Sheet", [])
    cash_flow = extracted.get("Cash Flow", [])

    if len(profit_loss) == 0 and len(balance_sheet) == 0 and len(cash_flow) == 0:

        raise ValueError(
            f"No financial records found in Data Sheet for {company}."
        )

    yearly_records = merge_financial_statements(
        profit_loss,
        balance_sheet,
        cash_flow
    )

    for record in yearly_records:

        record["Company"] = company

    ordered_records = []

    for record in yearly_records:

        ordered = {
            "Company": record["Company"],
            "Year": record["Year"]
        }

        for key, value in record.items():

            if key in ["Company", "Year"]:

                continue

            ordered[key] = value

        ordered_records.append(ordered)

    return ordered_records

#part 3
# ==========================================================
# PROCESS SINGLE COMPANY
# ==========================================================

def process_company(file_path):
    """
    Process one company's Excel workbook.

    Steps
    -----
    1. Read Profit & Loss sheet
    2. Read Balance Sheet
    3. Read Cash Flow
    4. Extract yearly records
    5. Merge all statements
    6. Add Company Name

    Parameters
    ----------
    file_path : str

    Returns
    -------
    list
        One dictionary for each financial year.
    """

    company = get_company_name(file_path)

    if PRINT_PROGRESS:

        print_separator()

        print(f"Processing : {os.path.basename(file_path)}")

        print_company_header(company)

    # ------------------------------------------------------
    # Prefer the actual Screener Data Sheet when available.
    # ------------------------------------------------------

    try:

        ordered_records = extract_data_sheet_records(file_path)

        if PRINT_PROGRESS:

            print()

            print("----------------------------------------")

            print(f"Company : {company}")

            print(f"Years Extracted : {len(ordered_records)}")

            print("----------------------------------------")

            print()

        return ordered_records

    except Exception:

        pass

    # ------------------------------------------------------
    # Fallback to legacy worksheet parsing.
    # ------------------------------------------------------

    try:

        pl_df = load_sheet(
            file_path,
            SHEETS["PL"]
        )

        bs_df = load_sheet(
            file_path,
            SHEETS["BS"]
        )

        cf_df = load_sheet(
            file_path,
            SHEETS["CF"]
        )

    except Exception as e:

        print(f"Unable to read workbook : {e}")

        return []

    # ------------------------------------------------------
    # Extract Statements
    # ------------------------------------------------------

    try:

        profit_loss = extract_sheet(
            pl_df,
            SHEETS["PL"]
        )

        balance_sheet = extract_sheet(
            bs_df,
            SHEETS["BS"]
        )

        cash_flow = extract_sheet(
            cf_df,
            SHEETS["CF"]
        )

    except Exception as e:

        print(f"Extraction Failed : {e}")

        return []

    # ------------------------------------------------------
    # Validate Extraction
    # ------------------------------------------------------

    validate_extraction(
        profit_loss,
        balance_sheet,
        cash_flow
    )

    # ------------------------------------------------------
    # Merge Statements
    # ------------------------------------------------------

    yearly_records = merge_financial_statements(
        profit_loss,
        balance_sheet,
        cash_flow
    )

    # ------------------------------------------------------
    # Add Company Name
    # ------------------------------------------------------

    for record in yearly_records:

        record["Company"] = company

    # ------------------------------------------------------
    # Sort Columns
    # ------------------------------------------------------

    ordered_records = []

    for record in yearly_records:

        ordered = {}

        ordered["Company"] = record["Company"]

        ordered["Year"] = record["Year"]

        for key, value in record.items():

            if key in ["Company", "Year"]:

                continue

            ordered[key] = value

        ordered_records.append(ordered)

    # ------------------------------------------------------
    # Logging
    # ------------------------------------------------------

    if PRINT_PROGRESS:

        print()

        print("----------------------------------------")

        print(f"Company : {company}")

        print(f"Years Extracted : {len(ordered_records)}")

        print("----------------------------------------")

        print()

    return ordered_records


# ==========================================================
# PROCESS ALL WORKBOOKS
# ==========================================================

def process_all_companies():
    """
    Process every workbook present in RAW_DATA_FOLDER.

    Returns
    -------
    list
        Complete extracted dataset.
    """

    all_records = []

    files = sorted(os.listdir(RAW_DATA_FOLDER))

    for file in files:

        # Ignore temporary Excel files

        if file.startswith("~$"):

            continue

        if not file.lower().endswith(".xlsx"):

            continue

        file_path = os.path.join(
            RAW_DATA_FOLDER,
            file
        )

        company_records = process_company(
            file_path
        )

        all_records.extend(
            company_records
        )

    return all_records
#part 4
# ==========================================================
# MAIN PROGRAM
# ==========================================================

if __name__ == "__main__":

    print_separator()

    print("STARTING FINANCIAL DATASET EXTRACTION")

    print_separator()

    print()

    # ------------------------------------------------------
    # Process all Excel workbooks
    # ------------------------------------------------------

    dataset = process_all_companies()

    # ------------------------------------------------------
    # Check extraction
    # ------------------------------------------------------

    if len(dataset) == 0:

        raise Exception(
            "No financial records were extracted."
        )

    # ------------------------------------------------------
    # Create DataFrame
    # ------------------------------------------------------

    print()

    print_separator()

    print("Creating Final Dataset")

    print_separator()

    final_df = pd.DataFrame(dataset)

    # ------------------------------------------------------
    # Remove Duplicate Records
    # ------------------------------------------------------

    before_duplicates = len(final_df)

    final_df.drop_duplicates(
        inplace=True
    )

    duplicate_count = (
        before_duplicates -
        len(final_df)
    )

    # ------------------------------------------------------
    # Remove Empty Columns
    # ------------------------------------------------------

    final_df.dropna(
        axis=1,
        how="all",
        inplace=True
    )

    # ------------------------------------------------------
    # Sort Dataset
    # ------------------------------------------------------

    if (
        "Company" in final_df.columns and
        "Year" in final_df.columns
    ):

        final_df.sort_values(
            by=[
                "Company",
                "Year"
            ],
            inplace=True
        )

        final_df.reset_index(
            drop=True,
            inplace=True
        )

    # ------------------------------------------------------
    # Basic Validation
    # ------------------------------------------------------

    print()

    print_separator()

    print("VALIDATING DATASET")

    print_separator()

    required_columns = [

        "Company",
        "Year",

        "Sales",

        "Operating Profit",

        "Net profit",

        "Equity Share Capital",

        "Reserves",

        "Borrowings",

        "Total Assets",

        "Cash from Operating Activity"

    ]

    missing_columns = []

    for column in required_columns:

        if column not in final_df.columns:

            missing_columns.append(column)

    if len(missing_columns) > 0:

        print()

        print("WARNING")

        print("Missing Columns:")

        for column in missing_columns:

            print(f" - {column}")

    else:

        print()

        print("Dataset Validation Passed.")

    # ------------------------------------------------------
    # Save Dataset
    # ------------------------------------------------------

    final_df.to_csv(
        FINANCIAL_DATASET,
        index=False,
        encoding=CSV_ENCODING
    )

    # ------------------------------------------------------
    # Final Summary
    # ------------------------------------------------------

    print()

    print_separator()

    print("RAW DATASET EXTRACTION COMPLETED")

    print_separator()

    total_files = len([

        file

        for file in os.listdir(RAW_DATA_FOLDER)

        if (
            file.lower().endswith(".xlsx")
            and
            not file.startswith("~$")
        )

    ])

    print()

    print(f"Excel Files Processed : {total_files}")

    print(f"Records Extracted     : {len(final_df)}")

    print(f"Duplicate Records     : {duplicate_count}")

    print(f"Total Columns         : {len(final_df.columns)}")

    print(f"Dataset Shape         : {final_df.shape}")

    print()

    print("Dataset Saved To")

    print(FINANCIAL_DATASET)

    print()

    print_separator()

    print("COLUMN LIST")

    print_separator()

    for column in final_df.columns:

        print(column)

    print()

    print_separator()

    print("FIRST FIVE RECORDS")

    print_separator()

    print(final_df.head())

    print()

    print_separator()

    print("DATASET READY FOR PREPROCESSING")

    print_separator()