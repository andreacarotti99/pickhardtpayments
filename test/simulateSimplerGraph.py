from pickhardtpayments.fork.Simulation import Simulation
from pickhardtpayments.pickhardtpayments import ChannelGraph

base = 20_000
channel_graph = ChannelGraph("../fork/SNAPSHOTS/cosimo_19jan2023_converted.json")
channel_graph.transform_channel_graph_to_simpler(tentative_nodes_to_keep=1000)

simulation = Simulation(channel_graph=channel_graph, base=base)
simulation.run_success_payments_simulation(
            payments_to_simulate=100,
            payments_amount=1000,
            mu=0,
            base=1000,
            distribution="weighted_by_capacity",
            dist_func="linear",
            verbose=True
        )
