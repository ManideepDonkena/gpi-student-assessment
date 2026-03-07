import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

try:
    df = pd.read_json("c:/Users/donke/Desktop/IKS_Work/Gunabased Survey/student-assessment/analysis/data/final_dataset_refined.json")
    print("All Columns in dataset:")
    print(list(df.columns))
except Exception as e:
    print(f"Error reading file: {e}")
