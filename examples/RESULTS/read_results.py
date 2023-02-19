import pandas as pd
from matplotlib import pyplot as plt
import os

RESULTS_FILE = "results.csv"


def print_info_results(df):
    # print("Avg deg: " + str(df['degree'].mean()))
    print("Avg cap: " + str(df['capacity'].mean()))
    print("Avg fee: " + str(df['total_fee'].mean()))
    # print("Avg routed trans: " + str(df['routed_transactions'].mean()))
    print("Number of nodes: " + str(df.shape[0]))
    return

def apply_filters(df):
    df.loc[df['total_fee'] > 1_000_000, 'total_fee'] = 1_000_000
    # df = df.loc[df['degree'] > 20]
    # df = df.loc[df['total_fee'] >= 125]
    # df = df.loc[df['routed_transactions'] >= 40]
    # df = df.loc[df['routed_transactions'] <= 100]
    # df.loc[df['ratio'] > 0.0004, 'ratio'] = 0.0004
    # df = df.loc[df['ratio'] > 0.000005]
    df = df.loc[df['capacity'] >= 250_000_000]
    return df

def main():
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
    plt.title("fee for each node")
    plt.suptitle("CAP of each node decreases (->) - DESC")
    plt.xlabel('node')
    plt.ylabel('fee')
    ax.set_xticklabels(df['node'],rotation=90, fontsize=4)
    # ax.set_xticklabels(df['node'],rotation=90, fontsize=4)
    plt.show()
    return



if __name__ == "__main__":
    main()





