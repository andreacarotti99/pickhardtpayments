"""
Now we try to observe what happens when low-ratio nodes try to replicate highest-ratio nodes:
if I am a low-ratio node with a given capacity x, I search for a node in the high ratio node list that has the closer
lower capacity compared to mine, then I try to replicate its channels and closing mine keeping the same total liquidity
"""
import pandas as pd


# Save into a df the csv with the results of the nodes performance
df = pd.read_csv('../RESULTS/simplifiednetworksimulations/labeled_results_1000trans_10000SAT_1000mu_distunif_amountdistfixe_1.csv')

# Save into a list the lowest roi nodes
low_roi_nodes = df.loc[df['ROI'] == 'LOW', 'node'].tolist()

# Save into a DF the highest roi nodes
high_roi_nodes = df.loc[df['ROI'] == 'HIGH']


for agent in low_roi_nodes:
    agent_capacity = df.loc[df['node'] == agent, 'capacity'].iloc[0]
    lower_capacity_nodes_than_agent = high_roi_nodes.loc[high_roi_nodes['capacity'] <= agent_capacity]
    sorted_lower_capacity_nodes_than_agent = lower_capacity_nodes_than_agent.sort_values(by='capacity', ascending=False)

    if not sorted_lower_capacity_nodes_than_agent.empty:
        highest_capacity_node_closer_to_agent = sorted_lower_capacity_nodes_than_agent.iloc[0]['node']

        print(f"node {agent[0:4]}.. cap: {agent_capacity} repl. node {highest_capacity_node_closer_to_agent[0:4]}.. cap: {sorted_lower_capacity_nodes_than_agent.iloc[0]['capacity']}")
    else:
        print("No nodes with 'HIGH' ROI value and lower capacity than node '{}'.".format(agent))


