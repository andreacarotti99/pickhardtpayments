import os
import pandas as pd
from pickhardtpayments.fork.Simulation import Simulation


class ExportResults(Simulation):
    def __init__(self, simulation: Simulation):
        self._simulation = simulation
        print("Saving results into dataframe...")
        df = pd.DataFrame(self._simulation.payments_fees_per_node.items(), columns=['node', 'total_fee'])
        df['capacity'] = df['node'].map(self._simulation.channel_graph.get_nodes_capacities())
        df['routed_payments'] = df['node'].map(self._simulation.routed_transactions_per_node)
        self._results_df = df

    def export_results(self, simulation_number: str = "1"):
        """
        Take a dataframe and exports it in the folder RESULTS as a csv file, the simulation number
        is used to distinguish between different simulation in the same run
        """

        output_dir = 'RESULTS'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        s = self._simulation

        if s.dist_func == "":
            output_file = f"results_{str(s.payments_to_simulate)}trans_{s.payments_amount}SAT_{s.mu}mu_{s.channel_graph.snapshot_file[10:-5]}" \
                      f"_dist_{s.distribution[0:4]}_{simulation_number}"
        else:
            output_file = f"results_{str(s.payments_to_simulate)}trans_{s.payments_amount}SAT_{s.mu}mu_{s.channel_graph.snapshot_file[10:-5]}" \
                      f"_dist_{s.distribution[0:4]}_{s.dist_func}_{simulation_number}"

        self._results_df.to_csv("%s/%s.csv" % (output_dir, output_file), index=False)

        print(f"Results successfully exported to csv in file: {output_file}")
        return

    def substitute_node_name(self, old_name, new_name):
        if old_name in self._results_df['node'].values:
            self._results_df.loc[self._results_df['node'] == old_name, 'node'] = new_name
        else:
            print(f"Node {old_name} not present in the dataframe, {new_name} was not set...")
        return



