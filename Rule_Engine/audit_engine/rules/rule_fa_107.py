from audit_engine.models import RuleSpec, Severity
from audit_engine.rules.factory import build_rule

RULE = build_rule(RuleSpec(
    rule_id='FA-107',
    name='Cash decline amid positive operating cash flow',
    group='Financial Analytics Rules',
    category='financial_analytics',
    validation_logic='cash_ocf_divergence',
    severity=Severity.MEDIUM,
    required_metrics=('Cash_Growth', 'Cash from Operating Activity'),
    description='Tests cash decline amid positive operating cash flow using only supplied financial-statement metrics.',
    business_purpose='Focuses audit review on a material inconsistency, adverse condition, or statistically unusual relationship.',
    formula='cash_ocf_divergence',
    threshold='No arbitrary threshold; logical condition or configurable tolerance',
    recommendation='Investigate the underlying drivers and obtain supporting evidence before relying on the reported balance.',
    risk_impact='Potential financial-statement reliability, liquidity, solvency, or earnings-quality risk.',
))
