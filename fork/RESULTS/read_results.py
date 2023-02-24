import pandas as pd
from matplotlib import pyplot as plt
import os

RESULTS_FILE = "results_10000trans_1000SAT_0mu_pickhardt_12apr2022_fixed.csv"




def print_info_results(df):
    # print("Avg deg: " + str(df['degree'].mean()))
    print("Avg capacity of each node: " + str(df['capacity'].mean()))
    print("Median capacity of each node: " + str(df['capacity'].median()))
    print("Avg fee earned by each node: " + str(df['total_fee'].mean()))
    print("Median fee earned by each node: " + str(df['total_fee'].median()))
    # print("Avg routed trans: " + str(df['routed_transactions'].mean()))
    print("Number of nodes that earned fees: " + str(df.shape[0]))
    return

def apply_filters(df):
    # df.loc[df['total_fee'] > 20_000_000, 'total_fee'] = 20_000_000
    # df = df.loc[df['degree'] > 20]
    # df = df.loc[df['total_fee'] >= 100]

    df = df.loc[df['routed_payments'] > 20]
    df = df.loc[df['routed_payments'] != 28]

    # df = df.loc[df['routed_transactions'] <= 100]
    # df.loc[df['ratio'] > 0.0004, 'ratio'] = 0.0004
    # df = df.loc[df['ratio'] > 0.000005]
    # df = df.loc[df['capacity'] >= 500_000_000]
    return df

def main():
    screen_size = plt.rcParams["figure.figsize"]
    plt.rcParams["figure.figsize"] = (screen_size[0]*2.1, screen_size[1]*1.5)


    current_file_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_file_directory, RESULTS_FILE)
    df = pd.read_csv(file_path)
    df['ratio'] = df['total_fee'].divide(df['capacity'], fill_value=0)
    df = df.sort_values(by='capacity',ascending=False)

    # Print info about the results
    print_info_results(df)

    # Performing the filtering to the results
    df = apply_filters(df)


    ax = df.plot(x='node', y='total_fee',kind='bar')
    plt.title("Total fee for each node")
    plt.suptitle("CAP of each node decreases (--->) - DESC")
    plt.xlabel('node')
    plt.ylabel('total_fee for each node')
    # ax.set_xticklabels(df['node'],rotation=90, fontsize=4)
    ax.set_xticklabels(df['routed_payments'],rotation=90, fontsize=3)

    plt.figtext(0.15, 0.01, 'Filter applied: # routed payments > 20, removed outlier node: 02...ce76b', fontsize=12, ha='left')


    fig = ax.get_figure()
    # Just if you want to save the results in a file
    fig.savefig('total_fee_mu_0_pickhardt_fixed_original.png')
    plt.show()
    return



if __name__ == "__main__":
    main()





