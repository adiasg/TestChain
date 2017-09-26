import test
import pandas
import psycopg2
import datetime
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns

def testAnalyze(number_of_peers, lambda_sync, lambda_generate, simulation_time):

    working_dir = str(sys.argv[1])
    if working_dir[-1]!='/':
        working_dir += '/'
    #working_dir = 'data/'+'8_600.0_2017-09-00:04.30/'
    print(working_dir)

    testParameters = {'number_of_peers': number_of_peers, 'lambda_sync': lambda_sync, 'lambda_generate': lambda_generate, 'simulation_time': simulation_time}
    testParametersDF = pandas.DataFrame([testParameters])

    blocksDF = pandas.read_csv(working_dir+'blocksDF.csv', index_col=0)
    blocksDF = blocksDF.sort_values(by=['time_of_insertion'])
    start_time = blocksDF.iloc[0]['time_of_insertion']
    #start_time = datetime.datetime.strptime( start_time, "%Y-%m-%d %H:%M:%S.%f" )
    #blocksDF['time_of_insertion'] = blocksDF.apply(lambda row: (datetime.datetime.strptime( row['time_of_insertion'], "%Y-%m-%d %H:%M:%S.%f" )-start_time).total_seconds(), axis=1)
    print("---------------------- blocksDF ----------------------")
    print(blocksDF.columns)
    print("\n")

    longestChainDF = pandas.read_csv(working_dir+'longestChainDF.csv', index_col=0)
    print("---------------------- longestChainDF ----------------------")
    print(longestChainDF.columns)
    print("\n")

    networkLongestChainDF = pandas.read_csv(working_dir+'networkLongestChainDF.csv', index_col=0)
    #networkLongestChainDF['time_of_insertion'] = networkLongestChainDF.apply(lambda row: (datetime.datetime.strptime( row['time_of_insertion'], "%Y-%m-%d %H:%M:%S.%f" )-start_time).total_seconds(), axis=1)
    networkLongestChainDF = networkLongestChainDF.sort_values(by=['time_of_insertion'])
    last_added_block = networkLongestChainDF.iloc[-1]
    num_orphaned_blocks = len(blocksDF.hash.unique())- len(networkLongestChainDF.hash.unique())
    start_time = networkLongestChainDF.iloc[0]['time_of_insertion']
    print("---------------------- networkLongestChainDF ----------------------")
    print(networkLongestChainDF.columns)
    print("\n")

    testResults = {}
    print("Performance Metrics:")
    testResults['last_add_time'] = last_added_block['time_of_insertion']-start_time+last_added_block['latency']
    print( "\tLast add time: {0}".format( testResults['last_add_time'] ))
    testResults['longest_100%_agreed_chain'] = len(networkLongestChainDF.iloc[1:])
    print( "\tLongest agreed chain length: {0}".format( testResults['longest_100%_agreed_chain'] ))
    testResults['latency'] = sum(networkLongestChainDF.iloc[1:]['latency'])/len(networkLongestChainDF.iloc[1:])
    print( "\tAverage Latency: {0} seconds per block".format( testResults['latency'] ))
    testResults['throughput'] = len(networkLongestChainDF.iloc[1:])/simulation_time
    print( "\tThroughput: {0} blocks per second".format( testResults['throughput'] ))
    testResults['orphaned_blocks'] = num_orphaned_blocks
    print( "\tNumber of orphaned blocks: {0}".format( testResults['orphaned_blocks'] ))
    print("\n")
    print("Last 100%-Agreed Block:")
    last_agreed_block = longestChainDF[ longestChainDF['percent_acceptance']==100 ].sort_values(by=['height']).iloc[-1]
    print("\tHash:", last_agreed_block['hash'])
    print("\tHeight:", last_agreed_block['height'])
    print("\n")
    testResults['last_100%_agreed_block'] = last_agreed_block['hash']
    testResultsDF = pandas.DataFrame([testResults])

    sns.set_style("darkgrid")
    #sns.set_context("paper", rc={"font.size":25,"axes.titlesize":20,"axes.labelsize":20})
    #sns.barplot(x='time_of_insertion', y='latency', data=networkLongestChainDF, palette="muted")
    b = sns.barplot(x='time_of_insertion', y='latency', data=networkLongestChainDF, palette="muted")
    b.set_xlabel('Time of insertion', fontsize=15)
    b.set_ylabel('Latency', fontsize=15)
    b.tick_params(labelsize=15)
    b.set_xticklabels(b.get_xticklabels(), rotation=90)
    #print(type(b.get_xticklabels()))
    #print(b.get_xticklabels())
    #for i in b.get_xticklabels():
        #print(i.get_text())
    b.set_xticklabels( map( int, map(float, [ tick_item.get_text() for tick_item in b.get_xticklabels() ] ) ) )
    sns.plt.show()

    """
    dir_name = str(number_of_peers)+'_'+str(simulation_time)+'_'+datetime.datetime.now().strftime('%Y-%m-%H:%M.%S')
    working_dir = 'data/'+dir_name+'/'
    os.makedirs(working_dir)

    blocksDF.to_csv(working_dir+'blocksDF.csv')
    logGenerateDF.to_csv(working_dir+'logGenerateDF.csv')
    logReceiveDF.to_csv(working_dir+'logReceiveDF.csv')
    longestChainDF.to_csv(working_dir+'longestChainDF.csv')
    networkLongestChainDF.to_csv(working_dir+'networkLongestChainDF.csv')
    testParametersDF.to_csv(working_dir+'testParametersDF.csv')
    testResultsDF.to_csv(working_dir+'testResultsDF.csv')
    """

if __name__ == '__main__':
    testAnalyze(7, 8, 10, 100)
