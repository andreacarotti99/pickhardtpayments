import os, json

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
    file_path = os.path.join(current_file_directory, "listchannels20220412.json")
    with open(file_path, 'r') as file:
        file_contents = file.read()
        data = json.loads(file_contents)
        print("Total number of nodes in the JSON file:", count_distinct_nodes(data))
        '''print_channel_info('03efccf2c383d7bf340da9a3f02e2c23104a0e4fe8ac1a880c8e2dc92fbdacd9df',
                           '02d4b432058ec31e38f6f35d22a487b7db04c4bf70f201f601b66f7b4358242b03',
                           data)
        print_channel_info('02d4b432058ec31e38f6f35d22a487b7db04c4bf70f201f601b66f7b4358242b03',
                           '02c1321de5a127023115b90f33ae1244349269f5d18d3ea4014be697e700c07ccc',
                           data)'''


        print_channel_info('02c1321de5a127023115b90f33ae1244349269f5d18d3ea4014be697e700c07ccc',
                           '027ce055380348d7812d2ae7745701c9f93e70c1adeb2657f053f91df4f2843c71',
                           data)

        print_channel_info('027ce055380348d7812d2ae7745701c9f93e70c1adeb2657f053f91df4f2843c71',
                           '02c1321de5a127023115b90f33ae1244349269f5d18d3ea4014be697e700c07ccc',
                           data)



    return

if __name__ == "__main__":
    main()
