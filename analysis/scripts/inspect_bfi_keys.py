import pandas as pd

try:
    df = pd.read_json("c:/Users/donke/Desktop/IKS_Work/Gunabased Survey/student-assessment/analysis/data/final_dataset_refined.json")
    print("Keys in first item of bigFiveItems:")
    if isinstance(df['bigFiveItems'].iloc[0], list) and len(df['bigFiveItems'].iloc[0]) > 0:
        print(df['bigFiveItems'].iloc[0][0].keys())
        print("First item content:")
        print(df['bigFiveItems'].iloc[0][0])
    else:
        print("bigFiveItems is not a non-empty list.")
except Exception as e:
    print(f"Error: {e}")
