from test import printTopBlocks

number_of_peers = 50
peers = [ '172.32.0.'+str(4+x) for x in range(number_of_peers) ]
printTopBlocks(peers)
