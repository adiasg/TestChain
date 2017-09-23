import test
from test import printBlock
import asyncio
import random

def printTopBlocks(peers):
    for peer in peers:
        topBlock = test.getTopBlock(peer, '5000')
        print('topBlock for '+peer+':')
        printBlock(topBlock)

def resetPeers(peers):
    data = {}
    data['prefix'] = ''
    data['hash'] = ''
    data['numberOfBlocks'] = 0
    data['difficulty'] = 0
    data['reset'] = True
    urls_data = [ ('http://'+peer+':5000/block/generateBlocks', data) for peer in peers ]
    test.postUrls(urls_data)

    printTopBlocks(peers)

def randomPeerPair(peers):
    return random.sample(peers, 2)

def dataGenerateBlock(peer):
    data = {}
    data['prefix'] = 'TEST-SYNC3-WEB'+peer[-1]+' '
    data['hash'] = ''
    data['numberOfBlocks'] = 1
    data['difficulty'] = 5#random.randrange(4,6)
    data['reset'] = False
    return data

async def printing_coro(string):
    print(string)

async def generate_coro(peers, generate_rate):
    while(True):
        await asyncio.sleep( random.expovariate(lambd=generate_rate) )
        generating_peers = random.sample(peers, 1)
        data_generating_peers = [ dataGenerateBlock(peer) for peer in generating_peers ]
        for iter in range(len(generating_peers)):
            asyncio.ensure_future( test.asyncPost( ('http://'+generating_peers[iter]+':5000/block/generateBlocks', data_generating_peers[iter]) ) )

async def sync_coro(peers, sync_rate):
    while(True):
        await asyncio.sleep( random.expovariate(lambd=sync_rate) )
        syncing_peers = randomPeerPair(peers)
        data = {'peerIp': syncing_peers[1]}
        asyncio.ensure_future( test.asyncPost( ('http://'+syncing_peers[0]+':5000/block/sync/initiate', data) ) )

async def wait(wait_time):
    await asyncio.sleep(wait_time)

if __name__ == '__main__':
    number_of_peers = 3
    avg_inter_sync_time_per_peer = 9
    avg_inter_generate_block_time_per_peer = 10
    lambda_sync = number_of_peers * 1.0 / avg_inter_sync_time_per_peer
    lambda_generate = number_of_peers * 1.0 / avg_inter_generate_block_time_per_peer

    peers = [ '172.32.0.'+str(4+x) for x in range(number_of_peers) ]

    resetPeers(peers)

    loop = asyncio.get_event_loop()
    future1 = asyncio.ensure_future( generate_coro(peers, lambda_generate) )
    future2 = asyncio.ensure_future( sync_coro(peers, lambda_sync) )
    #loop.run_until_complete( asyncio.gather(future1, future2) )
    loop.run_until_complete( wait(100) )

    printTopBlocks(peers)
