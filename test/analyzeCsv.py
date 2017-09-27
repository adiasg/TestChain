import test
import pandas
import psycopg2
import datetime
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns

def analyzeCsv():

    working_dir = str(sys.argv[1])
    if working_dir[-1]!='/':
        working_dir += '/'
    #working_dir = 'data/'+'8_600.0_2017-09-00:04.30/'
    print(working_dir)

    testParametersDF = pandas.read_csv(working_dir+'testParametersDF.csv', index_col=0)
    testResultsDF = pandas.read_csv(working_dir+'testResultsDF.csv', index_col=0)

    number_of_peers = testParametersDF.iloc[0]['number_of_peers']
    lambda_sync = testParametersDF.iloc[0]['lambda_sync']
    lambda_generate = testParametersDF.iloc[0]['lambda_generate']
    simulation_time = testParametersDF.iloc[0]['simulation_time']

    print("number_of_peers:", number_of_peers)
    print("lambda_sync:", lambda_sync)
    print("lambda_generate:", lambda_generate)
    print("simulation_time:", simulation_time)

    blocksDF = pandas.read_csv(working_dir+'blocksDF.csv', index_col=0)
    blocksDF = blocksDF.sort_values(by=['time_of_insertion'])
    #start_time = blocksDF.iloc[0]['time_of_insertion']
    start_time = blocksDF.query("height==0").iloc[-1]['time_of_insertion']
    print("Start time:", start_time)
    print("---------------------- blocksDF ----------------------")
    print(blocksDF.columns)
    print("\n")

    longestChainDF = pandas.read_csv(working_dir+'longestChainDF.csv', index_col=0)
    print("---------------------- longestChainDF ----------------------")
    print(longestChainDF.columns)
    print("\n")

    networkLongestChainDF = pandas.read_csv(working_dir+'networkLongestChainDF.csv', index_col=0)
    networkLongestChainDF = networkLongestChainDF.sort_values(by=['time_of_insertion'])
    last_added_block = networkLongestChainDF.iloc[-1]
    num_orphaned_blocks = len(blocksDF.hash.unique())- len(networkLongestChainDF.hash.unique())
    start_time = blocksDF.query("height==0").sort_values(by=['time_of_insertion']).iloc[-1]['time_of_insertion']
    print("Start time:", start_time)
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
    b = sns.barplot(x='time_of_insertion', y='latency', data=networkLongestChainDF, palette="muted")
    b.set_xlabel('Time of insertion', fontsize=15)
    b.set_ylabel('Latency', fontsize=15)
    b.tick_params(labelsize=15)
    b.set_xticklabels(b.get_xticklabels(), rotation=90)
    b.set_xticklabels( map( int, map(float, [ tick_item.get_text() for tick_item in b.get_xticklabels() ] ) ) )
    plt.show()

    blocksDF.to_csv(working_dir+'blocksDF.csv')
    #logGenerateDF.to_csv(working_dir+'logGenerateDF.csv')
    #logReceiveDF.to_csv(working_dir+'logReceiveDF.csv')
    #longestChainDF.to_csv(working_dir+'longestChainDF.csv')
    networkLongestChainDF.to_csv(working_dir+'networkLongestChainDF.csv')
    #testParametersDF.to_csv(working_dir+'testParametersDF.csv')
    testResultsDF.to_csv(working_dir+'testResultsDF.csv')

if __name__ == '__main__':
    analyzeCsv()
