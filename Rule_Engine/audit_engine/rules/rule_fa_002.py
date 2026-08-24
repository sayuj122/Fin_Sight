from audit_engine.models import RuleSpec, Severity
from audit_engine.rules.factory import build_rule

RULE = build_rule(RuleSpec(
    rule_id='FA-002',
    name='Adverse operating margin',
    group='Financial Analytics Rules',
    category='financial_analytics',
    validation_logic='negative_value',
    severity=Severity.MEDIUM,
    required_metrics=('Operating_Margin',),
    description='Tests adverse operating margin using only supplied financial-statement metrics.',
    business_purpose='Focuses audit review on a material inconsistency, adverse condition, or statistically unusual relationship.',
    formula='negative_value',
    threshold='No arbitrary threshold; logical condition or configurable tolerance',
    recommendation='Investigate the underlying drivers and obtain supporting evidence before relying on the reported balance.',
    risk_impact='Potential financial-statement reliability, liquidity, solvency, or earnings-quality risk.',
))
