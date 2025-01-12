import pandas as pd
from matplotlib import pyplot as plt
import os
from pickhardtpayments.fork.ComputeDemand import compute_C
from pickhardtpayments.pickhardtpayments import ChannelGraph, OracleLightningNetwork


RESULTS_FILE = "decrease_liquidity_send_paym_and_replicate/results_1000trans_10000SAT_10mu_cosimo_19jan2023_converted_dist_weig_linear_1.csv"

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
    df['node'] = df['node'].str[:6]
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

    # Setting up the size of the matplotlib graphics
    setup_graphics()

    # Reading the file provided at the beginning of the script
    df = read_file()

    df['ratio'] = df['total_fee'].divide(df['capacity'], fill_value=0)

    df = df.sort_values(by='capacity', ascending=False)

    df = df.head(400)
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
    ax.set_xticklabels(df['node'],rotation=90, fontsize=3)
    # plt.figtext(0.15, 0.01, 'Filter applied: # routed payments > 20, removed outlier node: 02...ce76b', fontsize=12, ha='left')
    fig = ax.get_figure()
    # Just if you want to save the results in a file
    # results_10000trans_1000SAT_10mu_pickhardt_12apr2022_fixed_const_fees_dist_norm.csv
    # fig.savefig('ratio_mu_10_pickhardt_fixed_const_fees_dist_norm.png')
    plt.show()
    return



if __name__ == "__main__":
    main()





