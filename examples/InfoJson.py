import os, json

def count_distinct_nodes(json_file):
    with open(json_file, 'r') as file:
        file_contents = file.read()
        nodes = set()
        data = json.loads(file_contents)
        for channel in data['channels']:
            nodes.add(channel['source'])
            nodes.add(channel['destination'])
        return len(nodes)

def main():
    current_file_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_file_directory, "listchannels20220412.json")
    count_distinct_nodes(file_path)
    print("Total number of nodes in the JSON file:", count_distinct_nodes(file_path))
    return

if __name__ == "__main__":
    main()
