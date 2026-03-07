import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import numpy as np

# Set style
import seaborn as sns
sns.set_theme(style="whitegrid")

# Load Cleaned Data
json_file = 'bfi44_cleaned.json'
if not os.path.exists(json_file):
    print(f"Error: {json_file} not found. Run clean_and_analyze.py first.")
    exit()

with open(json_file, 'r') as f:
    data = json.load(f)

# Flatten Data
rows = []
for session in data:
    guna = session.get('recalculated_guna', {})
    bfi = session.get('recalculated_bfi', {})
    
    if not guna or not bfi: continue
    
    row = {
        'Sattva': guna.get('Sattva'),
        'Rajas': guna.get('Rajas'),
        'Tamas': guna.get('Tamas'),
        'Extraversion': bfi.get('Extraversion'),
        'Agreeableness': bfi.get('Agreeableness'),
        'Conscientiousness': bfi.get('Conscientiousness'),
        'Neuroticism': bfi.get('Neuroticism'),
        'Openness': bfi.get('Openness')
    }
    rows.append(row)

df = pd.DataFrame(rows)
print(f"Loaded {len(df)} records for plotting.")

# Define Key Pairs to Plot (based on Hypotheses)
pairs = [
    ('Sattva', 'Conscientiousness'),
    ('Sattva', 'Agreeableness'),
    ('Sattva', 'Openness'),
    ('Rajas', 'Neuroticism'),
    ('Rajas', 'Extraversion'),
    ('Tamas', 'Neuroticism'),
    ('Tamas', 'Conscientiousness'),
    ('Tamas', 'Agreeableness')
]

# Create Output Directory
output_dir = "plots_scatter"
os.makedirs(output_dir, exist_ok=True)

# Generate Individual Scatter Plots with Regression Line
print("Generating Scatter Plots...")
for x_col, y_col in pairs:
    plt.figure(figsize=(8, 6))
    
    # Calculate Correlation
    r = df[x_col].corr(df[y_col])
    
    # Plot
    sns.regplot(data=df, x=x_col, y=y_col, scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
    
    plt.title(f'{x_col} vs {y_col} (r = {r:.2f})', fontsize=14)
    plt.xlabel(f'{x_col} Score', fontsize=12)
    plt.ylabel(f'{y_col} Score', fontsize=12)
    
    # Save
    filename = f"{output_dir}/scatter_{x_col}_{y_col}.png"
    plt.savefig(filename, dpi=100)
    plt.close()
    print(f"Saved {filename}")

# Generate a PairGrid for Overview (Optional but cool)
# We'll do a smaller subset to avoid clutter
print("Generating PairPlot...")
subset = df[['Sattva', 'Rajas', 'Tamas', 'Conscientiousness', 'Neuroticism']]
pp = sns.pairplot(subset, kind="reg", diag_kind="kde", plot_kws={'line_kws':{'color':'red'}, 'scatter_kws': {'alpha': 0.3}})
pp.fig.suptitle("Gunas vs Key Traits Overview", y=1.02)
pp.savefig(f"{output_dir}/pairplot_overview.png", dpi=100)
print(f"Saved {output_dir}/pairplot_overview.png")
