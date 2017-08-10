import hashlib
import json
import pickle
import psycopg2
import requests
import netifaces
import os
from flask import g

# TODO error handle for all db gets

class UserDefinedError(Exception):
    def __init__(self, msg):
        self.msg = msg

def get_cursor():
    return g.connectionToDb.cursor()

class Node:
    def __init__(self, DbName, app):
        self.peerList = []
        self.peerState = {}
        self.blockchain = Blockchain(DbName, app)
        self.nodeDeclaration = {"isPeer": "yes"}

    def getStatus(self):
        return self.blockchain.getStatus()

    def getNodeDeclaration(self):
        return json.dumps(self.nodeDeclaration)

    def buildTestNode(self, numberOfBlocks):
        self.blockchain.buildTestBlockchain(numberOfBlocks)

    def getLocalIp(self):
        localIpList = []
        interfaces = netifaces.interfaces()

        for interface in interfaces:
            ifaddress = netifaces.ifaddresses(interface)
            if(netifaces.AF_INET in ifaddress):
                link = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]
                localIpList.append(link['addr'])
            if(netifaces.AF_INET6 in ifaddress):
                link = netifaces.ifaddresses(interface)[netifaces.AF_INET6][0]
                localIpList.append(link['addr'])
        return localIpList

    def peerConnect(self, peerIp, peerDeclaration=None):
        print('peerConnect()')
        if(peerIp not in self.peerList):
            localIpList = self.getLocalIp()
            if(peerIp not in localIpList):
                # TODO error handling
                try:
                    if(peerDeclaration is None):
                        peerDeclaration = self.queryNodeDeclaration(peerIp)
                    if("isPeer" in peerDeclaration and peerDeclaration['isPeer']=='yes'):
                        self.peerList.append(peerIp)
                except:
                    print("Failed to add", peerIp, "\nCheck Node.peerConnect()")

    def connectToPeer(self, peerIp):
        print('connectToPeer()')
        try:
            if(peerIp not in self.peerList):
                localIpList = self.getLocalIp()
                if(peerIp not in localIpList):
                    requests.post('http://'+request.form['peerIp']+':5000/connect', timeout=5, data=node.getNodeDeclaration())
        except:
            print('Error in Blockchain.connectToPeer(), peerIp=', peerIp)

    def queryNodeDeclaration(self, peerIp):
        return requests.post('http://'+peerIp+':5000/', timeout=5).json()

    def queryPeerState(self, peerIp):
        state = self.queryPeerTopHash(peerIp)
        state['nodeDeclaration'] = self.queryNodeDeclaration(peerIp)
        return state

    def scanPeerState(self):
        self.peerState = {}
        for peerIp in self.peerList:
            self.peerState[peerIp] = self.queryPeerState(peerIp)
        return self.peerState

    def queryPeerTopHash(self, peer):
        return requests.post('http://'+peer+':5000/topHash', timeout=5).json()

    def getTopHash(self):
        return self.blockchain.topHash

    def scanTopHash(self):
        topHashList = {}
        for peer in self.peerList:
            topHashList[peer] = self.queryPeerTopHash(peer)
        return topHashList

    def getBlock(self, hash):
        block = self.blockchain.getBlock(hash)
        if(block is None):
            # TODO error handling
            return(None)
        return block.stringify()

    def getTopHashChain(self):
        number_of_hashes_to_send = 10
        return self.blockchain.getTopHashChain(number_of_hashes_to_send)

    def initiateSyncPeer(self, peerIp, syncMsg):
        print("initiateSyncPeer")
        print("syncMsg", syncMsg)
        print("peerIp", peerIp)
        return requests.post('http://'+peerIp+':5000/blocks/sync', json=self.getTopHashChain(), timeout=5).text

    def receiveSyncPeer(self, peerIp, peerTopHashChain):
        print("receiveSyncPeer")
        print(peerTopHashChain)
        print([row for row in peerTopHashChain.values()])
        if(self.getTopHash() in peerTopHashChain.values()):
            # node is behind of peer by relativeTopHashIndex blocks
            relativeTopHashIndex = 0
            for index in peerTopHashChain:
                if(peerTopHashChain[index]==self.getTopHash()):
                    relativeTopHashIndex = index
                    break

            for iter in range(int(relativeTopHashIndex)-1,-1,-1):
                #print("Requesting:", iter)
                block = queryPeerBlock(peerIp, peerTopHashChain[str(iter)])
                block.printBlock()
                self.blockchain.addBlock(block)

            return json.dumps({'state': '-'+relativeTopHashIndex})
        else:
            # node is ahead of peer or chain is forked
            return json.dumps(self.getTopHashChain())

    def queryPeerBlock(self, peerIp, hash):
        return Block.buildFromJson(requests.post('http://'+peerIp+':5000/blocks/request', data={'hash': hash}.json(), timeout=5))

class Blockchain:
    def __init__(self, DbName, app):
        #print('Blockchain.__init__')
        cursor = get_cursor()
        cursor.execute("DROP TABLE IF EXISTS test;")
        cursor.execute("CREATE TABLE test(hash text, block bytea);")
        g.connectionToDb.commit()
        genesisBlock = Block.generateGenesisBlock()
        #print('Generated genesis block')
        #genesisBlock.printBlock()
        cursor.execute("INSERT INTO test VALUES (%s, %s);", (genesisBlock.hash, pickle.dumps(genesisBlock)) )
        cursor.close()
        self.topHash = genesisBlock.hash
        #print('topHash:', self.topHash)
        self.blockchainLength = 0
        self.sumOfDifficuties = 0

    def getStatus(self):
        return {"Current Blockchain Length": self.blockchainLength, "Sum Of Difficulties": self.sumOfDifficuties}

    def buildTestBlockchain(self, numberOfBlocks):
        print("buildTestBlockchain()")
        topBlock = self.getBlock(self.topHash)

        for iter in range(1,numberOfBlocks+1):
            #print('iter:', iter, 'topHash:', self.topHash)
            nextBlock = Block({"Data": "Block number " + str(iter)}, topBlock.hash, mine=True)
            self.addBlock(nextBlock)
            topBlock = nextBlock

    def getBlock(self, hash):
        #print('Blockchain.getBlock()')
        #print('hash:', hash)
        try:
            cursor = get_cursor()
            cursor.execute( "SELECT * FROM test WHERE hash = %s;" , (hash, ) )
            res = cursor.fetchone()
            if(res is None):
                print('Returning None')
                print('hash:', hash)
                return None
            block = pickle.loads(res[1])
            cursor.close()
            return block
        except:
            raise UserDefinedError('error in Blockchain.getBlock()' + hash)

    def getTopHashChain(self, number_of_hashes_to_send):
        topHashChain = { 0: self.topHash}
        for iter in range(1, number_of_hashes_to_send):
            topHashChain[iter] = self.getPreviousHash(topHashChain[iter-1])
        return topHashChain

    def addBlock(self, block):
        #print("addBlock()")
        #block.printBlock()
        try:
            if(self.getBlock(block.hash) is None):
                print('Block already added')
            elif(block.verify()):
                #print('Got previous height:', (self.getPreviousBlock(block)).height)
                block.setHeight( (self.getPreviousBlock(block)).height + 1 )
                #print('The height is set as', block.height)
                cursor = get_cursor()
                cursor.execute('INSERT INTO test VALUES (%s,%s);', (block.hash, pickle.dumps(block)))
                # TODO longest chain based on sumOfDifficuties
                newHeight = self.findHeight(block.hash)
                if(newHeight > self.blockchainLength):
                    self.topHash = block.hash
                    self.blockchainLength = newHeight
                g.connectionToDb.commit()
                print('Added block with hash:', block.hash)
                print('Block height:', block.height)
                #self.getBlock(block.hash).printBlock()
                #block.printBlock()
            else:
                print('Block not verified')
                block.printBlock()
        except:
            raise UserDefinedError('error in Blockchain.addBlock()' + block.stringify())

    def findHeight(self, hash):
        print("findHeight()")
        block = self.getBlock(hash)
        height = 0
        genesisPreviousHash = '0'*64
        while(block.previousHash!=genesisPreviousHash):
            block = self.getPreviousBlock(block)
            height += 1
        #print("Height:", height)
        return height

    def getPreviousBlock(self, block):
        if(block.previousHash!='0'*64):
            return self.getBlock(block.previousHash)
        else:
            return "Block not found"

    def getPreviousHash(self, hash):
        if(hash=='0'*64):
            return None
        else:
            # TODO error handling
            return self.getBlock(hash).previousHash

    def jsonify(self):
        #print('Blockchain.jsonify()')
        chain_to_send = []
        block = self.getBlock(self.topHash)
        #print('block:')
        #block.printBlock()
        chain_to_send.append(block.jsonify())
        genesisPreviousHash = '0'*64
        while(block.previousHash!=genesisPreviousHash):
            block = self.getBlock(block.previousHash)
            chain_to_send.append(block.jsonify())
        return chain_to_send

class Block:
    def __init__(self, data, previousHash, mine=False):
        self.data = data
        self.difficulty = 1
        self.nonce = 0
        self.previousHash = previousHash
        self.hash = self.hashBlock()
        self.height = -1
        if(mine):
            self.mineBlock()

    def setHeight(self, height):
        self.height = height
        return

    def hashBlock(self):
        sha = hashlib.sha256()
        try:
            sha.update((str(self.data) + str(self.previousHash) + str(self.nonce)).encode('utf-8'))
            return sha.hexdigest()
        except:
            raise UserDefinedError('error in Block.hashBlock()' + self.stringify())

    def mineBlock(self):
        prefix = '0' * self.difficulty
        try:
            while(not( ( self.hash ).startswith(prefix) )):
                self.nonce += 1
                self.hash = self.hashBlock()
            return
        except:
            raise UserDefinedError('error in Block.mineBlock()' + self.stringify())

    def jsonify(self):
        try:
            return self.__dict__
        except:
            raise UserDefinedError('error in Block.jsonify()')

    def stringify(self):
        return json.dumps(self.jsonify())

    def verify(self):
        prefix = '0' * self.difficulty
        try:
            return( (self.hash).startswith(prefix) )
        except:
            raise UserDefinedError('error in Block.verify()' + self.stringify())

    def printBlock(self):
        try:
            print("Block:\n\tData:\t\t", self.data)
            print("\tPrevious Hash:\t", self.previousHash[:10])
            print("\tNonce:\t\t", self.nonce)
            print("\tDifficulty:\t", self.difficulty)
            print("\tHash:\t\t", self.hash[:10])
            try:
                print("\tHeight:\t\t", self.height)
            except:
                pass
            return
        except:
            raise UserDefinedError('error in Block.printBlock()' + self.stringify())

    @staticmethod
    def generateGenesisBlock():
        block = Block({"Data": "Genesis Block"}, '0'*64, False)
        block.difficulty = 0
        block.setHeight(0)
        block.mineBlock()
        return block

    @staticmethod
    def buildFromJson(json_dict):
        try:
            block = Block(json_dict['data'], json_dict['previousHash'])
            block.difficulty = int(json_dict['difficulty'])
            block.nonce = int(json_dict['nonce'])
            return block
        except:
            raise UserDefinedError('error in Block.buildFromJson()' + json.dumps(json_dict))
