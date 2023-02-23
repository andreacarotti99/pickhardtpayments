import os
import time
import pandas as pd
from pickhardtpayments.pickhardtpayments import ChannelGraph
from pickhardtpayments.pickhardtpayments import UncertaintyNetwork
from pickhardtpayments.pickhardtpayments import OracleLightningNetwork
from pickhardtpayments.pickhardtpayments import SyncSimulatedPaymentSession
import numpy as np


def export_results(df, payments_to_simulate, payments_amount, mu, snapshot_file):
    """
    Take a dataframe and exports it in the folder RESULTS as a csv file
    """
    output_dir = 'RESULTS'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file = "results_" + str(payments_to_simulate) + "trans_" + str(payments_amount) + "SAT_" + str(mu) + "mu_" + snapshot_file[:-5]

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


def run_success_payments_simulation(payment_session, uncertainity_network, payments_to_simulate, payments_amount, mu,
                                    base):
    """
    Run a simulation of pickhardt payments, every time there is an unsuccesful payment it retries.
    TO DO: fix the problem on the min cut flow (status: 3)
    """
    print("Starting simulation with " + str(payments_to_simulate) + " payments of " + str(payments_amount) + " sat.")
    paymentNumber = 0
    payments_fees = []
    payments_routing_nodes = []
    payment_session.forget_information()
    while paymentNumber < payments_to_simulate:
        print("******************************************************************************")
        print("Payment: " + str((paymentNumber + 1)))
        src = uncertainity_network.get_random_node()
        dst = uncertainity_network.get_random_node()
        while dst == src:
            dst = uncertainity_network.get_random_node()
        print("Source: " + str(src) + "\nDestination: " + str(dst))
        # perform the payment
        payment = payment_session.pickhardt_pay(src, dst, payments_amount, mu, base)
        if payment.successful:
            paymentNumber += 1
            payments_fees.append(payment.fee_per_node)
            payments_routing_nodes.append(payment.routing_nodes)
    return payments_fees, payments_routing_nodes


def main():
    payments_to_simulate = 10_000
    payments_amount = 1000
    mu = 0
    base = 20_000  # Base fee under which I add to the Uncertainty Graph the nodes (otherwise I ignore them)
    snapshot_file = "pickhardt_12apr2022_fixed.json"

    channel_graph = ChannelGraph("SNAPSHOTS/" + snapshot_file)
    uncertainty_network = UncertaintyNetwork(channel_graph, base)
    oracle_lightning_network = OracleLightningNetwork(channel_graph)
    payment_session = SyncSimulatedPaymentSession(oracle_lightning_network, uncertainty_network, prune_network=False)
    payment_session.forget_information()

    # RENE = "03efccf2c383d7bf340da9a3f02e2c23104a0e4fe8ac1a880c8e2dc92fbdacd9df"
    # C_OTTO = "027ce055380348d7812d2ae7745701c9f93e70c1adeb2657f053f91df4f2843c71"
    # NODE_1_HOP_TO_OTTO = "02d4b432058ec31e38f6f35d22a487b7db04c4bf70f201f601b66f7b4358242b03"
    # NODE_2_HOP_TO_OTTO = "02c1321de5a127023115b90f33ae1244349269f5d18d3ea4014be697e700c07ccc"
    # p1 = payment_session.pickhardt_pay(C, D, tested_amount, mu, base)

    # Saving into a dictionary the capacities for each node (from oracle)
    nodes_capacities = oracle_lightning_network.nodes_capacities()

    # Running the Simulation and
    # Saving into a list the fees for each payment (the fees for each payment is a dictionary with the node and its earned fees)
    payments_fees, payments_routing_nodes = run_success_payments_simulation(payment_session, uncertainty_network, payments_to_simulate,
                                                    payments_amount, mu, base)

    # Saving into a dictionary the total fees for each node (that charged any fee)
    total_fees_per_node = compute_fees_per_node(payments_fees)
    total_routed_payments_per_node = compute_routing_nodes(payments_routing_nodes)

    # Converting the fees of each node into a dataframe
    df = pd.DataFrame(total_fees_per_node.items(), columns=['node', 'total_fee'])

    # Mapping the capacities into the df total_fees (so we consider only the capacities of the nodes that earned fees)
    df['capacity'] = df['node'].map(nodes_capacities)
    df['routed_payments'] = df['node'].map(total_routed_payments_per_node)
    results = df

    print(results.head(10))

    export_results(results, payments_to_simulate, payments_amount, mu, snapshot_file)

    return


if __name__ == "__main__":
    np.random.seed(1)
    start = time.time()
    main()
    end = time.time()
    print("\nSimulation time: " + str(round((end - start) / 60, 2)) + " minutes")
