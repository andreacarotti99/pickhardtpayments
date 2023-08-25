import statistics

import networkx as nx

from pickhardtpayments.pickhardtpayments import ChannelGraph
from tqdm import tqdm


def compute_degrees_at_distance(G, radius: int):
    degrees_at_distance_x = {}
    for node in tqdm(G.nodes()):
        degrees_at_distance_x[node] = len(nx.ego_graph(G, node, radius=radius).nodes()) - 1
    return degrees_at_distance_x


def get_average_node_ppm_and_base_fee(channelGraph: ChannelGraph):
    """
    Returns two dictionary containing the avg ppm fee and the average base for each node
    Returns: dict_node_avg_ppm, dict_node_avg_base
    """
    node_avg_ppm = {}
    node_avg_base = {}
    for node in channelGraph.network.nodes:
        total_ppm = 0
        total_base = 0
        total_edges = 0
        connected_channels = channelGraph.get_connected_channels(node)
        for channel in connected_channels:
            total_ppm += channel.ppm
            total_base += channel.base_fee
            total_edges += 1
        node_avg_ppm[node] = total_ppm / total_edges if total_edges > 0 else 0
        node_avg_base[node] = total_base / total_edges if total_edges > 0 else 0
    return node_avg_ppm, node_avg_base

def get_median_node_ppm_and_base_fee(channelGraph: ChannelGraph):
    """
    Returns two dictionaries containing the median ppm fee and the median base fee for each node.
    Returns: dict_node_median_ppm, dict_node_median_base
    """
    dict_node_median_ppm = {}
    dict_node_median_base = {}
    for node in channelGraph.network.nodes:
        ppm_list = []
        base_list = []
        connected_channels = channelGraph.get_connected_channels(node)
        for channel in connected_channels:
            ppm_list.append(channel.ppm)
            base_list.append(channel.base_fee)
        dict_node_median_ppm[node] = statistics.median(ppm_list) if ppm_list else 0
        dict_node_median_base[node] = statistics.median(base_list) if base_list else 0
    return dict_node_median_ppm, dict_node_median_base
