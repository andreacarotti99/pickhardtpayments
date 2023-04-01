import pandas as pd

from pickhardtpayments.fork.Simulation import Simulation
from pickhardtpayments.pickhardtpayments import ChannelGraph
import copy


'''
simulate...
copy best node
    performance increased -> copy second node
    
    performance decreased -> if decrease_count == 4 stop
'''

base = 20_000
channel_graph = ChannelGraph("../SNAPSHOTS/cosimo_19jan2023_converted.json")
channel_graph.transform_channel_graph_to_simpler(tentative_nodes_to_keep=2000)

agent = channel_graph.get_highest_capacity_nodes(1)[0]

simulation = Simulation(channel_graph=channel_graph, base=base)
simulation.run_success_payments_simulation(
            payments_to_simulate=1000,
            payments_amount=1000,
            mu=1000,
            base=1000,
            distribution="weighted_by_capacity",
            dist_func="linear",
            verbose=False
        )
hrn = simulation.highest_ratio_nodes
prev_total_fee = simulation.get_fees(node=agent)

print("HRN list:")
print(hrn)

rtpn = simulation.routed_transactions_per_node

filtered_rtpn = {k: v for k, v in rtpn.items() if v > 10}

# hrn_filtered
hrn = [x for x in hrn if x in filtered_rtpn]


print(f"Agent:{agent}")
print("\n Starting the iterated game...")

df = pd.DataFrame()
df['ranking'] = ''
df['copied_node'] = ''
df['new_fees'] = ''
df['delta'] = ''

for i in range(10):
    cg = copy.deepcopy(channel_graph)
    cg.close_channels_up_to_amount(node=agent, threshold_to_reach=cg.get_expected_capacity(node=hrn[i]))
    cg.replicate_node(node_to_copy=hrn[i], new_node_id=agent)
    s = Simulation(channel_graph=cg, base=base)
    s.run_success_payments_simulation(
            payments_to_simulate=1000,
            payments_amount=1000,
            mu=1000,
            base=1000,
            distribution="weighted_by_capacity",
            dist_func="linear",
            verbose=False
        )

    # new_total_fee_agent = s.get_fees(node=agent) + s.get_fees(node="THIEF_" + str(i))
    new_total_fee_agent = s.get_fees(node=agent)
    delta = new_total_fee_agent - prev_total_fee
    print(f"Copying hrn number: {i}")
    # print(f"New fees agent + copy = {s.get_fees(node=agent)} + {s.get_fees(node='THIEF_' + str(i))} = {new_total_fee_agent}")
    print(f"New fees agent + copy = {new_total_fee_agent}")
    print(f"Delta with first simulation = {delta}")

    new_row = {'ranking': i, 'copied_node': hrn[i], 'new_fees': new_total_fee_agent, 'delta': delta}
    df = df.append(new_row, ignore_index=True)

print(df)

