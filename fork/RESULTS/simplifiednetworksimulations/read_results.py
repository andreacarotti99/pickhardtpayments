import pandas as pd
from matplotlib import pyplot as plt

df = pd.read_csv('results_1000trans_10000SAT_1000mu_distunif_amountdistfixe_1.csv')

df = df.sort_values(by='capacity', ascending=False)
ax = df.plot(x='node', y='ratio', kind='bar')
plt.yscale('log')
ax.set_xticklabels(df['routed_payments'], rotation=90, fontsize=3)
plt.show()
