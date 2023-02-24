import os
import random

import numpy as np

from pickhardtpayments.pickhardtpayments import OracleLightningNetwork


def capacity(v: str, graph: OracleLightningNetwork):
    """
    returns the capacity of a node given the node key and the network
    """
    return graph.nodes_capacities()[v]

def total_demand(v: str, graph: OracleLightningNetwork):
    """
    Computes the total demand for vertex v in a graph with vertex set V,
    capacity function capacity, and demand function f.
    """
    C = compute_C(graph)  # calculate the sum of f(capacity(u)) for all u in V
    total_demand = f(capacity(v, graph)) * C
    print(f"C = {C}\nTotal demand of node {v}: {total_demand}")
    return total_demand # return f(capacity(v)) times the sum calculated above


def f(c):
    """
     the total demand entering/leaving node v might be proportional to f(capacity(v)),
     for some function f. For example, f(c) = sort(c).
     In this case f(x) = x
    """
    return c

def compute_C(graph: OracleLightningNetwork):
    C = sum(f(graph.nodes_capacities().values()))
    return C

def get_random_node_weighted_by_capacity(d):
    """
    Randomly chooses a key from a dictionary proportional to its value.

    Args:
        d (dict): A dictionary with numeric values.

    Returns:
        Any: A key from the dictionary chosen randomly, proportional to its value.
    """
    # Get the keys and values from the dictionary
    keys = list(d.keys())
    values = np.array(list(d.values()))

    # Normalize the values to create a probability distribution
    probs = values / np.sum(values)

    # Use numpy's random.choice() method to choose a key from the dictionary
    random_key = np.random.choice(keys, p=probs)

    return random_key
