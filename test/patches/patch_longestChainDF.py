import os
import pandas

data_folder = 'data/'
for working_dir in os.listdir(data_folder):
    try:
        testParametersDF = pandas.read_csv(data_folder+working_dir+'/'+'testParametersDF.csv', index_col=0)
        testResultsDF = pandas.read_csv(data_folder+working_dir+'/'+'testResultsDF.csv', index_col=0)
        longestChainDF = pandas.read_csv(data_folder+working_dir+'/'+'longestChainDF.csv', index_col=0)
        #number_of_peers = testParametersDF.iloc[0]['number_of_peers']
        #longestChainDF = longestChainDF.sort_values(by=['percent_acceptance'])
        longestChainDF = longestChainDF[longestChainDF['percent_acceptance']>50]
        longestChainDF = longestChainDF.sort_values(by=['height'])
        print(longestChainDF.iloc[-1]['percent_acceptance'], longestChainDF.iloc[-1]['height'])
        testResultsDF['atleast_50%_agreed_chain'] = longestChainDF.iloc[-1]['height']
        testResultsDF['atleast_50%_agreed_hash'] = longestChainDF.iloc[-1]['hash']
        testResultsDF.to_csv(data_folder+working_dir+'/'+'testResultsDF.csv')
    except OSError:
        print('Error for directory:', working_dir)
