import test
import pandas
import psycopg2
import datetime
import os
import matplotlib.pyplot as plt
import seaborn as sns

def blockDataSeries(block_json):
    ds = pandas.Series()
    ds['height'] = block_json['height']
    ds['hash'] = block_json['hash']
    ds['previoushash'] = block_json['previousHash']
    return ds

def checkQuerySizes(queries):
    for query in queries:
        if len(query)==0:
            return False
    return True

def atleastOneQuery_peer(queries):
    for peer, query in queries:
        if len(query)>0:
            return True
    return False

def checkCurrentHashes(current_hashes):
    for iter in range( 1,len(current_hashes) ):
        if current_hashes[iter-1]!=current_hashes[iter]:
            return False
    return True

def analyze(number_of_peers, lambda_sync, lambda_generate, simulation_time):
    connect_str = " dbname='myproject' user='myprojectuser' password='password' host='172.32.0.2' port='5432' "
    connectionToDb = psycopg2.connect(connect_str)

    testParameters = {'number_of_peers': number_of_peers, 'lambda_sync': lambda_sync, 'lambda_generate': lambda_generate, 'simulation_time': simulation_time}
    print(testParameters)
    testParametersDF = pandas.DataFrame([testParameters])

    blocksDF = pandas.DataFrame()
    peer_noOfBlocks = {}
    for peer_id in range(1,number_of_peers+1):
        df = pandas.read_sql( "select hash, time_of_insertion, block->'previousHash' as previoushash, block->'height' as height, block->'sumOfDifficulty' as sumofdifficulty, block->'nonce' as nonce, block->'difficulty' as difficulty, block->'data' as data from blocks_web"+str(peer_id)+";", connectionToDb )
        df['peer_id'] = peer_id
        peer_noOfBlocks['web'+str(peer_id)] = len(df)
        #print(df.head())
        blocksDF = blocksDF.append(df, ignore_index=True, verify_integrity=True)
    blocksDF = blocksDF.sort_values(by=['time_of_insertion'])
    start_time = blocksDF.query("height==0").iloc[-1]['time_of_insertion']
    blocksDF['time_of_insertion'] = blocksDF.apply(lambda row: (row['time_of_insertion']-start_time).total_seconds(), axis=1)
    blocksDF = blocksDF.query("time_of_insertion<"+str(simulation_time))
    print("---------------------- blocksDF ----------------------")
    print(blocksDF.columns)
    #print(blocksDF)
    print(peer_noOfBlocks)
    print("\n")

    logGenerateDF = pandas.DataFrame()
    for peer_id in range(1,number_of_peers+1):
        df = pandas.read_sql( "select log_time, hash from log_block_generate_web"+str(peer_id)+";", connectionToDb )
        df['peer_id'] = peer_id
        #print(df.head())
        logGenerateDF = logGenerateDF.append(df, ignore_index=True, verify_integrity=True)
    logGenerateDF = logGenerateDF.sort_values(by=['log_time'])
    logGenerateDF['time_of_insertion'] = logGenerateDF.apply(lambda row: (row['log_time']-start_time).total_seconds(), axis=1)
    print("---------------------- logGenerateDF ----------------------")
    print(logGenerateDF.columns)
    #print(logGenerateDF)
    print("\n")

    logReceiveDF = pandas.DataFrame()
    for peer_id in range(1,number_of_peers+1):
        df = pandas.read_sql( "select log_time, hash from log_block_receive_web"+str(peer_id)+";", connectionToDb )
        df['peer_id'] = peer_id
        #print(df.head())
        logReceiveDF = logReceiveDF.append(df, ignore_index=True, verify_integrity=True)
    logReceiveDF = logReceiveDF.sort_values(by=['log_time'])
    logReceiveDF['time_of_insertion'] = logReceiveDF.apply(lambda row: (row['log_time']-start_time).total_seconds(), axis=1)
    print("---------------------- logReceiveDF ----------------------")
    print(logReceiveDF.columns)
    #print(logReceiveDF)
    print("\n")

    longestChainDF = pandas.DataFrame()
    peer_longestChainSize = {}
    for peer_id in range(1,number_of_peers+1):
        longestChain = test.getLongestChain('172.32.0.'+str(3+peer_id), '5000')
        peer_longestChainSize['web'+str(peer_id)] = len(longestChain)
        for block in longestChain:
            ds = blockDataSeries(block)
            ds['peer_id'] = peer_id
            longestChainDF = longestChainDF.append(ds, ignore_index=True, verify_integrity=True)

    queries = [ longestChainDF.query("peer_id=="+str(peer_id)+" and height==0") for peer_id in range(1,number_of_peers+1) ]
    last_common_hash = None
    while(checkQuerySizes(queries)):
        current_hashes = [ query.iloc[0]['hash'] for query in queries ]
        #print(current_hashes)
        if not checkCurrentHashes(current_hashes):
            break
        else:
            last_common_hash = queries[0].iloc[0]
            #print("For hash:", last_common_hash['hash'])
            latency_query = blocksDF.query(" hash=='"+last_common_hash['hash']+"' ").sort_values(by=['time_of_insertion'])
            #print(latency_query)
            generate_time = latency_query.iloc[0]['time_of_insertion']
            last_add_time = latency_query.iloc[-1]['time_of_insertion']
            #print("Min:", generate_time)
            #print("Max:", last_add_time)
            #print("Latency:", (last_add_time-generate_time).total_seconds() )
            blocksDF.loc[ (blocksDF['time_of_insertion']==generate_time)&(blocksDF['hash']==last_common_hash['hash']), 'latency' ] = last_add_time-generate_time
        queries = [ longestChainDF.query("peer_id=="+str(peer_id)+" and previoushash=='"+current_hashes[peer_id-1]+"'") for peer_id in range(1,number_of_peers+1) ]
    '''
    print("Last Common Block:")
    print("\tHash:", last_common_hash['hash'])
    print("\tHeight:", last_common_hash['height'])
    print("\n")
    '''

    #longestChainDF['latency'] = None
    longestChainDF['agreeing_peers'] = 0
    queries = [ ( peer_id, longestChainDF.query("peer_id=="+str(peer_id)+" and height==0") ) for peer_id in range(1,number_of_peers+1) ]
    last_common_hash = None
    while(atleastOneQuery_peer(queries)):
        current_hashes = []
        for peer, query in queries:
            if len(query)>0:
                current_hashes.append( ( peer, query.iloc[0] ) )
                #print( query.iloc[0] )
                #print( query.iloc[0].name )
                longestChainDF.loc[ longestChainDF['hash']==query.iloc[0]['hash'], 'agreeing_peers'] += 1
                #print( longestChainDF.loc[ query.iloc[0].name ] )
                #inp = input('Waiting...')
        #print(current_hashes)
        #print("len(current_hashes):", len(current_hashes))
        #for peer, hash in current_hashes:
            #print("\t", peer, hash['hash'])
        queries = [ ( peer_id, longestChainDF.query("peer_id=="+str(peer_id)+" and previoushash=='"+hash['hash']+"'") ) for peer_id, hash in current_hashes ]
    longestChainDF['percent_acceptance'] = longestChainDF.apply(lambda row: (100.0*row['agreeing_peers'])/number_of_peers, axis=1)
    #print(longestChainDF.sort_values(by=['agreeing_peers']))

    print("---------------------- longestChainDF ----------------------")
    print(longestChainDF.columns)
    #print(longestChainDF)
    print(peer_longestChainSize)
    print("\n")
    #print(longestChainDF.iloc[3])
    #print(type(longestChainDF.iloc[3]['height']))
    #print(type(longestChainDF.iloc[3]['peer_id']))
    #print(type(longestChainDF.iloc[3]['percent_acceptance']))
    #print(type(longestChainDF.iloc[3]['agreeing_peers']))
    #print(type(longestChainDF.iloc[3]['hash']))
    print("\n")

    networkLongestChainDF = blocksDF[ blocksDF['latency']>0 ]
    start_time = blocksDF.query("height==0").sort_values(by=['time_of_insertion']).iloc[-1]['time_of_insertion']
    #start_time = networkLongestChainDF.iloc[0]['time_of_insertion']
    last_added_block = networkLongestChainDF.iloc[-1]
    num_orphaned_blocks = len(blocksDF.hash.unique())- len(networkLongestChainDF.hash.unique())
    #print("Total Time:", (last_added_block['time_of_insertion']-start_time).total_seconds()+last_added_block['latency'])

    testResults = {}
    print("Performance Metrics:")
    print(type(last_added_block['time_of_insertion']))
    print(type(start_time))
    print(type(last_added_block['latency']))
    testResults['last_add_time'] = (last_added_block['time_of_insertion']-start_time)+last_added_block['latency']
    print( "\tLast add time: {0}".format( testResults['last_add_time'] ))
    testResults['longest_100%_agreed_chain'] = len(networkLongestChainDF.iloc[1:])
    print( "\tLongest agreed chain length: {0}".format( testResults['longest_100%_agreed_chain'] ))
    if len(networkLongestChainDF.iloc[1:]) > 0:
        testResults['latency'] = sum(networkLongestChainDF.iloc[1:]['latency'])/len(networkLongestChainDF.iloc[1:])
    else:
        testResults['latency'] = None
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

if __name__ == '__main__':
    analyze(20, 0.6, 0.4, 600)
