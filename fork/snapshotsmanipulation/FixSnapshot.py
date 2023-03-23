import json
from tqdm import tqdm

def main():
    with open('../SNAPSHOTS/pickhardt_12apr2022.json') as f:
        data = json.load(f)
    new_channels = []
    for channel in tqdm(data['channels']):
        opposite_channel = next((c for c in data['channels'] if c['source'] == channel['destination'] and c['destination'] == channel['source']), None)
        if opposite_channel is not None:
            new_channels.append(channel)
    new_data = {'channels': new_channels}
    with open('aaaa.json', 'w') as f:
        json.dump(new_data, f, indent=2)
    return


main()
