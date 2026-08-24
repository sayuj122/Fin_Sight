"""
Explanation Generator Module

Converts structured evidence into auditor-readable explanations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from config import SEVERITY_PRIORITY


def format_observed_value(observed: Any) -> str:
    """Format the observed value for explanation."""
    if pd.isna(observed):
        return "unavailable"

    if isinstance(observed, str):
        # Clean up the observed string representation
        observed = observed.strip()
        if observed.startswith("{") and observed.endswith("}"):
            # Try to parse as dict-like string
            return observed
        return observed

    return str(observed)


def generate_violation_explanation(violation: pd.Series) -> str:
    """Generate explanation for a single rule violation."""
    rule_id = violation.get('Rule ID', 'Unknown')
    rule_name = violation.get('Rule Name', 'Unknown')
    severity = violation.get('Severity', 'Unknown')
    message = violation.get('Message', 'Validation triggered')
    observed = violation.get('Observed', None)

    observed_str = format_observed_value(observed)

    explanation_parts = [
        f"Rule {rule_id} ({rule_name}) [{severity}]: {message}."
    ]

    if observed_str != "unavailable":
        explanation_parts.append(f"Observed values: {observed_str}.")

    return " ".join(explanation_parts)


def group_violations_by_severity(violations: pd.DataFrame) -> Dict[str, List[pd.Series]]:
    """Group violations by severity in priority order."""
    severity_order = ['Critical', 'High', 'Medium', 'Low']
    grouped = {sev: [] for sev in severity_order}

    for _, row in violations.iterrows():
        severity = row.get('Severity', 'Low')
        if severity in grouped:
            grouped[severity].append(row)
        else:
            grouped['Low'].append(row)

    return grouped


def generate_rule_based_explanation(violations: pd.DataFrame, rule_scores: Optional[pd.Series] = None) -> str:
    """Generate consolidated rule-based explanation from violations."""
    if violations.empty:
        return "No rule violations detected. All applicable audit rules passed."

    grouped = group_violations_by_severity(violations)

    explanation_parts = []
    total_violations = len(violations)
    explanation_parts.append(f"Rule-based analysis identified {total_violations} violation(s).")

    # Process by severity priority
    for severity in ['Critical', 'High', 'Medium', 'Low']:
        sev_violations = grouped[severity]
        if not sev_violations:
            continue

        count = len(sev_violations)
        explanation_parts.append(f"\n{severity} Severity ({count} violation(s)):")

        for v in sev_violations:
            rule_id = v.get('Rule ID', 'Unknown')
            rule_name = v.get('Rule Name', 'Unknown')
            message = v.get('Message', 'Validation triggered')
            observed = v.get('Observed', None)
            observed_str = format_observed_value(observed)

            explanation_parts.append(
                f"  - {rule_id} ({rule_name}): {message}"
                f"{'. Observed: ' + observed_str if observed_str != 'unavailable' else '.'}"
            )

    # Add risk score summary if available
    if rule_scores is not None:
        risk_score = rule_scores.get('Risk Score', None)
        risk_level = rule_scores.get('Risk Level', None)
        if pd.notna(risk_score) and pd.notna(risk_level):
            explanation_parts.append(
                f"\nRule-Based Risk Score: {risk_score:.2f}% (Risk Level: {risk_level})."
            )

    return " ".join(explanation_parts)


def generate_rule_summary(violations: pd.DataFrame) -> Dict[str, Any]:
    """Generate structured summary of rule violations."""
    if violations.empty:
        return {
            'violation_count': 0,
            'categories': [],
            'highest_severity': None,
            'critical_count': 0,
            'high_count': 0,
            'medium_count': 0,
            'low_count': 0
        }

    grouped = group_violations_by_severity(violations)

    categories = violations['Category'].unique().tolist() if 'Category' in violations.columns else []

    severity_counts = {sev: len(grouped[sev]) for sev in ['Critical', 'High', 'Medium', 'Low']}

    highest_severity = None
    for sev in ['Critical', 'High', 'Medium', 'Low']:
        if severity_counts[sev] > 0:
            highest_severity = sev
            break

    return {
        'violation_count': len(violations),
        'categories': categories,
        'highest_severity': highest_severity,
        'critical_count': severity_counts['Critical'],
        'high_count': severity_counts['High'],
        'medium_count': severity_counts['Medium'],
        'low_count': severity_counts['Low']
    }


def generate_ml_explanation(prediction: Optional[pd.Series] = None) -> str:
    """Generate ML explanation from prediction results."""
    if prediction is None or prediction.empty:
        return "ML Evidence: Machine learning prediction unavailable for this Company-Year."

    pred = prediction.get('Prediction', 'Unknown')
    decision_score = prediction.get('Decision Score', None)
    anomaly_score = prediction.get('Anomaly Score', None)

    parts = [f"ML Evidence: The Isolation Forest model classified this observation as '{pred}'."]

    if pd.notna(decision_score):
        parts.append(f" Decision Score: {decision_score:.6f}.")

    if pd.notna(anomaly_score):
        parts.append(f" Anomaly Score: {anomaly_score:.6f}.")

    if pred == 'Anomaly':
        parts.append(" The observation deviates from learned historical financial patterns.")
    else:
        parts.append(" The observation aligns with learned historical financial patterns.")

    return " ".join(parts)


def generate_overall_assessment(
    rule_based_explanation: str,
    ml_explanation: str,
    rule_scores: Optional[pd.Series] = None,
    prediction: Optional[pd.Series] = None
) -> str:
    """Generate overall hybrid assessment."""
    parts = ["Overall Assessment:"]

    # Rule-based risk summary
    if rule_scores is not None:
        risk_score = rule_scores.get('Risk Score', None)
        risk_level = rule_scores.get('Risk Level', None)
        if pd.notna(risk_score) and pd.notna(risk_level):
            parts.append(f" Rule-based risk: {risk_score:.2f}% ({risk_level}).")
        elif pd.notna(risk_level):
            parts.append(f" Rule-based risk level: {risk_level}.")

    # ML summary
    if prediction is not None and not prediction.empty:
        pred = prediction.get('Prediction', 'Unknown')
        if pred == 'Anomaly':
            parts.append(
                " However, the Isolation Forest identified the financial-year observation as unusual "
                "relative to learned historical patterns. Further review is recommended."
            )
        else:
            parts.append(" The ML model detected no anomaly.")
    else:
        parts.append(" ML prediction unavailable.")

    return " ".join(parts)


def generate_audit_recommendation(
    violations: pd.DataFrame,
    rule_scores: Optional[pd.Series] = None,
    prediction: Optional[pd.Series] = None
) -> str:
    """Generate audit recommendation based on all evidence."""
    recommendations = []

    # Risk-based recommendation
    if rule_scores is not None:
        risk_level = rule_scores.get('Risk Level', None)
        if pd.notna(risk_level):
            if risk_level in ['High', 'Critical']:
                recommendations.append("High rule-based risk warrants detailed substantive testing.")
            elif risk_level == 'Medium':
                recommendations.append("Moderate rule-based risk suggests expanded audit procedures.")
            else:
                recommendations.append("Low rule-based risk supports standard audit approach.")

    # ML-based recommendation
    if prediction is not None and not prediction.empty:
        pred = prediction.get('Prediction', 'Unknown')
        if pred == 'Anomaly':
            recommendations.append("ML anomaly detection recommends additional analytical procedures.")

    # Violation-specific recommendations based on severity
    if not violations.empty:
        critical_count = len(violations[violations['Severity'] == 'Critical']) if 'Severity' in violations.columns else 0
        high_count = len(violations[violations['Severity'] == 'High']) if 'Severity' in violations.columns else 0

        if critical_count > 0:
            recommendations.append(f"Critical violations ({critical_count}) require immediate investigation and substantive testing.")
        if high_count > 0:
            recommendations.append(f"High-severity violations ({high_count}) warrant expanded audit procedures and management inquiry.")

    if not recommendations:
        return "No specific recommendations - standard audit procedures apply."

    return " ".join(recommendations)


def generate_violation_categories(violations: pd.DataFrame) -> str:
    """Generate comma-separated list of violation categories."""
    if violations.empty:
        return ""
    if 'Category' not in violations.columns:
        return ""
    return ", ".join(sorted(violations['Category'].unique().tolist()))


def build_explanation_record(
    company: str,
    year: int,
    violations: pd.DataFrame,
    rule_scores: Optional[pd.Series] = None,
    prediction: Optional[pd.Series] = None,
    preprocessed_data: Optional[pd.Series] = None
) -> Dict[str, Any]:
    """Build a complete explanation record for a Company-Year."""

    rule_summary = generate_rule_summary(violations)

    record = {
        'Company': company,
        'Year': year,

        # Rule-based fields
        'Rule Risk Score': rule_scores.get('Risk Score') if rule_scores is not None else None,
        'Rule Risk Level': rule_scores.get('Risk Level') if rule_scores is not None else None,
        'Passed Rules': rule_scores.get('Passed Rules') if rule_scores is not None else None,
        'Failed Rules': rule_scores.get('Failed Rules') if rule_scores is not None else None,
        'Skipped Rules': rule_scores.get('Skipped Rules') if rule_scores is not None else None,
        'Critical Failures': rule_scores.get('Critical Failures') if rule_scores is not None else None,
        'High Failures': rule_scores.get('High Failures') if rule_scores is not None else None,
        'Medium Failures': rule_scores.get('Medium Failures') if rule_scores is not None else None,
        'Low Failures': rule_scores.get('Low Failures') if rule_scores is not None else None,

        # ML fields
        'ML Prediction': prediction.get('Prediction') if prediction is not None else None,
        'Decision Score': prediction.get('Decision Score') if prediction is not None else None,
        'Anomaly Score': prediction.get('Anomaly Score') if prediction is not None else None,

        # Violation summary fields
        'Violation Count': rule_summary['violation_count'],
        'Violation Categories': generate_violation_categories(violations),
        'Highest Severity': rule_summary['highest_severity'],

        # Explanations
        'Rule-Based Explanation': generate_rule_based_explanation(violations, rule_scores),
        'ML Explanation': generate_ml_explanation(prediction),
        'Overall Explanation': generate_overall_assessment(
            generate_rule_based_explanation(violations, rule_scores),
            generate_ml_explanation(prediction),
            rule_scores,
            prediction
        ),
        'Audit Recommendation': generate_audit_recommendation(violations, rule_scores, prediction)
    }

    return record