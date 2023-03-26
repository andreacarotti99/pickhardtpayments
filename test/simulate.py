from pickhardtpayments.fork.Simulation import Simulation
from pickhardtpayments.pickhardtpayments import ChannelGraph

base = 20_000
channel_graph = ChannelGraph("../fork/SNAPSHOTS/" + "cosimo_19jan2023_converted.json")
s = Simulation(channel_graph, base)
s.run_success_payments_simulation(
    payments_to_simulate=10,
    payments_amount=10_000,
    mu=1000,
    base=base,
    distribution="weighted_by_capacity",
    dist_func="linear",
    verbose=False
)

print(s.final_payment_fees_list)

