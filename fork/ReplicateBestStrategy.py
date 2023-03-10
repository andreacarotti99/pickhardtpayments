import networkx as nx
from matplotlib import pyplot as plt
from pickhardtpayments.fork.Simulation import Simulation
from pickhardtpayments.pickhardtpayments import ChannelGraph


class ReplicateBestStrategy:
    def __init__(self,
                 snapshot_file: str = "preferential_attachment_10.json",
                 payments_to_simulate: int = 300,
                 payments_amount: int = 1000,
                 mu: int = 0,
                 base: int = 20_000,
                 distribution: str = "uniform",
                 dist_func=str):
        self._snapshot_file = str(snapshot_file)
        self._payments_to_simulate = payments_to_simulate
        self._payments_amount = payments_amount
        self._mu = mu
        self._base = base
        self._distribution = distribution
        self._dist_func = dist_func

        self._channel_graph = ChannelGraph("SNAPSHOTS/" + self._snapshot_file)


    def run(self):

        # channel_graph = ChannelGraph("SNAPSHOTS/" + self._snapshot_file)
        # target_node = channel_graph.get_highest_capacity_nodes(5)[0]  # Extract the highest capacity nodes as a list and take the first one

        simulation_1 = Simulation(self._channel_graph, self._base)
        simulation_1.run_success_payments_simulation(self._payments_to_simulate, self._payments_amount, self._mu, self._base, self._distribution, self._dist_func)

        print(simulation_1.payments_fees_per_node)
        print(simulation_1.payments_ratios_per_node)
        print(self.get_node_with_highest_ratio(simulation_1.payments_ratios_per_node))

        highest_ratio_node = self.get_node_with_highest_ratio(simulation_1.payments_ratios_per_node)

        print(self._channel_graph.get_connected_nodes(highest_ratio_node))

        print(self._channel_graph.get_connected_channels(highest_ratio_node))

        self.create_node_with_same_strategy(highest_ratio_node, "COPY")

        pos = nx.spring_layout(self._channel_graph.network)
        node_sizes = [v * 14 for v in dict(self._channel_graph.network.degree()).values()]  # multiply the degree of the node by 10 to get the size of the node
        nx.draw(self._channel_graph.network, pos, node_color='blue', node_size=node_sizes, edge_color='red', width=0.4)
        labels = {n: str(n) for n in self._channel_graph.network.nodes()}
        nx.draw_networkx_labels(self._channel_graph.network, pos, labels, font_size=6, font_color='grey')
        plt.show()

        simulation_2 = Simulation(self._channel_graph, self._base)
        simulation_2.run_success_payments_simulation(self._payments_to_simulate, self._payments_amount, self._mu, self._base, self._distribution, self._dist_func)

        print(highest_ratio_node)

        print("capacity")
        print(self._channel_graph.get_capacity(highest_ratio_node))

        print(simulation_2.payments_fees_per_node)
        print(self._channel_graph.get_nodes_capacities())
        print(simulation_2.payments_ratios_per_node)

        '''
        for channel in self._channel_graph.get_connected_channels(highest_ratio_node):
            print(channel.capacity)

        for channel in self._channel_graph.get_connected_channels("COPY"):
            print(channel.capacity)
        '''

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


    def create_node_with_same_strategy(self, node_to_copy, new_node_id):
        connected_channels = self._channel_graph.get_connected_channels(node_to_copy)

        for channel in connected_channels:
            self._channel_graph.create_channel(
                new_node_id,
                channel.dest,
                channel.is_announced,
                channel.capacity,  # * 2 is because we obtain the channel (only one side) and we need to provide the total capacity of the channel to be created
                channel.flags, channel.is_active, channel.last_update, channel.base_fee, channel.ppm,
                channel.cltv_delta, channel.htlc_min_msat, channel.htlc_max_msat
            )



replicateBestStrategy = ReplicateBestStrategy()
replicateBestStrategy.run()
