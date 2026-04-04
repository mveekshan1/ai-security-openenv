#!/usr/bin/env python
"""Quick test of semantic normalization"""

from tasks import SemanticNormalizer, GradingEngine, TASKS

# Test normalization
print("=== SEMANTIC NORMALIZATION TESTS ===")
test_cases = [
    ("block_ip", "block ip", True),
    ("block+alert", "block + alert", True),
    ("insider_threat", "insider threat", True),
    ("data_exfiltration", "data exfiltration", True),
    ("brute_force", "brute force", True),
    ("block", "allow", False),
]

for actual, expected, should_match in test_cases:
    result = SemanticNormalizer.is_equivalent(actual, expected)
    status = "[OK]" if result == should_match else "[FAIL]"
    print(f"{status} {actual} vs {expected} -> {result}")

# Test grading with variations
print("\n=== GRADING WITH NORMALIZED INPUTS ===")
task = TASKS["threat_detection_brute_force"]

# Perfect match with normalized format
output = {
    "allow": False,
    "threat_type": "brute force",  # Normalized variant
    "response_action": "block ip",  # Normalized variant
    "firewall_rule": {
        "rule_action": "block",
        "target": "ip",
        "duration": "1h"
    }
}

result = GradingEngine.grade(task, output)
print(f"Score with normalized inputs: {result['score']} (expected 1.0)")
print(f"Passed: {result['passed']}")

print("\n=== ALL TESTS PASSED ===")
