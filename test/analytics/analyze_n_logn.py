# Script for plotting 'atleast_50%_agreed_chain' vs 'number_of_peers'
# with varying 'n_l_sync' and 'l_gen' and constant time

# 'n_l_sync' = 'lambda_sync'/'number_of_peers'

import os
import pandas
import matplotlib.pyplot as plt
import seaborn as sns
import math

data_dir = '../data/'
analyticsDF = pandas.DataFrame()
for working_dir in os.listdir(data_dir):
    working_dir = data_dir+working_dir+'/'
    try:
        testParametersDF = pandas.read_csv(working_dir+'testParametersDF.csv', index_col=0)
        testResultsDF = pandas.read_csv(working_dir+'testResultsDF.csv', index_col=0)
        testParametersDF['working_dir'] = working_dir
        analyticsDF = analyticsDF.append(pandas.concat([testResultsDF,testParametersDF], axis=1), ignore_index=True)
    except OSError:
        print("OSError for directory:", working_dir)

analyticsDF['n_l_sync'] = analyticsDF.apply(lambda row: round(row['lambda_sync']/(row['number_of_peers']*math.log(row['number_of_peers'],2)),3), axis=1)
analyticsDF = analyticsDF.sort_values(by=['simulation_time', 'number_of_peers', 'lambda_generate', 'lambda_sync'])
analyticsDF['l_gen'] = analyticsDF['lambda_generate']
analyticsDF['0.5-chain'] = analyticsDF['atleast_50%_agreed_chain']
print(analyticsDF.columns)

analyticsDF_600 = analyticsDF[analyticsDF['simulation_time']==600]

nls_values = [0.006, 0.012, 0.018]

query = analyticsDF_600[ ( analyticsDF_600['n_l_sync'].isin(nls_values) ) & ( analyticsDF_600['l_gen'].isin([0.2,0.4,0.6]) ) ]
g = sns.FacetGrid(query[['number_of_peers','l_gen','n_l_sync','0.5-chain','longest_100%_agreed_chain']], col="l_gen", row="n_l_sync")
g.map(sns.pointplot, "number_of_peers", "0.5-chain")
plt.show()

query = analyticsDF_600[ ( analyticsDF_600['n_l_sync'].isin(nls_values) ) & ( analyticsDF_600['l_gen'].isin([0.2,0.4,0.6]) ) ]
g = sns.FacetGrid(query[['number_of_peers','l_gen','n_l_sync','0.5-chain','longest_100%_agreed_chain']], col="l_gen", row="n_l_sync")
g.map(sns.barplot, "number_of_peers", "longest_100%_agreed_chain")
plt.show()

query = analyticsDF_600[ ( analyticsDF_600['n_l_sync'].isin(nls_values) ) & ( analyticsDF_600['l_gen'].isin([0.2,0.4,0.6]) ) ]
g = sns.FacetGrid(query[['number_of_peers','l_gen','n_l_sync','orphaned_blocks']], col="l_gen", row="n_l_sync")
g.map(sns.barplot, "number_of_peers", "orphaned_blocks")
plt.show()
