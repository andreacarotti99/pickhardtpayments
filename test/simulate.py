from pickhardtpayments.fork.Simulation import Simulation
from pickhardtpayments.pickhardtpayments import ChannelGraph, OracleLightningNetwork

base = 20_000
channel_graph = ChannelGraph("../fork/SNAPSHOTS/" + "cosimo_19jan2023_converted.json")

NODE_TO_COPY = "02dd2a0137967c6b393581443579f455678315da75ce173d868e53fa6a75e83c2f"

channel_graph.replicate_node(node_to_copy=NODE_TO_COPY, new_node_id="new")

oracle = OracleLightningNetwork(channel_graph)

oracle.print_node_info(node=NODE_TO_COPY)

oracle.print_node_info(node="new")


'''
channel_graph.transform_channel_graph_to_simpler(1000)
s = Simulation(channel_graph, base)
s.run_success_payments_simulation(
    payments_to_simulate=10000,
    payments_amount=10_000,
    mu=1000,
    base=base,
    distribution="weighted_by_capacity",
    dist_func="linear",
    verbose=False
)

print(s.final_payment_fees_list)
'''
