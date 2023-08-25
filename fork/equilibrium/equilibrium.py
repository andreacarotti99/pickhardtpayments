from pickhardtpayments.fork.Simulation import Simulation
from pickhardtpayments.pickhardtpayments import ChannelGraph
from pickhardtpayments.fork.ExportResults import ExportResults


base = 20_000
snapshot_path = '/Users/andreacarotti/Desktop/LN/_PickhardtPayments/pickhardtpayments/fork/SNAPSHOTS/cosimo_19jan2023_converted.json'
channel_graph = ChannelGraph(snapshot_path)
channel_graph.transform_channel_graph_to_simpler(
    tentative_nodes_to_keep=1000,
    strategy="weighted_by_capacity")
s = Simulation(channel_graph, base)
s.run_success_payments_simulation(
    payments_to_simulate=10,
    payments_amount=10_000,
    mu=100,
    base=base,
    distribution="weighted_by_capacity",
    dist_func="linear",
    verbose=False
)

export = ExportResults(simulation=s)
export.export_results()




