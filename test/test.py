import requests
import asyncio
import aiohttp
import random

def printBlock(json):
    print("Block:")
    print("\tData:\t\t", json['data'])
    print("\tPrevious Hash:\t", json['previousHash'][:10])
    print("\tNonce:\t\t", json['nonce'])
    print("\tDifficulty:\t", json['difficulty'])
    print("\tHash:\t\t", json['hash'][:10])
    print("\tHeight:\t\t", json['height'])
    print("\tSumOfDifficulty:", json['sumOfDifficulty'])

def generateBlocks(peerIp, portNo, data):
    return requests.post('http://'+peerIp+':'+portNo+'/block/generateBlocks', json=data).json()

def getTopBlock(peerIp, portNo):
    return (requests.get('http://'+peerIp+':'+portNo+'/block/topBlock').json())['topBlock']

def printTopBlocks(peers):
    for peer in peers:
        topBlock = getTopBlock(peer, '5000')
        print('topBlock for '+peer+':')
        printBlock(topBlock)

def getLongestChain(peerIp, portNo):
    return (requests.get('http://'+peerIp+':'+portNo+'/block/all').json())

def initiateSync(peerIp, portNo, peerToSync):
    return requests.post('http://'+peerIp+':'+portNo+'/block/sync/initiate', json={'peerIp': peerToSync}).json()

def resetPeers(peers):
    data = {}
    data['prefix'] = ''
    data['hash'] = ''
    data['numberOfBlocks'] = 0
    data['difficulty'] = 0
    data['reset'] = True
    urls_data = [ ('http://'+peer+':5000/block/generateBlocks', data) for peer in peers ]
    postUrls(urls_data)

    printTopBlocks(peers)

def randomPeerPair(peers):
    return random.sample(peers, 2)

def dataGenerateBlock(peer):
    data = {}
    data['prefix'] = 'TEST-SIMULATE-WEB_'+str( int( peer.split('.')[-1] )-3 )+' '
    data['hash'] = ''
    data['numberOfBlocks'] = 1
    data['difficulty'] = 5#random.randrange(4,6)
    data['reset'] = False
    return data

async def asyncPost(url_data):
    async with aiohttp.ClientSession() as session:
        url = url_data[0]
        data = url_data[1]
        async with session.post(url, json=data) as response:
            print(url, data, await response.json())
            response.close()

async def asyncWaitPost(url_data, wait):
    await asyncio.sleep(wait)
    async with aiohttp.ClientSession() as session:
        url = url_data[0]
        data = url_data[1]
        async with session.post(url, json=data) as response:
            print(url, data, await response.json())
            response.close()

def postUrls(urls_data):
    tasks = [ asyncio.ensure_future(asyncPost(url_data)) for url_data in urls_data ]
    loop = asyncio.get_event_loop()
    loop.run_until_complete( asyncio.wait(tasks) )

def runTasks(tasks):
    loop = asyncio.get_event_loop()
    loop.run_until_complete( asyncio.wait(tasks) )

async def generate_coro(peers, generate_rate):
    while(True):
        await asyncio.sleep( random.expovariate(lambd=generate_rate) )
        generating_peers = random.sample(peers, 1)
        data_generating_peers = [ dataGenerateBlock(peer) for peer in generating_peers ]
        for iter in range(len(generating_peers)):
            asyncio.ensure_future( asyncPost( ('http://'+generating_peers[iter]+':5000/block/generateBlocks', data_generating_peers[iter]) ) )

async def sync_coro(peers, sync_rate):
    while(True):
        await asyncio.sleep( random.expovariate(lambd=sync_rate) )
        syncing_peers = randomPeerPair(peers)
        data = {'peerIp': syncing_peers[1]}
        asyncio.ensure_future( asyncPost( ('http://'+syncing_peers[0]+':5000/block/sync/initiate', data) ) )

async def wait(wait_time):
    await asyncio.sleep(wait_time)
