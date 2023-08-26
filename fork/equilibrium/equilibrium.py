from pickhardtpayments.fork.Simulation import Simulation
from pickhardtpayments.pickhardtpayments import ChannelGraph
from pickhardtpayments.fork.ExportResults import ExportResults

import logging

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

base = 20_000
payments_to_simulate = 100
payments_amount = 10_000
mu = 100
distribution = "weighted_by_capacity"
dist_func = "linear"
verbose = False
tentative_nodes_to_keep = 30

snapshot_path = '/Users/andreacarotti/Desktop/LN/_PickhardtPayments/pickhardtpayments/fork/SNAPSHOTS/cosimo_19jan2023_converted.json'

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

#todo: fix the get_channel_without_short_channel_id because these nodes have many channels between nodes

for i in range(3):
    random_node = channel_graph.get_random_node_uniform_distribution()
    while len(channel_graph.get_connected_nodes(random_node)) > (tentative_nodes_to_keep//2):
        random_node = channel_graph.get_random_node_uniform_distribution()

    logging.debug('Random node picked: %s', random_node)

    for n in channel_graph.get_connected_nodes(random_node):  # I have to iterate over all neighbors of random_node
        for ch in channel_graph.get_channels(random_node, n):  # I have to iterate over all the channels between the two nodes

            # ch = channel_graph.get_channel_without_short_channel_id(random_node, n)
            logging.debug('|_ %d with %s', ch.capacity, str(ch.dest))

    old_neighbors = channel_graph.get_connected_nodes(random_node)
    new_neighbors = []

    for dest_node in channel_graph.get_connected_nodes(random_node):
        for ch in channel_graph.get_channels(random_node, n):

            logging.debug('closing channel with: %s', str(ch.dest))
            print('closing channel with: ', ch.dest)
            channel_graph.close_channel(random_node, dest_node, ch.short_channel_id)


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

    for n in channel_graph.get_connected_nodes(random_node):
        ch = channel_graph.get_channel_without_short_channel_id(random_node, n)
        logging.debug('|_ %d with %s', ch.capacity, str(ch.dest))


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

    logging.debug('\n')

    export = ExportResults(simulation=s)
    export.export_results(simulation_number=str(i+2))
