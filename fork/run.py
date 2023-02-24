import os
import time
import pandas as pd
from pickhardtpayments.fork.ComputeDemand import capacity, total_demand, compute_C, get_random_node_weighted_by_capacity
from pickhardtpayments.pickhardtpayments import ChannelGraph
from pickhardtpayments.pickhardtpayments import UncertaintyNetwork
from pickhardtpayments.pickhardtpayments import OracleLightningNetwork
from pickhardtpayments.pickhardtpayments import SyncSimulatedPaymentSession
import numpy as np

distributions = {
        "normal": "normal",
        "weighted_by_capacity": "weighted_by_capacity"
    }

def export_results(df, payments_to_simulate, payments_amount, mu, snapshot_file, distribution):
    """
    Take a dataframe and exports it in the folder RESULTS as a csv file
    """
    output_dir = 'RESULTS'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file = "results_" + str(payments_to_simulate) + "trans_" + str(payments_amount) + "SAT_" + str(mu) + \
                  "mu_" + snapshot_file[:-5] + "_dist_" + distribution[0:4]

    df.to_csv("%s/%s.csv" % (output_dir, output_file), index=False)

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

def choose_src_and_dst(distribution: str, n_capacities : dict, uncertainity_network: UncertaintyNetwork):
    if distribution == "normal":
        print("ok")
        src = uncertainity_network.get_random_node_uniform_distribution()
        dst = uncertainity_network.get_random_node_uniform_distribution()
        while dst == src:
                dst = get_random_node_weighted_by_capacity(n_capacities)
    elif distribution == "weighted_by_capacity":
        src = get_random_node_weighted_by_capacity(n_capacities)
        dst = get_random_node_weighted_by_capacity(n_capacities)
        while dst == src:
                dst = get_random_node_weighted_by_capacity(n_capacities)
    else:
        print("Distribution not found")
        exit()
    return src, dst


def run_success_payments_simulation(payment_session: SyncSimulatedPaymentSession,
                                    uncertainity_network: UncertaintyNetwork,
                                    oracle_lightning_network: OracleLightningNetwork,
                                    payments_to_simulate: int,
                                    payments_amount: int,
                                    mu: int,
                                    base: int,
                                    distribution: str = "normal"):
    """
    Run a simulation of Pickhardt payments, every time there is an unsuccessful payment it retries.
    """

    print(f"Starting simulation with {payments_to_simulate} payments of {payments_amount} sat.")
    print(f"mu = {mu}")
    print(f"base = {base}")
    print(f"distribution = {distribution}")

    paymentNumber = 0
    payments_fees = []
    payments_routing_nodes = []
    payment_session.forget_information()
    n_capacities = oracle_lightning_network.nodes_capacities()
    while paymentNumber < payments_to_simulate:
        print("******************************************************************************")
        print("Payment: " + str((paymentNumber + 1)))
        src, dst = choose_src_and_dst(distribution, n_capacities, uncertainity_network)
        print("Source: " + str(src) + "\nDestination: " + str(dst))
        # perform the payment
        payment = payment_session.pickhardt_pay(src, dst, payments_amount, mu, base)
        if payment.successful:
            paymentNumber += 1
            payments_fees.append(payment.fee_per_node)
            payments_routing_nodes.append(payment.routing_nodes)
    return payments_fees, payments_routing_nodes


def main():
    # SIMULATION PARAMETERS
    payments_to_simulate = 5
    payments_amount = 1000
    mu = 0
    base = 10_000  # Base fee under which I add to the Uncertainty Graph the nodes (otherwise I ignore them)
    snapshot_file = "pickhardt_12apr2022_fixed.json"
    distribution = "weighted_by_capacity"


    # SIMULATION STARTS
    print("Creating channel graph...")
    channel_graph = ChannelGraph("SNAPSHOTS/" + snapshot_file)
    print("Creating Uncertainty Network...")
    uncertainty_network = UncertaintyNetwork(channel_graph, base)
    print("Creating Oracle Network...")
    oracle_lightning_network = OracleLightningNetwork(channel_graph)
    print("Initializing Payment Session...")
    payment_session = SyncSimulatedPaymentSession(oracle_lightning_network, uncertainty_network, prune_network=False)
    payment_session.forget_information()




    # RENE = "03efccf2c383d7bf340da9a3f02e2c23104a0e4fe8ac1a880c8e2dc92fbdacd9df"
    # C_OTTO = "027ce055380348d7812d2ae7745701c9f93e70c1adeb2657f053f91df4f2843c71"
    # NODE_1_HOP_TO_OTTO = "02d4b432058ec31e38f6f35d22a487b7db04c4bf70f201f601b66f7b4358242b03"
    # NODE_2_HOP_TO_OTTO = "02c1321de5a127023115b90f33ae1244349269f5d18d3ea4014be697e700c07ccc"
    # p1 = payment_session.pickhardt_pay(C, D, tested_amount, mu, base)
    # print("Demand")
    # print(total_demand(RENE, oracle_lightning_network))

    # Saving into a dictionary the capacities for each node (from oracle)
    nodes_capacities = oracle_lightning_network.nodes_capacities()

    # Running the Simulation and
    # Saving into a list the fees for each payment (the fees for each payment is a dictionary with the node and its earned fees)
    payments_fees, payments_routing_nodes = run_success_payments_simulation(payment_session, uncertainty_network,
                                                                            oracle_lightning_network,
                                                                            payments_to_simulate,
                                                                            payments_amount, mu, base,
                                                                            distribution)

    # Saving into a dictionary the total fees for each node (that charged any fee)
    total_fees_per_node = compute_fees_per_node(payments_fees)
    total_routed_payments_per_node = compute_routing_nodes(payments_routing_nodes)

    # Converting the fees of each node into a dataframe
    df = pd.DataFrame(total_fees_per_node.items(), columns=['node', 'total_fee'])

    # Mapping the capacities into the df total_fees (so we consider only the capacities of the nodes that earned fees)
    df['capacity'] = df['node'].map(nodes_capacities)
    df['routed_payments'] = df['node'].map(total_routed_payments_per_node)
    results = df

    export_results(results, payments_to_simulate, payments_amount, mu, snapshot_file, distribution)

    return


if __name__ == "__main__":
    np.random.seed(1)
    start = time.time()
    main()
    end = time.time()
    print("\nSimulation time: " + str(round((end - start) / 60, 2)) + " minutes")
