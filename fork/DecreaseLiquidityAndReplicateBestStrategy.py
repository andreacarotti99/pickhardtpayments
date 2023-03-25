import random

from pickhardtpayments.fork.ExportResults import ExportResults
from pickhardtpayments.fork.Simulation import Simulation
from pickhardtpayments.fork.VisualNetworkRepresentation import VisualNetworkRepresentation
from pickhardtpayments.pickhardtpayments import ChannelGraph, OracleChannel, OracleLightningNetwork, SyncSimulatedPaymentSession, UncertaintyNetwork

# TODO: forcing the first hop of the send_back but by sending back the payment from the source (HRN) and not from the source neighbor's
class DecreaseLiquidityAndReplicateBestStrategy:
    def __init__(self, snapshot_file: str = "cosimo_19jan2023_converted.json"):
        self._snapshot_file = str(snapshot_file)
        self._channel_graph = ChannelGraph("SNAPSHOTS/" + self._snapshot_file)
        self._base = 20_000

    def run_detect_HRN(self):
        HCN = self._channel_graph.get_highest_capacity_nodes(1)[0]
        s1 = Simulation(self._channel_graph, self._base)
        s1.run_success_payments_simulation(
            payments_to_simulate=1000,
            payments_amount=10_000,
            mu=10,
            base=self._base,
            distribution="weighted_by_capacity",
            dist_func="linear",
            verbose=False
        )
        HRN = s1.highest_ratio_nodes[0]

        exportResults_1 = ExportResults(s1)
        exportResults_1.substitute_node_name(HRN, 'HRN' + '_' + HRN)
        exportResults_1.substitute_node_name(HCN, 'HCN' + '_' + HCN)
        exportResults_1.export_results("1")

        return

    def run_HRN_already_detected(self):
        HCN = self._channel_graph.get_highest_capacity_nodes(1)[0]
        HRN = "035d6f5b496f0a8bd3a05fb40b8bf7423afed11a8f2671a1980f6911b1be1685eb"

        o1 = OracleLightningNetwork(self._channel_graph)
        self.create_node_with_same_channels_and_entire_capacity_on_one_side(HRN, "THIEF", o1)
        HRN_expected_liquidity = self._channel_graph.get_expected_capacity(HRN)
        capacity_to_remove_from_HCN = 2 * HRN_expected_liquidity
        self.close_random_channels_up_to_amount(HCN, capacity_to_remove_from_HCN, o1)
        self._send_back_money_first_hop_forced(src="THIEF", dest=HCN, percentage_of_chan_cap_to_send=0.5, oracle=o1)

        s2 = Simulation(self._channel_graph, self._base)
        s2.run_success_payments_simulation(
            payments_to_simulate=1000,
            payments_amount=10_000,
            mu=10,
            base=self._base,
            distribution="weighted_by_capacity",
            dist_func="linear",
            verbose=False
        )

        exportResults_1 = ExportResults(s2)
        exportResults_1.substitute_node_name(HRN, 'HRN' + '_' + HRN)
        exportResults_1.substitute_node_name(HCN, 'HCN' + '_' + HCN)
        exportResults_1.export_results("2")

    def run(self):

        # self._channel_graph.transform_channel_graph_to_simpler(3000)

        HCN = self._channel_graph.get_highest_capacity_nodes(1)[0]

        THIEF = "THIEF"
        s1 = Simulation(self._channel_graph, self._base)
        s1.run_success_payments_simulation(
            payments_to_simulate=1000,
            payments_amount=10_000,
            mu=1000,
            base=self._base,
            distribution="weighted_by_capacity",
            dist_func="linear",
            verbose=False
        )

        # HRN = s1.highest_ratio_nodes[0]

        HRN = self._compute_best_performing_node(s1, routed_payment_threshold=10)


        exportResults_1 = ExportResults(s1)
        exportResults_1.substitute_node_name(HRN, 'HRN' + '_' + HRN)
        exportResults_1.substitute_node_name(HCN, 'HCN' + '_' + HCN)
        exportResults_1.export_results("1")

        self.create_node_with_same_channels_and_entire_capacity_on_one_side(HRN, THIEF, s1.oracle_lightning_network)
        HRN_expected_liquidity = self._channel_graph.get_expected_capacity(HRN)
        capacity_to_remove_from_HCN = 2 * HRN_expected_liquidity
        self.close_channels_up_to_amount(HCN, capacity_to_remove_from_HCN, s1.oracle_lightning_network)
        self._send_back_money_first_hop_forced(src=THIEF, dest=HCN, percentage_of_chan_cap_to_send=0.3, oracle=s1.oracle_lightning_network, mu=10)

        s2 = Simulation(self._channel_graph, self._base)  # Creates a new UncertaintyNetwork based on the channelGraph
        s2.run_success_payments_simulation(
            payments_to_simulate=1000,
            payments_amount=10_000,
            mu=1000,
            base=self._base,
            distribution="weighted_by_capacity",
            dist_func="linear",
            verbose=False
        )

        exportResults_2 = ExportResults(s2)
        exportResults_2.substitute_node_name(HRN, 'HRN' + '_' + HRN)
        exportResults_2.substitute_node_name(HCN, 'HCN' + '_' + HCN)
        exportResults_2.export_results("2")

        return

    def _compute_best_performing_node(self, simulation: Simulation, routed_payment_threshold: int):

        routed_payments_per_node = simulation.routed_transactions_per_node
        nodes_with_more_than_thres_routed_paym = {k: v for k, v in routed_payments_per_node.items() if v > routed_payment_threshold}
        for i, node in enumerate(simulation.highest_ratio_nodes):
            if node in nodes_with_more_than_thres_routed_paym:
                print(f"Best performing node is the {i} in the Highest Ratio Nodes")
                return node


    def _send_with_split(self, src: str, dest: str, amt: float, session: SyncSimulatedPaymentSession, mu: int):
        p = session.pickhardt_pay(src=src, dest=dest, amt=amt, mu=5, base=self._base, verbose=False)
        if not p.successful:
            self._send_with_split(src, dest, amt // 2, session, mu)
            self._send_with_split(src, dest, amt // 2, session, mu)

    def _send_back_money_first_hop_forced(self, src: str, dest: str, percentage_of_chan_cap_to_send: float,
                                          oracle: OracleLightningNetwork, mu: int = 5):
        assert 0 < percentage_of_chan_cap_to_send < 1

        uncertainty_network = UncertaintyNetwork(self._channel_graph, self._base)
        session = SyncSimulatedPaymentSession(oracle=oracle, uncertainty_network=uncertainty_network,
                                              prune_network=False)
        src_neighbors = self._channel_graph.get_connected_nodes(src)
        for i, neighbor in enumerate(src_neighbors):
            channel = self._channel_graph.get_channel_without_short_channel_id(src, neighbor)
            print(f"Attempting payment from src to neighbor {i + 1}/{len(src_neighbors)}")
            session.direct_payment(src=src, dest=neighbor, amount=(channel.capacity * percentage_of_chan_cap_to_send),
                                   oracle=oracle)

        for i, neighbor in enumerate(src_neighbors):
            channel = self._channel_graph.get_channel_without_short_channel_id(src, neighbor)
            print(f"Attempting payment from neighbor {i + 1}/{len(src_neighbors)} to dest")
            self._send_with_split(src=neighbor, dest=dest, amt=(channel.capacity * percentage_of_chan_cap_to_send), session=session, mu=mu)
        return

    def close_channels_up_to_amount(self, node: str, threshold_to_reach: float, oracle: OracleLightningNetwork):
        channels = self._channel_graph.get_connected_channels(node)

        # We create a dictionary storing {(dest: liquidity_to_dest), (...,...)} then we randomly extract destinations
        liquidity_dict = {}
        for channel in channels:
            liquidity = oracle.get_liquidity(channel.src, channel.dest)
            liquidity_dict[channel.dest] = liquidity

        # Depending on how we want to close the channels we sort the destinations (aka node connected) differently
        # destinations = self._sort_channels_randomly(liquidity_dict)
        destinations = self._sort_channels_by_increasing_capacity(liquidity_dict, oracle)

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
            l = oracle.get_liquidity(src=node, dest=dest)
            oracle.close_channel(src=node, dest=dest)

            self._remove_if_unreachable(dest, oracle)

            print(f"Channel from {node} to {dest} with liquidity {l} closed")
        return

    def _remove_if_unreachable(self, node: str, oracle: OracleLightningNetwork):
        if len(self._channel_graph.get_connected_nodes(node)) == 0:
            oracle.delete_node(node)

    def _sort_channels_randomly(self, liquidity_dict: dict()):
        destinations = list(liquidity_dict.keys())
        random.shuffle(destinations)
        return destinations

    def _sort_channels_by_increasing_capacity(self, liquidity_dict: dict(), oracle: OracleLightningNetwork):
        destinations = list(liquidity_dict.keys())
        capacity_dict = {}
        for d in destinations:
            capacity_dict[d] = oracle.get_total_actual_liquidity(d)
        sorted_capacity_dict = dict(sorted(capacity_dict.items(), key=lambda item: item[1]))
        # print(sorted_capacity_dict)
        sorted_capacity_dict_list = list(sorted_capacity_dict.keys())
        return sorted_capacity_dict_list

    def _generate_random_channel_id(self):
        rand1 = str(random.randint(100000, 999999))  # random 6-digit number
        rand2 = str(random.randint(1000, 9999))  # random 4-digit number
        rand3 = str(random.randint(1, 9))  # random 1-digit number
        return f"{rand1}x{rand2}x{rand3}"

    def create_node_with_same_channels_and_entire_capacity_on_one_side(self, node_to_copy: str, new_node_id: str,
                                                                       oracle: OracleLightningNetwork):
        """
        create a new node in the channel_graph with all the channels of a given node
        create new channels in the oracle with the entire capacity of the new channels on the side of the new node
        """

        connected_channels = self._channel_graph.get_connected_channels(node_to_copy)

        for channel in connected_channels:
            channel_id = self._generate_random_channel_id()
            self._channel_graph.create_channel(
                new_node_id,
                channel.dest,
                channel.is_announced,
                channel.capacity,  # with channel.capacity we create a full copy of the copied node
                channel.flags, channel.is_active, channel.last_update, channel.base_fee, channel.ppm,
                channel.cltv_delta, channel.htlc_min_msat, channel.htlc_max_msat, channel_id
            )

            oracle_channel = OracleChannel(
                self._channel_graph.get_channel_without_short_channel_id(new_node_id, channel.dest),
                channel.capacity  # The entire liquidity is on the side of the new node created
            )

            # Adding to the channel graph the edge
            self._channel_graph.network.add_edge(oracle_channel.src,
                                                 oracle_channel.dest,
                                                 key=channel_id,
                                                 channel=oracle_channel)

            oracle_channel_rev = OracleChannel(
                self._channel_graph.get_channel_without_short_channel_id(channel.dest, new_node_id),
                0
            )

            # adding edge to the channelGraph
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


decreaseLiquidityAndReplicateBestStrategy = DecreaseLiquidityAndReplicateBestStrategy()
decreaseLiquidityAndReplicateBestStrategy.run()
