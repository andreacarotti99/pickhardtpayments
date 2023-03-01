import random

def payoff(node1, node2):
    if node1 == 'split' and node2 == 'split':
        return 3, 3
    elif node1 == 'split' and node2 == 'not_split':
        return 0, 4
    elif node1 == 'not_split' and node2 == 'split':
        return 4, 0
    else:
        return 1, 1

game = {
    'node1': {
        'strategies': ['split', 'not_split'],
        'payoff': lambda x, y: payoff(x, y)[0]
    },
    'node2': {
        'strategies': ['split', 'not_split'],
        'payoff': lambda x, y: payoff(y, x)[1]
    }
}

def epsilon_nash_equilibrium(game, epsilon):
    # initialize each player's strategy as a random choice from their candidate strategies
    strategies = {}
    for node in game:
        strategies[node] = random.choice(game[node]['strategies'])

    # iterate until convergence
    converged = False
    while not converged:
        # for each node, calculate their best response to the other nodes' strategies
        print("iteration...")
        for node in game:
            # get the other nodes' strategies
            other_strategies = {p: strategies[p] for p in game if p != node}
            # create a function that takes the node's strategy as input and returns their payoff
            payoff_function = lambda x: game[node]['payoff'](x, other_strategies)
            # calculate the best response strategy
            best_response = max(game[node]['strategies'], key=payoff_function)
            # update the node's strategy with probability (1 - epsilon) or choose a random strategy with probability epsilon / (number of players)
            if random.uniform(0, 1) < epsilon / len(game):
                strategies[node] = random.choice(game[node]['strategies'])
            else:
                strategies[node] = best_response

        # check for convergence
        convergence = True
        for node in game:
            other_strategies = {p: strategies[p] for p in game if p != node}
            payoff_function = lambda x: game[node]['payoff'](x, other_strategies)
            current_payoff = payoff_function(strategies[node])
            best_payoff = payoff_function(max(game[node]['strategies'], key=payoff_function))
            if abs(current_payoff - best_payoff) > epsilon:
                convergence = False
                break

        # if all nodes' strategies are approximately optimal, stop iterating
        if convergence:
            converged = True

    return strategies

epsilon = 0.5
equilibrium = epsilon_nash_equilibrium(game, epsilon)
print("Epsilon Nash equilibrium: ", equilibrium)
