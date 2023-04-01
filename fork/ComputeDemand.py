import numpy as np
from pickhardtpayments.pickhardtpayments import OracleLightningNetwork
import math


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
    print(f"C = {C}\nTotal demand of node {v} = {C} * {f(capacity(v, graph))} = {total_demand}")
    return total_demand # return f(capacity(v)) times the sum calculated above


def f(c: float, dist_func: str):
    """
     the total demand entering/leaving node v might be proportional to f(capacity(v)),
     for some function f. For example, f(c) = sort(c).
     In this case f(x) = x
    """
    if dist_func == "linear":
        return c
    elif dist_func == "quadratic":
        return float(c**2)
    elif dist_func == "cubic":
        return float(c**3)
    elif dist_func == "exponential":
        return math.exp(c)

    return

def compute_C(graph: OracleLightningNetwork, dist_func: str):
    nodes_actual_capacities = graph.get_nodes_capacities()
    C = sum(np.array([f(val, dist_func) for val in nodes_actual_capacities.values()]))
    return C

def get_random_node_weighted_by_capacity(d, dist_func_name):
    """
    Randomly chooses a key from a dictionary proportional to its value.
    Args: d (dict): A dictionary with numeric values.
    Returns: Any: A key from the dictionary chosen randomly, proportional to its value.
    """
    # Get the keys and values from the dictionary
    keys = list(d.keys())

    values = np.array([f(val, dist_func_name) for val in d.values()])
    # values = np.array(list(f(d.values())))
    # print(values)
    # Normalize the values to create a probability distribution
    probs = values / np.sum(values)
    # Use numpy's random.choice() method to choose a key from the dictionary
    random_key = np.random.choice(keys, p=probs)
    return random_key
