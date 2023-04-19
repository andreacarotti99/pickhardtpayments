import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense

# Load and preprocess node information CSV
node_info_df = pd.read_csv('graphinfo.csv')
node_info_df = node_info_df.drop(columns=['bc_ppm', 'bc_base'])

# Result df
fees_df = pd.read_csv('results_1000trans_10000SAT_1000mu_distunif_amountdistfixe_1.csv')
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

for i in range(len(predictions)):
    print('Node:', X_test.index[i], 'Predicted Fee:', predictions[i], 'Actual Fee:', y_test.iloc[i])
