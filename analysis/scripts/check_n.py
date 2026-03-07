import pandas as pd

try:
    df = pd.read_json("c:/Users/donke/Desktop/IKS_Work/Gunabased Survey/student-assessment/analysis/data/final_dataset_refined.json")
    print(f"Total Rows in Dataset: {len(df)}")
    
    if 'demographics' in df.columns:
        demog = pd.DataFrame(df['demographics'].tolist())
        print(f"Total Demographics Rows: {len(demog)}")
        print("Missing Gita Familiarity:", demog['gitaFamiliarity'].isna().sum())
        print("Gita Familiarity Counts:")
        print(demog['gitaFamiliarity'].value_counts(dropna=False))
except Exception as e:
    print(f"Error: {e}")
