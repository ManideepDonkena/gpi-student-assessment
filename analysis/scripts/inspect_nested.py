import pandas as pd
pd.set_option('display.max_colwidth', None)

try:
    df = pd.read_json("c:/Users/donke/Desktop/IKS_Work/Gunabased Survey/student-assessment/analysis/data/final_dataset_refined.json")
    print("recalculated_guna (First Row):")
    print(df['recalculated_guna'].iloc[0])
    print("\nrecalculated_bfi (First Row):")
    print(df['recalculated_bfi'].iloc[0])
except Exception as e:
    print(f"Error: {e}")
