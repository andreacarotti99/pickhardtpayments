from pickhardtpayments.fork.Simulation import Simulation
from pickhardtpayments.pickhardtpayments import ChannelGraph, OracleLightningNetwork

base = 20_000
channel_graph = ChannelGraph("../fork/SNAPSHOTS/" + "cosimo_19jan2023_converted.json")


NODE_WITH_NEW_CHANNELS = "02418a22158cbfbba214df5204bf42287e928f8415b4bee903379999679ead65c5"
NODE_TO_COPY = "02dd2a0137967c6b393581443579f455678315da75ce173d868e53fa6a75e83c2f"


oracle = OracleLightningNetwork(channel_graph)
oracle.print_node_info(node=NODE_WITH_NEW_CHANNELS)
print()
oracle.print_node_info(node=NODE_TO_COPY)
print()

channel_graph.replicate_node(node_to_copy=NODE_TO_COPY, new_node_id=NODE_WITH_NEW_CHANNELS)
oracle = OracleLightningNetwork(channel_graph)

oracle.print_node_info(node=NODE_WITH_NEW_CHANNELS)

oracle.close_channels_up_to_amount(node=NODE_WITH_NEW_CHANNELS, threshold_to_reach=5000000*4)

# channel_graph.close_channels_up_to_amount(node=NODE_WITH_NEW_CHANNELS, threshold_to_reach=5000000*4)






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
