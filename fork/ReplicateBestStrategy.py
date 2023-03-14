from tqdm import tqdm

from pickhardtpayments.fork.ExportResults import ExportResults
from pickhardtpayments.fork.Simulation import Simulation
from pickhardtpayments.fork.VisualNetworkRepresentation import VisualNetworkRepresentation
from pickhardtpayments.pickhardtpayments import ChannelGraph, OracleLightningNetwork, OracleChannel
from pickhardtpayments.pickhardtpayments.ChannelGraph import generate_random_channel_id


class ReplicateBestStrategy:
    def __init__(self,
                 snapshot_file: str = "preferential_attachment_100.json",
                 payments_to_simulate: int = 1000,
                 payments_amount: int = 1000,
                 mu: int = 0,
                 base: int = 20_000,
                 distribution: str = "uniform",
                 dist_func: str = ""):
        self._snapshot_file = str(snapshot_file)
        self._payments_to_simulate = payments_to_simulate
        self._payments_amount = payments_amount
        self._mu = mu
        self._base = base
        self._distribution = distribution
        self._dist_func = dist_func
        self._channel_graph = ChannelGraph("SNAPSHOTS/" + self._snapshot_file)

    def run(self):

        highest_capacity_node = self._channel_graph.get_highest_capacity_nodes(5)[0]

        simulation_1 = Simulation(self._channel_graph, self._base)
        simulation_1.run_success_payments_simulation(self._payments_to_simulate, self._payments_amount, self._mu,
                                                     self._base, self._distribution, self._dist_func)

        # print(simulation_1.payments_fees_per_node)
        # print(simulation_1.payments_ratios_per_node)

        highest_ratio_node = self.get_node_with_highest_ratio(simulation_1.payments_ratios_per_node)

        exportResults_1 = ExportResults(simulation_1)
        exportResults_1.substitute_node_name(highest_ratio_node, 'HRN_' + highest_ratio_node)
        exportResults_1.substitute_node_name(highest_capacity_node, 'HCN_' + highest_capacity_node)
        exportResults_1.export_results("1")

        # 1) Initial network
        visualNetworkRepresentation = VisualNetworkRepresentation(self._channel_graph)
        visualNetworkRepresentation.show_network([highest_ratio_node, highest_capacity_node])

        # The liquidity is not yet set, after the creation of the channel the oracle is not set
        self.create_node_with_same_strategy(highest_ratio_node, "HCN_COPY",
                                            self._channel_graph.get_capacity(highest_capacity_node),
                                            simulation_1.oracle_lightning_network)

        print(self._channel_graph.network.nodes())

        # 2) Showing the network after creating the node with the same strategy but capacity of the highest ratio node
        visualNetworkRepresentation = VisualNetworkRepresentation(self._channel_graph)
        visualNetworkRepresentation.show_network([highest_ratio_node, "HCN_COPY", highest_capacity_node])

        self.remove_and_connect(highest_capacity_node, simulation_1.oracle_lightning_network)

        # 3) Showing the network after removing the real high capacity node
        visualNetworkRepresentation = VisualNetworkRepresentation(self._channel_graph)
        visualNetworkRepresentation.show_network([highest_ratio_node, "HCN_COPY"])

        simulation_2 = Simulation(self._channel_graph, self._base)
        simulation_2.run_success_payments_simulation(self._payments_to_simulate, self._payments_amount, self._mu,
                                                     self._base, self._distribution, self._dist_func)

        # print(simulation_2.routed_transactions_per_node)
        # print(simulation_2.payments_fees_per_node)
        # print(simulation_2.payments_ratios_per_node)

        exportResults_2 = ExportResults(simulation_2)
        exportResults_2.substitute_node_name(highest_ratio_node, 'HRN' + '_' + highest_ratio_node)
        exportResults_2.export_results("2")

        return

    def get_node_with_highest_ratio(self, d):
        """
        Given a dictionary `d`, returns the key with the highest value.
        If there are multiple keys with the same highest value, returns the first one encountered.
        """
        highest_value = max(d.values())
        for key, value in d.items():
            if value == highest_value:
                return key

    def create_node_with_same_strategy(self, node_to_copy, new_node_id, new_node_total_liquidity,
                                       oracle: OracleLightningNetwork):
        # We extract all the channels of the node considered
        connected_channels = self._channel_graph.get_connected_channels(node_to_copy)

        num_connected_channels = len(connected_channels)

        # We split the capacity of the copying node into the number of channels that the copied node has
        new_capacity_of_channels = new_node_total_liquidity / num_connected_channels

        for channel in connected_channels:
            channel_id = generate_random_channel_id()
            self._channel_graph.create_channel(
                new_node_id,
                channel.dest,
                channel.is_announced,
                new_capacity_of_channels,  # with channel.capacity we create a full copy of the copied node
                channel.flags, channel.is_active, channel.last_update, channel.base_fee, channel.ppm,
                channel.cltv_delta, channel.htlc_min_msat, channel.htlc_max_msat, channel_id
            )

            oracle_channel = OracleChannel(
                self._channel_graph.get_channel_without_short_channel_id(new_node_id, channel.dest),
                new_capacity_of_channels / 2
            )

            # Adding to the channel graph the edge
            self._channel_graph.network.add_edge(oracle_channel.src,
                                                 oracle_channel.dest,
                                                 key=channel_id,
                                                 channel=oracle_channel)

            oracle_channel_rev = OracleChannel(
                self._channel_graph.get_channel_without_short_channel_id(channel.dest, new_node_id),
                new_capacity_of_channels / 2
            )

            self._channel_graph.network.add_edge(oracle_channel_rev.src,
                                                 oracle_channel_rev.dest,
                                                 key=channel_id,
                                                 channel=oracle_channel_rev)

            oracle.network.add_edge(oracle_channel.src,
                                    oracle_channel.dest,
                                    key=channel_id,
                                    channel=oracle_channel)

            oracle.network.add_edge(oracle_channel_rev.src,
                                    oracle_channel_rev.dest,
                                    key=channel_id,
                                    channel=oracle_channel_rev)

        return

    def remove_and_connect(self, node, oracle: OracleLightningNetwork):
        neighbors = list(self._channel_graph.network.neighbors(node))
        print(f"Creating the clique: removing {node} and connecting neighbors...")
        for i in tqdm(range(len(neighbors))):
            channel_i_node = self._channel_graph.get_channel_without_short_channel_id(neighbors[i], node)
            for j in range(i + 1, len(neighbors)):
                channel_j_node = self._channel_graph.get_channel_without_short_channel_id(neighbors[j], node)

                liquidity_to_divide_i = oracle.get_liquidity(neighbors[i], node)
                new_liquidity_i = liquidity_to_divide_i / (
                        len(list(self._channel_graph.network.predecessors(node))) - 1)

                liquidity_to_divide_j = oracle.get_liquidity(neighbors[j], node)
                new_liquidity_j = liquidity_to_divide_j / (
                        len(list(self._channel_graph.network.predecessors(node))) - 1)

                self._channel_graph.create_channel(
                    channel_i_node.src,
                    channel_j_node.src,
                    channel_i_node.is_announced,
                    new_liquidity_i + new_liquidity_j,
                    channel_i_node.flags,
                    channel_i_node.is_active,
                    channel_i_node.last_update,
                    channel_i_node.base_fee,
                    channel_i_node.ppm,
                    channel_i_node.cltv_delta, channel_i_node.htlc_min_msat, channel_i_node.htlc_max_msat
                )

                oracle_channel = OracleChannel(
                    self._channel_graph.get_channel_without_short_channel_id(neighbors[i], neighbors[j]),
                    new_liquidity_i)
                chan_id = generate_random_channel_id()
                self._channel_graph.network.add_edge(oracle_channel.src,
                                                     oracle_channel.dest,
                                                     key=chan_id,
                                                     channel=oracle_channel)

                oracle_channel_rev = OracleChannel(
                    self._channel_graph.get_channel_without_short_channel_id(neighbors[j], neighbors[i]),
                    new_liquidity_j)
                self._channel_graph.network.add_edge(oracle_channel_rev.src,
                                                     oracle_channel_rev.dest,
                                                     key=chan_id,
                                                     channel=oracle_channel_rev)

        self._channel_graph.delete_node(node)
        return


replicateBestStrategy = ReplicateBestStrategy()
replicateBestStrategy.run()
