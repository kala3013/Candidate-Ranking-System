"""Quick test to verify backend loads correctly."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

# Print all routes
print("Backend loaded successfully!")
print("\nAPI Routes:")
for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
    if rule.rule.startswith('/api'):
        methods = rule.methods - {'HEAD', 'OPTIONS'}
        print(f"  {methods} {rule.rule}")

print(f"\nTotal API routes: {sum(1 for r in app.url_map.iter_rules() if r.rule.startswith('/api'))}")
print("\nAll systems ready!")