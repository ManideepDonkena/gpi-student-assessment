import pandas as pd
import numpy as np
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns

# --- PATH CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ANALYSIS_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(ANALYSIS_DIR, "data")
REPORTS_DIR = os.path.join(ANALYSIS_DIR, "reports")
IMAGES_DIR = os.path.join(ANALYSIS_DIR, "images")

os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# --- CONFIGURATION ---
INPUT_FILE = os.path.join(DATA_DIR, "final_dataset_refined.json")
REPORT_FILE = os.path.join(REPORTS_DIR, "PHASE2_RELIABILITY_REPORT.md")

# Guna Item Definitions (ID Prefix -> Category)
GUNA_MAPPING = {
    "S_": "Sattva",
    "R_": "Rajas",
    "T_": "Tamas"
}

# Big Five Mapping (Item ID -> Trait, Reverse)
BFI44_MAPPING = {
    "BFI1": {"trait": "Extraversion", "reverse": False},
    "BFI2": {"trait": "Agreeableness", "reverse": True},
    "BFI3": {"trait": "Conscientiousness", "reverse": False},
    "BFI4": {"trait": "Neuroticism", "reverse": False},
    "BFI5": {"trait": "Openness", "reverse": False},
    "BFI6": {"trait": "Extraversion", "reverse": True},
    "BFI7": {"trait": "Agreeableness", "reverse": False},
    "BFI8": {"trait": "Conscientiousness", "reverse": True},
    "BFI9": {"trait": "Neuroticism", "reverse": True},
    "BFI10": {"trait": "Openness", "reverse": False},
    "BFI11": {"trait": "Extraversion", "reverse": False},
    "BFI12": {"trait": "Agreeableness", "reverse": True},
    "BFI13": {"trait": "Conscientiousness", "reverse": False},
    "BFI14": {"trait": "Neuroticism", "reverse": False},
    "BFI15": {"trait": "Openness", "reverse": False},
    "BFI16": {"trait": "Extraversion", "reverse": False},
    "BFI17": {"trait": "Agreeableness", "reverse": False},
    "BFI18": {"trait": "Conscientiousness", "reverse": True},
    "BFI19": {"trait": "Neuroticism", "reverse": False},
    "BFI20": {"trait": "Openness", "reverse": False},
    "BFI21": {"trait": "Extraversion", "reverse": True},
    "BFI22": {"trait": "Agreeableness", "reverse": False},
    "BFI23": {"trait": "Conscientiousness", "reverse": True},
    "BFI24": {"trait": "Neuroticism", "reverse": True},
    "BFI25": {"trait": "Openness", "reverse": False},
    "BFI26": {"trait": "Extraversion", "reverse": False},
    "BFI27": {"trait": "Agreeableness", "reverse": True},
    "BFI28": {"trait": "Conscientiousness", "reverse": False},
    "BFI29": {"trait": "Neuroticism", "reverse": False},
    "BFI30": {"trait": "Openness", "reverse": False},
    "BFI31": {"trait": "Extraversion", "reverse": True},
    "BFI32": {"trait": "Agreeableness", "reverse": False},
    "BFI33": {"trait": "Conscientiousness", "reverse": False},
    "BFI34": {"trait": "Neuroticism", "reverse": True},
    "BFI35": {"trait": "Openness", "reverse": True},
    "BFI36": {"trait": "Extraversion", "reverse": False},
    "BFI37": {"trait": "Agreeableness", "reverse": True},
    "BFI38": {"trait": "Conscientiousness", "reverse": False},
    "BFI39": {"trait": "Neuroticism", "reverse": False},
    "BFI40": {"trait": "Openness", "reverse": False},
    "BFI41": {"trait": "Openness", "reverse": True},
    "BFI42": {"trait": "Agreeableness", "reverse": False},
    "BFI43": {"trait": "Conscientiousness", "reverse": True},
    "BFI44": {"trait": "Openness", "reverse": False}
}

def load_data(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}")
        return None
    with open(filepath, 'r') as f:
        data = json.load(f)
    print(f"Loaded {len(data)} records from {filepath}")
    return data

def extract_item_scores(data):
    """
    Extracts item-level scores AND text.
    Returns: 
      dfs: { 'Sattva': df, ... }
      texts: { 'S_J': "I prefer...", ... }
    """
    # Initialize containers
    guna_items = {k: [] for k in GUNA_MAPPING.values()}
    bfi_items = {trait: [] for trait in set(m['trait'] for m in BFI44_MAPPING.values())}
    item_texts = {}
    
    for session in data:
        # --- Process Guna Items ---
        guna_resps = session.get('gunaDetails', {})
        session_guna = {k: {} for k in GUNA_MAPPING.values()}
        
        for item_id, details in guna_resps.items():
            val = details.get('value')
            text = details.get('text')
            
            if val is None: continue
            if text and item_id not in item_texts:
                item_texts[item_id] = text
            
            # Determine category
            category = None
            for prefix, cat in GUNA_MAPPING.items():
                if item_id.startswith(prefix):
                    category = cat
                    break
            
            if category:
                session_guna[category][item_id] = val
        
        for cat, items in session_guna.items():
            if items: 
                guna_items[cat].append(items)

        # --- Process Big Five Items ---
        bfi_resps = session.get('bigFiveDetails', {})
        session_bfi = {trait: {} for trait in bfi_items.keys()}
        
        for item_id, details in bfi_resps.items():
            val = details.get('value')
            text = details.get('text')
            
            if val is None: continue
            if text and item_id not in item_texts:
                item_texts[item_id] = text
            
            meta = BFI44_MAPPING.get(item_id)
            if not meta: continue
            
            trait = meta['trait']
            reverse = meta['reverse']
            
            # Reverse score if needed
            final_score = (6 - val) if reverse else val
            session_bfi[trait][item_id] = final_score
            
        for trait, items in session_bfi.items():
            if items:
                bfi_items[trait].append(items)

    # Convert to DataFrames
    dfs = {}
    for cat, rows in guna_items.items():
        if rows:
            dfs[cat] = pd.DataFrame(rows)
            
    for trait, rows in bfi_items.items():
        if rows:
            dfs[trait] = pd.DataFrame(rows)
            # Sort columns numerically/alphabetically for consistency
            dfs[trait] = dfs[trait].reindex(sorted(dfs[trait].columns, key=lambda x: int(x[3:]) if 'BFI' in x else x), axis=1)

    return dfs, item_texts

def calculate_cronbach_alpha(df):
    """Calculates Cronbach's Alpha."""
    df_clean = df.dropna()
    if df_clean.empty or df_clean.shape[1] < 2: return 0.0
    
    item_variances = df_clean.var(axis=0, ddof=1)
    total_scores = df_clean.sum(axis=1)
    total_variance = total_scores.var(ddof=1)
    
    n_items = df_clean.shape[1]
    if total_variance == 0: return 0.0
    
    alpha = (n_items / (n_items - 1)) * (1 - (item_variances.sum() / total_variance))
    return alpha

def calculate_item_stats(df, scale_name):
    stats = []
    current_alpha = calculate_cronbach_alpha(df)
    total_scores = df.sum(axis=1)
    
    for item in df.columns:
        # Corrected Item-Total Correlation
        rest_scores = total_scores - df[item]
        itc = df[item].corr(rest_scores)
        
        # Alpha if deleted
        df_dropped = df.drop(columns=[item])
        alpha_dropped = calculate_cronbach_alpha(df_dropped)
        
        flag = ""
        if itc < 0.3: flag += "Low ITC "
        if alpha_dropped > current_alpha + 0.01: flag += "Alpha Improve "
        
        stats.append({
            "Item": item,
            "ITC": itc,
            "Alpha_if_Deleted": alpha_dropped,
            "Flag": flag.strip()
        })
        
    return pd.DataFrame(stats), current_alpha

def plot_itc(stats_df, scale_name, output_path, item_texts):
    """Generates a bar chart of Item-Total Correlations with text labels."""
    plt.figure(figsize=(12, 8))
    
    colors = ['red' if x < 0.3 else 'skyblue' for x in stats_df['ITC']]
    sns.barplot(x='Item', y='ITC', data=stats_df, palette=colors)
    plt.axhline(0.3, color='black', linestyle='--', label='Min Acceptable (0.3)')
    
    # Add truncated text labels to x-axis
    labels = []
    for item in stats_df['Item']:
        text = item_texts.get(item, "")
        # display ID + truncated text
        trunc = (text[:30] + '..') if len(text) > 30 else text
        labels.append(f"{item}\n{trunc}")
        
    plt.xticks(ticks=range(len(labels)), labels=labels, rotation=45, ha='right', fontsize=9)
    # Increase bottom margin for labels
    plt.subplots_adjust(bottom=0.25)
    
    plt.title(f'Item-Total Correlations: {scale_name}')
    plt.ylim(-0.5, 1.0)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_correlation_heatmap(df, scale_name, output_path):
    """Generates a heatmap of Item-Item correlations."""
    corr = df.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=False, cmap='coolwarm', center=0, vmin=-1, vmax=1)
    plt.title(f'Item Correlation Heatmap: {scale_name}')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def generate_report():
    print("Starting Phase 2 Reliability Analysis...")
    
    data = load_data(INPUT_FILE)
    if not data: return
    
    scale_dfs, item_texts = extract_item_scores(data)
    
    report_lines = []
    report_lines.append("# Phase 2: Reliability & Item Analysis Report 📉")
    report_lines.append(f"\n**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d')}")
    report_lines.append(f"**Dataset**: N={len(data)}")
    
    # Process Order
    order = ["Sattva", "Rajas", "Tamas"] + sorted([k for k in scale_dfs.keys() if k not in ["Sattva", "Rajas", "Tamas"]])
    
    summary_table = []
    summary_table.append("| Scale | Items | Cronbach's Alpha | Status |")
    summary_table.append("| :--- | :---: | :---: | :--- |")
    
    detailed_sections = []
    
    for scale in order:
        if scale not in scale_dfs: continue
        
        df = scale_dfs[scale]
        stats_df, alpha = calculate_item_stats(df, scale)
        
        # Status
        status = "✅ Excellent" if alpha >= 0.9 else \
                 "✅ Good" if alpha >= 0.8 else \
                 "⚠️ Acceptable" if alpha >= 0.7 else \
                 "⚠️ Questionable" if alpha >= 0.6 else "❌ Poor"
                 
        summary_table.append(f"| **{scale}** | {len(df.columns)} | **{alpha:.3f}** | {status} |")
        
        # Plots
        itc_path = os.path.join(IMAGES_DIR, f"reliability_{scale.lower()}.png")
        plot_itc(stats_df, scale, itc_path, item_texts)
        
        corr_path = os.path.join(IMAGES_DIR, f"heatmap_{scale.lower()}.png")
        plot_correlation_heatmap(df, scale, corr_path)

        # Detailed Section
        detailed_sections.append(f"\n### {scale} (Alpha: {alpha:.3f})")
        
        # Add carousel/grid of images
        detailed_sections.append(f"![ITC Chart](../images/reliability_{scale.lower()}.png)")
        detailed_sections.append(f"![Correlation Heatmap](../images/heatmap_{scale.lower()}.png)")
        
        bad_items = stats_df[stats_df['Flag'] != ""]
        if bad_items.empty:
             detailed_sections.append("\n✅ **All items are performing well.** No removal recommended.")
        else:
            detailed_sections.append("\n⚠️ **Potential Problematic Items:**")
            detailed_sections.append("\n| Item | Question Text | ITC | Alpha if Deleted | Issue Flag |")
            detailed_sections.append("| :--- | :--- | :---: | :---: | :--- |")
            
            for _, row in bad_items.iterrows():
                text = item_texts.get(row['Item'], "").replace("\n", " ").replace("|", "-")
                detailed_sections.append(f"| {row['Item']} | {text} | {row['ITC']:.3f} | **{row['Alpha_if_Deleted']:.3f}** | {row['Flag']} |")
                
            toxic_items = bad_items[bad_items['Alpha_if_Deleted'] > alpha]
            if not toxic_items.empty:
                 detailed_sections.append(f"\n**Recommendation**: Consider removing **{', '.join(toxic_items['Item'].tolist())}** to improve scale reliability.")

    report_lines.append("\n## 1. Reliability Summary")
    report_lines.extend(summary_table)
    report_lines.append("\n> **Note**: Alpha > 0.7 is generally considered acceptable.")
    
    report_lines.append("\n## 2. Detailed Item Analysis & Charts")
    report_lines.extend(detailed_sections)
    
    # Save Report
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
        
    print(f"Analysis complete. Report saved to {REPORT_FILE}")

if __name__ == "__main__":
    generate_report()
