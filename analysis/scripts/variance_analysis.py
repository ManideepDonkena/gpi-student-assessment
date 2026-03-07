"""Quick script to calculate shared vs unique variance between Gunas and Big Five."""
import json, os
import pandas as pd
import numpy as np
from scipy import stats as scipy_stats

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")

data = json.load(open(os.path.join(DATA_DIR, "final_dataset_refined.json")))
rows = [{**s.get('recalculated_guna', {}), **s.get('recalculated_bfi', {})} for s in data]
df = pd.DataFrame(rows)

gunas = ['Sattva', 'Rajas', 'Tamas']
bfis = ['Extraversion', 'Agreeableness', 'Conscientiousness', 'Neuroticism', 'Openness']

print("=" * 60)
print("SHARED VARIANCE ANALYSIS (R-squared)")
print("=" * 60)

for g in gunas:
    print(f"\n--- {g} ---")
    total_shared = 0
    for b in bfis:
        r = df[g].corr(df[b])
        r2 = r**2 * 100
        total_shared += r2
        marker = " <<<" if r2 > 20 else ""
        print(f"  {b:20s}: r = {r:+.3f}, R² = {r2:5.1f}%{marker}")
    avg_shared = total_shared / len(bfis)
    unique = 100 - min(total_shared, 100)  # Rough estimate
    print(f"  {'TOTAL shared':20s}: {total_shared:.1f}%")
    print(f"  {'UNIQUE to Guna':20s}: ~{unique:.0f}%")

print("\n" + "=" * 60)
print("INTER-GUNA CORRELATIONS")
print("=" * 60)
for i, g1 in enumerate(gunas):
    for j, g2 in enumerate(gunas):
        if j > i:
            r, p = scipy_stats.pearsonr(df[g1], df[g2])
            print(f"  {g1} ↔ {g2}: r = {r:+.3f} (p = {p:.4f})")

print("\n" + "=" * 60)
print("MULTIPLE REGRESSION: How much Big Five EXPLAINS each Guna")
print("=" * 60)
from sklearn.linear_model import LinearRegression

for g in gunas:
    X = df[bfis].dropna()
    y = df[g].loc[X.index]
    reg = LinearRegression().fit(X, y)
    r2 = reg.score(X, y) * 100
    print(f"  {g}: R² = {r2:.1f}% explained by Big Five → {100-r2:.1f}% UNIQUE")
