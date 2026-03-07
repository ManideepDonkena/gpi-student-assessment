import json
import pandas as pd
import numpy as np
import os

def df_to_markdown(df):
    if df.empty: return ""
    headers = list(df.columns)
    header_row = "| " + " | ".join(map(str, headers)) + " |"
    separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"
    rows = ["| " + " | ".join(map(str, row.values)) + " |" for _, row in df.iterrows()]
    return "\n".join([header_row, separator_row] + rows)

def inspect_outliers():
    print("Inspecting Tamas Outliers (Detailed Item Analysis)...")
    
    # Load cleaned BFI-44 data
    json_path = "bfi44_cleaned.json"
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    with open(json_path, "r") as f:
        data = json.load(f)

    cleaned_data = []  
    outlier_details = []

    for i, s in enumerate(data):
        guna_resps = s.get('gunaResponses', {})
        tamas_vals = [v for k, v in guna_resps.items() if k.startswith('T_')]
        
        # Calculate Response Variance (Check for Straight-Lining)
        # If variance is near 0, they answered the same thing for everything (e.g., all 7s)
        resp_variance = np.var(tamas_vals) if tamas_vals else 0
        
        row = {
            "ID": i+1,
            "Gender": s.get('demographics', {}).get('gender', 'Unknown'),
            "Age": s.get('demographics', {}).get('age', 'Unknown'),
            "Tamas": s.get('recalculated_guna', {}).get('Tamas'),
            "Neuroticism": s.get('recalculated_bfi', {}).get('Neuroticism'),
            "Time_Guna(m)": round(s.get('time_guna_min', 0), 1),
            "Var(Tamas)": round(resp_variance, 2),
            "Raw_Tamas": tamas_vals  # Store for detailed look
        }
        cleaned_data.append(row)
        
    df = pd.DataFrame(cleaned_data)
    
    # Calculate Mean/SD for Tamas
    mean_t = df['Tamas'].mean()
    std_t = df['Tamas'].std()
    
    threshold = mean_t + (2 * std_t)
    print(f"Tamas Mean: {mean_t:.2f} | SD: {std_t:.2f}")
    print(f"Outlier Threshold (+2 SD): {threshold:.2f}")
    
    # Filter Outliers
    outliers = df[df['Tamas'] > threshold].sort_values(by='Tamas', ascending=False)
    
    print(f"\n--- {len(outliers)} High-Tamas Outliers Identified ---")
    
    summary_table = outliers.drop(columns=['Raw_Tamas']).copy()
    print(df_to_markdown(summary_table))
    
    print("\n\n--- Detailed Profile Analysis ---")
    
    for _, student in outliers.iterrows():
        print(f"\nStudent ID: {student['ID']}")
        print(f"  > Tamas Score: {student['Tamas']:.2f} (Very High)")
        print(f"  > Response Variance: {student['Var(Tamas)']} (Low < 0.5 suggests pattern clicking)")
        print(f"  > Time Taken: {student['Time_Guna(m)']} min")
        print(f"  > Neuroticism: {student['Neuroticism']:.2f} (Exp: High)")
        
        # Analyze Raw Responses
        raw = student['Raw_Tamas']
        counts = pd.Series(raw).value_counts().sort_index()
        print(f"  > Answer Distribution: {counts.to_dict()}")
        
        if student['Var(Tamas)'] < 0.5:
             print("  ⚠️ ALERT: STRAIGHT-LINING DETECTED (Low Variance)")
        elif student['Time_Guna(m)'] < 3.5:
             print("  ⚠️ ALERT: SPEED-RUN DETECTED (Fast Completion)")
        elif student['Neuroticism'] < 2.5:
             print("  ⚠️ ALERT: INCONSISTENT TRAITS (High Tamas usually means High Neuroticism)")
        else:
             print("  ✅ DATA LOOKS VALID (Consistent & Deliberate)")

if __name__ == "__main__":
    inspect_outliers()
