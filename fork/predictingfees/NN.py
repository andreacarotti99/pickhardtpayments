import numpy as np
import pandas as pd
from keras import Sequential
from keras.layers import Dense
from sklearn.model_selection import train_test_split

from sklearn.preprocessing import MinMaxScaler


# Save into a df the info about all the 1000 highest capacity nodes
node_info_df = pd.read_csv('graphinfo.csv')

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

# Save into a df the ratio about all the nodes that routed at least one transaction (not all the nodes)
fees_df = pd.read_csv('labeled_results_10000trans_10000SAT_1000mu_distunif_amountdistfixe_1.csv')

# Keep only the columns node and ROI
fees_df = fees_df.loc[:, ['node', 'ROI']]

merged_df = pd.merge(node_info_df, fees_df, on='node', how='inner')

merged_df = merged_df.sort_values('ROI', ascending=False)

# Sample the dataset such that we have the same amount of labels for each category
counts = merged_df['ROI'].value_counts()
min_count = counts.min()
new_df = pd.concat([merged_df[merged_df['ROI'] == category].sample(n=min_count, replace=True) for category in counts.index])
new_df = new_df.reset_index(drop=True)


# --------------------------------

new_df = new_df.drop(columns=[
    'node',
    'closeness_pickhardt',
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
])


categories = ['HIGH', 'MEDIUM', 'LOW', 'NO ROI']
new_df['ROI'] = pd.Categorical(new_df['ROI'], categories=categories, ordered=True)

X = new_df.drop('ROI', axis=1)  # Input features (node information)
y = new_df['ROI']  # Output variable (fees earned)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

model = Sequential()
model.add(Dense(units=X_train.shape[1], activation='relu', input_dim=X_train.shape[1]))
model.add(Dense(units=16, activation='relu'))
model.add(Dense(units=16, activation='relu'))
model.add(Dense(units=len(categories), activation='softmax'))  # use softmax activation for multi-class classification

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])  # use categorical cross-entropy loss for multi-class classification

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
