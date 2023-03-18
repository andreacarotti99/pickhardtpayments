import time
import pandas as pd
from pickhardtpayments.pickhardtpayments import UncertaintyNetwork
from pickhardtpayments.pickhardtpayments import OracleLightningNetwork
from pickhardtpayments.pickhardtpayments import SyncSimulatedPaymentSession

from pickhardtpayments.pickhardtpayments import ChannelGraph

start = time.time()
snapshot_file = "cosimo_19jan2023_converted.json"
channel_graph = ChannelGraph("SNAPSHOTS/" + snapshot_file)
base = 20_000

# RENE_OTTO
RENE = "03efccf2c383d7bf340da9a3f02e2c23104a0e4fe8ac1a880c8e2dc92fbdacd9df"
OTTO = "027ce055380348d7812d2ae7745701c9f93e70c1adeb2657f053f91df4f2843c71"

# RANDOM_1
A = "0390b5d4492dc2f5318e5233ab2cebf6d48914881a33ef6a9c6bcdbb433ad986d0"
B = "03148dba0e3cb3c15250fb6a40d6456b109581570448aa72d0a4e1a56eaf81d970"

# RANDOM_2
C = "035e4ff418fc8b5554c5d9eea66396c227bd429a3251c8cbc711002ba215bfc226"
D = "03b2d5c9409d42e0b13abfc23cd3908a6cec05fadf602dc4e98b1a714528289437"

# RANDOM_3
E = "022812f0e94549f4543c8f796b4c21f942fbbe82538a6947082560084f1c2626d1"
F = "037667a61f11bdfd28a04c8c2031c388ff8cc52d00a87e62910bf03e1667312d64"

# RANDOM_4
G = "02b7f410d4b9d62c3e94dcf8d6b7e960e44edc21de52a5c3856c99c8cfbcb0b8a4"
H = "03a5fc8c266931d54cae62e6745997350d05b834ce49f845a5025844e3cd7dc589"

mus = [0, 10, 100, 500, 1000, 5000, 10_000, 100_000, 1_000_000]
amts = [1000, 10_000, 100_000, 1_000_000, 10_000_000]
tuples = []

'''
uncertainty_network = UncertaintyNetwork(channel_graph, base)
oracle_lightning_network = OracleLightningNetwork(channel_graph)
payment_session = SyncSimulatedPaymentSession(oracle_lightning_network, uncertainty_network,
                                              prune_network=False)
p1 = payment_session.pickhardt_pay(src=E, dest=F, amt=1_000_000, mu=1000, base=base, verbose=True)
payment_session.forget_information()

print(p1.expectation_to_deliver_round_1)
'''

for i in range(len(amts)):
    for j in range(len(mus)):
        uncertainty_network = UncertaintyNetwork(channel_graph, base)
        oracle_lightning_network = OracleLightningNetwork(channel_graph)
        payment_session = SyncSimulatedPaymentSession(oracle_lightning_network, uncertainty_network,
                                                      prune_network=False)
        p1 = payment_session.pickhardt_pay(src=G, dest=H, amt=amts[i], mu=mus[j], base=base, verbose=True)
        payment_session.forget_information()

        if p1.fee_per_node is not None:
            tuples.append((amts[i], mus[j], sum(p1.fee_per_node.values()), p1.successful, p1.expectation_to_deliver_round_1))
        else:
            tuples.append((amts[i], mus[j], -1, p1.successful, -1))
            break

columns = ['amount', 'mu', 'total_fees', 'successful', 'expectation_round_1']
df = pd.DataFrame(tuples, columns=columns)
df.to_csv('amount_fees_mu.csv', index=False)
print(df)


end = time.time()
print("\nSimulation time: " + str(round((end - start) / 60, 2)) + " minutes")
