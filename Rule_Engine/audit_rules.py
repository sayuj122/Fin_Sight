"""
==========================================================
Project:
Hybrid Rule-Based and Explainable Financial Statement
Anomaly Detection Framework

File:
audit_rules.py

Purpose:
Automatically load all RuleSpec objects from
audit_engine/rules.
==========================================================
"""

import importlib
import pkgutil

from audit_engine import rules

# ==========================================================
# LOAD ALL RULES
# ==========================================================

ALL_RULES = []

for _, module_name, is_pkg in pkgutil.iter_modules(rules.__path__):

    if is_pkg:
        continue

    if module_name.startswith("__"):
        continue

    if module_name == "factory":
        continue

    module = importlib.import_module(

        f"audit_engine.rules.{module_name}"

    )

    if hasattr(module, "RULE"):

        ALL_RULES.append(

            module.RULE

        )

# ==========================================================
# SORT RULES
# ==========================================================

ALL_RULES.sort(
    key=lambda rule: rule.spec.rule_id
)

# ==========================================================
# HELPER FUNCTION
# ==========================================================

def get_all_rules():

    return ALL_RULES

# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print(f"Total Rules Loaded : {len(ALL_RULES)}")

    for rule in ALL_RULES[:10]:
        print(rule.spec.rule_id, "-", rule.spec.name)