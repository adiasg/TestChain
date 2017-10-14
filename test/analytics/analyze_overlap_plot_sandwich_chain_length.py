import os
import pandas
import matplotlib.pyplot as plt
import seaborn as sns
import math
import numpy

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
analyticsDF = analyticsDF[(analyticsDF['lambda_generate'].isin([0.2,0.4,0.6]))]

# print('analyticsDF')
# print("size:", analyticsDF.shape)
# print("unique:", analyticsDF.working_dir.unique().shape)

query_n2 = analyticsDF[(analyticsDF['lambda_sync']/(analyticsDF['number_of_peers']*(analyticsDF['number_of_peers']-1))).round(3).isin([0.002,0.004,0.007])].copy()
query_n2['n2'] = True
query_n2['normalized_lambda_sync'] = query_n2.apply(lambda row: round((row['lambda_sync']/(row['number_of_peers']*(row['number_of_peers']-1))), 3) , axis=1)
# print('query_n2')
# print("size:", query_n2.shape)
# print("unique:", query_n2.working_dir.unique().shape)

query_n_logn = analyticsDF[(analyticsDF['lambda_sync']/(analyticsDF['number_of_peers']*numpy.log2(analyticsDF['number_of_peers']))).round(3).isin([0.006,0.012,0.018])].copy()
query_n_logn['n_logn'] = True
query_n_logn['normalized_lambda_sync'] = query_n_logn.apply(lambda row: round(row['lambda_sync']/(row['number_of_peers']*math.log(row['number_of_peers'],2)),3), axis=1)
# print('query_n_logn')
# print("size:", query_n_logn.shape)
# print("unique:", query_n_logn.working_dir.unique().shape)

query_n = analyticsDF[(analyticsDF['lambda_sync']/(analyticsDF['number_of_peers'])).round(2).isin([0.02,0.04,0.06])].copy()
query_n['n'] = True
query_n['normalized_lambda_sync'] = query_n.apply(lambda row: round((row['lambda_sync']/row['number_of_peers']),2), axis=1)
# print('query_n')
# print("size:", query_n.shape)
# print("unique:", query_n.working_dir.unique().shape)

query = query_n.append(query_n2)
query = query.append(query_n_logn)
query = query[(query['simulation_time']==600) & (query['number_of_peers'].isin([10,15,20,25]))]
# print('query')
# print("size:", query.shape)
# print("unique:", query.working_dir.unique().shape)

lambda_generate_list = [0.2, 0.4]
nls_list = [ [0.02, 0.006, 0.002] ]
#lambda_generate_list = [0.4]
#nls_list = [ (0.04, 0.004) ]

for lambda_generate in lambda_generate_list:
    for nls in nls_list:
        print("lambda_generate:", lambda_generate)
        print("nls:", nls)
        query_temp = query[ (query['lambda_generate']==lambda_generate) & query['normalized_lambda_sync'].isin(nls) ]
        query_temp = query_temp.sort_values(by=['working_dir'])
        print('query_temp')
        print("size:", query_temp.shape)
        print("unique:", query_temp.working_dir.unique().shape)

        # query_temp_10 = query_temp[query_temp['number_of_peers']==10]
        # print('query_temp_10')
        # print("size:", query_temp_10.shape)
        # print("unique:", query_temp_10.working_dir.unique().shape)
        #
        # query_temp.to_csv('test_1.csv')
        point_plot = None
        point_plot = sns.pointplot(x='number_of_peers', y='0.5-chain', hue='normalized_lambda_sync', data=query_temp)
        #g = sns.FacetGrid(query_temp, hue='normalized_lambda_sync')
        #g.map(sns.pointplot, 'number_of_peers', '0.5-chain')
        fig = point_plot.get_figure()
        img_name = (str(lambda_generate) + '_' + str(nls[0]) + '_' + str(nls[1]) + '_' + str(nls[2])).replace('.','') + '.png'
        fig.savefig('plots/sandwich/'+img_name, dpi=400)
        plt.show()
