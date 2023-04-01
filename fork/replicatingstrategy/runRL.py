import random
import gym
import numpy as np
from gym import spaces
from gym.envs.registration import register
from pickhardtpayments.fork.replicatingstrategy.RLStrategy import CustomEnv
from pickhardtpayments.pickhardtpayments import ChannelGraph

register(
    id='CustomEnv-v0',
    entry_point='path.to.CustomEnv',
)


base = 20_000
channelGraph = ChannelGraph("../SNAPSHOTS/cosimo_19jan2023_converted.json")

channelGraph.transform_channel_graph_to_simpler(tentative_nodes_to_keep=1000)

COPIER = random.choice(list(channelGraph.network.nodes()))
COPY_1 = random.choice(list(channelGraph.network.nodes()))
COPY_2 = random.choice(list(channelGraph.network.nodes()))
COPY_3 = random.choice(list(channelGraph.network.nodes()))
NODES_TO_COPY = [COPY_1, COPY_2, COPY_3]


# Step 2: Create an instance of the CustomEnv environment
env = CustomEnv(channelGraph=channelGraph, base=20_000, agent_node=COPIER, nodes_to_copy=NODES_TO_COPY)

# Step 3: Define hyperparameters for the Q-learning algorithm
learning_rate = 0.1
discount_factor = 0.99
exploration_rate = 1.0
max_exploration_rate = 1.0
min_exploration_rate = 0.01
exploration_decay_rate = 0.001
num_episodes = 1000
max_steps_per_episode = 5

# Step 4: Initialize a Q-table with random values
num_states = len(NODES_TO_COPY)
num_actions = env.action_space.n
q_table = np.zeros((num_states, num_actions))

# Step 5: Train the Q-table by iteratively updating its values based on experience gained through interactions with the environment
rewards_all_episodes = []
for episode in range(num_episodes):
    state = env.reset()
    done = False
    rewards_current_episode = 0

    for step in range(max_steps_per_episode):
        # Exploration-exploitation trade-off
        exploration_rate_threshold = np.random.uniform(0, 1)
        if exploration_rate_threshold > exploration_rate:
            action = np.argmax(q_table[state, :])
        else:
            action = env.action_space.sample()

        # Take the chosen action and observe the new state and reward
        new_state, reward, done, _ = env.step(action)

        # Update Q-table
        state = state.astype(int)
        new_state = new_state.astype(int)
        q_table[state, action] = q_table[state, action] * (1 - learning_rate) + learning_rate * (reward + discount_factor * np.max(q_table[new_state, :]))

        state = new_state
        rewards_current_episode += reward

        print(state)

        if done:
            break

    # Exploration rate decay
    exploration_rate = min_exploration_rate + (max_exploration_rate - min_exploration_rate) * np.exp(-exploration_decay_rate * episode)

    rewards_all_episodes.append(rewards_current_episode)

# Step 6: Use the trained Q-table to make decisions in the environment
state = env.reset()
for step in range(max_steps_per_episode):
    action = np.argmax(q_table[state, :])
    new_state, _, done, _ = env.step(action)
    state = new_state

    print(state)

    if done:
        break
