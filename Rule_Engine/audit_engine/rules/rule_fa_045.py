from audit_engine.models import RuleSpec, Severity
from audit_engine.rules.factory import build_rule

RULE = build_rule(RuleSpec(
    rule_id='FA-045',
    name='Peer outlier: inventory ratio',
    group='Financial Analytics Rules',
    category='financial_analytics',
    validation_logic='feature_zscore',
    severity=Severity.MEDIUM,
    required_metrics=('Inventory_Ratio',),
    description='Tests peer outlier: inventory ratio using only supplied financial-statement metrics.',
    business_purpose='Focuses audit review on a material inconsistency, adverse condition, or statistically unusual relationship.',
    formula='feature_zscore',
    threshold='Robust z-score against same-year peer population (configurable)',
    recommendation='Investigate the underlying drivers and obtain supporting evidence before relying on the reported balance.',
    risk_impact='Potential financial-statement reliability, liquidity, solvency, or earnings-quality risk.',
))
