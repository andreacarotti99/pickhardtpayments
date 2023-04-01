import gym
from gym import spaces
import networkx as nx
import numpy as np

from pickhardtpayments.fork.Simulation import Simulation
from pickhardtpayments.pickhardtpayments import ChannelGraph


class CustomEnv(gym.Env):
    def __init__(self, channelGraph: ChannelGraph, base: int, agent_node, nodes_to_copy):
        self.copied_nodes = None
        self.channelGraph = channelGraph
        self.graph = channelGraph.network
        self.agent_node = agent_node
        self.nodes_to_copy = nodes_to_copy
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(low=-1, high=1, shape=(len(self.nodes_to_copy),), dtype=np.float32)
        self.prev_total_fee = 0
        self.simulation = None
        self.base = base

    def reset(self):
        self.prev_total_fee = 0
        self.copied_nodes = []
        self.simulation = Simulation(channel_graph=self.channelGraph, base=self.base)
        return self._get_observation()

    def step(self, action):

        if action == 0:  # replicate all edges of a node in nodes_to_copy
            print("action 0: copy a node")
            node_to_copy = self.nodes_to_copy[np.random.randint(len(self.nodes_to_copy))]
            if node_to_copy not in self.copied_nodes:
                node_to_copy_capacity = self.channelGraph.get_expected_capacity(node_to_copy)
                self.channelGraph.close_channels_up_to_amount(node=self.agent_node, threshold_to_reach=node_to_copy_capacity)
                self.channelGraph.replicate_node(node_to_copy=node_to_copy, new_node_id=self.agent_node)
                self.copied_nodes.append(node_to_copy)
        elif action == 1:  # remove previously copied node
            print("action 1: remove channels of the copied node")
            if len(self.copied_nodes) > 0:
                node_copied = self.copied_nodes.pop()

                self.channelGraph.remove_replicated_channels(node_copied=node_copied, node_copier=self.agent_node)

        else:
            raise ValueError("Invalid action")

        # simulate and compute reward
        self.simulation.run_success_payments_simulation(
            payments_to_simulate=100,
            payments_amount=1000,
            mu=0,
            base=1000,
            distribution="uniform",
            dist_func="",
            verbose=False
        )

        new_total_fee_agent = self.simulation.get_fees(node=self.agent_node)

        reward = new_total_fee_agent - self.prev_total_fee
        self.prev_total_fee = new_total_fee_agent

        return self._get_observation(), reward, False, {}

    def _get_observation(self):
        observation = []
        for node in self.nodes_to_copy:
            if node in self.copied_nodes:
                observation.append(1)
            else:
                observation.append(-1)
        return np.array(observation, dtype=np.float32)
