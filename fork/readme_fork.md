# Scope of the fork

The scope of this fork of `pickhardtpayments` is trying to perform analysis using the [Pickhardt Payments](https://ln.rene-pickhardt.de#PickhardtPayments) routing algorithm and explore how
nodes in the network can earn more from routing payments and how to discourage the formation of large hubs in the Lightning Network.

## Run a simulation of multiple payments

```
base = 20_000
channel_graph = ChannelGraph(snapshot_path)
channel_graph.transform_channel_graph_to_simpler(1000)
s = Simulation(channel_graph, base)
s.run_success_payments_simulation(
    payments_to_simulate=10000,
    payments_amount=10_000,
    mu=1000,
    base=base,
    distribution="weighted_by_capacity",
    dist_func="linear",
    verbose=False
)
```
