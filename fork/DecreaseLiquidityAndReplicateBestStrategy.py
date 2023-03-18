import random
from pickhardtpayments.fork.Simulation import Simulation
from pickhardtpayments.fork.VisualNetworkRepresentation import VisualNetworkRepresentation
from pickhardtpayments.pickhardtpayments import ChannelGraph, OracleChannel, OracleLightningNetwork, \
    SyncSimulatedPaymentSession, UncertaintyNetwork, UncertaintyChannel


class DecreaseLiquidityAndReplicateBestStrategy:
    def __init__(self, snapshot_file: str = "preferential_attachment_1000.json"):
        self._snapshot_file = str(snapshot_file)
        self._channel_graph = ChannelGraph("SNAPSHOTS/" + self._snapshot_file)
        self._base = 20_000

    def run(self):
        # Extract the Highest Capacity Node (HCN)
        HCN = self._channel_graph.get_highest_capacity_nodes(1)[0]

        # Giving a name to the node that will replicate the strategy of HRN
        THIEF = "THIEF"

        # Run a simulation to extract who is the Highest Ratio Node (HRN)
        s1 = Simulation(self._channel_graph, self._base)
        s1.run_success_payments_simulation(
            payments_to_simulate=100,
            payments_amount=10_000,
            mu=10,
            base=self._base,
            distribution="uniform",
            dist_func="",
            verbose=False
        )

        # Extract the Highest Ratio Node (HRN) pub key
        HRN = s1.highest_ratio_nodes[0]

        # Create a node THIEF that replicates all the channels of the HRN but the liquidity of the THIEF is only on its side
        self.create_node_with_same_channels_and_entire_capacity_on_one_side(HRN, THIEF, s1.oracle_lightning_network)

        # ------------ everything good up to here -------------

        oracle = s1.oracle_lightning_network
        channel_graph = s1.channel_graph
        uncertaninty_network = s1.uncertainty_network

        # Close a number of channels of HCN such that the total liquidity of the closed channels corresponds
        # to the total liquidity of the new channels opened in the new node. This total corresponds to the expected_capacity(HRN)
        HRN_expected_liquidity = self._channel_graph.get_expected_capacity(HRN)

        print(f"\nHRN ({HRN}) expected capacity:", HRN_expected_liquidity)

        # Since the channels opened have the same capacity of the channels copied but the liquidity is only on one
        # side we need double of the expected liquidity of HRN
        capacity_to_remove_from_HCN = 2 * HRN_expected_liquidity
        print(f"\nThe capacity to remove from HCN ({HCN}) is {capacity_to_remove_from_HCN}")


        # Removing channels up to the amount of the capacity of the newly created node
        self.close_random_channels_up_to_amount(HCN, capacity_to_remove_from_HCN, s1.oracle_lightning_network)

        oracle = s1.oracle_lightning_network
        uncertaninty_network = UncertaintyNetwork(s1.channel_graph, self._base)
        channel_graph = s1.channel_graph



        s = SyncSimulatedPaymentSession(oracle=oracle, uncertainty_network=uncertaninty_network, prune_network=False)
        print()
        s.pickhardt_pay(THIEF, HCN, 100000, 0, 20_000, True)


        # Sending back half of the capacity of the channel to the original node, forcing the 1st hop of the routing
        # TODO: sending back half of the capacity to the original node

        self.send_back_money(THIEF, HCN, oracle, uncertaninty_network)

        v = VisualNetworkRepresentation(s1.channel_graph)
        v.show_network([HCN, HRN, THIEF])


        print(s1.payments_ratios_per_node)
        # print(s2.payments_ratios_per_node)

        return

    def send_back_money(self, src: str, dest: str, oracle: OracleLightningNetwork, uncertainty_network: UncertaintyNetwork):
        session = SyncSimulatedPaymentSession(oracle, uncertainty_network, False)
        src_neighbors = oracle.channel_graph.get_connected_nodes(src)
        for neighbor in src_neighbors:
            print("Sending to neighbor")
            amount_to_send = oracle.channel_graph.get_channel_without_short_channel_id(src, neighbor).capacity / 2

            for i in range(10):
                session.pickhardt_pay(src,
                                      neighbor,
                                      amount_to_send / 10,
                                      0,
                                      self._base,
                                      False
                                      )

        return

    def close_random_channels_up_to_amount(self, node: str, threshold_to_reach: float, oracle: OracleLightningNetwork):
        channels = self._channel_graph.get_connected_channels(node)
        liquidity_dict = {}
        for channel in channels:
            liquidity = oracle.get_liquidity(channel.src, channel.dest)
            liquidity_dict[channel.dest] = liquidity
        destinations = list(liquidity_dict.keys())
        random.shuffle(destinations)
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
            print(f"Channel from {node} to {dest} with liquidity {l} closed")
        return

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
