import networkx as nx
import pandas as pd

from pickhardtpayments.pickhardtpayments import ChannelGraph

base = 20_000
channel_graph = ChannelGraph("../fork/SNAPSHOTS/cosimo_19jan2023_converted.json")
file_name = "results_1000trans_10000SAT_1000mu_cosimo_19jan2023_converted_dist_weig_linear_1.csv"
result_path = "../fork/RESULTS/replicate_best_strategy/decrease_liquidity_send_paym_and_replicate/" + file_name
df = pd.read_csv(result_path)
df = df.sort_values('ratio', ascending=False)
HRNs = df['node'].tolist()

print(df.head())

G = channel_graph.network


for i in range(len(HRNs)):
    if HRNs[i].startswith("HRN_") or HRNs[i].startswith("HCN_"):
        HRNs[i] = HRNs[i][4:]
    if HRNs[i].startswith("THIEF_"):
        HRNs[i] = HRNs[i][6:]

    print(f"{G.degree(HRNs[i])}\t{nx.eigenvector_centrality_numpy(G)[HRNs[i]]}")
