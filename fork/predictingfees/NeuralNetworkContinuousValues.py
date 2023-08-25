import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense

# Load and preprocess node information CSV
from sklearn.preprocessing import MinMaxScaler

node_info_df = pd.read_csv('graphinfo.csv')
# node_info_df = node_info_df.drop(columns=['bc_ppm', 'bc_base'])

# normalize data that are not between 0 and 1
# the columns in the df are
# [node, avg_ppm, avg_base, bc_ppm, bc_base, degree, exp_cap, bc_standard, ec_standard, median_base,
# median_ppm, closeness_standard, degree_2_hops, bc_capacity]
scaler = MinMaxScaler()
# node_info_df['degree'] = scaler.fit_transform(node_info_df[['degree']])
node_info_df['degree_2_hops'] = scaler.fit_transform(node_info_df[['degree_2_hops']])
node_info_df['exp_cap'] = scaler.fit_transform(node_info_df[['exp_cap']])
# node_info_df['avg_ppm'] = scaler.fit_transform(node_info_df[['avg_ppm']])
node_info_df['avg_base'] = scaler.fit_transform(node_info_df[['avg_base']])
node_info_df['median_ppm'] = scaler.fit_transform(node_info_df[['median_ppm']])
node_info_df['median_base'] = scaler.fit_transform(node_info_df[['median_base']])

node_info_df = node_info_df.drop([
    # 'avg_ppm',
    'avg_base',
    # 'bc_ppm',
    'bc_base',
    # 'degree',
    # 'exp_cap',
    'bc_standard',
    # 'ec_standard',
    'median_base',
    # 'median_ppm',
    # 'closeness_standard',
    'degree_2_hops',
    # 'bc_capacity',
    # 'bc_base',
    ], axis=1)

print(node_info_df)

# Reading the result df with the fees
fees_df = pd.read_csv('labeled_results_10000trans_10000SAT_1000mu_distunif_amountdistfixe_1.csv')
fees_df = fees_df.loc[:, ['node', 'total_fee']]


# Merge node information and fees earned dataframes
merged_df = pd.merge(node_info_df, fees_df, on='node', how='inner')
merged_df = merged_df.drop(columns=['node'])




# Split data into training and testing sets
X = merged_df.drop('total_fee', axis=1)  # Input features (node information)
y = merged_df['total_fee']  # Output variable (fees earned)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define the neural network model
model = Sequential()
# Adding layers to the model, e.g. Dense layers with appropriate activation functions and input/output dimensions)
# model.add(Dense(units=64, activation='relu', input_dim=X_train.shape[1]))
model.add(Dense(units=64, activation='relu', input_dim=X_train.shape[1]))
model.add(Dense(units=32, activation='relu'))
model.add(Dense(units=1, activation='linear'))

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])



# Train the model
model.fit(X_train, y_train, epochs=100, batch_size=32, verbose=1)

# Evaluate the model
loss = model.evaluate(X_test, y_test, batch_size=64)
print('Test loss:', loss)

# Use the trained model for prediction
predictions = model.predict(X_test)


# Print the actual and predicted categories for each node in the test set
for i in range(len(predictions)):
    print('\n\nNode:', X_test.index[i], 'Predicted fee:', predictions[i], '\nActual fee:\n', y_test.iloc[i])
