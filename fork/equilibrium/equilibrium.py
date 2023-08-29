from pickhardtpayments.fork.Simulation import Simulation
from pickhardtpayments.pickhardtpayments import ChannelGraph
from pickhardtpayments.fork.ExportResults import ExportResults

import logging
import csv


log_format = "%(message)s"
log_file = "results_10trans_10000SAT_100mu__distweig_linear_amountsdistfixe_1.log"
logging.basicConfig(filename=log_file, level=logging.DEBUG, format=log_format, filemode='w')

# Testing if the LN has reached a fee equilibrium:
# 1) Deciding parameters of the simulation: num. of nodes to keep, strategy for choosing nodes, payment amount, number of payments, distribution of payments
# 2) Running a simulation, obtaining some fees for every node
# 3) Randomly picking a node
# 4) Changing the channels of the node with other channels of the same capacity (starting randomly then using some strategy)
# 5) Running a new simulation, obtaining some fees for every node and specifically for the changed node
# 6) Repeating 3), 4) and 5) 10 times and observe the difference in fee earned by the randomly picked node

# -- params -----------------------------

base = 20_000
payments_to_simulate = 1000
payments_amount = 10_000
mu = 100
distribution = "weighted_by_capacity"
dist_func = "linear"
verbose = False
tentative_nodes_to_keep = 500
total_tests = 30
snapshot_path = '/Users/andreacarotti/Desktop/LN/_PickhardtPayments/pickhardtpayments/fork/SNAPSHOTS/cosimo_19jan2023_converted.json'

logging.debug('base: %s', str(base))
logging.debug('payments_to_simulate: %s', str(payments_to_simulate))
logging.debug('payments_amount: %s', str(payments_amount))
logging.debug('mu: %s', str(mu))
logging.debug('distribution: %s', str(distribution))
logging.debug('base: %s', str(base))
logging.debug('dist_func: %s', str(dist_func))
logging.debug('tentative_nodes_to_keep: %s', str(tentative_nodes_to_keep))
logging.debug('total_tests: %s', str(total_tests))
logging.debug('snapshot_path: %s', str(snapshot_path))

# ----------------------------------------

channel_graph = ChannelGraph(snapshot_path)
channel_graph.transform_channel_graph_to_simpler(
    tentative_nodes_to_keep=tentative_nodes_to_keep,
    strategy="weighted_by_capacity")

s = Simulation(channel_graph, base)
s.run_success_payments_simulation(
    payments_to_simulate=payments_to_simulate,
    payments_amount=payments_amount,
    mu=mu,
    base=base,
    distribution=distribution,
    dist_func=dist_func,
    verbose=verbose
)

export = ExportResults(simulation=s)
export.export_results()

old_ratio_random_nodes = {}
new_ratio_random_nodes = {}
random_nodes = []


for i in range(total_tests):

    # Choosing a target random node, this node will be used for comparison by changing its channels
    random_node = channel_graph.get_random_node_uniform_distribution()
    while len(channel_graph.get_connected_nodes(random_node)) > (tentative_nodes_to_keep//2):
        random_node = channel_graph.get_random_node_uniform_distribution()
    random_nodes.append(random_node)
    logging.debug('Random node picked: %s', random_node)
    old_ratio_random_nodes[random_node] = s.get_ratio(random_node)

    # printing all the channels of the target node
    for dest_node in channel_graph.get_connected_nodes(random_node):  # I have to iterate over all neighbors of random_node
        for ch in channel_graph.get_channels(random_node, dest_node):  # I have to iterate over all the channels between the two nodes
            # ch = channel_graph.get_channel_without_short_channel_id(random_node, n)
            logging.debug('|_ %d with %s', ch.capacity, str(ch.dest))

    # old_neighbors are the orginal neighbors of the target node that will be substituted
    old_neighbors = channel_graph.get_connected_nodes(random_node)

    # new_neighbors are the new neighbors of the target node after closing all old channels
    new_neighbors = []

    for dest_node in channel_graph.get_connected_nodes(random_node):
        for ch in channel_graph.get_channels(random_node, dest_node):

            # Proceeding in closing the old channels (one by one) and opening a new channel of equal size
            logging.debug('closing channel with: %s', str(ch.dest))
            print('closing channel with: ', ch.dest)
            channel_graph.close_channel(random_node, dest_node, ch.short_channel_id)

            # Randomly picking the new node to which we create the channel to
            new_random_node = channel_graph.get_random_node_uniform_distribution()
            while new_random_node == random_node or new_random_node in old_neighbors or new_random_node in new_neighbors:
                print('The node chosen was already connected to the random target node! Choosing andother node...')
                new_random_node = channel_graph.get_random_node_uniform_distribution()

            logging.debug('opening channel with: %s', str(new_random_node))
            print('opening channel with: ', new_random_node)
            channel_graph.create_channel(random_node, new_random_node, ch.is_announced, ch.capacity,
                                         ch.flags, ch.is_active, ch.last_update, ch.base_fee, ch.ppm, ch.cltv_delta,
                                         ch.htlc_min_msat, ch.htlc_max_msat, str(ch.short_channel_id) + '_2')
            new_neighbors.append(new_random_node)

    # printing all the new channels of the target node
    for dest_node in channel_graph.get_connected_nodes(random_node):
        for ch in channel_graph.get_channels(random_node, dest_node):
            logging.debug('|_ %d with %s', ch.capacity, str(ch.dest))

    # Proceeding with a new simulation given the new channels of the target node
    sn = Simulation(channel_graph, base)
    sn.run_success_payments_simulation(
        payments_to_simulate=payments_to_simulate,
        payments_amount=payments_amount,
        mu=mu,
        base=base,
        distribution=distribution,
        dist_func=dist_func,
        verbose=verbose
    )

    new_ratio_random_nodes[random_node] = sn.get_ratio(random_node)
    logging.debug('\n')
    export = ExportResults(simulation=sn)
    export.export_results(simulation_number=str(i+2))


# Comparing the old ratios of the target node with the new one and saving the result in a csv file
combined_data = [(node, old_ratio_random_nodes[node], new_ratio_random_nodes[node]) for node in random_nodes]
combined_data.sort()
csv_filename = "node_ratios.csv"
with open(csv_filename, mode='w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Public Key", "Old Ratio", "New Ratio"])
    csv_writer.writerows(combined_data)

print(f"New ratios has been exported to {csv_filename}")
