
import os
import json
import glob
import pandas as pd
import matplotlib.pyplot as plt

INPUT_DIR = "dummy_students"

# BFI-10 Scoring (Reverse items need 6-x)
BFI_MAP = {
    "BF1": ("Extraversion", True),
    "BF2": ("Agreeableness", False),
    "BF3": ("Conscientiousness", True),
    "BF4": ("Neuroticism", True),
    "BF5": ("Openness", True),
    "BF6": ("Extraversion", False),
    "BF7": ("Agreeableness", True),
    "BF8": ("Conscientiousness", False),
    "BF9": ("Neuroticism", False),
    "BF10": ("Openness", False)
}

# Guna Proxy Reverse Map (Item ID -> Is Reverse)
GUNA_REVERSE = {
    "S14": True,  # Self-realization is not important
    "R15": True,  # Simple life (No luxury)
}

def load_data(source=None):
    """
    Load data from either a directory of JSONs (dummy) or a single JSON list (firebase).
    """
    records = []
    data_list = []
    
    if source and os.path.isfile(source):
        # Load single JSON list (Firebase dump)
        with open(source, 'r') as f:
            content = json.load(f)
            if isinstance(content, list):
                data_list = content
            else:
                data_list = [content]
    else:
        # Load directory (default dummy)
        target_dir = source if source else INPUT_DIR
        files = glob.glob(os.path.join(target_dir, "*.json"))
        for f in files:
            with open(f, 'r') as file:
                data_list.append(json.load(file))
    
    for data in data_list:
        # Guna Scores (Mean with Reverse Coding)
        g_r = data.get('gunaResponses', {})
        s_vals, r_vals, t_vals = [], [], []
        
        for q_id, val in g_r.items():
            # Likert 1-5 Reverse: 6 - val
            score = 6 - val if GUNA_REVERSE.get(q_id) else val
            
            if q_id.startswith('S'): s_vals.append(score)
            elif q_id.startswith('R'): r_vals.append(score)
            elif q_id.startswith('T'): t_vals.append(score)
        
        # Big Five Scores
        bf_r = data.get('bigFiveResponses', {})
        bf_scores = {t: [] for t in ["Extraversion", "Agreeableness", "Conscientiousness", "Neuroticism", "Openness"]}
        
        for iid, val in bf_r.items():
            if iid not in BFI_MAP: continue
            trait, reverse = BFI_MAP[iid]
            score = 6 - val if reverse else val
            bf_scores[trait].append(score)
        
        # Behavioral Metadata
        gm = data.get('gunaMetadata', {})
        bm = data.get('bigFiveMetadata', {})
        
        total_time = gm.get('timeMs', 0) + bm.get('timeMs', 0)
        total_dist = gm.get('cursorDistancePx', 0) + bm.get('cursorDistancePx', 0)
        total_changes = gm.get('answerChanges', 0) + bm.get('answerChanges', 0)

        record = {
            "Sattva": sum(s_vals)/len(s_vals) if s_vals else 0,
            "Rajas": sum(r_vals)/len(r_vals) if r_vals else 0,
            "Tamas": sum(t_vals)/len(t_vals) if t_vals else 0,
            "Time_Sec": total_time / 1000,
            "Cursor_Dist": total_dist,
            "Ans_Changes": total_changes
        }
        
        for trait, vals in bf_scores.items():
            record[trait] = sum(vals)/len(vals) if vals else 0
            
        records.append(record)
            
    return pd.DataFrame(records)

def run_analysis():
    # Try loading firebase data first, else dummy
    source = "firebase_dump.json" if os.path.exists("firebase_dump.json") else INPUT_DIR
    df = load_data(source)
    print(f"Loaded {len(df)} student records from {source}.")
    
    if len(df) < 5:
        print("Not enough data for correlation analysis.")
        return

    # Correlation Matrix
    cols = ["Sattva", "Rajas", "Tamas", 
            "Extraversion", "Agreeableness", "Conscientiousness", "Neuroticism", "Openness",
            "Time_Sec", "Cursor_Dist", "Ans_Changes"]
            
    corr = df[cols].corr()
    print("\nCorrelation Matrix:\n", corr)
    
    # Save Heatmap using Matplotlib only
    plt.figure(figsize=(12, 10))
    plt.imshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
    plt.colorbar()
    
    # Add labels
    ticks = range(len(cols))
    plt.xticks(ticks, cols, rotation=45, ha='right')
    plt.yticks(ticks, cols)
    
    # Add text annotations (filter NaNs)
    for i in range(len(cols)):
        for j in range(len(cols)):
            val = corr.iloc[i, j]
            if pd.notna(val):
                text = f"{val:.2f}"
                plt.text(j, i, text, ha='center', va='center', color='black', fontsize=8)
            
    plt.title("Correlation: Gunas vs Big Five vs Behavior")
    plt.tight_layout()
    plt.savefig("correlation_heatmap.png")
    print("Saved correlation_heatmap.png")
    
    # Hypothesis Checks
    print("\n--- Hypothesis Checks ---")
    try:
        print(f"H1: Sattva ~ Conscientiousness: r = {corr.loc['Sattva','Conscientiousness']:.2f} (Expected > 0)")
        print(f"H2: Rajas ~ Neuroticism:       r = {corr.loc['Rajas','Neuroticism']:.2f} (Expected > 0)")
        print(f"H3: Tamas ~ Openness:          r = {corr.loc['Tamas','Openness']:.2f} (Expected < 0)")
    except KeyError:
        print("Could not compute all hypotheses (missing columns).")
    
    print("\n--- Behavioral Insights ---")
    try:
        print(f"B1: Rajas ~ Cursor Dist:       r = {corr.loc['Rajas', 'Cursor_Dist']:.2f} (Expected > 0)")
        print(f"B2: Tamas ~ Time Taken:        r = {corr.loc['Tamas', 'Time_Sec']:.2f} (Expected > 0, slow)")
    except KeyError:
        pass

if __name__ == "__main__":
    run_analysis()
