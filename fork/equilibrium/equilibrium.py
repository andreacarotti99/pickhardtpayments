from pickhardtpayments.fork.Simulation import Simulation
from pickhardtpayments.pickhardtpayments import ChannelGraph
from pickhardtpayments.fork.ExportResults import ExportResults


# Testing if the LN has reached a fee equilibrium:
# 1) Deciding parameters of the simulation: num. of nodes to keep, strategy for choosing nodes, payment amount, number of payments, distribution of payments
# 2) Running a simulation, obtaining some fees for every node
# 3) Randomly picking a node
# 4) Changing the channels of the node with other channels of the same capacity (starting randomly then using some strategy)
# 5) Running a new simulation, obtaining some fees for every node and specifically for the changed node
# 6) Repeating 3), 4) and 5) 10 times and observe the difference in fee earned by the randomly picked node

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




