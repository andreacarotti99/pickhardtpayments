import pandas as pd
from matplotlib import pyplot as plt
import os
from pickhardtpayments.fork.ComputeDemand import compute_C
from pickhardtpayments.pickhardtpayments import ChannelGraph, OracleLightningNetwork

# INTERESTING: andamento \_/
# RESULTS_FILE = "results_1000trans_1000SAT_0mu_pickhardt_12apr2022_fixed_const_fees_dist_weig.csv"

RESULTS_FILE = "results_1000trans_1000SAT_0mu_cosimo_19jan2023_converted_dist_uniform.csv"

def print_info_results(df):
    print("Avg capacity of each node: " + str(df['capacity'].mean()))
    print("Median capacity of each node: " + str(df['capacity'].median()))
    print("Avg fee earned by each node: " + str(df['total_fee'].mean()))
    print("Median fee earned by each node: " + str(df['total_fee'].median()))
    print("Avg routed trans: " + str(df['routed_payments'].mean()))
    print("Number of nodes that earned fees: " + str(df.shape[0]))
    return

def apply_filters(df):
    # df.loc[df['ratio'] > 0.0001, 'ratio'] = 0.0001
    # df = df.loc[df['degree'] > 20]
    # df = df.loc[df['total_fee'] >= 100]
    # df = df.loc[df['node'] != "0294e9ad2727d623fb22870e32f167d4d014e2f7adccb0926802f0bd4d17959093"]
    # df = df.loc[df['routed_payments'] != 28]
    # df = df.loc[df['routed_payments'] >= 3]
    # df.loc[df['ratio'] > 0.0004, 'ratio'] = 0.0004
    # df = df.loc[df['ratio'] <= 0.001]
    # df = df.loc[df['capacity'] >= 25_000_000]
    # df = df.loc[df['capacity'] >= 200_000_000]
    # df = df.loc[df['capacity'] <= 1_000_000_000]
    # df = df.head(56)
    # df = df.tail(56)
    lowest_cap_nodes_mean = df.tail(10)['ratio'].mean() * 100
    lowest_cap_nodes_median = df.tail(10)['ratio'].median() * 100
    highest_cap_nodes_mean = df.head(10)['ratio'].mean() * 100
    highest_cap_nodes_median = df.head(10)['ratio'].median() * 100
    print(f"lowest_cap_nodes_mean: {lowest_cap_nodes_mean}")
    print(f"lowest_cap_nodes_median: {lowest_cap_nodes_median}")
    print(f"highest_cap_nodes_mean: {highest_cap_nodes_mean}")
    print(f"highest_cap_nodes_median: {highest_cap_nodes_median}")
    return df

def f_df(x):
    return x**2

def setup_graphics():
    screen_size = plt.rcParams["figure.figsize"]
    plt.rcParams["figure.figsize"] = (screen_size[0]*2.1, screen_size[1]*1.5)

def read_file():
    current_file_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_file_directory, RESULTS_FILE)
    df = pd.read_csv(file_path)
    return df

def main():
    snapshot_file = "pickhardt_12apr2022_fixed.json"
    channel_graph = ChannelGraph("../SNAPSHOTS/" + snapshot_file)
    oracle_lightning_network = OracleLightningNetwork(channel_graph)
    C = compute_C(oracle_lightning_network, "quadratic")

    # Setting up the size of the matplotlib graphics
    setup_graphics()

    # Reading the file provided at the beginning of the script
    df = read_file()

    df['ratio'] = df['total_fee'].divide(df['capacity'], fill_value=0)

    # Create a colum with routed_payments^2
    df = df.assign(new_routed_payments=df['routed_payments'] * df['routed_payments'])

    # Create a column average fee per payment to get the average fee for each payment
    df = df.assign(avg_fee_per_payment=df['total_fee']/df['routed_payments'])

    # Create a column 'new_fees' where we compute the expected fees earned by each node with the new number of routed payments
    df = df.assign(new_fees=df['new_routed_payments']*df['avg_fee_per_payment'])

    # Create a column new ratio taking into account the expected new fees earned divided by the capacity of each node
    df = df.assign(new_ratio=df['new_fees'] / df['capacity'])

    # Applying function f(x) = x^2
    df['f_capacity'] = df['capacity'].apply(f_df)

    df = df.assign(demand_prof=C * df['f_capacity'])
    df = df.assign(fees_prof=df['avg_fee_per_payment'] * df['demand_prof'])
    df = df.assign(ratio_prof=df['fees_prof']/df['capacity'])


    df = df.sort_values(by='capacity', ascending=False)

    df = df.head(600)

    # Print info about the results
    print_info_results(df)

    # Performing the filtering to the results
    df = apply_filters(df)

    # ax = df.plot(x='node', y='ratio',kind='line')
    ax = df.plot(x='node', y='ratio', kind='bar')
    plt.title("Ratio for each node")
    plt.suptitle("CAP of each node decreases (--->) - DESC")
    plt.xlabel('node')
    plt.ylabel('ratio for each node')
    plt.yscale('log')
    # ax.set_xticklabels(df['node'],rotation=90, fontsize=4)
    ax.set_xticklabels(df['routed_payments'],rotation=90, fontsize=3)
    # plt.figtext(0.15, 0.01, 'Filter applied: # routed payments > 20, removed outlier node: 02...ce76b', fontsize=12, ha='left')
    fig = ax.get_figure()
    # Just if you want to save the results in a file
    # results_10000trans_1000SAT_10mu_pickhardt_12apr2022_fixed_const_fees_dist_norm.csv
    # fig.savefig('ratio_mu_10_pickhardt_fixed_const_fees_dist_norm.png')
    plt.show()
    return



if __name__ == "__main__":
    main()





