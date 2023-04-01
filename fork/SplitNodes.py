import json
from heapq import nlargest
from tqdm import tqdm


def find_nodes_with_highest_capacity(file_name, n=10):

    with open(file_name, "r") as file:
        json_string = file.read()

        # Parse the JSON string into a dictionary
        data = json.loads(json_string)

        # Create a dictionary to store the capacity of each node
        capacities = {}

        # Loop through each channel in the JSON data
        for channel in data["channels"]:
            # Calculate the capacity of the source node for this channel
            capacity = channel["satoshis"] / 2
            source_node = channel["source"]

            # Add the capacity to the dictionary for the source node
            if source_node in capacities:
                capacities[source_node] += capacity
            else:
                capacities[source_node] = capacity

        # Find the top n nodes with the highest capacity
        top_nodes = nlargest(n, capacities, key=capacities.get)

    return top_nodes

def split_channels(nodes, json_path):
    # Load the JSON file
    with open(json_path, "r") as file:
        data = json.load(file)

    # Create a set of node IDs to look for
    nodes_set = set(nodes)

    # Loop through the channels and split those connected to the nodes
    for channel in tqdm(data["channels"]):
        if channel["source"] in nodes_set:
            # Create two new channels with half the satoshis and amount_msat
            channel_1 = channel.copy()
            channel_1["source"] += "_1"
            channel_1["satoshis"] //= 2
            channel_1["amount_msat"] = str(int(channel_1["amount_msat"][:-4]) // 2) + "msat"

            channel_2 = channel.copy()
            channel_2["source"] += "_2"
            channel_2["satoshis"] //= 2
            channel_2["amount_msat"] = str(int(channel_2["amount_msat"][:-4]) // 2) + "msat"

            # Replace the original channel with the two new ones
            data["channels"].remove(channel)
            data["channels"].append(channel_1)
            data["channels"].append(channel_2)

    return data

def export_file(data, file_name, nodes):
    output = file_name[:-5] + "_" + str(len(nodes)) + "_nodes_split.json"
    with open(output, "w") as file:
        json.dump(data, file, indent=2)

def main():
    file_name = "pickhardt_12apr2022_fixed.json"
    file_path = "SNAPSHOTS/" + file_name
    number_of_nodes_to_split = 10
    hcn = find_nodes_with_highest_capacity(file_path, number_of_nodes_to_split)
    print(f"Splitting the first {number_of_nodes_to_split} nodes (capacity):")
    print(hcn)
    data = split_channels(hcn, file_path)
    export_file(data, file_name, hcn)
    print("Split successful new json was generated...")
    return

if __name__ == "__main__":
    main()
