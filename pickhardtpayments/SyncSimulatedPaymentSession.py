"""
SyncSimulatedPaymentSession.py
====================================
The core module of the pickhardt payment project.
An example payment is executed and statistics are run.
"""

import logging
import sys
from typing import List

from .Attempt import Attempt, AttemptStatus
from .Payment import Payment
from .UncertaintyNetwork import UncertaintyNetwork
from .OracleLightningNetwork import OracleLightningNetwork

from ortools.graph import pywrapgraph

import time
import networkx as nx

import copy


def set_logger():
    # Set Logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s', datefmt='%H:%M:%S')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)
    file_handler = logging.FileHandler('pickhardt_pay.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)


class SyncSimulatedPaymentSession:
    """
    A PaymentSession is used to create the min cost flow problem from the UncertaintyNetwork

    This happens by adding several parallel arcs coming from the piece wise linearization of the
    UncertaintyChannel to the min_cost_flow object. 

    The main API call is `pickhardt_pay` which invokes a sequential loop to conduct trial and error
    attempts. The loop could easily send out all onions concurrently but this does not make sense 
    against the simulated OracleLightningNetwork. 
    """

    def __init__(self,
                 oracle: OracleLightningNetwork,
                 uncertainty_network: UncertaintyNetwork,
                 prune_network: bool = True):
        self._oracle = oracle
        self._uncertainty_network = uncertainty_network
        self._prune_network = prune_network
        self._prepare_integer_indices_for_nodes()

    def _prepare_integer_indices_for_nodes(self):
        """
        necessary for the OR-lib by google and the min cost flow solver

        let's initialize the look-up tables for node_ids to integers from [0,...,#number of nodes]
        this is necessary because of the API of the Google Operations Research min cost flow solver
        """
        self._mcf_id = {}
        self._node_key = {}
        for k, node_id in enumerate(self._uncertainty_network.network.nodes()):

            self._mcf_id[node_id] = k
            self._node_key[k] = node_id


    def _prepare_mcf_solver(self, src, dest, amt, mu, base_fee):
        """
        GO to https://developers.google.com/optimization/flow/mincostflow to understand the code in this method...

        computes the uncertainty network given our prior belief and prepares the min cost flow solver

        This function can define a value for mu to control how heavily we combine the uncertainty cost and fees Also
        the function supports only taking channels into account that don't charge a base_fee higher or equal to `base`

        returns the instantiated min_cost_flow object from the Google OR-lib that contains the piecewise linearized
        problem
        """
        self._min_cost_flow = pywrapgraph.SimpleMinCostFlow()
        self._arc_to_channel = {}

        for s, d, channel in self._uncertainty_network.network.edges(data="channel"):
            # ignore channels with too large base fee
            if channel.base_fee > base_fee:
                continue
            # FIXME: Remove Magic Number for pruning
            # Prune channels away that have too low success probability! This is a huge runtime boost
            # However the pruning would be much better to work on quantiles of normalized cost
            # So as soon as we have better Scaling, Centralization and feature engineering we can
            # probably have a more focused pruning
            if self._prune_network and channel.success_probability(amt=250_000) < 0.9:
                continue
            cnt = 0
            # QUANTIZATION):
            # debug
            # plc0 = channel.get_piecewise_linearized_costs(mu=0)
            # plc1 = channel.get_piecewise_linearized_costs(mu=1)
            # plc10 = channel.get_piecewise_linearized_costs(mu=10)
            # plc100 = channel.get_piecewise_linearized_costs(mu=100)
            # plc1000 = channel.get_piecewise_linearized_costs(mu=1000)


            for capacity, cost in channel.get_piecewise_linearized_costs(mu=mu):
                index = self._min_cost_flow.AddArcWithCapacityAndUnitCost(self._mcf_id[s],
                                                                          self._mcf_id[d],
                                                                          capacity,
                                                                          cost)
                self._arc_to_channel[index] = (s, d, channel, 0)
                if self._prune_network and cnt > 1:
                    break
                cnt += 1

        # Add node supply to 0 for all nodes
        for i in self._uncertainty_network.network.nodes():
            self._min_cost_flow.SetNodeSupply(self._mcf_id[i], 0)

        # add amount to sending node --> https://developers.google.com/optimization/flow/mincostflow
        # print(self._mcf_id)
        self._min_cost_flow.SetNodeSupply(
            self._mcf_id[src], int(amt))  # /QUANTIZATION))

        # add -amount to recipient nods
        self._min_cost_flow.SetNodeSupply(
            self._mcf_id[dest], -int(amt))  # /QUANTIZATION))

    def _next_hop(self, path):
        """
        generator to iterate through edges indexed by node id of paths

        The path is a list of node ids. Each call returns a tuple src, dest of an edge in the path    
        """
        for i in range(1, len(path)):
            src = path[i - 1]
            dest = path[i]
            yield src, dest

    def _make_channel_path(self, G: nx.MultiDiGraph, path: List[str]):
        """
        network x returns a path as a list of node_ids. However, we need a list of `UncertaintyChannels`
        Since the graph has parallel edges it is quite some work to get the actual channels that the
        min cost flow solver produced
        """
        channel_path = []
        bottleneck = 2 ** 63
        for src, dest in self._next_hop(path):
            w = 2 ** 63
            c = None
            flow = 0
            for sid in G[src][dest].keys():
                if G[src][dest][sid]["weight"] < w:
                    w = G[src][dest][sid]["weight"]
                    c = G[src][dest][sid]["channel"]
                    flow = G[src][dest][sid]["flow"]
            channel_path.append(c)

            if flow < bottleneck:
                bottleneck = flow

        return channel_path, bottleneck

    def _dissect_flow_to_paths(self, s, d):
        """
        A standard algorithm to dissect a flow into several paths.


        FIXME: Note that this dissection while accurate is probably not optimal in practice. 
        As noted in our Probabilistic payment delivery paper the payment process is a bernoulli trial 
        and I assume it makes sense to dissect the flow into paths of similar likelihood to make most
        progress but this is a mere conjecture at this point. I expect quite a bit of research will be
        necessary to resolve this issue.
        """
        # first collect all linearized edges which are assigned a non-zero flow put them into a networkx graph
        G = nx.MultiDiGraph()
        for i in range(self._min_cost_flow.NumArcs()):
            flow = self._min_cost_flow.Flow(i)  # *QUANTIZATION
            if flow == 0:
                continue

            src, dest, channel, _ = self._arc_to_channel[i]
            if G.has_edge(src, dest):
                if channel.short_channel_id in G[src][dest]:
                    G[src][dest][channel.short_channel_id]["flow"] += flow
            else:
                # FIXME: cost is not reflecting exactly the piecewise linearization
                # Probably not such a big issue as we just dissect flow
                G.add_edge(src, dest, key=channel.short_channel_id, flow=flow,
                           channel=channel, weight=channel.combined_linearized_unit_cost())
        used_flow = 1
        attempts = []

        # allocate flow to shortest / cheapest paths from src to dest as long as this is possible
        # decrease flow along those edges. This is a standard mechanism to dissect a flow into paths
        while used_flow > 0:
            try:
                path = nx.shortest_path(G, s, d)
            except:
                break
            channel_path, used_flow = self._make_channel_path(G, path)
            attempts.append(Attempt(channel_path, used_flow))

            # reduce the flow from the selected path
            for pos, hop in enumerate(self._next_hop(path)):
                src, dest = hop
                channel = channel_path[pos]
                G[src][dest][channel.short_channel_id]["flow"] -= used_flow
                if G[src][dest][channel.short_channel_id]["flow"] == 0:
                    G.remove_edge(src, dest, key=channel.short_channel_id)
        return attempts

    def _generate_candidate_paths(self, src, dest, amt, mu, base, verbose):
        """
        computes the optimal payment split to deliver `amt` from `src` to `dest` and updates our belief about the
        liquidity

        This is one step within the payment loop.

        Returns the residual amount of the `amt` that could ne be delivered and the paid fees
        (on a per channel base not including fees for downstream fees) for the delivered amount

        the function also prints some results on statistics about the paths of the flow to stdout.
        """
        # initialisation of List of Attempts for this round.
        attempts_in_round = List[Attempt]

        # First we prepare the min cost flow by getting arcs from the uncertainty network
        # debug
        # print("GENERATING CANDIDATE PATHS...")
        self._prepare_mcf_solver(src, dest, amt, mu, base)
        start = time.time()
        # print("solving mcf...")
        status = self._min_cost_flow.Solve()

        if status != self._min_cost_flow.OPTIMAL:
            if verbose:
                print('There was an issue with the min cost flow input.')
                print(f'Status: {status}')

            # exit(1)
            issue_min_cost_flow = True
            return -1, -1, issue_min_cost_flow
        else:
            issue_min_cost_flow = False


        attempts_in_round = self._dissect_flow_to_paths(src, dest)
        end = time.time()

        # to avoid the issue with min cost flow input we try to work around the problem by not considering those transactions
        # for which the min cost flow problem occurs

        return attempts_in_round, end - start, issue_min_cost_flow

    def _estimate_payment_statistics(self, attempts):
        """
        estimates the success probability of paths and computes fees (without paying downstream fees)

        @returns the statistics in the `payments` dictionary
        """
        # compute fees and probabilities of candidate paths for evaluation
        for attempt in attempts:
            attempt.routing_fee, attempt.probability = self._uncertainty_network.get_features_of_candidate_path(
                attempt.path, attempt.amount)
            # logging.debug("fee: {attempt.routing_fee} msat, p = {attempt.probability:.4%}, amount: {attempt.amount}")

            # to correctly compute conditional probabilities of non-disjoint paths in the same set of paths
            self._uncertainty_network.allocate_amount_on_path(attempt.path, attempt.amount)

        # remove allocated amounts for all planned onions before doing actual attempts
        for attempt in attempts:
            self._uncertainty_network.allocate_amount_on_path(
                attempt.path, -attempt.amount)


    def _attempt_payments(self, attempts: List[Attempt]):
        """
        we attempt all planned payments and test the success against the oracle in particular this
        method changes - depending on the outcome of each payment - our belief about the uncertainty
        in the UncertaintyNetwork.
        successful onions are collected to be transacted on the OracleNetwork if complete payment can be delivered
        """
        # test actual payment attempts
        for attempt in attempts:
            success, erring_channel = self._oracle.send_onion(
                attempt.path, attempt.amount)
            if success:
                # TODO: let this happen in Payment class? Or in Attempt class - with status change as settlement
                attempt.status = AttemptStatus.ARRIVED
                # handling amounts on path happens in Attempt Class.
                self._uncertainty_network.allocate_amount_on_path(
                    attempt.path, attempt.amount)

                # unnecessary, because information is in attempt (Status INFLIGHT)
                # settled_onions.append(payments[key])
            else:
                attempt.status = AttemptStatus.FAILED
                attempt.empty_feeEarned_per_node()

    def _evaluate_attempts(self, payment: Payment, verbose=False, cnt=0):
        """
        helper function to collect statistics about attempts and print them

        returns the `residual` amount that could not have been delivered and some statistics
        """
        total_fees = 0
        paid_fees = 0
        residual_amt = 0
        expected_sats_to_deliver = 0
        amt = 0
        arrived_attempts = []
        failed_attempts = []
        if verbose:
            print("\nStatistics about {} candidate onions:\n".format(len(payment.attempts)))
            print("successful attempts:")
            print("--------------------")
        for arrived_attempt in payment.filter_attempts(AttemptStatus.ARRIVED):
            amt += arrived_attempt.amount
            total_fees += arrived_attempt.routing_fee / 1000.
            expected_sats_to_deliver += arrived_attempt.probability * arrived_attempt.amount

            if verbose:
                print(" p = {:6.2f}% amt: {:9} sats  hops: {} ppm: {:5}".format(
                    arrived_attempt.probability * 100, arrived_attempt.amount, len(arrived_attempt.path),
                    int(arrived_attempt.routing_fee * 1000 / arrived_attempt.amount)))
            paid_fees += arrived_attempt.routing_fee

        if verbose:
            print("\nfailed attempts:")
            print("----------------")
        for failed_attempt in payment.filter_attempts(AttemptStatus.FAILED):
            amt += failed_attempt.amount
            total_fees += failed_attempt.routing_fee / 1000.
            expected_sats_to_deliver += failed_attempt.probability * failed_attempt.amount
            if verbose:
                print(" p = {:6.2f}% amt: {:9} sats  hops: {} ppm: {:5}".format(
                    failed_attempt.probability * 100, failed_attempt.amount, len(failed_attempt.path),
                    int(failed_attempt.routing_fee * 1000 / failed_attempt.amount)))
            residual_amt += failed_attempt.amount


        fraction = expected_sats_to_deliver * 100. / amt

        # cnt is equal to 0 when it is the first round (first attempt in trying to send the payment)
        if cnt == 0:
            payment.expectation_to_deliver_round_1 = fraction

        if verbose:
            print("\nAttempt Summary:")
            print("=================")
            print("\nTried to deliver \t{:10} sats".format(amt))

            print("expected to deliver {:10} sats \t({:4.2f}%)".format(
                int(expected_sats_to_deliver), fraction))



            fraction = (amt - residual_amt) * 100. / (amt)
            print("actually delivered {:10} sats \t({:4.2f}%)".format(
                amt - residual_amt, fraction))
            print("deviation: \t\t{:4.2f}".format(
                (amt - residual_amt) / (expected_sats_to_deliver + 1)))
            print("planned_fee: {:8.3f} sat".format(total_fees))
            print("paid fees: {:8.3f} sat".format(paid_fees))
        return residual_amt, paid_fees, len(payment.attempts), len(failed_attempts)

    def get_feeEarned_per_node_successful_attempts(self, attempts: List[Attempt]):
        """
        Returns a dictionary containing the nodes that earned fee and the total fee they earned from those attempts
        """
        fees_per_node = {}
        for attempt in attempts:
            for node, fee in attempt.feeEarned_per_node.items():
                if node in fees_per_node:
                    fees_per_node[node] += fee
                else:
                    fees_per_node[node] = fee
        return fees_per_node

    def get_payment_routing_nodes(self, attempts: List[Attempt]):
        """
        Returns a dictionary containing the nodes that routed at least one payment with the number of payments they routed
        """
        routing_nodes = {}
        for attempt in attempts:
            for node, fee in attempt.feeEarned_per_node.items():
                if node in routing_nodes:
                    routing_nodes[node] += 1
                else:
                    routing_nodes[node] = 1
        return routing_nodes

    def forget_information(self):
        """
        forgets all the information in the UncertaintyNetwork that is a member of the PaymentSession
        """
        self._uncertainty_network.reset_uncertainty_network()

    def activate_network_wide_uncertainty_reduction(self, n):
        """
        Pipes API call to the UncertaintyNetwork
        """
        self._uncertainty_network.activate_network_wide_uncertainty_reduction(
            n, self._oracle)

    def pickhardt_pay(self, src, dest, amt, mu, base, verbose):
        """
        conduct one experiment! might need to call oracle.reset_uncertainty_network() first
        I could not put it here as some experiments require sharing of liquidity information

        """
        # Added because we don't require the sharing of liquidity
        self.forget_information()

        # set_logger()
        # logging.info('*** new pickhardt payment ***')

        # Setup
        entropy_start = self._uncertainty_network.entropy()
        cnt = 0
        total_fees = 0
        total_number_failed_paths = 0

        # Initialise Payment
        # currently with underscore to not mix up with existing variable 'payment'
        payment = Payment(src, dest, amt)

        # This is the main payment loop. It is currently blocking and synchronous but may be
        # implemented in a concurrent way. Also, we stop after 10 rounds which is pretty arbitrary
        # a better stop criteria would be if we compute infeasible flows or if the probabilities
        # are too low or residual amounts decrease to slowly
        while amt > 0 and cnt < 10:
            if verbose:
                print("Round number: ", cnt + 1)
                print("Try to deliver", amt, "satoshi:")

            sub_payment = Payment(payment.sender, payment.receiver, amt)
            # transfer to a min cost flow problem and run the solver
            # paths is the lists of channels, runtime the time it took to calculate all candidates in this round
            paths, runtime, issue_min_cost_flow = self._generate_candidate_paths(payment.sender, payment.receiver, amt, mu, base, verbose)

            if issue_min_cost_flow:
                payment.successful = False
                return payment

            sub_payment.add_attempts(paths)

            # print(paths)

            # make attempts, try to send onion and register if success or not
            # update our information about the UncertaintyNetwork
            self._attempt_payments(sub_payment.attempts)

            # run some simple statistics and depict them
            amt, paid_fees, num_paths, number_failed_paths = self._evaluate_attempts(sub_payment, verbose, cnt)

            # Setting expectation to deliver of the payment and not the sub_payment
            if sub_payment.expectation_to_deliver_round_1 is not None:
                payment.expectation_to_deliver_round_1 = round(sub_payment.expectation_to_deliver_round_1, 2)
            else:
                payment.expectation_to_deliver_round_1 = -1

            if verbose:
                print("Runtime of flow computation: {:4.2f} sec ".format(runtime))
                print("\n================================================================\n")

            total_number_failed_paths += number_failed_paths
            total_fees += paid_fees
            cnt += 1

            # add attempts of sub_payment to payment
            payment.add_attempts(sub_payment.attempts)

        # When residual amount is 0 / enough successful onions have been found, then settle payment. Else drop onions.
        if amt == 0:
            for onion in payment.filter_attempts(AttemptStatus.ARRIVED):
                try:
                    self._oracle.settle_payment(onion.path, onion.amount)
                    onion.status = AttemptStatus.SETTLED
                except Exception as e:
                    print("There was a problem... Payment Failed for this reason:")
                    print(e)
                    payment.successful = False
                    return payment
            payment.successful = True
            payment.fee_per_node = self.get_feeEarned_per_node_successful_attempts(payment.attempts)
            if verbose:
                print("Payment fees per node:")
                print(payment.fee_per_node)
                print("Payment was successful")

            payment.routing_nodes = self.get_payment_routing_nodes(payment.attempts)

        payment.end_time = time.time()

        entropy_end = self._uncertainty_network.entropy()

        if verbose:
            print("SUMMARY:")
            print("========")
            print("Rounds of mcf-computations:\t", cnt)
            print("Number of attempts made:\t", len(payment.attempts))
            print("Number of failed attempts:\t", len(list(payment.filter_attempts(AttemptStatus.FAILED))))
            print("Failure rate: {:4.2f}% ".format(
                len(list(payment.filter_attempts(AttemptStatus.FAILED))) * 100. / len(payment.attempts)))
            print("total Payment lifetime (including inefficient memory management): {:4.3f} sec".format(
                payment.end_time - payment.start_time))
            print("Learnt entropy: {:5.2f} bits".format(entropy_start - entropy_end))
            print("fee for settlement of delivery: {:8.3f} sat --> {} ppm".format(
                payment.settlement_fees/1000, int(payment.settlement_fees * 1000 / payment.total_amount)))
            print("used mu:", mu)

        return payment

    def direct_payment(self, src: str, dest: str, amount: float, oracle: OracleLightningNetwork):

        payment = Payment(src, dest, amount)

        channel = oracle.get_channel_without_short_channel_id(src, dest)
        rev_channel = oracle.get_channel_without_short_channel_id(dest, src)


        if channel is not None:
            if channel.actual_liquidity >= amount:
                channel.actual_liquidity = channel.actual_liquidity - amount
                rev_channel.actual_liquidity = rev_channel.actual_liquidity + amount
                payment.successful = True
                print(f"Payment from {src} to {dest} was successful")
            else:
                print("Unable to perform direct payment, the liquidity is not enough")
                payment.successful = False
                print(f"Payment from {src} to {dest} failed")
        return payment




