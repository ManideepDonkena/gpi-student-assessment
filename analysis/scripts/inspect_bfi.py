import pandas as pd
pd.set_option('display.max_colwidth', None)

try:
    df = pd.read_json("c:/Users/donke/Desktop/IKS_Work/Gunabased Survey/student-assessment/analysis/data/final_dataset_refined.json")
    print("bigFiveItems (First Row):")
    print(df['bigFiveItems'].iloc[0])
except Exception as e:
    print(f"Error: {e}")
