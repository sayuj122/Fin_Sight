from audit_engine.models import RuleSpec, Severity
from audit_engine.rules.factory import build_rule

RULE = build_rule(RuleSpec(
    rule_id='FA-066',
    name='Unstable trend: operating margin',
    group='Financial Analytics Rules',
    category='financial_analytics',
    validation_logic='feature_volatility',
    severity=Severity.MEDIUM,
    required_metrics=('Operating_Margin',),
    description='Tests unstable trend: operating margin using only supplied financial-statement metrics.',
    business_purpose='Focuses audit review on a material inconsistency, adverse condition, or statistically unusual relationship.',
    formula='feature_volatility',
    threshold='Robust z-score against same-year peer population (configurable)',
    recommendation='Investigate the underlying drivers and obtain supporting evidence before relying on the reported balance.',
    risk_impact='Potential financial-statement reliability, liquidity, solvency, or earnings-quality risk.',
))
