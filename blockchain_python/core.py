import hashlib
import json
import pickle
import psycopg2
import requests
import netifaces

class Node:
    def __init__(self, DbName, app):
        self.peerList = []
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

    def peerConnect(self, peerIp):
        if(peerIp not in self.peerList):
            localIpList = self.getLocalIp()
            if(peerIp not in localIpList):
                self.peerList.append(peerIp)

    def queryPeerTopHash(self, peer):
        print("queryPeerTopHash")
        print('http://'+peer+':5000/topHash')
        print(requests.post('http://'+peer+':5000/topHash').json())
        return requests.post('http://'+peer+':5000/topHash').json()

    def getTopHash(self):
        return self.blockchain.topHash

    def scanTopHash(self):
        topHashList = {}
        for peer in self.peerList:
            topHashList[peer] = self.queryPeerTopHash(peer)
        return topHashList

class Blockchain:
    def __init__(self, DbName, app):
        connect_str = " dbname='myproject' user='myprojectuser' host='localhost' password='password' "
        self.connectionToDb = psycopg2.connect(connect_str)
        self.cursor = self.connectionToDb.cursor()
        self.cursor.execute("DROP TABLE IF EXISTS test;")
        self.cursor.execute("CREATE TABLE test(hash text, block bytea);")
        genesisBlock = Block.generateGenesisBlock()
        #print("PICKLE OF GEN BLK\n", type(pickle.dumps(genesisBlock)), pickle.dumps(genesisBlock))
        self.cursor.execute("INSERT INTO test VALUES (%s, %s);", (genesisBlock.hash, pickle.dumps(genesisBlock)) )
        self.topHash = genesisBlock.hash
        self.blockchainLength = 0
        self.sumOfDifficuties = 0

    def getStatus(self):
        return {"Current Blockchain Length": self.blockchainLength, "Sum Of Difficulties": self.sumOfDifficuties}

    def buildTestBlockchain(self, numberOfBlocks):
        #print("buildTestBlockchain()")
        top_block = self.getBlock(self.topHash)

        for iter in range(1,numberOfBlocks+1):
            next_block = Block({"Data": "Block number " + str(iter)}, top_block.hash)
            self.addBlock(next_block)
            top_block = next_block

    def getBlock(self, hash):
        self.cursor.execute( "SELECT * FROM test WHERE hash = %s;" , (hash, ) )
        res = self.cursor.fetchone()
        block = pickle.loads(res[1])
        #block.printBlock()
        return block

    def addBlock(self, block):
        #print("addBlock()")
        if(block.verify()):
            block.setHeight( (self.getPreviousBlock(block)).height + 1 )
            self.cursor.execute('INSERT INTO test VALUES (%s,%s);', (block.hash, pickle.dumps(block)))
            newHeight = self.findHeight(block.hash)
            if(newHeight > self.blockchainLength):
                self.topHash = block.hash
                self.blockchainLength = newHeight
            self.connectionToDb.commit()

    def findHeight(self, hash):
        #print("findHeight()")getBlock
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

    def jsonify(self):
        chain_to_send = []
        block = self.getBlock(self.topHash)
        chain_to_send.append(block.jsonify())
        genesisPreviousHash = '0'*64
        while(block.previousHash!=genesisPreviousHash):
            block = self.getBlock(block.previousHash)
            chain_to_send.append(block.jsonify())
        return chain_to_send

class Block:
    def __init__(self, data, previousHash, mine=True):
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
        sha.update((str(self.data) + str(self.previousHash) + str(self.nonce)).encode('utf-8'))
        return sha.hexdigest()

    def mineBlock(self):
        prefix = '0' * self.difficulty
        while(not( ( self.hash ).startswith(prefix) )):
            self.nonce += 1
            self.hash = self.hashBlock()
        return

    def jsonify(self):
        return self.__dict__

    def stringify(self):
        return json.dumps(self.jsonify())

    def verify(self):
        prefix = '0' * self.difficulty
        return( (self.hash).startswith(prefix) )

    def printBlock(self):
        print("Block:\n\tData:\t\t", self.data)
        print("\tPrevious Hash:\t", self.previousHash[:10])
        print("\tNonce:\t\t", self.nonce)
        print("\tDifficulty:\t", self.difficulty)
        print("\tHash:\t\t", self.hash[:10])
        return

    @staticmethod
    def generateGenesisBlock():
        block = Block({"Data": "Genesis Block"}, '0'*64, False)
        block.difficulty = 0
        block.setHeight(0)
        block.mineBlock()
        return block

    @staticmethod
    def buildFromJson(json_dict):
        block = Block(json_dict['data'], json_dict['previousHash'])
        block.difficulty = int(json_dict['difficulty'])
        block.nonce = int(json_dict['nonce'])
        return block
