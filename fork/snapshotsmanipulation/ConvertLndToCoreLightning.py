import json
import os


def from_lnd_to_corelightning(json_file, file_name):
    with open(json_file, 'r') as file:
        # Read the contents of the file
        file_contents = file.read()
        lnd = json.loads(file_contents)
        ln_channels = {"channels": []}
        for channel in lnd["edges"]:
            if channel["node1_policy"] is not None and channel["node2_policy"] is not None:
                new_channel_1 = {
                    "source": channel["node1_pub"],
                    "destination": channel["node2_pub"],
                    "short_channel_id": channel["channel_id"],
                    "public": True,
                    "satoshis": int(channel["capacity"]),
                    "amount_msat": str(int(channel["capacity"])*1000) + "msat",
                    "message_flags": 1,
                    "channel_flags": 0,
                    "active": True,
                    "last_update": channel["last_update"],
                    "base_fee_millisatoshi": int(channel["node1_policy"]["fee_base_msat"]),
                    "fee_per_millionth": int(channel["node1_policy"]["fee_rate_milli_msat"]),
                    "delay": channel["node1_policy"]["time_lock_delta"],
                    "htlc_minimum_msat": channel["node1_policy"]["min_htlc"] + "msat",
                    "htlc_maximum_msat": str(int((channel["node2_policy"]["min_htlc"]))*1000) + "msat",
                    "features": ""
                }
                new_channel_2 = {
                    "source": channel["node2_pub"],
                    "destination": channel["node1_pub"],
                    "short_channel_id": channel["channel_id"],
                    "public": True,
                    "satoshis": int(channel["capacity"]),
                    "amount_msat": str(int(channel["capacity"])*1000) + "msat",
                    "message_flags": 1,
                    "channel_flags": 0,
                    "active": True,
                    "last_update": channel["last_update"],
                    "base_fee_millisatoshi": int(channel["node2_policy"]["fee_base_msat"]),
                    "fee_per_millionth": int(channel["node2_policy"]["fee_rate_milli_msat"]),
                    "delay": channel["node2_policy"]["time_lock_delta"],
                    "htlc_minimum_msat": channel["node2_policy"]["min_htlc"] + "msat",
                    "htlc_maximum_msat": str(int((channel["node2_policy"]["min_htlc"]))*1000) + "msat",
                    "features" : ""
                }
                ln_channels["channels"].append(new_channel_1)
                ln_channels["channels"].append(new_channel_2)
    with open(file_name, "w") as outfile:
        outfile.write(json.dumps(ln_channels, indent=4))
    print("Json file converted from lnd to core-lightning successfully created!")
    print("File name: " + file_name)
    return


file_to_convert = "lntrafficanalysis_2019.json"
file_path = os.path.join("..", "SNAPSHOTS", file_to_convert)
from_lnd_to_corelightning(file_path, "new_file.json")
