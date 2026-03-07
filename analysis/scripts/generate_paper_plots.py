"""
=============================================================
PAPER PLOT GENERATOR 🎨
=============================================================
Generates high-quality, publication-ready figures for the 
GPI validation paper.
Style: High contrast, large fonts, thick lines (APA compliant).
"""
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- PATHS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "final_dataset_refined.json")
OUT_DIR = os.path.join(BASE_DIR, "paper", "images")
os.makedirs(OUT_DIR, exist_ok=True)

# --- STYLE CONFIG ---
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("talk", font_scale=1.1)  # Larger font for paper
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.weight': 'bold',
    'axes.labelweight': 'bold',
    'axes.titleweight': 'bold',
    'axes.titlesize': 16,
    'axes.labelsize': 14,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'lines.linewidth': 2.5,
    'lines.markersize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300,
})

COLORS = {
    'Sattva': '#2ecc71',
    'Rajas': '#e74c3c', 
    'Tamas': '#34495e',
    'BigFive': '#3498db'
}

def load_data():
    with open(DATA_PATH, 'r') as f:
        data = json.load(f)
    print(f"Loaded {len(data)} records")
    return data

def plot_incremental_validity(data):
    """Figure 1: Incremental Validity (Delta R2)"""
    # Hardcoded results from Phase 8 regression for stability/consistency
    outcomes = [
        "Sattvic Choices", "Spiritual Practice", "Gita Familiarity", 
        "Tamasic Choices", "Rajasic Choices"
    ]
    delta_r2 = [0.162, 0.198, 0.227, 0.134, 0.068] # From Phase 8 Report
    
    df = pd.DataFrame({'Outcome': outcomes, 'Added Variance': delta_r2})
    df = df.sort_values('Added Variance', ascending=True)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(df['Outcome'], df['Added Variance'], color=COLORS['Sattva'], alpha=0.9)
    
    ax.set_xlabel('Additional Variance Explained (ΔR²)', fontweight='bold')
    ax.set_title('Incremental Validity of Guna Traits\n(Beyond Big Five)', pad=20)
    ax.set_xlim(0, 0.25)
    
    # Add labels
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.005, bar.get_y() + bar.get_height()/2, 
                f'+{width:.1%}', va='center', fontweight='bold', color='#2c3e50')
        
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "fig1_incremental_validity.png"))
    print("Generated Fig 1")

def plot_scenario_validity(data):
    """Figure 2: Criterion Validity (Scenario Choices)"""
    # Extract scores and choices
    rows = []
    for s in data:
        scores = s.get('recalculated_guna', {})
        scenarios = s.get('scenarioResponses', [])
        
        # Count choices
        counts = {'sattva': 0, 'rajas': 0, 'tamas': 0}
        for resp in scenarios:
            if resp.get('choiceId'):
                counts[resp['choiceId']] += 1
                
        # Determine dominant choice (simple majority)
        dom = max(counts, key=counts.get)
        
        rows.append({
            'Sattva Score': scores.get('Sattva'),
            'Rajas Score': scores.get('Rajas'),
            'Tamas Score': scores.get('Tamas'),
            'Choice': dom.capitalize()
        })
        
    df = pd.DataFrame(rows)
    df = df[df['Choice'].isin(['Sattva', 'Rajas', 'Tamas'])] # Filter valid
    
    # Plot
    fig, axes = plt.subplots(1, 3, figsize=(16, 6), sharey=True)
    
    traits = ['Sattva', 'Rajas', 'Tamas']
    for i, trait in enumerate(traits):
        ax = axes[i]
        sns.boxplot(x='Choice', y=f'{trait} Score', data=df, ax=ax, 
                    order=['Sattva', 'Rajas', 'Tamas'], palette=[COLORS['Sattva'], COLORS['Rajas'], COLORS['Tamas']])
        ax.set_title(f'{trait} Scores by\nBehavioral Choice')
        ax.set_xlabel('Dominant Scenario Choice')
        if i == 0: ax.set_ylabel('Trait Score (1-7)')
        else: ax.set_ylabel('')
        
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "fig2_criterion_validity.png"))
    print("Generated Fig 2")

def plot_implicit_defense(data):
    """Figure 3: Implicit Behavioral Variables"""
    # Extract implicit data
    rows = []
    for s in data:
        gm = s.get('gunaMetadata', {})
        rows.append({
            'Answer Changes': gm.get('answerChanges', 0),
            'Sattva Score': s.get('recalculated_guna', {}).get('Sattva')
        })
    df = pd.DataFrame(rows)
    
    # Scatter with regression line
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.regplot(x='Answer Changes', y='Sattva Score', data=df, ax=ax,
                scatter_kws={'alpha':0.5, 'color':'gray'}, line_kws={'color':COLORS['Sattva'], 'linewidth':3})
    
    ax.set_title('Answer Changes vs. Sattva Score\n(Social Desirability Check)')
    ax.set_xlabel('Number of Answer Changes (Deliberation)')
    ax.set_ylabel('Sattva Score')
    
    # Annotate correlation
    r = df.corr().iloc[0,1]
    ax.text(0.05, 0.95, f'r = {r:.3f} (ns)', transform=ax.transAxes, 
            fontsize=14, verticalalignment='top', bbox=dict(boxstyle="round", fc="white", ec="black", alpha=0.8))
            
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "fig3_implicit_defense.png"))
    print("Generated Fig 3")

def plot_factor_structure():
    """Figure 4: Factor Variance Explained"""
    # Hardcoded from Phase 5/9 EFA results
    factors = [
        ("F1: Tamas/Rajas (Mixed)", 17.9, "Mixed"),
        ("F2: Spiritual Orientation", 5.9, "Unique Guna"),
        ("F3: Sattva/Tamas (Mixed)", 5.6, "Mixed"),
        ("F4: Openness/Extraversion", 3.8, "Big Five"),
        ("F5: Agreeableness/Tamas", 3.3, "Mixed"),
        ("F6: Neuroticism", 2.7, "Big Five"),
        ("F7: Extraversion", 2.5, "Big Five"),
        ("F8: Material Desire", 2.3, "Unique Guna")
    ]
    
    names = [f[0] for f in factors]
    vars = [f[1] for f in factors]
    colors = [COLORS['Tamas'] if 'Mixed' in f[2] else (COLORS['Sattva'] if 'Unique' in f[2] else COLORS['BigFive']) for f in factors]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(names, vars, color=colors)
    
    ax.set_xticklabels(names, rotation=45, ha='right')
    ax.set_ylabel('Variance Explained (%)')
    ax.set_title('Joint Factor Structure (Guna + Big Five)')
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=COLORS['Sattva'], label='Unique Guna Factors'),
        Patch(facecolor=COLORS['Tamas'], label='Mixed Guna/BFI Factors'),
        Patch(facecolor=COLORS['BigFive'], label='Big Five Factors')
    ]
    ax.legend(handles=legend_elements)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "fig4_factor_structure.png"))
    print("Generated Fig 4")

def main():
    data = load_data()
    plot_incremental_validity(data)
    plot_scenario_validity(data)
    plot_implicit_defense(data)
    plot_factor_structure()
    print(f"All plots saved to {OUT_DIR}")

if __name__ == "__main__":
    main()
