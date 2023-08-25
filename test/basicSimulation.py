from pickhardtpayments.fork.ExportResults import ExportResults
from pickhardtpayments.fork.Simulation import Simulation
from pickhardtpayments.pickhardtpayments import ChannelGraph

base = 20_000
channel_graph = ChannelGraph("../fork/SNAPSHOTS/" + "cosimo_19jan2023_converted.json")

channel_graph.transform_channel_graph_to_simpler(tentative_nodes_to_keep=1000, strategy="weighted_by_capacity")

simulation = Simulation(channel_graph=channel_graph, base=base)
simulation.run_success_payments_simulation(
            payments_to_simulate=10_000,
            payments_amount=10_000,
            mu=1,
            base=20_000,
            distribution="uniform",
            dist_func="",
            verbose=False,
            payments_amount_distribution="fixed"
        )
ER = ExportResults(simulation)
ER.export_results()
