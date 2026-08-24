from audit_engine.models import RuleSpec, Severity
from audit_engine.rules.factory import build_rule

RULE = build_rule(RuleSpec(
    rule_id='CF-006',
    name='Depreciation non-cash adjustment plausibility',
    group='Handbook Rules',
    category='cross_statement',
    validation_logic='ocf_reconciliation_proxy',
    severity=Severity.HIGH,
    required_metrics=('Net profit', 'Depreciation', 'Cash from Operating Activity'),
    description='Tests depreciation non-cash adjustment plausibility using only supplied financial-statement metrics.',
    business_purpose='Focuses audit review on a material inconsistency, adverse condition, or statistically unusual relationship.',
    formula='ocf_reconciliation_proxy',
    threshold='No arbitrary threshold; logical condition or configurable tolerance',
    recommendation='Investigate the underlying drivers and obtain supporting evidence before relying on the reported balance.',
    risk_impact='Potential financial-statement reliability, liquidity, solvency, or earnings-quality risk.',
))
