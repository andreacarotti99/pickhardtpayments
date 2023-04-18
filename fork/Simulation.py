import os
import time
import random

import pandas as pd
from tqdm import tqdm

from pickhardtpayments.fork.ComputeDemand import get_random_node_weighted_by_capacity
from pickhardtpayments.pickhardtpayments import SyncSimulatedPaymentSession, UncertaintyNetwork, OracleLightningNetwork, \
    ChannelGraph


class Simulation:

    def __init__(self, channel_graph: ChannelGraph, base: int, oracle_lightning_network=None):
        self._final_payment_fees_list = None
        self._payments_ratios_per_node = None
        self._payments_fees_per_transaction = None
        self._payments_routing_nodes_per_transaction = None
        self._payments_fees_per_node = None
        self._routed_transactions_per_node = None

        self._channel_graph = channel_graph
        self._base = base

        self._uncertainty_network = UncertaintyNetwork(self._channel_graph, self._base)

        if oracle_lightning_network is None:
            self._oracle_lightning_network = OracleLightningNetwork(self._channel_graph)
        else:
            self._oracle_lightning_network = oracle_lightning_network

        self._payment_session = SyncSimulatedPaymentSession(self._oracle_lightning_network, self._uncertainty_network,
                                                            prune_network=False)

        # At each new run these parameters get updated
        self._payments_to_simulate = None,
        self._payments_amount = None,
        self._mu = None,
        self._base = None,
        self._distribution = None,
        self._dist_func = None

    @property
    def payment_session(self):
        return self._payment_session

    @property
    def uncertainty_network(self):
        return self._uncertainty_network

    def run_success_payments_simulation(self,
                                        payments_to_simulate: int = 1000,
                                        payments_amount: int = 1000,
                                        mu: float = 10,
                                        base: int = 1000,
                                        distribution: str = "uniform",
                                        dist_func: str = "",
                                        verbose=False,
                                        payments_amount_distribution: str = "fixed"):
        """
        Run a simulation of Pickhardt payments, every time there is an unsuccessful payment it retries.
        """

        start = time.time()

        self._payments_to_simulate = payments_to_simulate
        self._payments_amount = payments_amount
        self._mu = mu
        self._base = base
        self._distribution = distribution
        self._dist_func = dist_func
        self._payments_amount_distribution = payments_amount_distribution

        print(f"\nStarting simulation with {payments_to_simulate} payments of {payments_amount} sat.")
        print(f"mu = {mu}")
        print(f"base = {base}")
        print(f"distribution = {distribution}")
        if dist_func != "":
            print(f"demand function f = {dist_func}")
        if distribution == "weighted_by_capacity":
            if dist_func == "":
                print("You need to specify the distribution function!")
                exit()

        paymentNumber = 0
        payments_fees_per_node_list = []
        payments_routing_nodes = []
        final_payment_fees_list = []
        self._payment_session.forget_information()
        n_capacities = self._channel_graph.get_nodes_capacities()
        if not verbose:
            pbar = tqdm(total=payments_to_simulate)

        while paymentNumber < payments_to_simulate:
            if verbose:
                print("*" * 90)
                print(f"Payment: {paymentNumber + 1}")
            src, dst = self._choose_src_and_dst(distribution, n_capacities, dist_func)
            if verbose:
                print(f"Source: {src}\nDestination: {dst}")
            # perform the payment

            if payments_amount_distribution == "random":
                payments_amount = random.randint(10000, 1000000)

            try:
                payment = self._payment_session.pickhardt_pay(src, dst, payments_amount, mu, base, verbose)
            except KeyError:
                continue
            if payment.successful:
                paymentNumber += 1
                payments_fees_per_node_list.append(payment.fee_per_node)
                payments_routing_nodes.append(payment.routing_nodes)

                fees_list = [value for value in payment.fee_per_node.values()]
                payment.final_payment_fees = sum(fees_list) if fees_list else 0
                final_payment_fees_list.append(payment.final_payment_fees)
                # print("fees:", payment.settlement_fees)
                # print("correct fees", payment.final_payment_fees)
                if not verbose:
                    pbar.update(1)

        self.payments_fees_per_transaction = payments_fees_per_node_list
        self.payments_routing_nodes_per_transaction = payments_routing_nodes
        self._final_payment_fees_list = final_payment_fees_list
        end = time.time()
        print("\nSimulation time: " + str(round((end - start) / 60, 2)) + " minutes")
        return

    def _choose_src_and_dst(self, distribution: str, n_capacities: dict, dist_func: str):
        """
        randomly chooses two nodes as source and destination of the transaction given a probability distribution
        """

        if distribution == "uniform":
            src = self.channel_graph.get_random_node_uniform_distribution()
            dst = self.channel_graph.get_random_node_uniform_distribution()
            # src = self._uncertainty_network.get_random_node_uniform_distribution()
            # dst = self._uncertainty_network.get_random_node_uniform_distribution()
            while dst == src:
                dst = self._uncertainty_network.get_random_node_uniform_distribution()
        elif distribution == "weighted_by_capacity":
            src = get_random_node_weighted_by_capacity(n_capacities, dist_func)
            dst = get_random_node_weighted_by_capacity(n_capacities, dist_func)
            while dst == src:
                dst = get_random_node_weighted_by_capacity(n_capacities, dist_func)

        else:
            print("Distribution not found")
            exit()
        return src, dst

    def _compute_routing_nodes(self, payments_routing_nodes):
        """
        takes a list of dictionaries containing the number of routed payments of the nodes
        """
        routing_nodes = {}
        for p in payments_routing_nodes:
            for node, routed_payments in p.items():
                if node in routing_nodes:
                    routing_nodes[node] += 1
                else:
                    routing_nodes[node] = 1
        return routing_nodes

    def _compute_fees_per_node(self, payments_fees):
        """
        takes a list of dictionaries containing the fee earned by each node in the payment and returns a single
        dictionary that contains the sum of values (fees) for each key (nodes) across all dictionaries:
        """
        fees_per_node = {}
        for p in payments_fees:
            for node, fee in p.items():
                if node in fees_per_node:
                    fees_per_node[node] += fee
                else:
                    fees_per_node[node] = fee
        return fees_per_node

    def get_fees(self, node):
        """
        returns the fees earned by node, if the node was split returns the sum of the fees earned by its splits
        """
        total = 0
        found = 0
        for n in self._payments_fees_per_node:
            if n.startswith(node):
                found = 1
                total += self._payments_fees_per_node[n]
        if found:
            return total
        else:
            print(f"The node {node} and any of its splits didn't route any payment...")
            return 0

    def get_ratio(self, node):
        """
        returns the ratio between total fees earned by the SUM of ALL the nodes and the sum of the capacities
        of all the split (if any) of the node provided
        """
        return self.get_fees(node) / self._channel_graph.get_expected_capacity(node)

    def _get_all_ratios(self):
        all_ratios = dict()
        for n in self._payments_fees_per_node.keys():
            all_ratios[n] = self.get_fees(n) / self._channel_graph.get_expected_capacity(n)
        return all_ratios

    def _get_highest_ratio_nodes(self, d):
        """
        Given a dictionary `d`, returns a list of keys sorted from the highest value to the lowest value.
        """
        sorted_keys = sorted(d, key=lambda k: d[k], reverse=True)
        return sorted_keys

    def payments_fees_of_given_node(self, node):
        return self._payments_fees_per_node[node]

    @property
    def payments_fees_per_transaction(self):
        return self._payments_fees_per_transaction

    @property
    def payments_fees_per_node(self):
        return self._payments_fees_per_node

    @payments_fees_per_transaction.setter
    def payments_fees_per_transaction(self, list_payments_fees):
        self._payments_fees_per_node = self._compute_fees_per_node(list_payments_fees)
        self._payments_ratios_per_node = self._get_all_ratios()
        self._payments_fees_per_transaction = list_payments_fees

    @property
    def payments_routing_nodes_per_transaction(self):
        return self._payments_routing_nodes_per_transaction

    @property
    def routed_transactions_per_node(self):
        return self._routed_transactions_per_node

    @payments_routing_nodes_per_transaction.setter
    def payments_routing_nodes_per_transaction(self, list_payment_routing_nodes):
        self._routed_transactions_per_node = self._compute_routing_nodes(list_payment_routing_nodes)
        self._payments_routing_nodes_per_transaction = list_payment_routing_nodes

    @property
    def payments_ratios_per_node(self):
        return self._payments_ratios_per_node

    @property
    def oracle_lightning_network(self):
        return self._oracle_lightning_network

    @property
    def channel_graph(self):
        return self._channel_graph

    @property
    def payments_to_simulate(self):
        return self._payments_to_simulate

    @property
    def payments_amount(self):
        return self._payments_amount

    @property
    def mu(self):
        return self._mu

    @property
    def base(self):
        return self._base

    @property
    def distribution(self):
        return self._distribution

    @property
    def dist_func(self):
        return self._dist_func

    @property
    def highest_ratio_nodes(self):
        """
        returns a list of the nodes ordered from the highest to the lowest ratio
        """
        return self._get_highest_ratio_nodes(self._payments_ratios_per_node)

    @property
    def routed_transactions_per_node(self):
        """
        returns a dictionary of the nodes with the number of routed transactions for each node
        """
        return self._routed_transactions_per_node

    @property
    def final_payment_fees_list(self):
        return self._final_payment_fees_list

    @final_payment_fees_list.setter
    def final_payment_fees_list(self, fees_list):
        self._final_payment_fees_list = fees_list
