import pandas as pd
from pickhardtpayments.fork.Simulation import Simulation
from pickhardtpayments.fork.replicatingstrategy.SortingMetrics import *
from pickhardtpayments.pickhardtpayments import ChannelGraph
import copy

"""
In the iterated game what we try to do is the following:
1)  We first run a simulation (this step can be skipped if you already have data from a previous simulation)
2)  We create a list of nodes_to_copy, this list should contain nodes according to some criteria 
    (e.g. nodes betwenness centrality, or highest ratio nodes)
3)  We define a node to observe "agent"
4)  Finally we observe the fees earned by the node agent after copying the first 10 nodes of the list nodes_to_copy 
    (and we write down the difference in percentage compared to the initial simulation)
5)  We save the result in a csv file
"""


# SIMULATION PARAMETERS:
payments_to_simulate = 1000
payments_amount = 500_000
mu = 0
base = 20_000
distribution = "uniform"
dist_func = ""
verbose = False

# -------------------------------------------------------------------------------------

channel_graph = ChannelGraph("../SNAPSHOTS/cosimo_19jan2023_converted.json")
channel_graph.transform_channel_graph_to_simpler(tentative_nodes_to_keep=1000, strategy="weighted_by_capacity")
agent = channel_graph.get_highest_capacity_nodes(1)[0]

simulation = Simulation(channel_graph=channel_graph, base=base)
simulation.run_success_payments_simulation(
            payments_to_simulate=payments_to_simulate,
            payments_amount=payments_amount,
            mu=mu,
            base=base,
            distribution=distribution,
            dist_func=dist_func,
            verbose=verbose
        )
hrn = simulation.highest_ratio_nodes
prev_total_fee = simulation.get_fees(node=agent)

print("HRN list:")
print(hrn)

rtpn = simulation.routed_transactions_per_node

filtered_rtpn = {k: v for k, v in rtpn.items() if v > 10}

# hrn_filtered
hrn = [x for x in hrn if x in filtered_rtpn]


# nodes_to_copy = hrn

# nodes_importance_dict = compute_importance_for_each_node(channel_graph, 1000)
# sorted_important_nodes = sort_dict_by_value_descending(nodes_importance_dict)
# nodes_to_copy = sorted_important_nodes

assign_fee_and_cap_weight(channel_graph=channel_graph, amount=payments_amount)
betwenness_weighted_cap_and_fee_dict = betwenness_weighted_cap_and_fee_dict(channel_graph, fee_weight=0, cap_weight=1)
nodes_to_copy = sort_dict_by_value_descending(betwenness_weighted_cap_and_fee_dict)


print(f"Agent:{agent}")
print("\n Starting the iterated game...")

df = pd.DataFrame()
df['ranking'] = ''
df['copied_node'] = ''
df['new_fees'] = ''
df['delta'] = ''
df['perc_delta'] = ''

for i in range(10):
    print(f"Replicating node {i} in ranking")
    cg = copy.deepcopy(channel_graph)
    cg.close_channels_up_to_amount(node=agent, threshold_to_reach=cg.get_expected_capacity(node=nodes_to_copy[i]))
    cg.replicate_node(node_to_copy=nodes_to_copy[i], new_node_id=agent)
    #TODO: I need to make sure that if I replicate a node, the edges I am replicating are not edges that my node agent already
    # has, otherwise I am creating two channels towards the same edge

    s = Simulation(channel_graph=cg, base=base)
    s.run_success_payments_simulation(
            payments_to_simulate=payments_to_simulate,
            payments_amount=payments_amount,
            mu=mu,
            base=base,
            distribution=distribution,
            dist_func=dist_func,
            verbose=verbose
        )

    # new_total_fee_agent = s.get_fees(node=agent) + s.get_fees(node="THIEF_" + str(i))
    new_total_fee_agent = s.get_fees(node=agent)
    delta = new_total_fee_agent - prev_total_fee
    print(f"Copying nodes_to_copy number: {i}")
    # print(f"New fees agent + copy = {s.get_fees(node=agent)} + {s.get_fees(node='THIEF_' + str(i))} = {new_total_fee_agent}")
    print(f"New fees agent + copy = {new_total_fee_agent}")
    print(f"Delta with first simulation = {delta}")

    new_row = {'ranking': i, 'copied_node': nodes_to_copy[i], 'new_fees': new_total_fee_agent, 'delta': delta, 'perc_delta': (delta*100)/prev_total_fee}
    df = df.append(new_row, ignore_index=True)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
print(df)

filename = "graphhcn_uniform_random_metric_betwenness_fee_0_cap_1_mu0_amount500000.csv"
df.to_csv("../RESULTS/iterated_game/" + filename, index=False)
