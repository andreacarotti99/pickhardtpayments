import os, json
import statistics

def median_fee_per_millionth(data):
    channels = data['channels']
    fees = [c['fee_per_millionth'] for c in channels]
    median_fee = statistics.median(fees)
    return median_fee
def median_base_fee(data):
    channels = data['channels']
    base_fees = [c['base_fee_millisatoshi'] for c in channels]
    median_base_fee = statistics.median(base_fees)
    return median_base_fee
def avg_base_fee(data):
    channels = data['channels']
    total_base_fee = sum(c['base_fee_millisatoshi'] for c in channels)
    average_base_fee = total_base_fee / len(channels)
    return average_base_fee

def avg_fee_per_millionth(data):
    channels = data['channels']
    total_base_fee = sum(c['fee_per_millionth'] for c in channels)
    average_fee = total_base_fee / len(channels)
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

def main():
    current_file_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_file_directory, "SNAPSHOTS/" + "pickhardt_12apr2022_fixed.json")
    with open(file_path, 'r') as file:
        file_contents = file.read()
        data = json.loads(file_contents)
        print("Total number of nodes in the JSON file:", count_distinct_nodes(data))
        print("Avg base fee:", avg_base_fee(data))
        print("Median base fee:", median_base_fee(data))
        print("Avg fee per millionth:", avg_fee_per_millionth(data))
        print("Median fee per millionth:", median_fee_per_millionth(data))


        print_channel_info('033ac2f9f7ff643c235cc247c521663924aff73b26b38118a6c6821460afcde1b3',
                           '028c1f8d907879ee8691ddab3547e93c5ec2098cc0f38cc39c4ee989cb3a10ae71',
                           data)

        print_channel_info('028c1f8d907879ee8691ddab3547e93c5ec2098cc0f38cc39c4ee989cb3a10ae71',
                           '033ac2f9f7ff643c235cc247c521663924aff73b26b38118a6c6821460afcde1b3',
                           data)
    return

if __name__ == "__main__":
    main()
