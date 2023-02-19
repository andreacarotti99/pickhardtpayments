import os
import time

import pandas as pd

from pickhardtpayments.pickhardtpayments import ChannelGraph
from pickhardtpayments.pickhardtpayments import UncertaintyNetwork
from pickhardtpayments.pickhardtpayments import OracleLightningNetwork
from pickhardtpayments.pickhardtpayments import SyncSimulatedPaymentSession
import numpy as np

DEFAULT_BASE_THRESHOLD = 0

def export_results(df):
    output_dir = 'RESULTS'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    df.to_csv("%s/results.csv" % output_dir, index=False)

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

def run_success_payments_simulation(payment_session, uncertainity_network, payments_to_simulate, payments_amount, mu, base):

        print("Starting simulation with " + str(payments_to_simulate) + " payments of " + str(payments_amount) + " sat.")
        paymentNumber = 0
        senders_fee = {}
        payments_fees = []
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

        # print(total_fees_per_node)
        return payments_fees

def main():
    channel_graph = ChannelGraph("listchannels20220412.json")
    uncertainty_network = UncertaintyNetwork(channel_graph)
    oracle_lightning_network = OracleLightningNetwork(channel_graph)
    payment_session = SyncSimulatedPaymentSession(oracle_lightning_network, uncertainty_network, prune_network=False)
    payment_session.forget_information()

    RENE = "03efccf2c383d7bf340da9a3f02e2c23104a0e4fe8ac1a880c8e2dc92fbdacd9df"
    C_OTTO = "027ce055380348d7812d2ae7745701c9f93e70c1adeb2657f053f91df4f2843c71"
    NODE_1_HOP_TO_OTTO = "02d4b432058ec31e38f6f35d22a487b7db04c4bf70f201f601b66f7b4358242b03"
    NODE_2_HOP_TO_OTTO = "02c1321de5a127023115b90f33ae1244349269f5d18d3ea4014be697e700c07ccc"

    # print(oracle_lightning_network.network.get_edge_data(RENE, NODE_1_HOP_TO_OTTO, '624881x1940x0')['channel'].actual_liquidity)

    A = "03ea257b4bfbc1fde63be9deedadad8032fbfb082c35327f55d77ee89ab2cd3a89"
    B = "0344ae9dbca74941379d84594af16b6895c77257a12e6bcd62b23a5c665569809f"

    C = "0300207d05df00069fc218080c3b728b84ded4889112d0cf4e0d30a74fb5898e62"
    D = "0321bcb5ff9f039348e4522f47dea1cffb823631f3fe8bbdbadf349376b12fc087"

    tested_amount = 1000  # sats
    mu = 0
    base = 10_000_000

    # p1 = payment_session.pickhardt_pay(C, D, tested_amount, mu, base)
    # p2 = payment_session.pickhardt_pay(RENE, C_OTTO, tested_amount, mu=0, base=0)

    # print(p.fee_per_node)
    # print(oracle_lightning_network.network.get_edge_data(RENE, NODE_1_HOP_TO_OTTO, '624881x1940x0')['channel'].actual_liquidity)


    payments_to_simulate = 1000
    payments_amount = 1000

    # saving into a dictionary containing the capacities for each node
    nodes_capacities = oracle_lightning_network.nodes_capacities()

    # saving into a list the fees for each payment
    payments_fees = run_success_payments_simulation(payment_session, uncertainty_network, payments_to_simulate, payments_amount, mu, base)

    # saving into a dictionary the total fees for each node (that charged any fee)
    total_fees_per_node = compute_fees_per_node(payments_fees)

    df_total_fees_per_node = pd.DataFrame(total_fees_per_node.items(), columns=['node', 'total_fee'])
    # print(df_total_fees_per_node.items)

    # Mapping the capacities into the df total_fees (so we consider only the capacities of the nodes that earned fees)
    df_total_fees_per_node['capacity'] = df_total_fees_per_node['node'].map(nodes_capacities)
    results = df_total_fees_per_node

    print(results.head(100))

    export_results(results)

    return


if __name__ == "__main__":
    np.random.seed(1)
    start = time.time()
    main()
    end = time.time()
    print("\nSimulation time: " + str(round((end-start)/60, 2)) + " minutes")
