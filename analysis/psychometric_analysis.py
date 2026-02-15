import json
import pandas as pd
import numpy as np
import os

# Mappings from items.js and clean_and_analyze.py
BFI10_MAPPING = {
    "BF1": {"trait": "Extraversion", "reverse": True},
    "BF2": {"trait": "Agreeableness", "reverse": False},
    "BF3": {"trait": "Conscientiousness", "reverse": True},
    "BF4": {"trait": "Neuroticism", "reverse": True},
    "BF5": {"trait": "Openness", "reverse": True},
    "BF6": {"trait": "Extraversion", "reverse": False},
    "BF7": {"trait": "Agreeableness", "reverse": True},
    "BF8": {"trait": "Conscientiousness", "reverse": False},
    "BF9": {"trait": "Neuroticism", "reverse": False},
    "BF10": {"trait": "Openness", "reverse": False},
}

# Standard BFI-44 approximation
BFI44_MAPPING = {
    f"BFI{i}": {"trait": trait, "reverse": reverse} 
    for i, (trait, reverse) in enumerate([
        ("Extraversion", False), ("Agreeableness", True), ("Conscientiousness", False), ("Neuroticism", False), ("Openness", False),
        ("Extraversion", True), ("Agreeableness", False), ("Conscientiousness", True), ("Neuroticism", True), ("Openness", False),
        ("Extraversion", False), ("Agreeableness", True), ("Conscientiousness", False), ("Neuroticism", False), ("Openness", False),
        ("Extraversion", False), ("Agreeableness", False), ("Conscientiousness", True), ("Neuroticism", False), ("Openness", False),
        ("Extraversion", True), ("Agreeableness", False), ("Conscientiousness", True), ("Neuroticism", True), ("Openness", False),
        ("Extraversion", False), ("Agreeableness", True), ("Conscientiousness", False), ("Neuroticism", False), ("Openness", False),
        ("Extraversion", True), ("Agreeableness", False), ("Conscientiousness", False), ("Neuroticism", True), ("Openness", True),
        ("Extraversion", False), ("Agreeableness", True), ("Conscientiousness", False), ("Neuroticism", False), ("Openness", False),
        ("Openness", True), ("Agreeableness", False), ("Conscientiousness", True), ("Openness", False)
    ], 1)
}

def cronbach_alpha(df):
    # df: rows are people, columns are items
    k = df.shape[1]
    if k <= 1: return 0.0
    item_vars = df.var(axis=0, ddof=1).sum()
    total_var = df.sum(axis=1).var(ddof=1)
    if total_var == 0: return 0.0
    alpha = (k / (k-1)) * (1 - (item_vars / total_var))
    return alpha

def analyze_reliability(json_file, cohort_name):
    if not os.path.exists(json_file):
        return f"Error: {json_file} not found."
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    if not data:
        return f"No data in {json_file}."

    report = [f"\n### Psychometric Validity: {cohort_name} (N={len(data)})"]
    
    # 1. Prepare Guna Data
    guna_items = {"Sattva": [], "Rajas": [], "Tamas": []}
    # Find all guna keys present
    all_guna_keys = set()
    for s in data:
        all_guna_keys.update(s.get('gunaResponses', {}).keys())
    
    guna_keys = {
        "Sattva": [k for k in all_guna_keys if k.startswith("S_")],
        "Rajas": [k for k in all_guna_keys if k.startswith("R_")],
        "Tamas": [k for k in all_guna_keys if k.startswith("T_")]
    }

    report.append("\n#### Internal Consistency (Cronbach's Alpha)")
    
    # Guna Reliability
    guna_resps = [s.get('gunaResponses', {}) for s in data]
    df_guna = pd.DataFrame(guna_resps).fillna(3) # Midpoint fallback
    
    results = []
    for subscale, keys in guna_keys.items():
        if not keys: continue
        sub_df = df_guna[keys]
        alpha = cronbach_alpha(sub_df)
        results.append({"Scale": subscale, "Items": len(keys), "Alpha": alpha})
    
    # Big Five Reliability
    mapping = BFI44_MAPPING if "44" in cohort_name else BFI10_MAPPING
    bf_traits = ["Extraversion", "Agreeableness", "Conscientiousness", "Neuroticism", "Openness"]
    
    bf_resps_raw = [s.get('bigFiveResponses', {}) for s in data]
    bf_resps_processed = []
    for resp in bf_resps_raw:
        processed = {}
        for q_id, val in resp.items():
            if q_id in mapping:
                meta = mapping[q_id]
                processed[q_id] = (6 - val) if meta["reverse"] else val
        bf_resps_processed.append(processed)
    
    df_bf = pd.DataFrame(bf_resps_processed).fillna(3)
    
    for trait in bf_traits:
        keys = [k for k, v in mapping.items() if v["trait"] == trait and k in df_bf.columns]
        if not keys: continue
        sub_df = df_bf[keys]
        alpha = cronbach_alpha(sub_df)
        results.append({"Scale": trait, "Items": len(keys), "Alpha": alpha})
    
    res_df = pd.DataFrame(results)
    # Manual Markdown Formatting
    report.append("| Scale | Items | Alpha |")
    report.append("| :--- | :--- | :--- |")
    for _, row in res_df.iterrows():
        report.append(f"| {row['Scale']} | {row['Items']} | {row['Alpha']:.3f} |")

    # 2. Item-Total Correlation (Top/Bottom items)
    report.append("\n#### Item-Total Analysis (Strengths & Weaknesses)")
    
    def get_itc(df):
        total = df.sum(axis=1)
        itc = {}
        for col in df.columns:
            # Correlation of item with total-minus-item (Corrected Item-Total Correlation)
            rest = total - df[col]
            if rest.var() == 0 or df[col].var() == 0:
                itc[col] = 0.0
            else:
                itc[col] = np.corrcoef(df[col], rest)[0, 1]
        return itc

    all_itcs = []
    # Just Guna for brevity in report or specific traits
    for subscale, keys in guna_keys.items():
        if len(keys) < 2: continue
        itc_vals = get_itc(df_guna[keys])
        for k, v in itc_vals.items():
            all_itcs.append({"Scale": subscale, "Item": k, "ITC": v})
            
    itc_df = pd.DataFrame(all_itcs).sort_values("ITC", ascending=False)
    
    report.append("\nTop 5 Strongest Items (Guna):")
    report.append("| Scale | Item | ITC |")
    report.append("| :--- | :--- | :--- |")
    for _, row in itc_df.head(5).iterrows():
        report.append(f"| {row['Scale']} | {row['Item']} | {row['ITC']:.3f} |")
    
    report.append("\nBottom 5 Weakest Items (Guna):")
    report.append("| Scale | Item | ITC |")
    report.append("| :--- | :--- | :--- |")
    for _, row in itc_df.tail(5).iterrows():
        report.append(f"| {row['Scale']} | {row['Item']} | {row['ITC']:.3f} |")
    
    return "\n".join(report)

if __name__ == "__main__":
    report10 = analyze_reliability("bfi10_cleaned.json", "BFI-10 Cohort")
    report44 = analyze_reliability("bfi44_cleaned.json", "BFI-44 Cohort")
    
    with open("PSYCHOMETRIC_VALIDITY_REPORT.md", "w") as f:
        f.write("# Psychometric Validity & Reliability Report\n")
        f.write("This report analyzes the internal consistency (Cronbach's Alpha) and item validity of the GPI assessment.\n")
        f.write(report10)
        f.write("\n\n---\n")
        f.write(report44)
    
    print("Report generated: PSYCHOMETRIC_VALIDITY_REPORT.md")
