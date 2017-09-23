import requests
import asyncio
import aiohttp

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

def initiateSync(peerIp, portNo, peerToSync):
    return requests.post('http://'+peerIp+':'+portNo+'/block/sync/initiate', json={'peerIp': peerToSync}).json()

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
