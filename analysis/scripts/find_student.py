import json

def find_student():
    with open("bfi44_cleaned.json", "r") as f:
        data = json.load(f)
        
    print(f"Total records in BFI-44 Cleaned JSON: {len(data)}")
    
    found_count = 0
    tamas_threshold = 5.0
    
    print(f"\nSearching for Candidates: Male, Age 19, Tamas > {tamas_threshold}...")
    
    for i, s in enumerate(data):
        # Safely get values
        guna = s.get('recalculated_guna', {})
        tamas = guna.get('Tamas', 0)
        
        demos = s.get('demographics', {})
        age = demos.get('age', 'Unknown')
        gender = demos.get('gender', 'Unknown')
        
        time = s.get('time_guna_min', 0)
        
        # Check Candidate (Looser Match)
        if gender == 'Male' and str(age) == '19' and tamas > tamas_threshold:
            print(f"\n✅ CANDIDATE Match at Index {i} (ID {i+1}):")
            print(f"  - Tamas: {tamas:.4f}")
            print(f"  - Time: {time:.2f} min")
            print(f"  - Age: {age}")
            found_count += 1
            
    if found_count == 0:
        print("\n❌ No candidates found.")
        # Debug: Print top 5 highest Tamas scores to see what's going on
        print("\n--- Top 5 Highest Tamas Scores ---")
        sorted_data = sorted(data, key=lambda x: x.get('recalculated_guna', {}).get('Tamas', 0), reverse=True)
        for j in range(min(5, len(sorted_data))):
             s = sorted_data[j]
             t = s.get('recalculated_guna', {}).get('Tamas', 0)
             a = s.get('demographics', {}).get('age')
             g = s.get('demographics', {}).get('gender')
             print(f"Rank {j+1}: Tamas={t:.4f}, Age={a}, Gender={g}")

if __name__ == "__main__":
    find_student()
