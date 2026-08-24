from audit_engine.models import RuleSpec, Severity
from audit_engine.rules.factory import build_rule

RULE = build_rule(RuleSpec(
    rule_id='FA-099',
    name='Receivables growth exceeding revenue growth',
    group='Financial Analytics Rules',
    category='financial_analytics',
    validation_logic='relationship_adverse',
    severity=Severity.HIGH,
    required_metrics=('Receivable_Growth', 'Revenue_Growth'),
    description='Tests receivables growth exceeding revenue growth using only supplied financial-statement metrics.',
    business_purpose='Focuses audit review on a material inconsistency, adverse condition, or statistically unusual relationship.',
    formula='relationship_adverse',
    threshold='No arbitrary threshold; logical condition or configurable tolerance',
    recommendation='Investigate the underlying drivers and obtain supporting evidence before relying on the reported balance.',
    risk_impact='Potential financial-statement reliability, liquidity, solvency, or earnings-quality risk.',
))
