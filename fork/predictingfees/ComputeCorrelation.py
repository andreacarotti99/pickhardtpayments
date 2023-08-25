import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from pickhardtpayments.pickhardtpayments import ChannelGraph
import seaborn as sns



pd.set_option('display.max_columns', None)


# ------- Reading data from csv and merging dataframes ---------

# graphinfo contains the dataset about the first 1000 highest capacity nodes
node_info_df = pd.read_csv('graphinfo.csv')

# scaling the features between 0 and 1
scaler = MinMaxScaler()
node_info_df['degree'] = scaler.fit_transform(node_info_df[['degree']])
node_info_df['degree_2_hops'] = scaler.fit_transform(node_info_df[['degree_2_hops']])
node_info_df['exp_cap'] = scaler.fit_transform(node_info_df[['exp_cap']])
node_info_df['avg_ppm'] = scaler.fit_transform(node_info_df[['avg_ppm']])
node_info_df['avg_base'] = scaler.fit_transform(node_info_df[['avg_base']])
node_info_df['median_ppm'] = scaler.fit_transform(node_info_df[['median_ppm']])
node_info_df['median_base'] = scaler.fit_transform(node_info_df[['median_base']])

# Reading the result df with the fees. df_fees contains the df of nodes that routed at least one transaction
df_fees = pd.read_csv('labeled_results_10000trans_10000SAT_1000mu_distunif_amountdistfixe_1.csv')
df_fees = df_fees.loc[:, ['node', 'ROI', 'ratio', 'total_fee']]

# We obtain a dictionary containing for each node the ROI value (also for those nodes not in the df that didn't route transactions)
# Loading graph from snapshot
channel_graph = ChannelGraph("../../fork/SNAPSHOTS/cosimo_19jan2023_converted.json")
simpler_graph = channel_graph.transform_channel_graph_to_simpler(tentative_nodes_to_keep=1000,
                                                                 strategy="weighted_by_capacity")
myDiGraph = channel_graph.getDiGraph(amount=10_000, mu=1000)

# Create a DataFrame with all the nodes in the digraph
df_all_nodes = pd.DataFrame({'node': list(myDiGraph.nodes())})

# perform the left join to obtain a df with all the nodes and all the fees
df_fees_complete = pd.merge(df_all_nodes, df_fees, how='left', on='node')

# fill the NaN values with 0
df_fees_complete['ratio'] = df_fees_complete['ratio'].fillna(0)
df_fees_complete['total_fee'] = df_fees_complete['total_fee'].fillna(0)

# Finally merge the two df
df_final = pd.merge(df_fees_complete, node_info_df, how='inner', on='node')


df_final['ROI'] = df_final['ROI'].fillna('NO ROI')
df_final = df_final.sort_values('ROI', ascending=True)
df_final.to_csv('test.csv')


# ------- Computing the Pearson correlation ---------

# Iterate through the columns and compute the correlation coefficients with the target column
print(df_final.columns)
print()

print(f"{'Measure':<25}{'Correlation coefficient ratio':>37}{'Correlation coefficient fee':>38}")
print("-" * 100)

target_column_1 = 'ratio'
target_column_2 = 'total_fee'
for column in df_final.columns:
    if column != target_column_1 and column != target_column_2 and column != 'node' and column != 'ROI':
        corr_coeff_1 = df_final[column].corr(df_final[target_column_1])
        corr_coeff_2 = df_final[column].corr(df_final[target_column_2])
        print(f"{column:<25}{corr_coeff_1:>25.4f}{corr_coeff_2:>35.4f}")

# ------- Computing the correlation heatmap ---------

df_final = df_final.drop('closeness_pickhardt', axis=1)

corr_matrix = df_final.corr()

# plot the matrix as a heatmap

mask = np.zeros_like(corr_matrix, dtype=np.bool)
mask[np.triu_indices_from(mask)] = True

# plot the matrix as a heatmap
sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm')
plt.xticks(fontsize=6)
plt.yticks(fontsize=6)
plt.show()
