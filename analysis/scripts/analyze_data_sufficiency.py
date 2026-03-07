import pandas as pd
import numpy as np
import math
import json
import os
import math
import json

# Load Data from Cleaned JSON (BFI-44 Cohort)
json_file = 'bfi44_cleaned.json'
if not os.path.exists(json_file):
    print(f"Error: {json_file} not found. Run clean_and_analyze.py first.")
    exit()

with open(json_file, 'r') as f:
    data = json.load(f)

# Extract Demographics into DataFrame
rows = []
for session in data:
    demos = session.get('demographics', {})
    rows.append({
        'Gender': demos.get('gender', 'Unknown'),
        'Year': demos.get('year', 'Unknown'),
        'Occupation': demos.get('occupation', 'Unknown')
    })

df = pd.DataFrame(rows)

# Data is already cleaned by clean_and_analyze.py
clean_n = len(df)

# Subgroup Counts
gender_counts = df['Gender'].value_counts()
year_counts = df['Year'].value_counts()

# Power Analysis Approximation for T-test
# Formula: Power is a function of delta, n, sigma, alpha.
# For d=0.5, alpha=0.05, 2-tailed:
# N=64 per group gives 0.80 power.
# We will just show the N per group and compare to benchmark.

power_gender_status = "Unknown"
if 'Male' in gender_counts and 'Female' in gender_counts:
    n1 = gender_counts['Male']
    n2 = gender_counts['Female']
    total_n_gender = n1 + n2
    # Harmonic mean approximation for unbalanced design
    n_harmonic = 2 * n1 * n2 / (n1 + n2)
    
    # Benchmarks for d=0.5 (Medium Effect), alpha=0.05
    if n_harmonic >= 128: # approx 64 per group
        power_gender_status = "Excellent (> 0.80)"
    elif n_harmonic >= 80: # approx 40 per group
        power_gender_status = "Good (~0.60 - 0.70)"
    elif n_harmonic >= 40: # approx 20 per group
        power_gender_status = "Low (~0.30 - 0.40)"
    else:
        power_gender_status = "Very Low (< 0.30)"

# Recommendation Logic
recommendations = []
if clean_n < 100:
    recommendations.append("Total N < 100: Factor Analysis results may be unstable (Ideal N > 150).")
else:
    recommendations.append("Total N > 100: Acceptable for preliminary Factor Analysis.")

if "Low" in power_gender_status:
    recommendations.append(f"Gender Comparison Power is {power_gender_status}. Need more balanced data (aim for ~60 per group).")
else:
    recommendations.append(f"Gender Comparison Power is {power_gender_status}.")

print(f"--- Data Sufficiency Analysis ---")
print(f"Total Clean Records: {clean_n}")
print(f"\n[Subgroups]")
print(f"Gender:\n{gender_counts.to_string()}")
print(f"\nYear:\n{year_counts.to_string()}")

print(f"\n[Statistical Power]")
print(f"Power for Gender Diff (Medium Effect d=0.5): {power_gender_status}")

print(f"\n[Recommendations]")
for rec in recommendations:
    print(f"- {rec}")

print(f"\n[Factor Analysis Feasibility]")
# Items per scale approx 25
print(f"Sample-to-Item Ratio (approx 25 items): {clean_n/25:.1f}:1 (Ideal > 5:1)")
