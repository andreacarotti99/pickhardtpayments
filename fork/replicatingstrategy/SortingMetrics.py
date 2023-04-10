import networkx as nx
from networkx import Graph, MultiDiGraph
from pickhardtpayments.pickhardtpayments import ChannelGraph, Channel
from math import log2 as log


def weight_function(u, v, channel: Channel, mu, amount):
    fee = int(channel.ppm * amount / 1000) + channel.base_fee
    print("(channel.capacity + 1 - amount) / (channel.capacity + 1) =",
          (channel.capacity + 1 - amount) / (channel.capacity + 1))
    print("-log(...) =", (-log((channel.capacity + 1 - amount) / (channel.capacity + 1))))
    print("mu * amount * fee =", mu * amount * fee)
    print((-log((channel.capacity + 1 - amount) / (channel.capacity + 1))) + mu * amount * fee)
    return (-log((channel.capacity + 1 - amount) / (channel.capacity + 1))) + mu * amount * fee


def assign_pickhardt_weights(channel_graph: ChannelGraph, mu, amount):
    G = channel_graph.network
    for u, v, keys, channel in G.edges(data="channel", keys=True):
        G[u][v][keys]['weight'] = weight_function(u, v, channel, mu, amount)


def assign_fee_and_cap_weight(channel_graph: ChannelGraph, amount):
    G = channel_graph.network
    for u, v, keys, channel in G.edges(data="channel", keys=True):
        G[u][v][keys]['channel_fee_weight'] = int(channel.ppm * amount / 1000) + channel.base_fee
        # print("fee: ", int(channel.ppm * amount / 1000) + channel.base_fee)
        G[u][v][keys]['channel_cap_weight'] = 1000 / channel.capacity
        # print("cap weight", 1000 / (channel.capacity))


def betwenness_weighted_cap_and_fee_dict(channel_graph: ChannelGraph, fee_weight: float, cap_weight: float):

    """
    takes the channel_graph and converts it from MultiDiGraph to DiGraph to compute the betwenness,
    the betwenness is computed using the capacity of the channels and the fee of the channels
    the values of the betwenness is normalized and then a weighted average is created

    """
    G = channel_graph.network

    # convert MultiDiGraph to Graph to compute betwenness centrality
    G_weighted = nx.DiGraph()
    for u, v, keys, channel in G.edges(data="channel", keys=True):
        G_weighted.add_edge(u, v,
                            channel_total_fee=G[u][v][keys]['channel_fee_weight'],
                            channel_cap_weight=G[u][v][keys]['channel_cap_weight'])

    bc_fee = nx.betweenness_centrality(G_weighted, weight='channel_fee_weight', normalized=True)
    bc_cap = nx.betweenness_centrality(G_weighted, weight='channel_cap_weight', normalized=True)

    # print("bc_fee", bc_fee.values())
    # print("bc_cap", bc_cap.values())

    combined_bc = {k: fee_weight * bc_fee[k] + cap_weight * bc_cap[k] for k in G_weighted.nodes}

    return combined_bc


def betwenness_pickhardt_weight_dict(channel_graph: ChannelGraph):
    standardGraph = nx.Graph(channel_graph.network)
    betweenness = nx.betweenness_centrality(standardGraph, weight='weight')
    node_betweenness = {node: betweenness[node] for node in standardGraph.nodes()}
    return node_betweenness


def compute_importance_for_each_node(channel_graph: ChannelGraph, amt: int):
    """
    amt: is the hypothetical amount sent in the payment
    returns a dict containing the importance of each node according to the metric:
    SUM_edges( (amt_to_send * ppm / 1000 + base_fee) * 1 / channel_capacity ) / num_of_edges
    """

    nodes_importance = {}

    for node in channel_graph.network.nodes:
        # print(f"importance for node {node}")
        sum_importance = 0
        connected_channels = channel_graph.get_connected_channels(node)

        for channel in connected_channels:
            # print(f"channel cap: {channel.capacity}")
            # print(f"channel ppm: {channel.ppm}")
            # print(f"channel base fee: {channel.base_fee}")
            sum_importance += (((channel.ppm * amt) / 1000) + channel.base_fee) * 1 / channel.capacity
        importance = sum_importance / len(connected_channels)
        nodes_importance[node] = importance
    return nodes_importance


def compute_avg_chan_cap_for_each_node(channel_graph: ChannelGraph):
    """
    returns a dictionary containing the average channel capacity of each node
    """
    # SUM_edges( (1 / (amt_to_send * ppm / 1000 + base_fee)) * channel_capacity ) / num_of_edges

    nodes_importance = {}

    for node in channel_graph.network.nodes:
        print(f"importance for node {node}")
        sum_importance = 0
        connected_channels = channel_graph.get_connected_channels(node)

        for channel in connected_channels:
            print(f"channel cap: {channel.capacity}")
            print(f"channel ppm: {channel.ppm}")
            print(f"channel base fee: {channel.base_fee}")
            sum_importance += channel.capacity / 2
        importance = sum_importance / len(connected_channels)
        nodes_importance[node] = importance
    return nodes_importance


def compute_edge_betweenness_for_each_node(G: Graph):
    ebc = nx.edge_betweenness_centrality(G)
    # bc_dict = {node: betweenness for node, betweenness in bc.items()}
    return ebc


def sort_dict_by_value_descending(my_dict: dict) -> []:
    return sorted(my_dict, key=lambda x: my_dict[x], reverse=True)


def sort_dict_by_value_ascending(my_dict: dict) -> []:
    return sorted(my_dict, key=lambda x: my_dict[x], reverse=False)
