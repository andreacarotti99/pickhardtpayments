# Scope of the fork

The scope of this fork of `pickhardtpayments` is trying to perform analysis using the [Pickhardt Payments](https://ln.rene-pickhardt.de#PickhardtPayments) routing algorithm and explore how
nodes in the network can earn more from routing payments and how to discourage the formation of large hubs in the Lightning Network.

## Run a simulation of multiple payments

base: is the base fee threshold, edges with base_fee over the threshold are removed from the graph.

distribution: can be "uniform" or "weighted_by_capacity", depending on how we want the payment to be distributed in the graph.

dist_func: is the distribution function according to the capacity of the node that can be "linear", "quadratic", "cubic" or "exponential".
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

#### Export the results of the simulation

```
export = ExportResults(simulation=s)
export.export_results()
```

#### Get the fees of a given node

```
node_pub_key = '02da0713ab1b12eeb01f212944a435077f39f1b767ee5c24b01cdb4b0b9377b66f'
node_pub_key_fees = simulation.get_fees(node_pub_key)
```

#### Get the ratio (fees / capacity) of a given node

```
node_pub_key = '02da0713ab1b12eeb01f212944a435077f39f1b767ee5c24b01cdb4b0b9377b66f'
node_pub_key_ratio = simulation.get_ratio(node_pub_key)
```

