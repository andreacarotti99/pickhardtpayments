import json
import os



def create_fake_snapshot(original_snapshot_json, new_file_converted_name, base_fee=1000, ppm=49):
    """
    creates a fake core-lightning snapshot with fixed fees (base_fee and ppm) given an original
    snapshot
    """
    with open(original_snapshot_json, 'r') as file:
        file_contents = file.read()
        f = json.loads(file_contents)
        converted_channels = {"channels": []}
        for channel in f["channels"]:
            new_channel = {
                "source": channel["source"],
                "destination": channel["destination"],
                "short_channel_id": channel["short_channel_id"],
                "public": channel["public"],
                "satoshis": channel["satoshis"],
                "amount_msat": channel["amount_msat"],
                "message_flags": channel["message_flags"],
                "channel_flags": channel["channel_flags"],
                "active": channel["active"],
                "last_update": channel["last_update"],
                "base_fee_millisatoshi": base_fee,
                "fee_per_millionth": ppm,
                "delay": channel["delay"],
                "htlc_minimum_msat": channel["htlc_minimum_msat"],
                "htlc_maximum_msat": channel["htlc_maximum_msat"],
                "features": ""
            }
            converted_channels["channels"].append(new_channel)
    with open(new_file_converted_name, "w") as outfile:
        outfile.write(json.dumps(converted_channels, indent=4))
        print(f"New file {new_file_converted_name} with base_fee = {base_fee} and ppm = {ppm} was successfully created")
    return


file_to_convert = "lntrafficanalysis_2019_converted.json"
file_path = os.path.join("..", "SNAPSHOTS", file_to_convert)
create_fake_snapshot(file_path, "new_file.json")
