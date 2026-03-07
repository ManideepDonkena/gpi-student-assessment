import json
import os

def remove_dummy_data():
    files_to_clean = ["original_gpi_dump.json", "bfi44_cleaned.json"]
    
    for filename in files_to_clean:
        if not os.path.exists(filename):
            print(f"Skipping {filename} (not found)")
            continue
            
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            original_count = len(data)
            cleaned_data = []
            
            for session in data:
                demos = session.get('demographics', {})
                gender = demos.get('gender', '')
                occupation = demos.get('occupation', '') # Checking if this field exists
                
                # Check for the specific dummy condition
                # Note: 'Homemaker' might be in a different field if occupation isn't standard
                # But based on user request "working as home maker"
                
                if gender == 'Male' and occupation == 'Homemaker':
                    continue
                
                cleaned_data.append(session)
            
            removed_count = original_count - len(cleaned_data)
            
            if removed_count > 0:
                print(f"Removed {removed_count} dummy records from {filename}")
                with open(filename, 'w') as f:
                    json.dump(cleaned_data, f, indent=2)
            else:
                print(f"No dummy records found in {filename}")
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    remove_dummy_data()
