
import pandas as pd
import numpy as np
from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy import stats

def load_and_prep_data():
    # Load the refined dataset
    try:
        df = pd.read_json("c:/Users/donke/Desktop/IKS_Work/Gunabased Survey/student-assessment/analysis/data/final_dataset_refined.json")
    except ValueError:
        print("Error: Could not load JSON file.")
        return None

    # 1. Flatten Guna Items (for EFA)
    if 'gunaResponses' in df.columns:
        # If it's already a dict/list of dicts
        guna_items = pd.DataFrame(df['gunaResponses'].tolist())
    else:
        # Try to find it if nested? No, inspected columns showed it likely exists
        # It might be named differently or need parsing
        print("Warning: 'gunaResponses' column not found directly.")
        return None

    # Handle missing/non-numeric in items
    guna_items = guna_items.apply(pd.to_numeric, errors='coerce').fillna(3)

    # 2. Extract Scores (Guna & Big Five)
    # Using 'recalculated_guna' and 'recalculated_bfi'
    if 'recalculated_guna' in df.columns:
        guna_scores = pd.DataFrame(df['recalculated_guna'].tolist())
    else:
        guna_scores = pd.DataFrame()

    if 'recalculated_bfi' in df.columns:
        bfi_scores = pd.DataFrame(df['recalculated_bfi'].tolist())
    else:
        bfi_scores = pd.DataFrame()

    # 3. Extract Demographics (Gender, Gita Familiarity)
    if 'demographics' in df.columns:
        demog = pd.DataFrame(df['demographics'].tolist())
        # Clean Gender
        demog['Male'] = demog['gender'].apply(lambda x: 1 if str(x).lower().strip() in ['male', 'm'] else 0)
        
        # Clean Gita Familiarity (Ordinal Proxy)
        # Assuming values might be strings like "Completely Unfamiliar", etc.
        # We need to map them if possible. Let's just print unique values to check later or assume 1-5 scalar if numeric.
        # If text, we'll try a simple mapping if known, otherwise skip.
        # Previous context didn't show values, but 'Mid' or 'High' etc.
        # Let's try to map: 'Not Familiar': 1, 'Slightly': 2, 'Moderately': 3, 'Very': 4, 'Extremely': 5
        # If it's already numeric, good.
        # For now, let's keep it and check types later.
    else:
        demog = pd.DataFrame()

    # Combine all
    combined = pd.concat([guna_items, guna_scores, bfi_scores, demog], axis=1)
    
    # Store lists of column names for easy access
    item_cols = guna_items.columns.tolist()
    guna_score_cols = ['Sattva', 'Rajas', 'Tamas'] # Ensure these match keys in recalculated_guna
    bfi_score_cols = bfi_scores.columns.tolist()
    
    return combined, item_cols, guna_score_cols, bfi_score_cols

def run_promax_efa(df, item_cols):
    print("\n--- 1. Oblique Rotation EFA (Promax) on Guna Items ---")
    
    # Filter items that are in REMOVAL_LIST if desired? 
    # Or use all to show "raw" structure? 
    # Let's use all validated items (from refined set).
    # Assuming 'item_cols' are the ones we want (i.e. all available in gunaResponses).
    
    # Check KMO
    try:
        kmo_all, kmo_model = calculate_kmo(df[item_cols])
        print(f"KMO Score: {kmo_model:.3f}")
    except:
        print("KMO Calculation Failed (Singular Matrix?)")

    # Run EFA with Promax
    # We expect 3 factors for Gunas
    fa = FactorAnalyzer(n_factors=3, rotation='promax')
    fa.fit(df[item_cols])
    
    # Get loadings
    loadings = pd.DataFrame(fa.loadings_, index=item_cols, columns=['Factor1', 'Factor2', 'Factor3'])
    
    # Identify Factors based on max loading
    loadings['Max_Factor'] = loadings.abs().idxmax(axis=1)
    
    # Print Loading Summary
    print("\nItems per Factor (Promax):")
    print(loadings['Max_Factor'].value_counts())
    
    # Show Factor Correlations (Phi)
    if hasattr(fa, 'phi_'):
        print("\nFactor Correlation Matrix (Phi):")
        print(pd.DataFrame(fa.phi_, index=['F1','F2','F3'], columns=['F1','F2','F3']).round(2))
    else:
        print("\nPhi matrix not available.")
        
    return fa, kmo_model

def check_correlations(df, guna_cols, bfi_cols):
    print("\n--- 2. Correlations: Guna Scores vs Big Five Scores ---")
    
    # Ensure columns exist
    valid_guna = [c for c in guna_cols if c in df.columns]
    valid_bfi = [c for c in bfi_cols if c in df.columns]
    
    if not valid_guna or not valid_bfi:
        print("Missing Guna or BFI columns for correlation.")
        return 0, 0

    corr_matrix = df[valid_guna + valid_bfi].corr()
    
    # Extract just the Guna x Big5 block
    guna_bfi_corr = corr_matrix.loc[valid_guna, valid_bfi]
    
    print("\nCorrelation Matrix (Rows: Guna, Cols: Big5):")
    print(guna_bfi_corr.round(2))
    
    # Check max correlation
    max_corr = guna_bfi_corr.abs().max().max()
    print(f"\nMaximum Correlation: {max_corr:.2f}")
    if max_corr < 0.4:
         print(">> RESULT: Low to Moderate overlap. Supports distinctness claim.")
    else:
         print(">> RESULT: High overlap. Nuance required in claims.")
         
    return max_corr

def check_vif(df, guna_cols, bfi_cols):
    print("\n--- 3. Multicollinearity Diagnostics (VIF) ---")
    
    features = bfi_cols + guna_cols
    # Add Gender if available
    if 'Male' in df.columns:
        features.append('Male')
        
    # Clean Data
    X = df[features].dropna()
    X = sm.add_constant(X)
    
    vif_data = pd.DataFrame()
    vif_data["feature"] = X.columns
    vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(len(X.columns))]
    
    print(vif_data.sort_values(by='VIF', ascending=False))
    
    # Exclude constant from max check
    predictor_vifs = vif_data[vif_data['feature'] != 'const']['VIF']
    return predictor_vifs.max() if not predictor_vifs.empty else 0

def run_regression_defense(df, guna_cols, bfi_cols):
    print("\n--- 4. Incremental Validity Regression ---")
    
    # Outcome: Gita Familiarity (Ordinal) 
    # Or Sattvic Choice if we can calculate it.
    # Let's check 'gitaFamiliarity' values first
    if 'gitaFamiliarity' not in df.columns:
        print("Outcome variable 'gitaFamiliarity' not found.")
        return 0

    # Helper to map Likert if it's text
    # Assuming standard 5-point? Or check unique
    unique_vals = df['gitaFamiliarity'].unique()
    print(f"Outcome Levels: {unique_vals}")
    
    # Simple mapping if needed (customize based on output)
    # If it's already numeric 1-5, great. If text, we might need a map.
    # For now, assume it's capable of being treated as numeric or we map it.
    # If fails, we catch it.
    
    # Try to convert to numeric
    df['Outcome'] = pd.to_numeric(df['gitaFamiliarity'], errors='coerce')
    
    # If mostly NaNs, it was text. Map it.
    if df['Outcome'].isna().sum() > len(df) * 0.5:
        # Define mapping based on actual data: ['Very Familiar', 'Somewhat', 'Heard of it', 'Not at all']
        mapping = {
            'Not at all': 1, 
            'Heard of it': 2, 
            'Somewhat': 3, 
            'Very Familiar': 4
        }
        # Apply mapping
        df['Outcome'] = df['gitaFamiliarity'].map(mapping)
        
        # Fill remaining NaNs if any (e.g. unknown strings) with median or drop
        # Let's drop them for regression
        print(f"Mapped 'gitaFamiliarity' to numeric. Valid N: {df['Outcome'].notna().sum()}")

    # If Outcome is still bad, we can't run regression.
    if df['Outcome'].nunique() < 2:
        print("Skipping regression: Outcome variable has insufficient variance or valid data.")
        return 0

    # Regression Steps
    # Step 1: Big 5 + Gender
    predictors_1 = [c for c in bfi_cols if c in df.columns]
    if 'Male' in df.columns: predictors_1.append('Male')
    
    X1 = sm.add_constant(df[predictors_1].dropna())
    # Align indices
    y = df.loc[X1.index, 'Outcome']
    
    model1 = sm.OLS(y, X1).fit()
    print(f"\nStep 1 R2 (Big5 + Gender): {model1.rsquared:.3f}")
    
    # Step 2: Add Gunas
    predictors_2 = predictors_1 + [c for c in guna_cols if c in df.columns]
    X2 = sm.add_constant(df[predictors_2].loc[X1.index]) # Ensure same rows
    
    model2 = sm.OLS(y, X2).fit()
    print(f"Step 2 R2 (+ Gunas): {model2.rsquared:.3f}")
    delta_r2 = model2.rsquared - model1.rsquared
    print(f"Delta R2: {delta_r2:.3f}")
    
    # Check significance of Gunas
    print("\nGuna Coefficients in Step 2:")
    print(model2.params[[c for c in guna_cols if c in df.columns]])
    print("P-values:")
    print(model2.pvalues[[c for c in guna_cols if c in df.columns]])
    
    return delta_r2

def main():
    import json
    import os
    
    data_tuple = load_and_prep_data()
    if not data_tuple:
        return
        
    df, item_cols, guna_choice, bfi_cols = data_tuple
    
    stats = {}
    stats['N'] = len(df)
    
    # Run Analyses
    if len(item_cols) > 5:
        fa, kmo = run_promax_efa(df, item_cols)
        stats['KMO'] = kmo
    else:
        print("Not enough items for EFA.")
        stats['KMO'] = 0
        
    stats['Max_Corr'] = check_correlations(df, guna_choice, bfi_cols)
    stats['Max_VIF'] = check_vif(df, guna_choice, bfi_cols)
    stats['Delta_R2'] = run_regression_defense(df, guna_choice, bfi_cols)
    
    # Save to JSON for workflow automation
    output_path = "c:/Users/donke/Desktop/IKS_Work/Gunabased Survey/student-assessment/analysis/data/defense_stats.json"
    try:
        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=4)
        print(f"\n✅ Stats saved to {output_path}")
    except Exception as e:
        print(f"\n⚠️ Could not save stats: {e}")

if __name__ == "__main__":
    main()
