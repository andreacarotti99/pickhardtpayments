import os, json
import statistics

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def median_satoshis_channel_cap(data):
    channels = data['channels']
    fees = [c['satoshis'] for c in channels]
    median_fee = statistics.median(fees)
    return median_fee

def median_fee_per_millionth(data):
    channels = data['channels']
    fees = [c['fee_per_millionth'] for c in channels if c['fee_per_millionth'] < 20_000]
    median_fee = statistics.median(fees)
    return median_fee


def median_base_fee(data):
    channels = data['channels']
    base_fees = [c['base_fee_millisatoshi'] for c in channels if c['base_fee_millisatoshi'] < 20_000]
    median_base_fee = statistics.median(base_fees)
    return median_base_fee


def avg_base_fee(data):
    channels = data['channels']
    base_fees = [c['base_fee_millisatoshi'] for c in channels if c['base_fee_millisatoshi'] < 20_000]
    average_base_fee = statistics.mean(base_fees)
    return average_base_fee


def avg_fee_per_millionth(data):
    channels = data['channels']
    total_base_fee = [c['fee_per_millionth'] for c in channels if c['fee_per_millionth'] < 20_000]
    average_fee = statistics.mean(total_base_fee)
    return average_fee


def print_channel_info(source, dest, data):
    for channel in data['channels']:
        if channel['source'] == source and channel['destination'] == dest:
            formatted_channel = json.dumps(channel, indent=4)
            print(formatted_channel)
    return


def count_distinct_nodes(data):
    nodes = set()
    for channel in data['channels']:
        nodes.add(channel['source'])
        nodes.add(channel['destination'])
    return len(nodes)


def plot_fee_per_millionth_distribution(data):
    fee_per_millionth = [channel["fee_per_millionth"] for channel in data['channels']]
    fee_per_millionth_counts = {}
    for value in fee_per_millionth:
        if value not in fee_per_millionth_counts:
            fee_per_millionth_counts[value] = 1
        else:
            fee_per_millionth_counts[value] += 1

    df_fee_per_millionth = pd.DataFrame(list(fee_per_millionth_counts.items()), columns=["fee_per_millionth", "frequency"])
    df_fee_per_millionth = df_fee_per_millionth.sort_values(by='fee_per_millionth', ascending=True)
    df_fee_per_millionth = df_fee_per_millionth.loc[df_fee_per_millionth['frequency'] > 50]

    # Set plot title and axis labels


    ax = df_fee_per_millionth.plot(x='fee_per_millionth', y='frequency', kind='bar')
    ax.set_xticklabels(df_fee_per_millionth['fee_per_millionth'], rotation=90, fontsize=5)


    plt.title("Distribution of Fee per millionth (millisatoshi) for Lightning Channels")
    plt.xlabel("Fee per millionth (millisatoshi)")
    plt.ylabel("Number of Channels")

    # Show plot
    plt.show()
    return
def plot_base_fee_distribution(data):
    # Extract base_fee_millisatoshi values from channels
    base_fees = [channel["base_fee_millisatoshi"] for channel in data['channels']]

    base_fee_value_counts = {}
    for value in base_fees:
        if value not in base_fee_value_counts:
            base_fee_value_counts[value] = 1
        else:
            base_fee_value_counts[value] += 1

    df_base_fee = pd.DataFrame(list(base_fee_value_counts.items()), columns=["base_fee", "frequency"])
    df_base_fee = df_base_fee.sort_values(by='base_fee', ascending=True)
    df_base_fee = df_base_fee.loc[df_base_fee['frequency'] > 50]

    ax = df_base_fee.plot(x='base_fee', y='frequency', kind='bar')

    ax.set_xticklabels(df_base_fee['base_fee'], rotation=90, fontsize=6)

    plt.title("Distribution of Base Fee (millisatoshi) for Lightning Channels")
    plt.xlabel("Base Fee (millisatoshi)")
    plt.ylabel("Number of Channels")
    # Set plot title and axis labels
    # Show plot
    plt.show()

    return

def plot_capacity_distribution(data):
    satoshis = pd.Series([channel["satoshis"] for channel in data["channels"]])

    bin_size = 100_000

    bins = pd.interval_range(start=0, end=15_000_000, freq=bin_size)

    satoshis_binned = pd.cut(satoshis, bins=bins)
    satoshis_count = satoshis_binned.value_counts().sort_index()

    bin_lefts = [interval.left for interval in satoshis_count.index]


    plt.figure(figsize=(14, 7))
    plt.bar(bin_lefts, satoshis_count, width=bin_size, align='edge')

    plt.xlabel('Channel Capacity (satoshis)', fontsize=12)
    plt.ylabel('Count')
    plt.title('Capacity Distribution')
    plt.yscale("log")
    tick_interval = 1
    plt.xticks(bin_lefts[::tick_interval], rotation=90, fontsize=5)
    plt.show()






def main():
    current_file_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_file_directory, "../SNAPSHOTS/" + "cosimo_19jan2023_converted.json")
    with open(file_path, 'r') as file:
        file_contents = file.read()
        data = json.loads(file_contents)
        print("Total number of nodes in the JSON file:", count_distinct_nodes(data))
        print("Avg base fee:", avg_base_fee(data))
        print("Median base fee:", median_base_fee(data))
        print("Avg fee per millionth:", avg_fee_per_millionth(data))
        print("Median fee per millionth:", median_fee_per_millionth(data))
        print(f"Median satoshis per channel: {median_satoshis_channel_cap(data)}")

        plot_capacity_distribution(data)

        '''
        print_channel_info('033ac2f9f7ff643c235cc247c521663924aff73b26b38118a6c6821460afcde1b3',
                           '028c1f8d907879ee8691ddab3547e93c5ec2098cc0f38cc39c4ee989cb3a10ae71',
                           data)

        print_channel_info('028c1f8d907879ee8691ddab3547e93c5ec2098cc0f38cc39c4ee989cb3a10ae71',
                           '033ac2f9f7ff643c235cc247c521663924aff73b26b38118a6c6821460afcde1b3',
                           data)
        '''

        plot_base_fee_distribution(data)
        plot_fee_per_millionth_distribution(data)

    return


main()
