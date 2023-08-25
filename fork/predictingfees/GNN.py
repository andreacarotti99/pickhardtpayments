import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from keras import layers, Model
from stellargraph.mapper import FullBatchNodeGenerator
from stellargraph.layer import GCN
from pickhardtpayments.pickhardtpayments import ChannelGraph
import stellargraph as sg

# Loading graph from snapshot
channel_graph = ChannelGraph("../../fork/SNAPSHOTS/cosimo_19jan2023_converted.json")
simpler_graph = channel_graph.transform_channel_graph_to_simpler(tentative_nodes_to_keep=1000, strategy="weighted_by_capacity")
myDiGraph = channel_graph.getDiGraph(amount=10_000, mu=1000)

# Read the csv with the fees earned by every node
fees_df = pd.read_csv('labeled_results_10000trans_10000SAT_1000mu_distunif_amountdistfixe_1.csv')
node_labels_df = fees_df.loc[:, ['node', 'ROI']]

# Convert the string labels to numerical labels using LabelEncoder
le = LabelEncoder()
node_labels_df["ROI"] = le.fit_transform(node_labels_df["ROI"])

# We obtain a dictionary containing for each node the ROI value (also for those nodes not in the df that didn't route transactions)
node_labels_all = {}
for node in myDiGraph.nodes():
    if node in node_labels_df['node'].values:
        node_labels_all[node] = node_labels_df.loc[node_labels_df['node'] == node, 'ROI'].values[0]
    else:
        node_labels_all[node] = np.int64(0)

# create a DataFrame from the dictionary and set the index
node_labels_df = pd.DataFrame.from_dict(node_labels_all, orient='index', columns=['ROI'])
node_labels_df.index.name = 'node'

print(node_labels_df)

# G = sg.StellarGraph.from_networkx(myDiGraph, node_features=df, edge_weight_attr='ppm')

# print(G.info())

# Split the data into training and testing sets
# train_nodes, test_nodes = train_test_split(G.nodes(), test_size=0.2, random_state=0)

# print(train_nodes.value_counts())

'''




# Define a FullBatchNodeGenerator for training the model
generator = FullBatchNodeGenerator(G, method="gcn")

# Define the GCN model
gcn = GCN(layer_sizes=[16, 8], activations=["relu", "relu"], generator=generator, dropout=0.5)

# Define the input and output tensors for the model
x_inp, x_out = gcn.in_out_tensors()

# Define the final layer for the model
predictions = layers.Dense(units=1, activation="sigmoid")(x_out)

# Define the model
model = Model(inputs=x_inp, outputs=predictions)

# Compile the model
model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["acc"])

# Train the model
train_gen = generator.flow(train_nodes)
test_gen = generator.flow(test_nodes)
history = model.fit(train_gen, epochs=100, validation_data=test_gen, verbose=2)

# Predict the features of a node
#  node_id = "1234"  # Replace with the ID of the node you want to predict the feature of
#  node_data = node_labels_all[node_id]  # Get the features of the node
#  node_data = np.array([node_data])  # Convert the features to a numpy array
#  node_pred = model.predict(generator.flow([node_id], node_data))  # Predict the feature of the node

# print(node_pred)

'''
