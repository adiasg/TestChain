import requests

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
