import json
import pandas as pd
import numpy as np

def calculate_stats():
    try:
        with open('bfi44_cleaned.json', 'r') as f:
            data = json.load(f)
        
        print(f"Loaded {len(data)} sessions.")
        
        # Extract Guna scores
        guna_data = []
        for session in data:
            if 'recalculated_guna' in session:
                guna_data.append(session['recalculated_guna'])
            elif 'computedScores' in session and 'gunaRaw' in session['computedScores']:
                 # Fallback if recalculated not present, but clean_and_analyze adds recalculated_guna
                 guna_data.append(session['computedScores']['gunaRaw'])
        
        df = pd.DataFrame(guna_data)
        
        # Ensure numeric
        cols = ['Sattva', 'Rajas', 'Tamas']
        for col in cols:
            df[col] = pd.to_numeric(df[col])
            
        print("\n--- Updated Guna Statistics (N={}) ---".format(len(df)))
        stats = df[cols].agg(['mean', 'std'])
        print(stats)
        
        print("\nFormatted for JS:")
        print("const populationStats = {")
        for col in cols:
            mean = stats.loc['mean', col]
            sd = stats.loc['std', col]
            print(f"  {col}: {{ mean: {mean:.2f}, sd: {sd:.2f} }},")
        print("};")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    calculate_stats()
