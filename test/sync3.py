import unittest
import test
from test import printBlock, postUrls
import asyncio
import random

async def runTest_gen(iterations):
    for iter in range(iterations):
        data1_gen = {}
        data1_gen['prefix'] = 'TEST-SYNC3-WEB1 '
        data1_gen['hash'] = ''
        data1_gen['numberOfBlocks'] = random.randrange(5,30)
        data1_gen['difficulty'] = random.randrange(3,5)
        data1_gen['reset'] = False

        data2_gen = {}
        data2_gen['prefix'] = 'TEST-SYNC3-WEB2 '
        data2_gen['hash'] = ''
        data2_gen['numberOfBlocks'] = random.randrange(5,30)
        data2_gen['difficulty'] = random.randrange(3,5)
        data2_gen['reset'] = False

        data3_gen = {}
        data3_gen['prefix'] = 'TEST-SYNC3-WEB3 '
        data3_gen['hash'] = ''
        data3_gen['numberOfBlocks'] = random.randrange(5,30)
        data3_gen['difficulty'] = random.randrange(3,5)
        data3_gen['reset'] = False

        asyncio.ensure_future( test.asyncPost( (url1+'/block/generateBlocks', data1_gen) ) )
        asyncio.ensure_future( test.asyncPost( (url2+'/block/generateBlocks', data2_gen) ) )
        asyncio.ensure_future( test.asyncPost( (url3+'/block/generateBlocks', data3_gen) ) )

        await asyncio.sleep(3)

async def runTest_sync(iterations):
    for iter in range(iterations):
        data1_sync = {}
        data1_sync['peerIp'] = '172.32.0.'+random.choice( ['5','6'] )

        data2_sync = {}
        data2_sync['peerIp'] = '172.32.0.'+random.choice( ['4','6'] )

        data3_sync = {}
        data3_sync['peerIp'] = '172.32.0.'+random.choice( ['4','5'] )

        asyncio.ensure_future( test.asyncWaitPost( (url1+'/block/sync/initiate', data1_sync), random.uniform(0,1.2) ) )
        asyncio.ensure_future( test.asyncWaitPost( (url2+'/block/sync/initiate', data2_sync), random.uniform(0,1.2) ) )
        asyncio.ensure_future( test.asyncWaitPost( (url3+'/block/sync/initiate', data3_sync), random.uniform(0,1.2) ) )

        await asyncio.sleep(3)

peer1 = '172.32.0.4'
peer2 = '172.32.0.5'
peer3 = '172.32.0.6'
defaultPortNo = '5000'

url1 = 'http://'+peer1+':'+defaultPortNo
url2 = 'http://'+peer2+':'+defaultPortNo
url3 = 'http://'+peer3+':'+defaultPortNo


data1 = {}
data1['prefix'] = 'TEST-SYNC3 '
data1['hash'] = ''
data1['numberOfBlocks'] = 0
data1['difficulty'] = 4
data1['reset'] = True

data2 = {}
data2['prefix'] = 'TEST-SYNC3 '
data2['hash'] = ''
data2['numberOfBlocks'] = 0
data2['difficulty'] = 4
data2['reset'] = True

data3 = {}
data3['prefix'] = 'TEST-SYNC3 '
data3['hash'] = ''
data3['numberOfBlocks'] = 0
data3['difficulty'] = 4
data3['reset'] = True

#generateBlocksResponse1 = test.generateBlocks(peer1, defaultPortNo, data1)
#generateBlocksResponse2 = test.generateBlocks(peer2, defaultPortNo, data2)

urls_data = [ ( url1+'/block/generateBlocks', data1 ),
              ( url2+'/block/generateBlocks', data2 ),
              ( url3+'/block/generateBlocks', data3 )
]
postUrls(urls_data)

topBlock1 = test.getTopBlock(peer1, defaultPortNo)
topBlock2 = test.getTopBlock(peer2, defaultPortNo)
topBlock3 = test.getTopBlock(peer3, defaultPortNo)
print('topBlock1:')
printBlock(topBlock1)
print('topBlock2:')
printBlock(topBlock2)
print('topBlock3:')
printBlock(topBlock3)

#---------------------------------------------------------------------------------------------

loop = asyncio.get_event_loop()
f1 = asyncio.ensure_future(runTest_gen(4))
f2 = asyncio.ensure_future(runTest_sync(4))
loop.run_until_complete(asyncio.gather(f1,f2))

topBlock1 = test.getTopBlock(peer1, defaultPortNo)
topBlock2 = test.getTopBlock(peer2, defaultPortNo)
topBlock3 = test.getTopBlock(peer3, defaultPortNo)
print('topBlock1:')
printBlock(topBlock1)
print('topBlock2:')
printBlock(topBlock2)
print('topBlock3:')
printBlock(topBlock3)

"""
for iter in range(3):
    print('############################################### Iteration:'+str(iter)+' ###############################################')
    data1_gen = {}
    data1_gen['prefix'] = 'TEST-SYNC3-WEB1 '
    data1_gen['hash'] = ''
    data1_gen['numberOfBlocks'] = random.randrange(5,30)
    data1_gen['difficulty'] = random.randrange(3,6)
    data1_gen['reset'] = False

    data2_gen = {}
    data2_gen['prefix'] = 'TEST-SYNC3-WEB2 '
    data2_gen['hash'] = ''
    data2_gen['numberOfBlocks'] = random.randrange(5,30)
    data2_gen['difficulty'] = random.randrange(3,6)
    data2_gen['reset'] = False

    data3_gen = {}
    data3_gen['prefix'] = 'TEST-SYNC3-WEB3 '
    data3_gen['hash'] = ''
    data3_gen['numberOfBlocks'] = random.randrange(5,30)
    data3_gen['difficulty'] = random.randrange(3,6)
    data3_gen['reset'] = False

    #---------------------------------------------------------------------------------------------

    data1_sync = {}
    data1_sync['peerIp'] = '172.32.0.'+random.choice( ['5','6'] )
    print(data1_sync)

    data2_sync = {}
    data2_sync['peerIp'] = '172.32.0.'+random.choice( ['4','6'] )
    print(data2_sync)

    data3_sync = {}
    data3_sync['peerIp'] = '172.32.0.'+random.choice( ['4','5'] )
    print(data3_sync)

    tasks = [
            asyncio.ensure_future( test.asyncPost( (url1+'/block/generateBlocks', data1_gen) ) ),
            asyncio.ensure_future( test.asyncPost( (url2+'/block/generateBlocks', data2_gen) ) ),
            asyncio.ensure_future( test.asyncPost( (url3+'/block/generateBlocks', data3_gen) ) ),
            asyncio.ensure_future( test.asyncWaitPost( (url1+'/block/sync/initiate', data1_sync), random.uniform(0,0.8) ) ),
            asyncio.ensure_future( test.asyncWaitPost( (url2+'/block/sync/initiate', data2_sync), random.uniform(0,0.8) ) ),
            asyncio.ensure_future( test.asyncWaitPost( (url3+'/block/sync/initiate', data3_sync), random.uniform(0,0.8) ) ),
    ]

    test.runTasks(tasks)

    print('*********** After run:'+str(iter)+' ***********')
    topBlock1 = test.getTopBlock(peer1, defaultPortNo)
    topBlock2 = test.getTopBlock(peer2, defaultPortNo)
    topBlock3 = test.getTopBlock(peer3, defaultPortNo)
    print('topBlock1:')
    printBlock(topBlock1)
    print('topBlock2:')
    printBlock(topBlock2)
    print('topBlock3:')
    printBlock(topBlock3)
"""
