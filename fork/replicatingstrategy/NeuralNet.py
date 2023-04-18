import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense

# Load and preprocess node information CSV
node_info_df = pd.read_csv('node_info.csv')

# Result df
fees_df = pd.read_csv('../RESULTS/replicate_best_strategy/decrease_liquidity_send_paym_and_replicate/results_10000trans_10000SAT_100mu_cosimo_19jan2023_converted_dist_weig_linear_1.csv')
fees_df = fees_df.loc[:, ['node', 'total_fee']]


# Merge node information and fees earned dataframes
merged_df = pd.merge(node_info_df, fees_df, on='node', how='inner')

# Split data into training and testing sets
X = merged_df.drop('fees_earned', axis=1)  # Input features (node information)
y = merged_df['fees_earned']  # Output variable (fees earned)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define the neural network model
model = Sequential()
# Adding layers to the model, e.g. Dense layers with appropriate activation functions and input/output dimensions)
model.add(Dense(units=64, activation='relu', input_dim=X_train.shape[1]))
model.add(Dense(units=32, activation='relu'))
model.add(Dense(units=1, activation='linear'))

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(X_train, y_train, epochs=100, batch_size=32, verbose=1)

# Evaluate the model
mse = model.evaluate(X_test, y_test, batch_size=32)
print('Mean Squared Error:', mse)

# Use the trained model for prediction
predictions = model.predict(X_test)
