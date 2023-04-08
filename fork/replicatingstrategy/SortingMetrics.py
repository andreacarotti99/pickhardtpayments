import networkx as nx
from networkx import Graph

from pickhardtpayments.pickhardtpayments import ChannelGraph


def compute_importance_for_each_node(channel_graph: ChannelGraph, amt: int):

    """
    returns a dict containing the importance of each node according to the metric:
    SUM_edges( (1 / (amt_to_send * ppm / 1000 + base_fee)) * channel_capacity ) / num_of_edges
    """

    nodes_importance = {}

    for node in channel_graph.network.nodes:
        print(f"importance for node {node}")
        sum_importance = 0
        connected_channels = channel_graph.get_connected_channels(node)

        for channel in connected_channels:
            print(f"channel cap: {channel.capacity}")
            print(f"channel ppm: {channel.ppm}")
            print(f"channel base fee: {channel.base_fee}")
            sum_importance += (1 / (((channel.ppm * amt)/1000)+channel.base_fee)) * channel.capacity
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


def sort_dict_by_value_descending(my_dict: dict):
    return sorted(my_dict, key=lambda x: my_dict[x], reverse=True)


