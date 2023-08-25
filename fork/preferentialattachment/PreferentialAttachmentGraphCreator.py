import json
import networkx as nx
import random
from matplotlib import pyplot as plt
from tqdm import tqdm


def create_preferential_attachment_graph(num_of_nodes: int):
    # Create an empty graph
    G = nx.Graph()
    # Add the first two nodes with an edge between them
    G.add_node(0)
    G.add_node(1)
    G.add_edge(0, 1)
    # Add the remaining n-2 nodes
    for i in tqdm(range(2, num_of_nodes)):
        # Compute the sum of degrees of all nodes in the graph
        degree_sum = sum(dict(G.degree()).values())
        # Create a list of nodes and their corresponding degrees
        node_degrees = [(node, degree) for node, degree in G.degree()]
        # Compute the probability of adding the new node to each existing node
        probabilities = [degree / degree_sum for node, degree in node_degrees]
        # Use the probabilities to select a node to connect to
        selected_node = random.choices(population=list(range(len(node_degrees))), weights=probabilities)[0]
        # Add the new node to the graph and connect it to the selected node
        G.add_node(i)
        G.add_edge(i, node_degrees[selected_node][0])
    return G


def create_snapshot(G, fee_base_msat: int = 1000, fee_ppm: int = 24, capacity_sat: int = 2_000_000):
    # create a list of channels
    channels = []

    for u, v in G.edges():
        short_channel_id = str(random.randint(100000000000000000, 999999999999999999))
        channel_uv = {
            "source": str(u),
            "destination": str(v),
            "short_channel_id": short_channel_id,
            "public": True,
            "satoshis": capacity_sat,
            "amount_msat": str(capacity_sat) + "000msat",
            "message_flags": 1,
            "channel_flags": 0,
            "active": True,
            "last_update": 0000000000,
            "base_fee_millisatoshi": fee_base_msat,
            "fee_per_millionth": fee_ppm,
            "delay": 144,
            "htlc_minimum_msat": "1000msat",
            "htlc_maximum_msat": "100000000msat",
            "features": ""
        }
        channels.append(channel_uv)

        # create a channel from v to u
        channel_vu = {
            "source": str(v),
            "destination": str(u),
            "short_channel_id": short_channel_id,
            "public": True,
            "satoshis": capacity_sat,
            "amount_msat": str(capacity_sat) + "000msat",
            "message_flags": 1,
            "channel_flags": 0,
            "active": True,
            "last_update": 0000000000,
            "base_fee_millisatoshi": fee_base_msat,
            "fee_per_millionth": fee_ppm,
            "delay": 144,
            "htlc_minimum_msat": "1000msat",
            "htlc_maximum_msat": "100000000msat",
            "features": ""
        }
        channels.append(channel_vu)

    # create a dictionary with the channels list
    json_data = {"channels": channels}

    # serialize the dictionary to a JSON string and print it
    with open('preferential_attachment_' + str(G.number_of_nodes()) + '.json', 'w') as f:
        json.dump(json_data, f, indent=4)

    return


random.seed(1)
G = create_preferential_attachment_graph(num_of_nodes=1000)
create_snapshot(G)

# Illustrating the graph G created in matplotlib
pos = nx.spring_layout(G)
node_sizes = [v * 5 for v in dict(G.degree()).values()]  # multiply the degree of the node by 10 to get the size of the node
nx.draw(G, pos, node_color='blue', node_size=node_sizes, edge_color='gray', width=0.3)
plt.show()
