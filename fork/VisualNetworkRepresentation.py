import networkx as nx
from matplotlib import pyplot as plt
from pickhardtpayments.pickhardtpayments import ChannelGraph


class VisualNetworkRepresentation:
    def __init__(self, channel_graph: ChannelGraph):
        self._channel_graph = channel_graph

    def show_network(self, highlight_nodes=None):
        pos = nx.spring_layout(self._channel_graph.network)
        node_sizes = [v * 14 for v in dict(self._channel_graph.network.degree()).values()]
        node_colors = ['blue'] * len(self._channel_graph.network.nodes())
        if highlight_nodes:
            for node in highlight_nodes:
                node_colors[self.get_node_index(node)] = '#b2e061'
        nx.draw(self._channel_graph.network, pos, node_color=node_colors, node_size=node_sizes, edge_color='#fd7f6f', width=0.4)
        labels = {n: str(n) for n in self._channel_graph.network.nodes()}
        nx.draw_networkx_labels(self._channel_graph.network, pos, labels, font_size=6, font_color='#7eb0d5')
        plt.show()

    def get_node_index(self, node_id):
        index = 0
        for node in list(self._channel_graph.network.nodes()):
            if node == node_id or str(node) == str(node_id):
                return index
            index += 1
        return None
