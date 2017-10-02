# Script for plotting 'atleast_50%_agreed_chain' vs 'number_of_peers'
# with varying 'normalized_lambda_sync' and 'lambda_generate' and constant time

# 'normalized_lambda_sync' = 'lambda_sync'/'number_of_peers*(number_of_peers-1)'

import os
import pandas
import matplotlib.pyplot as plt
import seaborn as sns

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

analyticsDF = analyticsDF.sort_values(by=['simulation_time', 'number_of_peers', 'lambda_generate', 'lambda_sync'])
print(analyticsDF.columns)

analyticsDF_600 = analyticsDF[analyticsDF['simulation_time']==600]
analyticsDF_600['normalized_lambda_sync'] = analyticsDF_600.apply(lambda row: round(row['lambda_sync']/(row['number_of_peers']*(row['number_of_peers']-1)),3), axis=1)

query = analyticsDF_600[ ( analyticsDF_600['normalized_lambda_sync'].isin([0.002,0.004,0.007]) ) & ( analyticsDF_600['lambda_generate'].isin([0.2,0.4,0.6]) ) ]
g = sns.FacetGrid(query[['number_of_peers','lambda_generate','normalized_lambda_sync','atleast_50%_agreed_chain','longest_100%_agreed_chain']], col="lambda_generate", row="normalized_lambda_sync")
g.map(sns.barplot, "number_of_peers", "atleast_50%_agreed_chain")
plt.show()

query = analyticsDF_600[ ( analyticsDF_600['normalized_lambda_sync'].isin([0.002,0.004,0.007]) ) & ( analyticsDF_600['lambda_generate'].isin([0.2,0.4,0.6]) ) ]
g = sns.FacetGrid(query[['number_of_peers','lambda_generate','normalized_lambda_sync','atleast_50%_agreed_chain','longest_100%_agreed_chain']], col="lambda_generate", row="normalized_lambda_sync")
g.map(sns.barplot, "number_of_peers", "longest_100%_agreed_chain")
plt.show()

query = analyticsDF_600[ ( analyticsDF_600['normalized_lambda_sync'].isin([0.002,0.004,0.007]) ) & ( analyticsDF_600['lambda_generate'].isin([0.2,0.4,0.6]) ) ]
g = sns.FacetGrid(query[['number_of_peers','lambda_generate','normalized_lambda_sync','orphaned_blocks']], col="lambda_generate", row="normalized_lambda_sync")
g.map(sns.barplot, "number_of_peers", "orphaned_blocks")
plt.show()
