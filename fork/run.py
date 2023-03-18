import os
import time
import pandas as pd
from matplotlib import pyplot as plt

from pickhardtpayments.fork.ComputeDemand import capacity, total_demand, compute_C, get_random_node_weighted_by_capacity
from pickhardtpayments.fork.Simulation import Simulation
from pickhardtpayments.pickhardtpayments import ChannelGraph
from pickhardtpayments.pickhardtpayments import UncertaintyNetwork
from pickhardtpayments.pickhardtpayments import OracleLightningNetwork
from pickhardtpayments.pickhardtpayments import SyncSimulatedPaymentSession
import numpy as np
from mpl_toolkits.mplot3d import Axes3D


distributions = {
    "uniform": "uniform",
    "weighted_by_capacity": "weighted_by_capacity"
}

distribution_functions = {
    "linear": "linear",
    "quadratic": "quadratic",
    "cubic": "cubic",
    "exponential": "exponential"
}


def export_results(df, payments_to_simulate, payments_amount, mu, snapshot_file, distribution, dist_func):
    """
    Take a dataframe and exports it in the folder RESULTS as a csv file
    """
    output_dir = 'RESULTS'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file = "results_" + str(payments_to_simulate) + "trans_" + str(payments_amount) + "SAT_" + str(mu) + \
                  "mu_" + snapshot_file[:-5] + "_dist_" + distribution[0:4] + "_" + dist_func
    df.to_csv("%s/%s.csv" % (output_dir, output_file), index=False)
    return


def compute_routing_nodes(payments_routing_nodes):
    """
    takes a list of dictionaries containing the number of routed payments of the nodes
    """
    routing_nodes = {}
    for p in payments_routing_nodes:
        for node, routed_payments in p.items():
            if node in routing_nodes:
                routing_nodes[node] += 1
            else:
                routing_nodes[node] = 1
    return routing_nodes


def compute_fees_per_node(payments_fees):
    """
    takes a list of dictionaries containing the fee earned by each node in the payment and returns a single
    dictionary that contains the sum of values (fees) for each key (nodes) across all dictionaries:
    """
    fees_per_node = {}
    for p in payments_fees:
        for node, fee in p.items():
            if node in fees_per_node:
                fees_per_node[node] += fee
            else:
                fees_per_node[node] = fee
    return fees_per_node


def choose_src_and_dst(distribution: str, n_capacities: dict, uncertainity_network: UncertaintyNetwork, dist_func: str):
    """
    randomly chooses two nodes as source and destination of the transaction given a probability distribution
    """

    if distribution == "uniform":
        src = uncertainity_network.get_random_node_uniform_distribution()
        dst = uncertainity_network.get_random_node_uniform_distribution()
        while dst == src:
            dst = uncertainity_network.get_random_node_uniform_distribution()
    elif distribution == "weighted_by_capacity":
        src = get_random_node_weighted_by_capacity(n_capacities, dist_func)
        dst = get_random_node_weighted_by_capacity(n_capacities, dist_func)
        while dst == src:
            dst = get_random_node_weighted_by_capacity(n_capacities, dist_func)

    else:
        print("Distribution not found")
        exit()
    return src, dst


def run_success_payments_simulation(payment_session: SyncSimulatedPaymentSession,
                                    uncertainity_network: UncertaintyNetwork,
                                    oracle_lightning_network: OracleLightningNetwork,
                                    payments_to_simulate: int = 10,
                                    payments_amount: int = 1000,
                                    mu: int = 10,
                                    base: int = 1000,
                                    distribution: str = "uniform",
                                    dist_func=str):
    """
    Run a simulation of Pickhardt payments, every time there is an unsuccessful payment it retries.
    """

    print(f"Starting simulation with {payments_to_simulate} payments of {payments_amount} sat.")
    print(f"mu = {mu}")
    print(f"base = {base}")
    print(f"distribution = {distribution}")
    print(f"function f = {dist_func}")

    paymentNumber = 0
    payments_fees = []
    payments_routing_nodes = []
    payment_session.forget_information()
    n_capacities = oracle_lightning_network.nodes_capacities()
    while paymentNumber < payments_to_simulate:
        print("*" * 90)
        print(f"Payment: {paymentNumber + 1}")
        src, dst = choose_src_and_dst(distribution, n_capacities, uncertainity_network, dist_func)
        print(f"Source: {src}\nDestination: {dst}")
        # perform the payment
        payment = payment_session.pickhardt_pay(src, dst, payments_amount, mu, base)
        if payment.successful:
            paymentNumber += 1
            payments_fees.append(payment.fee_per_node)
            payments_routing_nodes.append(payment.routing_nodes)
    return payments_fees, payments_routing_nodes


def main():
    # SIMULATION PARAMETERS
    payments_to_simulate = 1
    payments_amount = 1000
    mu = 100_000
    base = 20_000  # Base fee under which I add to the Uncertainty Graph the nodes (otherwise I ignore them)
    snapshot_file = "cosimo_19jan2023_converted.json"
    distribution = "uniform"
    dist_func = ""

    # SIMULATION STARTS
    print(f"Creating channel graph from {snapshot_file}...")
    channel_graph = ChannelGraph("SNAPSHOTS/" + snapshot_file)
    print(f"Created graph with {channel_graph.network.number_of_nodes()} nodes and {channel_graph.network.number_of_edges()} edges...")

    '''
    print("Creating Uncertainty Network...")
    uncertainty_network = UncertaintyNetwork(channel_graph, base)
    print("Creating Oracle Network...")
    oracle_lightning_network = OracleLightningNetwork(channel_graph)
    print("Initializing Payment Session...")
    payment_session = SyncSimulatedPaymentSession(oracle_lightning_network, uncertainty_network, prune_network=False)
    payment_session.forget_information()
    '''

    RENE = "03efccf2c383d7bf340da9a3f02e2c23104a0e4fe8ac1a880c8e2dc92fbdacd9df"
    C_OTTO = "027ce055380348d7812d2ae7745701c9f93e70c1adeb2657f053f91df4f2843c71"

    A = "0390b5d4492dc2f5318e5233ab2cebf6d48914881a33ef6a9c6bcdbb433ad986d0"
    B = "03148dba0e3cb3c15250fb6a40d6456b109581570448aa72d0a4e1a56eaf81d970"

    # SIMULATION STARTS

    incr_mu = 0
    incr_amt = 0

    mus = [0, 10, 100, 500, 1000, 5000, 10_000, 100_000, 1_000_000]
    amts = [1000, 10_000, 100_000, 1_000_000, 10_000_000]
    fees = []
    successes = []

    tuples = []




    for i in range(len(amts)):
        for j in range(len(mus)):
            uncertainty_network = UncertaintyNetwork(channel_graph, base)
            oracle_lightning_network = OracleLightningNetwork(channel_graph)
            payment_session = SyncSimulatedPaymentSession(oracle_lightning_network, uncertainty_network,
                                                          prune_network=False)
            p1 = payment_session.pickhardt_pay(src=A, dest=B, amt=amts[i], mu=mus[j], base=base, verbose=True)
            payment_session.forget_information()

            if p1.fee_per_node is not None:
                tuples.append((amts[i], mus[j], sum(p1.fee_per_node.values()), p1.successful))
            else:
                tuples.append((amts[i], mus[j], -1, p1.successful))
                break

    print(tuples)
    



    columns = ['amount', 'mu', 'total_fees', 'successful']
    df = pd.DataFrame(tuples, columns=columns)

    df.to_csv('amount_fees_mu.csv', index=False)


    print(df)




    # NODE_1_HOP_TO_OTTO = "02d4b432058ec31e38f6f35d22a487b7db04c4bf70f201f601b66f7b4358242b03"
    # NODE_2_HOP_TO_OTTO = "02c1321de5a127023115b90f33ae1244349269f5d18d3ea4014be697e700c07ccc"
    # print("Demand")
    # print(total_demand(RENE, oracle_lightning_network))

    '''
    print(simulation.payments_fees_per_transaction)
    '''

    '''

    # Saving into a dictionary the capacities for each node (from oracle)
    nodes_capacities = oracle_lightning_network.nodes_capacities()

    # Running the Simulation and
    # Saving into a list the fees for each payment (the fees for each payment is a dictionary with the node and its earned fees)
    payments_fees, payments_routing_nodes = run_success_payments_simulation(payment_session, uncertainty_network,
                                                                            oracle_lightning_network,
                                                                            payments_to_simulate,
                                                                            payments_amount, mu, base,
                                                                            distribution,
                                                                            dist_func)
                                                                            
    

    # Saving into a dictionary the total fees for each node (that charged any fee)
    total_fees_per_node = compute_fees_per_node(payments_fees)
    total_routed_payments_per_node = compute_routing_nodes(payments_routing_nodes)

    # Converting the fees of each node into a dataframe
    df = pd.DataFrame(total_fees_per_node.items(), columns=['node', 'total_fee'])

    # Mapping the capacities into the df total_fees (so we consider only the capacities of the nodes that earned fees)
    df['capacity'] = df['node'].map(nodes_capacities)
    df['routed_payments'] = df['node'].map(total_routed_payments_per_node)
    results = df

    # export_results(results, payments_to_simulate, payments_amount, mu, snapshot_file, distribution, dist_func)
    
    '''

    return


if __name__ == "__main__":
    np.random.seed(1)
    start = time.time()
    main()
    end = time.time()
    print("\nSimulation time: " + str(round((end - start) / 60, 2)) + " minutes")
