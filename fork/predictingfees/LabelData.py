import pandas as pd
from matplotlib import pyplot as plt

'''
This script is used to assign a label to data extracted from simulation. Specifically we are categorizing 
each node from the labels list depending on its ratio value.
'''


labels = ["LOW", "MEDIUM", "HIGH"]
thresholds = [0.0001, 0.0003]

file_to_label = 'results_10000trans_10000SAT_1000mu_distunif_amountdistfixe_1.csv'

df = pd.read_csv(file_to_label)
df = df.sort_values('ratio', ascending=False)

df.loc[df['ratio'] == 0, 'ROI'] = "NO ROI"

df_NO_ROI = df[df['ratio'] == 0]
df_REST = df[df['ratio'] > 0]

df_REST['ROI'] = pd.cut(df_REST['ratio'], bins=[-float('inf')] + thresholds + [float('inf')], labels=labels)

df_final = df_REST.append(df_NO_ROI)

df_final.to_csv('labeled_' + file_to_label, index=False)


