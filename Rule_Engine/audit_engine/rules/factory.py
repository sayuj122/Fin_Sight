from __future__ import annotations
import math
import pandas as pd
from audit_engine.base import BaseRule
from audit_engine.models import RuleResult, RuleSpec, Severity, Status


def _z(value, values):
    values = pd.Series(values).dropna()
    if len(values) < 3 or pd.isna(value): return None
    median = values.median(); mad = (values - median).abs().median()
    return None if mad == 0 else 0.6745 * (value - median) / mad


def _company(row):
    value = row.get("Company", "")
    return "" if pd.isna(value) else str(value)


def _year(row):
    value = row.get("Year", 0)
    if pd.isna(value):
        return 0
    try:
        return int(value)
    except Exception:
        return 0


def _result(spec, row, status, message, observed=None):
    return RuleResult(
        spec.rule_id,
        status,
        spec.severity,
        _company(row),
        _year(row),
        message,
        observed or {}
    )


def _missing_values(vals):
    return [m for m, v in vals.items() if pd.isna(v)]


def _first_prior(frame, row, metric):
    prior = frame.loc[
        (frame.Company == row.Company) & (frame.Year < row.Year),
        metric
    ].tail(1)
    if not len(prior) or pd.isna(prior.iloc[0]):
        return None
    return prior.iloc[0]


class DeclarativeRule(BaseRule):
    def __init__(self, spec): self.spec = spec
    def evaluate(self, frame, index, config):
        row = frame.loc[index]; logic = self.spec.validation_logic; tol = config["tolerance"];
        missing = [m for m in self.spec.required_metrics if m not in frame.columns]
        if missing: return _result(self.spec, row, Status.SKIPPED, f"Unavailable metrics: {missing}")
        vals = {m: row.get(m) for m in self.spec.required_metrics}
        if logic == "missing_required": failed = any(pd.isna(row.get(c)) or str(row.get(c)).strip() == "" for c in ("Company", "Year"))
        elif logic == "numeric_fields":
            failed = False
            for c in frame.columns:
                if c in {"Company", "Report Date"}:
                    continue
                value = row.get(c)
                if pd.isna(value):
                    continue
                try:
                    float(value)
                except Exception:
                    failed = True
                    break
        elif logic == "required_columns": failed = False
        else:
            missing_values = _missing_values(vals)
            if missing_values:
                return _result(self.spec, row, Status.SKIPPED, f"Unavailable metric values: {missing_values}", vals)
            if logic == "negative_screen": failed = any((pd.notna(v) and v < 0) for v in vals.values())
            elif logic == "year_date_match": failed = pd.notna(row.get("Report Date")) and str(int(row["Year"])) not in str(row["Report Date"])
            elif logic == "accounting_equation": failed = abs(row["Total Assets"] - row["Total Liabilities"]) > tol
            elif logic == "negative_equity": failed = row["Equity Share Capital"] + row["Reserves"] < 0
            elif logic in {"feature_zscore", "outlier", "feature_volatility", "common_size_shift", "margin_instability"}:
                metric = self.spec.required_metrics[0]; z = _z(row[metric], frame.loc[frame["Year"] == row["Year"], metric]); failed = z is not None and abs(z) > config["z_score"]; vals["robust_z"] = z
            elif logic == "config_max": failed = row[self.spec.required_metrics[0]] > config["ratio_limits"][self.spec.required_metrics[0]]
            elif logic == "config_min": failed = row[self.spec.required_metrics[0]] < config["ratio_limits"][self.spec.required_metrics[0]]
            elif logic == "negative_value": failed = pd.notna(row[self.spec.required_metrics[0]]) and row[self.spec.required_metrics[0]] < 0
            elif logic in {"declining_trend", "increasing_trend", "sustained_negative"}:
                metric = self.spec.required_metrics[0]
                history = frame.loc[(frame.Company == row.Company) & (frame.Year <= row.Year), metric].dropna().tail(config["minimum_history"])
                if len(history) < config["minimum_history"]:
                    return _result(self.spec, row, Status.SKIPPED, f"Insufficient history for {metric}", vals)
                failed = (
                    history.is_monotonic_decreasing if logic == "declining_trend"
                    else history.is_monotonic_increasing if logic == "increasing_trend"
                    else (history < 0).all()
                )
            elif logic == "expense_spike":
                prior_val = _first_prior(frame, row, "Total Expenses")
                if prior_val is None:
                    return _result(self.spec, row, Status.SKIPPED, "Unavailable prior-year Total Expenses", vals)
                z = _z(row["Total Expenses"], frame.loc[frame.Year == row.Year, "Total Expenses"])
                failed = z is not None and abs(z) > config["z_score"]
            elif logic == "growth_gap":
                left, right = self.spec.required_metrics
                if pd.isna(row[left]) or pd.isna(row[right]):
                    return _result(self.spec, row, Status.SKIPPED, f"Unavailable metric values: {left}, {right}", vals)
                failed = row[left] > 0 and row[right] < 0
            elif logic == "reserve_rollforward":
                prior_val = _first_prior(frame, row, "Reserves")
                if prior_val is None:
                    return _result(self.spec, row, Status.SKIPPED, "Unavailable prior-year Reserves", vals)
                failed = abs((row["Reserves"] - prior_val) - (row["Net profit"] - row["Dividend Amount"])) > tol
            elif logic == "cash_delta_tieout":
                prior_val = _first_prior(frame, row, "Cash & Bank")
                if prior_val is None:
                    return _result(self.spec, row, Status.SKIPPED, "Unavailable prior-year Cash & Bank", vals)
                failed = abs((row["Cash & Bank"] - prior_val) - row["Net Cash Flow"]) > tol
            elif logic == "financing_plausibility":
                prior_val = _first_prior(frame, row, "Borrowings")
                if prior_val is None:
                    return _result(self.spec, row, Status.SKIPPED, "Unavailable prior-year Borrowings", vals)
                failed = abs(row["Cash from Financing Activity"] - (row["Borrowings"] - prior_val - row["Dividend Amount"])) > max(tol, abs(row["Cash from Financing Activity"]) * config["z_score"])
            elif logic == "ocf_reconciliation_proxy": failed = False
            elif logic == "dividend_reserves": failed = row["Dividend Amount"] > max(row["Reserves"], 0)
            elif logic == "interest_reasonableness":
                z = _z(row["Interest"], frame.loc[frame.Year == row.Year, "Interest"])
                failed = z is not None and abs(z) > config["z_score"]
            elif logic == "relationship_adverse":
                left, right = self.spec.required_metrics
                if pd.isna(row[left]) or pd.isna(row[right]):
                    return _result(self.spec, row, Status.SKIPPED, f"Unavailable metric values: {left}, {right}", vals)
                failed = row[left] > 0 and row[right] < 0
            elif logic == "ocf_below_profit":
                if pd.isna(row.get("Cash from Operating Activity")) or pd.isna(row.get("Net profit")):
                    return _result(self.spec, row, Status.SKIPPED, "Unavailable metric values: Cash from Operating Activity, Net profit", vals)
                failed = row["Cash from Operating Activity"] < row["Net profit"]
            elif logic == "cash_ocf_divergence":
                if pd.isna(row.get("Cash_Growth")) or pd.isna(row.get("Cash from Operating Activity")):
                    return _result(self.spec, row, Status.SKIPPED, "Unavailable metric values: Cash_Growth, Cash from Operating Activity", vals)
                failed = row["Cash_Growth"] < 0 and row["Cash from Operating Activity"] > 0
            elif logic == "cash_flow_composition":
                z = _z(row["Cash from Financing Activity"], frame.loc[frame.Year == row.Year, "Cash from Financing Activity"])
                failed = z is not None and abs(z) > config["z_score"]
            else: return _result(self.spec, row, Status.SKIPPED, f"Unsupported logic: {logic}")
        return _result(self.spec, row, Status.FAIL if failed else Status.PASS, "Validation triggered" if failed else "Validation passed", vals)


def build_rule(spec): return DeclarativeRule(spec)
