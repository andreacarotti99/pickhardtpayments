import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense

# Load and preprocess node information CSV
from sklearn.preprocessing import MinMaxScaler

from pickhardtpayments.pickhardtpayments import ChannelGraph

node_info_df = pd.read_csv('graphinfo.csv')
# node_info_df = node_info_df.drop(columns=['bc_ppm', 'bc_base'])

# normalize data that are not between 0 and 1
# the columns in the df are
# [node,avg_ppm,avg_base, bc_ppm, bc_base, degree, exp_cap, bc_standard, ec_standard, median_base,
# median_ppm, closeness_standard, degree_2_hops, bc_capacity]
scaler = MinMaxScaler()
node_info_df['degree'] = scaler.fit_transform(node_info_df[['degree']])
node_info_df['degree_2_hops'] = scaler.fit_transform(node_info_df[['degree_2_hops']])
node_info_df['exp_cap'] = scaler.fit_transform(node_info_df[['exp_cap']])
node_info_df['avg_ppm'] = scaler.fit_transform(node_info_df[['avg_ppm']])
node_info_df['avg_base'] = scaler.fit_transform(node_info_df[['avg_base']])
node_info_df['median_ppm'] = scaler.fit_transform(node_info_df[['median_ppm']])
node_info_df['median_base'] = scaler.fit_transform(node_info_df[['median_base']])

node_info_df = node_info_df.drop([
    'avg_ppm',
    'avg_base',
    'bc_ppm',
    'bc_base',
    'degree',
    'exp_cap',
    'bc_standard',
    'ec_standard',
    'median_base',
    'median_ppm',
    'closeness_standard',
    'degree_2_hops',
    # 'bc_capacity', not existent
    # 'bc_pickhardt'
    ],
    axis=1)

# Reading the result df with the fees
fees_df = pd.read_csv('labeled_results_10000trans_10000SAT_1000mu_distunif_amountdistfixe_1.csv')
fees_df = fees_df.loc[:, ['node', 'ROI']]

# We obtain a dictionary containing for each node the ROI value (also for those nodes not in the df that didn't route transactions)
# Loading graph from snapshot
channel_graph = ChannelGraph("../../fork/SNAPSHOTS/cosimo_19jan2023_converted.json")
simpler_graph = channel_graph.transform_channel_graph_to_simpler(tentative_nodes_to_keep=1000, strategy="weighted_by_capacity")
myDiGraph = channel_graph.getDiGraph(amount=10_000, mu=1000)
node_labels_all = {}
for node in myDiGraph.nodes():
    if node in fees_df['node'].values:
        node_labels_all[node] = fees_df.loc[fees_df['node'] == node, 'ROI'].values[0]
    else:
        node_labels_all[node] = 'NO ROI'
# node_labels_df = pd.DataFrame.from_dict(node_labels_all, orient='index', columns=['ROI'])
node_labels_df = pd.DataFrame(list(node_labels_all.items()), columns=['node', 'ROI'])



# Merge node information and fees earned dataframes
merged_df = pd.merge(node_info_df, fees_df, on='node', how='inner')
# merged_df = pd.merge(node_info_df, node_labels_df, on='node', how='inner')
merged_df = merged_df.drop(columns=['node'])



# Convert 'ROI' to a categorical type with specific order
categories = ['HIGH', 'LOW', 'NO ROI']
merged_df['ROI'] = pd.Categorical(merged_df['ROI'], categories=categories, ordered=True)



# Split data into training and testing sets
X = merged_df.drop('ROI', axis=1)  # Input features (node information)
y = merged_df['ROI']  # Output variable (fees earned)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)



# Define the neural network model
model = Sequential()
# Adding layers to the model, e.g. Dense layers with appropriate activation functions and input/output dimensions)
# model.add(Dense(units=64, activation='relu', input_dim=X_train.shape[1]))
model.add(Dense(units=X_train.shape[1], activation='relu', input_dim=X_train.shape[1]))
model.add(Dense(units=16, activation='relu'))
model.add(Dense(units=len(categories), activation='softmax'))  # use softmax activation for multi-class classification

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy']) # use categorical cross-entropy loss for multi-class classification

# Convert categories to one-hot encoded vectors
y_train = pd.get_dummies(y_train)
y_test = pd.get_dummies(y_test)

# Train the model
model.fit(X_train, y_train, epochs=60, batch_size=64, verbose=1)

# Evaluate the model
loss, accuracy = model.evaluate(X_test, y_test, batch_size=64)
print('Test loss:', loss)
print('Test accuracy:', accuracy)

# Use the trained model for prediction
predictions = model.predict(X_test)

# Convert predicted probabilities to categorical values
predicted_categories = pd.Categorical.from_codes(np.argmax(predictions, axis=1), categories=categories)

# Print the actual and predicted categories for each node in the test set
for i in range(len(predictions)):
    print('\n\nNode:', X_test.index[i], 'Predicted ROI:', predicted_categories[i], '\nActual ROI:\n', y_test.iloc[i])
