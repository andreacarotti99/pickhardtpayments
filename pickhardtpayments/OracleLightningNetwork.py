from typing import List

from .ChannelGraph import ChannelGraph
from .OracleChannel import OracleChannel
import networkx as nx

DEFAULT_BASE_THRESHOLD = 0


class OracleLightningNetwork(ChannelGraph):


    def __init__(self, channel_graph: ChannelGraph):
        self._channel_graph = channel_graph
        self._network = nx.MultiDiGraph()
        for src, dest, short_channel_id, channel in channel_graph.network.edges(data="channel", keys=True):
            oracle_channel = None

            # If Channel in opposite direction already exists with liquidity information match the channel
            if self._network.has_edge(dest, src):
                if short_channel_id in self._network[dest][src]:
                    capacity = channel.capacity
                    opposite_channel = self._network[dest][src][short_channel_id]["channel"]
                    opposite_liquidity = opposite_channel.actual_liquidity
                    oracle_channel = OracleChannel(
                        channel, capacity - opposite_liquidity)

            if oracle_channel is None:
                oracle_channel = OracleChannel(channel)

            self._network.add_edge(oracle_channel.src,
                                   oracle_channel.dest,
                                   key=short_channel_id,
                                   channel=oracle_channel)

    @property
    def network(self):
        return self._network

    @property
    def channel_graph(self):
        return self._channel_graph

    def send_onion(self, path, amt):
        """

        :rtype: object
        """
        for channel in path:
            oracle_channel = self.get_channel(
                channel.src, channel.dest, channel.short_channel_id)
            success_of_probe = oracle_channel.can_forward(
                channel.in_flight + amt)
            # print(channel,amt,success_of_probe)
            channel.update_knowledge(amt, success_of_probe)
            if not success_of_probe:
                return False, channel
        return True, None


    def theoretical_maximum_payable_amount(self, source: str, destination: str, base_fee: int = DEFAULT_BASE_THRESHOLD):
        """
        Uses the information from the oracle to compute the min-cut between source and destination

        This is only useful for experiments and simulations if one wants to know what would be 
        possible to actually send before starting the payment loop
        """
        test_network = nx.DiGraph()
        for src, dest, channel in self.network.edges(data="channel"):
            # liquidity = 0
            # for channel in channels:
            if channel.base_fee > base_fee:
                continue
            liquidity = self.get_channel(
                src, dest, channel.short_channel_id).actual_liquidity
            if liquidity > 0:
                if test_network.has_edge(src, dest):
                    test_network[src][dest]["capacity"] += liquidity
                else:
                    test_network.add_edge(src,
                                          dest,
                                          capacity=liquidity)

        mincut, _ = nx.minimum_cut(test_network, source, destination)
        return mincut

    def settle_payment(self, path: List[OracleChannel], payment_amount: int):
        """
        receives a List of channels and payment amount and adjusts the balances of the channels along the path.

        settle_payment should only be called after all send_onions for a payment terminated successfully!
        # TODO testing
        """
        for channel in path:
            settlement_channel = self.get_channel(channel.src, channel.dest, channel.short_channel_id)
            return_settlement_channel = self.get_channel(channel.dest, channel.src, channel.short_channel_id)

            # print(settlement_channel)
            # print(return_settlement_channel)


            if settlement_channel.actual_liquidity > payment_amount:
                # decrease channel balance in sending channel by amount
                settlement_channel.actual_liquidity = settlement_channel.actual_liquidity - payment_amount
                # increase channel balance in the other direction by amount
                return_settlement_channel.actual_liquidity = return_settlement_channel.actual_liquidity + payment_amount
            else:
                raise Exception("""Channel liquidity on Channel {} is lower than payment amount.
                    \nPayment cannot settle.""".format(channel.short_channel_id))
        return 0

    def get_liquidity(self, src: str, dest: str):
        channel = self.get_channel_without_short_channel_id(src, dest)
        # print(channel)
        return channel.actual_liquidity

    def set_liquidity(self, src: str, dest: str, new_liquidity: float):
        """
        the liquidity between two nodes A and B is set such that if the total capacity of the channel is C and the new
        liquidity from A to B is L then in the oracle liquidity(A->B) = L and liquidity(B->A) = C - L
        """
        channel = self._channel_graph.get_channel_without_short_channel_id(src=src, dest=dest)
        rev_channel = self._channel_graph.get_channel_without_short_channel_id(src=dest, dest=src)
        if new_liquidity > channel.capacity:
            print("The new liquidity exceeds the channel capacity, liquidity not set")
            return
        else:
            channel.actual_liquidity = new_liquidity
            rev_channel.actual_liquidity = channel.capacity - new_liquidity

    def get_total_actual_liquidity(self, node: str):
        neighbors = self._channel_graph.get_connected_nodes(node=node)
        # print(neighbors)
        total_actual_liquidity = 0
        for neighbor in neighbors:
            total_actual_liquidity += self.get_liquidity(node, neighbor)
        return total_actual_liquidity

    def close_channel(self, src: str, dest: str):
        """
        closes all the channels btw src and dest
        IMPORTANT: both the channels in the ORACLE and in the CHANNELGRAPH are closed! (not just in one of the two)
        """
        if self.network.has_edge(src, dest):
            edge_keys = list(self.network[src][dest].keys())
            for edge_key in edge_keys:
                self.network.remove_edge(src, dest, edge_key)
                self.network.remove_edge(dest, src, edge_key)
                self._channel_graph.network.remove_edge(src, dest, edge_key)
                self._channel_graph.network.remove_edge(dest, src, edge_key)
        else:
            print(f"No edges between {src} and {dest}, 0 channels were closed")
        return

    def delete_node(self, node):
        """
        remove the node and all its channels from the OracleLightningNetwork and from ChannelGraph
        """
        try:
            node_is_present = self.network[node]
            print(f"Removing node: {node} from Oracle...")
        except Exception as e:
            print(f"Node {node} not found...")
            return
        predecessors = list(self.network.predecessors(node))
        for p in predecessors:
            channel = self.get_channel_without_short_channel_id(p, node)
            rev_channel = self.get_channel_without_short_channel_id(node, p)
            # print(channel)
            # print(rev_channel)

            self._channel_graph.network.remove_edge(channel.src, channel.dest, key=channel.short_channel_id)
            self._channel_graph.network.remove_edge(rev_channel.src, rev_channel.dest, key=rev_channel.short_channel_id)
            self.network.remove_edge(channel.src, channel.dest, key=channel.short_channel_id)
            self.network.remove_edge(rev_channel.src, rev_channel.dest, key=rev_channel.short_channel_id)
        self.network.remove_node(node)
        self._channel_graph.delete_node(node)
        return

    def print_node_info(self, node: str):
        try:
            node_is_present = self.network[node]
            print(f"Channels of node: {node}")
            successors = list(self.network.successors(node))

            for p in successors:
                channel = self.get_channel_without_short_channel_id(node, p)
                print(f"|___ {p}: liquidity: {channel.actual_liquidity}/{channel.capacity}")
        except Exception as e:
            print(e)
            print(f"Node {node} not found...")
            return
        return

    def _sort_channels_by_increasing_capacity(self, liquidity_dict: dict()):
        destinations = list(liquidity_dict.keys())
        capacity_dict = {}
        for d in destinations:
            capacity_dict[d] = self.get_total_actual_liquidity(d)
        sorted_capacity_dict = dict(sorted(capacity_dict.items(), key=lambda item: item[1]))
        # print(sorted_capacity_dict)
        sorted_capacity_dict_list = list(sorted_capacity_dict.keys())
        return sorted_capacity_dict_list

    def _remove_if_unreachable(self, node: str):
        if len(self._channel_graph.get_connected_nodes(node)) == 0:
            self.delete_node(node)
        return

    def close_channels_up_to_amount(self, node: str, threshold_to_reach: float):
        channels = self._channel_graph.get_connected_channels(node)
        # We create a dictionary storing {(dest: liquidity_to_dest), (...,...)} then we randomly extract destinations
        liquidity_dict = {}
        for channel in channels:
            liquidity = self.get_liquidity(channel.src, channel.dest)
            liquidity_dict[channel.dest] = liquidity
        # Depending on how we want to close the channels we sort the destinations (aka node connected) differently
        # destinations = self._sort_channels_randomly(liquidity_dict)
        destinations = self._sort_channels_by_increasing_capacity(liquidity_dict)
        result = []
        total = 0
        for d in destinations:
            channel_liquidity = liquidity_dict[d]
            if total + channel_liquidity >= threshold_to_reach:
                result.append(d)
                break
            result.append(d)
            total += channel_liquidity
        for dest in result:
            l = self.get_liquidity(src=node, dest=dest)
            self.close_channel(src=node, dest=dest)
            self._remove_if_unreachable(dest)
            print(f"Channel from {node} to {dest} with liquidity {l} closed")
        return
