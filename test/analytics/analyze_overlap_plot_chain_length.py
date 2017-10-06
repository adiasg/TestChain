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

analyticsDF['0.5-chain'] = analyticsDF['atleast_50%_agreed_chain']

query_n2 = analyticsDF[(analyticsDF['lambda_sync']/(analyticsDF['number_of_peers']*(analyticsDF['number_of_peers']-1))).round(3).isin([0.002,0.004,0.007]) & (analyticsDF['lambda_generate'].isin([0.2,0.4,0.6]))]
query_n2['n2'] = True
query_n2['normalized_lambda_sync'] = query_n2.apply(lambda row: round((row['lambda_sync']/(row['number_of_peers']*(row['number_of_peers']-1))), 3) , axis=1)

query_n = analyticsDF[(analyticsDF['lambda_sync']/(analyticsDF['number_of_peers'])).round(2).isin([0.02,0.04,0.06]) & (analyticsDF['lambda_generate'].isin([0.2,0.4,0.6]))]
query_n['n'] = True
query_n['normalized_lambda_sync'] = query_n.apply(lambda row: round((row['lambda_sync']/row['number_of_peers']),2), axis=1)

query = query_n.append(query_n2)
query = query[(query['simulation_time']==600) & (query['number_of_peers'].isin([10,15,20,25]))]

lambda_generate_list = [0.2, 0.4, 0.6]
nls_list = [ (0.02, 0.002), (0.04, 0.004), (0.06, 0.007) ]
#lambda_generate_list = [0.4]
#nls_list = [ (0.04, 0.004) ]

for lambda_generate in lambda_generate_list:
    for nls in nls_list:
        print("lambda_generate:", lambda_generate)
        print("nls:", nls)
        query_temp = query[ (query['lambda_generate']==lambda_generate) & ((query['normalized_lambda_sync']==nls[0]) | (query['normalized_lambda_sync']==nls[1])) ]
        g = sns.FacetGrid(query_temp, hue='normalized_lambda_sync')
        g.map(sns.pointplot, 'number_of_peers', '0.5-chain')
        img_name = (str(lambda_generate) + '_' + str(nls[0]) + '_' + str(nls[1])).replace('.','') + '.png'
        g.savefig('plots/overlap_chain_length/'+img_name, dpi=400)
        #plt.show()
