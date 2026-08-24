from audit_engine.models import RuleSpec, Severity
from audit_engine.rules.factory import build_rule

RULE = build_rule(RuleSpec(
    rule_id='FA-108',
    name='Cash-flow composition outlier',
    group='Financial Analytics Rules',
    category='financial_analytics',
    validation_logic='cash_flow_composition',
    severity=Severity.MEDIUM,
    required_metrics=('Cash from Operating Activity', 'Cash from Investing Activity', 'Cash from Financing Activity'),
    description='Tests cash-flow composition outlier using only supplied financial-statement metrics.',
    business_purpose='Focuses audit review on a material inconsistency, adverse condition, or statistically unusual relationship.',
    formula='cash_flow_composition',
    threshold='Robust z-score against same-year peer population (configurable)',
    recommendation='Investigate the underlying drivers and obtain supporting evidence before relying on the reported balance.',
    risk_impact='Potential financial-statement reliability, liquidity, solvency, or earnings-quality risk.',
))
