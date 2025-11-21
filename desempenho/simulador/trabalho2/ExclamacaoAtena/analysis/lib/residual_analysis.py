import csv
import sys
import math

def analyze_residuals(csv_file):
    print(f"Loading data from {csv_file}...")
    
    data = []
    headers = []
    
    try:
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            for row in reader:
                if not row: continue
                data.append(row)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    try:
        idx_little = headers.index('little_error')
        idx_state = headers.index('system_state_id') if 'system_state_id' in headers else -1
        idx_policy = headers.index('active_policy') if 'active_policy' in headers else -1
    except ValueError as e:
        print(f"Error: Missing required columns. {e}")
        return

    residuals = []
    state_counts = {}
    policy_counts = {}
    
    for row in data:
        try:
            res = float(row[idx_little])
            residuals.append(res)
            
            if idx_state != -1:
                state = row[idx_state]
                state_counts[state] = state_counts.get(state, 0) + 1
                
            if idx_policy != -1:
                policy = row[idx_policy]
                policy_counts[policy] = policy_counts.get(policy, 0) + 1
                
        except ValueError:
            continue
            
    # Stats
    if residuals:
        mean_res = sum(residuals) / len(residuals)
        sq_diff = sum((x - mean_res)**2 for x in residuals)
        std_res = math.sqrt(sq_diff / len(residuals))
        
        print("\nLittle's Law Residuals Analysis:")
        print(f"Count: {len(residuals)}")
        print(f"Mean: {mean_res:.6f}")
        print(f"Std Dev: {std_res:.6f}")
        print(f"Min: {min(residuals):.6f}")
        print(f"Max: {max(residuals):.6f}")
    
    if state_counts:
        print("\nTop 5 Visited States:")
        sorted_states = sorted(state_counts.items(), key=lambda item: item[1], reverse=True)
        for s, c in sorted_states[:5]:
            print(f"State {s}: {c}")
            
    if policy_counts:
        print("\nActive Policy Distribution:")
        for p, c in policy_counts.items():
            print(f"{p}: {c}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 residual_analysis.py <simulation_output.csv>")
    else:
        analyze_residuals(sys.argv[1])
