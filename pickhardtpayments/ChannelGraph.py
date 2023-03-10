import json
import random
import time
import networkx as nx

from . import OracleLightningNetwork
from .Channel import Channel
from pickhardtpayments.fork.SplitNodes import *


class ChannelGraph:
    """
    Represents the public information about the Lightning Network that we see from Gossip and the 
    Bitcoin Blockchain. 

    The channels of the Channel Graph are directed and identified uniquely by a triple consisting of
    (source_node_id, destination_node_id, short_channel_id). This allows the ChannelGraph to also 
    contain parallel channels.
    """

    def _get_channel_json(self, filename: str):
        """
        extracts the dictionary from the file that contains lightning-cli listchannels json string
        """
        f = open(filename)
        return json.load(f)["channels"]

    def __init__(self, lightning_cli_listchannels_json_file: str):
        """
        Importing the channel_graph from core lightning listchannels command the file can be received by 
        #$ lightning-cli listchannels > listchannels.json

        """

        self._channel_graph = nx.MultiDiGraph()
        channels = self._get_channel_json(lightning_cli_listchannels_json_file)
        self._channels = channels
        for channel in channels:
            channel = Channel(channel)
            self._channel_graph.add_edge(
                channel.src, channel.dest, key=channel.short_channel_id, channel=channel)

    @property
    def network(self):
        return self._channel_graph

    def get_channel(self, src: str, dest: str, short_channel_id: str):
        """
        returns a specific channel object identified by source, destination and short_channel_id
        from the ChannelGraph
        """
        if self.network.has_edge(src, dest):
            if short_channel_id in self.network[src][dest]:
                return self.network[src][dest][short_channel_id]["channel"]

    def get_channel_without_short_channel_id(self, src: str, dest: str):
        """
        returns a specific channel object identified by source, destination but without short_channel_id
        from the ChannelGraph, the first channel_id between source and destination is picked
        """
        if self.network.has_edge(src, dest):
            first_short_channel_id = next(iter(self.network[src][dest]))
            return self.network[src][dest][first_short_channel_id]["channel"]

    def split_on_node_and_round(self, node, round_num):
        if round_num == 1:
            self.split_on_node(node)
            return
        else:
            nodes_to_split = [node]
            for i in range(round_num - 1):
                new_nodes = []
                for n in nodes_to_split:
                    new_nodes += [f"{n}_{j + 1}" for j in range(2)]
                nodes_to_split = new_nodes
            for n in nodes_to_split:
                self.split_on_node(n)

    def split_on_node(self, node):
        """
        node: the node you want to split from which you want to obtain two new nodes node_1 and node_2
        edit the channel graph by creating two new nodes with the same edges of the splitted node but with
        half of the capacity
        """
        try:
            node_is_present = self.network[node]
            print(f"Executing splitting on node {node}...")
        except Exception as e:
            print(f"Node {node} not found, split was not executed...")
            return

        # get the list of nodes
        predecessors = list(self.network.predecessors(node))

        for p in predecessors:
            # print(self.network[p][node])
            channel = self.get_channel_without_short_channel_id(p, node)
            rev_channel = self.get_channel_without_short_channel_id(node, p)

            # print(channel)
            # print(rev_channel)
            # print()

            # print(channel)

            channel_1 = {
                "source": str(p),
                "destination": str(node) + "_1",
                "short_channel_id": channel.short_channel_id + "_1",
                "public": channel.is_announced,
                "satoshis": channel.capacity // 2,
                "amount_msat": str((channel.capacity // 2) * 1000) + "msat",
                "message_flags": channel.flags,
                "channel_flags": channel.flags,
                "active": channel.is_active,
                "last_update": channel.last_update,
                "base_fee_millisatoshi": channel.base_fee,
                "fee_per_millionth": channel.ppm,
                "delay": channel.cltv_delta,
                "htlc_minimum_msat": channel.htlc_min_msat,
                "htlc_maximum_msat": channel.htlc_max_msat,
                "features": ""
            }

            channel_1_rev = {
                "source": str(node) + "_1",
                "destination": p,
                "short_channel_id": rev_channel.short_channel_id + "_1",
                "public": rev_channel.is_announced,
                "satoshis": rev_channel.capacity // 2,
                "amount_msat": str((rev_channel.capacity // 2) * 1000) + "msat",
                "message_flags": rev_channel.flags,
                "channel_flags": rev_channel.flags,
                "active": rev_channel.is_active,
                "last_update": rev_channel.last_update,
                "base_fee_millisatoshi": rev_channel.base_fee,
                "fee_per_millionth": rev_channel.ppm,
                "delay": rev_channel.cltv_delta,
                "htlc_minimum_msat": rev_channel.htlc_min_msat,
                "htlc_maximum_msat": rev_channel.htlc_max_msat,
                "features": ""
            }

            channel_2 = {
                "source": str(p),
                "destination": str(node) + "_2",
                "short_channel_id": channel.short_channel_id + "_2",
                "public": channel.is_announced,
                "satoshis": channel.capacity // 2,
                "amount_msat": str((channel.capacity // 2) * 1000) + "msat",
                "message_flags": channel.flags,
                "channel_flags": channel.flags,
                "active": channel.is_active,
                "last_update": channel.last_update,
                "base_fee_millisatoshi": channel.base_fee,
                "fee_per_millionth": channel.ppm,
                "delay": channel.cltv_delta,
                "htlc_minimum_msat": channel.htlc_min_msat,
                "htlc_maximum_msat": channel.htlc_max_msat,
                "features": ""
            }

            channel_2_rev = {
                "source": str(node) + "_2",
                "destination": p,
                "short_channel_id": rev_channel.short_channel_id + "_2",
                "public": rev_channel.is_announced,
                "satoshis": rev_channel.capacity // 2,
                "amount_msat": str((rev_channel.capacity // 2) * 1000) + "msat",
                "message_flags": rev_channel.flags,
                "channel_flags": rev_channel.flags,
                "active": rev_channel.is_active,
                "last_update": rev_channel.last_update,
                "base_fee_millisatoshi": rev_channel.base_fee,
                "fee_per_millionth": rev_channel.ppm,
                "delay": rev_channel.cltv_delta,
                "htlc_minimum_msat": rev_channel.htlc_min_msat,
                "htlc_maximum_msat": rev_channel.htlc_max_msat,
                "features": ""
            }

            channel_1 = Channel(channel_1)
            channel_1_rev = Channel(channel_1_rev)

            channel_2 = Channel(channel_2)
            channel_2_rev = Channel(channel_2_rev)

            self.network.add_edge(
                channel_1.src, channel_1.dest, key=channel_1.short_channel_id, channel=channel_1)
            self.network.add_edge(
                channel_1_rev.src, channel_1_rev.dest, key=channel_1_rev.short_channel_id, channel=channel_1_rev)
            self.network.add_edge(
                channel_2.src, channel_2.dest, key=channel_2.short_channel_id, channel=channel_2)
            self.network.add_edge(
                channel_2_rev.src, channel_2_rev.dest, key=channel_2_rev.short_channel_id, channel=channel_2_rev)

            self.network.remove_edge(channel.src, channel.dest, key=channel.short_channel_id)
            self.network.remove_edge(channel.dest, channel.src, key=channel.short_channel_id)

        self.network.remove_node(node)

    def get_highest_capacity_nodes(self, n=10):
        """
        n: is the number of highest capacity nodes you want to retrieve
        returns the list of the n highest capacity nodes from the highest capacity to the lowest capacity
        """
        channels = self._channels
        # Create a dictionary to store the capacity of each node
        capacities = {}
        # Loop through each channel in the JSON data
        for channel in channels:
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

    def get_closest_half_capacity_node(self, node):
        oracle = OracleLightningNetwork(self._channel_graph)
        node_capacities = oracle.nodes_capacities()
        node_capacity = self.get_original_capacity(node) / 2

        closest_node = None
        min_difference = float('inf')
        for n, cap in node_capacities.items():
            difference = abs(cap - node_capacity)
            if difference < min_difference:
                closest_node = n
                min_difference = difference
        return closest_node

    def get_closest_half_capacity_node_by_round(self, node, round_num):

        oracle = OracleLightningNetwork(self._channel_graph)
        node_capacities = oracle.nodes_capacities()
        node_capacity = self.get_original_capacity(node) / (2 ** round_num)

        closest_node = None
        min_difference = float('inf')
        for n, cap in node_capacities.items():
            difference = abs(cap - node_capacity)
            if difference < min_difference:
                closest_node = n
                min_difference = difference
        return closest_node

    def get_connected_nodes(self, node):
        return list(self.network.successors(node))

    def create_channel(self, source, dest, is_announced, total_capacity_of_channel, flags, is_active, last_update, base_fee, ppm,
                       cltv_delta, htlc_min_msat, htlc_max_msat):

        channel_id = generate_random_channel_id()

        channel = {
            "source": str(source),
            "destination": str(dest),
            "short_channel_id": channel_id,
            "public": is_announced,
            "satoshis": total_capacity_of_channel,
            "amount_msat": str((total_capacity_of_channel) * 1000) + "msat",
            "message_flags": flags,
            "channel_flags": flags,
            "active": is_active,
            "last_update": last_update,
            "base_fee_millisatoshi": base_fee,
            "fee_per_millionth": ppm,
            "delay": cltv_delta,
            "htlc_minimum_msat": htlc_min_msat,
            "htlc_maximum_msat": htlc_max_msat,
            "features": ""
        }

        channel_rev = {
            "source": str(dest),
            "destination": str(source),
            "short_channel_id": channel_id,
            "public": is_announced,
            "satoshis": total_capacity_of_channel,
            "amount_msat": str((total_capacity_of_channel) * 1000) + "msat",
            "message_flags": flags,
            "channel_flags": flags,
            "active": is_active,
            "last_update": last_update,
            "base_fee_millisatoshi": base_fee,
            "fee_per_millionth": ppm,
            "delay": cltv_delta,
            "htlc_minimum_msat": htlc_min_msat,
            "htlc_maximum_msat": htlc_max_msat,
            "features": ""
        }

        channel = Channel(channel)
        channel_rev = Channel(channel_rev)

        self.network.add_edge(
            channel.src, channel.dest, key=channel.short_channel_id, channel=channel)
        self.network.add_edge(
            channel_rev.src, channel_rev.dest, key=channel_rev.short_channel_id, channel=channel_rev)

        return

    def get_connected_channels(self, node):
        """
        returns a list of the channels of the given node (ONLY ONE SIDE OF THE CHANNELS SO HALF OF THE CAPACITY)
        """

        connected_nodes = self.get_connected_nodes(node)
        channels = []
        for dst in connected_nodes:
            channels.append(self.get_channel_without_short_channel_id(node, dst))
        return channels

    def get_nodes_capacities(self):
        """ compute the capacities for each node in the graph and returns a dictionary with the nodes and their capacity"""
        nodes_capacities = {}
        for src, dest, channel in self.network.edges(data="channel"):
            if src in nodes_capacities:
                nodes_capacities[src] += channel.capacity // 2
            else:
                nodes_capacities[src] = channel.capacity // 2
        return nodes_capacities

    def get_capacity(self, node):
        return self.get_nodes_capacities()[node]

def generate_random_channel_id():
    rand1 = str(random.randint(100000, 999999))  # random 6-digit number
    rand2 = str(random.randint(1000, 9999))  # random 4-digit number
    rand3 = str(random.randint(1, 9))  # random 1-digit number
    return f"{rand1}x{rand2}x{rand3}"


