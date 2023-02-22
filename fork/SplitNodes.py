import json
from heapq import nlargest

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
    node_ids = set(node["node_id"] for node in nodes)

    # Loop through the channels and split those connected to the nodes
    for channel in data["channels"]:
        if channel["source"] in node_ids:
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

    # Write the modified JSON file
    output = json_path + "_" + str(len(nodes)) + "_nodes_split"
    with open(output, "w") as file:
        json.dump(data, file, indent=2)


def main():
    file_name = "listchannels20220412.json"
    hcn = find_nodes_with_highest_capacity(file_name, 10)
    split_channels(hcn, file_name)
    return

if __name__ == "__main__":
    main()
