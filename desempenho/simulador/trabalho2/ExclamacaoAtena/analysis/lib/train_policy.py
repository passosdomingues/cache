import csv
import sys
import os

def train_policy(csv_file, output_matrix="policy_matrix.csv"):
    print(f"Training policy from {csv_file}...")
    
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

    # Map headers to indices
    try:
        idx_state = headers.index('system_state_id')
        idx_policy = headers.index('active_policy')
        idx_occupancy = headers.index('total_occupancy')
    except ValueError as e:
        print(f"Error: Missing required columns. {e}")
        return

    # Q-Learning / Policy Improvement
    policy_map = {
        "LONGEST_QUEUE": 0,
        "SHORTEST_QUEUE": 1,
        "ROUND_ROBIN": 2,
        "STRICT_PRIORITY": 3,
        "MAX_AVG_WAIT": 4,
        "SALLES_UTILITY": 5, # Assuming these might appear
        "C_MU_RULE": 6,
        "WEIGHTED_ROUND_ROBIN": 7,
        "WHITTLE_INDEX": 8,
        "MARKOV_SWITCHING": 9, # Should not be a sub-policy choice usually
        "NONE": -1
    }
    
    # Aggregate rewards
    # Key: (state, policy_name), Value: [sum_occupancy, count]
    agg_data = {}
    
    max_state = 0
    
    for row in data:
        try:
            state = int(row[idx_state])
            policy = row[idx_policy]
            occupancy = float(row[idx_occupancy])
            
            if state > max_state:
                max_state = state
                
            key = (state, policy)
            if key not in agg_data:
                agg_data[key] = [0.0, 0]
            
            agg_data[key][0] += occupancy
            agg_data[key][1] += 1
            
        except ValueError:
            continue
            
    print("\nObserved Average Occupancy per (State, Policy):")
    
    # Find best policy per state
    best_policy_per_state = {}
    num_states = max_state + 1
    
    # Pre-fill with default (0)
    for s in range(num_states):
        best_policy_per_state[s] = 0
        
    for state in range(num_states):
        best_action = 0
        min_cost = float('inf')
        found_data = False
        
        for policy_name, policy_id in policy_map.items():
            key = (state, policy_name)
            if key in agg_data:
                avg_cost = agg_data[key][0] / agg_data[key][1]
                # print(f"State {state}, Policy {policy_name}: {avg_cost:.4f}")
                
                if avg_cost < min_cost:
                    min_cost = avg_cost
                    best_action = policy_id
                    found_data = True
        
        if found_data:
            best_policy_per_state[state] = best_action
            
    # Write to CSV
    with open(output_matrix, 'w') as f:
        f.write("state_id,policy_id\n")
        for state in range(num_states):
            policy_id = best_policy_per_state.get(state, 0)
            f.write(f"{state},{policy_id}\n")
            
    print(f"Saved optimized policy matrix to {output_matrix}")
    
    covered_states = set()
    for (s, p) in agg_data.keys():
        covered_states.add(s)
    print(f"Covered {len(covered_states)} states with data.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 train_policy.py <simulation_output.csv> [output_matrix.csv]")
    else:
        output = "policy_matrix.csv"
        if len(sys.argv) > 2:
            output = sys.argv[2]
        train_policy(sys.argv[1], output)
