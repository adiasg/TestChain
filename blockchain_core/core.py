from flask import jsonify, g
import hashlib
import json
import pickle
import psycopg2
#import netifaces
import requests
#from threading import Thread

def get_cursor():
    return g.connectionToDb.cursor()
    '''
    try:
        return g.connectionToDb.cursor()
    except RuntimeError:
        try:
            connect_str = " dbname='myproject' user='myprojectuser' password='password' host='postgres' port='5432' "
            connectionToDb = psycopg2.connect(connect_str)
        except psycopg2.OperationalError:
            connect_str = " dbname='myproject' user='myprojectuser' host='localhost' password='password' "
            connectionToDb = psycopg2.connect(connect_str)
        return connectionToDb.cursor()
    '''

class Node:
    def __init__(self):
        self.nodeDeclaration = {'isPeer': True}
        self.blockchain = Blockchain()
        self.peerList = ['172.19.0.2']

    def getNodeDeclaration(self):
        return self.nodeDeclaration

    def getStatus(self):
        return self.blockchain.getStatus()

    def getPeerList(self):
        return self.peerList

    def getTopHash(self):
        return self.blockchain.getTopHash()

    def buildTestNode(self, numberOfBlocks):
        self.blockchain.buildTestBlockchain(numberOfBlocks)

    def nodeGenerateBlocks(self, numberOfBlocks):
        self.blockchain.generateBlocks(numberOfBlocks)
        return {'status': 'generated '+str(numberOfBlocks)+' blocks'}

    def nodeGenerateBlocksWithPrefix(self, numberOfBlocks,prefix):
        self.blockchain.generateBlocksWithPrefix(numberOfBlocks,prefix)
        return {'status': 'generated '+str(numberOfBlocks)+' blocks with prefix : ' + prefix}

    def nodeInduceFork(self,number_of_blocks_to_generate,hash,prefix):
        self.blockchain.inducefork(number_of_blocks_to_generate,hash,prefix)
        return {'status': 'generated '+str(number_of_blocks_to_generate)+' blocks with prefix : ' + prefix +'   Starting from hash : '+ hash}

    def getTopChainNumber(self, number_of_hashes_to_send):
        return self.blockchain.getTopChainNumber(number_of_hashes_to_send)

    def getAllBlocks(self):
        return self.blockchain.jsonify()

    def getBlock(self, hash):
        block = self.blockchain.getBlock(hash)
        if block is not None:
            return block.jsonify()
        return None

    def addBlock(self, block_json):
        block = self.blockchain.makeBlock(block_json)
        self.blockchain.addBlock(block)
        return block.jsonify()
    '''
    def blockprop(self,block):
        for peerIp in self.peerList:
            url = 'http://'+ peerIp + ':5000'+'/block/incomingBlocks'
            requests.post(url,json=block,timeout=30).json()
    '''        


    def getHostIps(self):
        '''hostIpList = []
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            ifaddress = netifaces.ifaddresses(interface)
            if(netifaces.AF_INET in ifaddress):
                link = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]
                hostIpList.append(link['addr'])
            if(netifaces.AF_INET6 in ifaddress):
                link = netifaces.ifaddresses(interface)[netifaces.AF_INET6][0]
                hostIpList.append(link['addr'])
        return hostIpList'''
        return ['localhost', '127.0.0.1']

    def connectPeer(self, peerIp):
        if(peerIp not in self.peerList):
            hostIpList = self.getHostIps()
            if(peerIp not in hostIpList):
                url = 'http://'+peerIp+':5000/'
                peerDeclaration = requests.get(url,timeout=30).json()
                self.addPeer(peerIp, peerDeclaration['nodeDeclaration'])

    def addPeer(self, peerIp, peerDeclaration):
        if('isPeer' in peerDeclaration and peerDeclaration['isPeer'] is True):
            self.peerList.append(peerIp)

    def sendTopHashChain(self, peerIp, topHashChain):
        url = 'http://'+peerIp+':5000/block/sync'
        data = {'topHashChain': topHashChain}
        requests.post(url, json=data, timeout=30)

    def receiveSync(self, peerIp, peerTopHash):
        print('receiveSync()')
        print('\tpeerTopHash:', peerTopHash)
        if self.blockchain.getBlock(peerTopHash) is None:
            print('\treturning:', {'status': 'lagging', 'topHash': self.blockchain.getTopHash()})
            return {'status': 'lagging', 'topHash': self.blockchain.getTopHash()}
        else:
            print('\treturning:', {'status': 'leading', 'topHashChain': self.blockchain.getTopChainHash(peerTopHash)})
            return {'status': 'leading', 'topHashChain': self.blockchain.getTopChainHash(peerTopHash)}

    def initiateSync(self, peerIp):
        print('initiateSync()')
        if peerIp not in self.getHostIps():
            url = 'http://'+peerIp+':5000/block/sync'
            data = {'topHash': self.blockchain.getTopHash()}
            # TODO this throws exception on timeout
            status_response = requests.post(url, json=data, timeout=30).json()
            print('\tgot status_response:', status_response)
            if status_response is not None and 'status' in status_response:
                if status_response['status']=='lagging' and 'topHash' in status_response:
                    if self.blockchain.getBlock(status_response['topHash']) is None:
                        # TODO - verify forked?
                        print('\tForked')
                        self.sendTopHashChain(peerIp, self.blockchain.getTopChainNumber(10))
                        #sendTopChainNumberThread = Thread(target=self.sendTopHashChain, args=(peerIp, self.blockchain.getTopChainNumber(20)) )
                        #sendTopChainNumberThread.start()
                    else:
                        print('\tLagging')
                        self.sendTopHashChain(peerIp, self.blockchain.getTopChainHash(status_response['topHash']))
                        #sendTopHashChainThread = Thread(target=self.sendTopHashChain, args=(peerIp, self.blockchain.getTopChainHash(status_response['topHash'])) )
                        #sendTopHashChainThread.start()
                    return {'status': 'Sent topHashChain', 'peerStatus': status_response['status']}
                elif status_response['status']=='leading' and 'topHashChain' in status_response:
                    print('\tLeading')
                    self.queryBlocksFromPeer(peerIp, status_response['topHashChain'])
                    #queryBlocksFromPeerThread = Thread(target=self.queryBlocksFromPeer, args=(peerIp, status_response['topHashChain']) )
                    #queryBlocksFromPeerThread.start()
                    return {'status': 'received topHashChain', 'peerStatus': status_response['status']}
        return {'error': 'Node.initiateSync()'}

    def receiveTopHashChain(self, peerIp, topHashChain):
        print('receiveTopHashChain()')
        print('Chain:')
        print(topHashChain)
        self.queryBlocksFromPeer(peerIp, topHashChain)
        #queryBlocksFromPeerThread = Thread(target=self.queryBlocksFromPeer, args=(peerIp, topHashChain) )
        #queryBlocksFromPeerThread.start()
        return {'status': 'received topChainHash'}

    def queryBlocksFromPeer(self, peerIp, topHashChain):
        print('queryBlocksFromPeer()')
        key=max(topHashChain, key=int)
        key = int(key)
        while(key>=0):
            self.queryBlockFromPeer(peerIp, topHashChain[str(key)])
            key = key-1

    def queryBlockFromPeer(self, peerIp, hash):
        print('queryBlockFromPeer()')
        url = 'http://'+peerIp+':5000/block/request'
        data = {'hash': hash}
        print(data)
        block_json = requests.post(url, json=data, timeout=30).json()
        block = Block.buildFromJson(block_json)
        if block is not None:
            #block.printBlock()
            print('Trying add block')
            self.blockchain.addBlock(block)

class Blockchain:
    def __init__(self):
        cursor = get_cursor()
        cursor.execute("DROP TABLE IF EXISTS blocks;")
        cursor.execute("CREATE TABLE blocks(hash text, block bytea);")
        g.connectionToDb.commit()
        cursor.execute("DROP TABLE IF EXISTS status;")
        cursor.execute("CREATE TABLE status(key text, value text);")
        g.connectionToDb.commit()
        genesisBlock = Block.generateGenesisBlock()
        cursor.execute("INSERT INTO blocks VALUES (%s, %s);", (genesisBlock.hash, pickle.dumps(genesisBlock)) )
        g.connectionToDb.commit()
        cursor.close()
        self.storeTopHash(genesisBlock.hash)
        self.maxSumOfDifficulty = 0

    def storeTopHash(self, topHash):
        cursor = get_cursor()
        cursor.execute("SELECT value FROM status WHERE key = %s;", ("topHash", ))
        res = cursor.fetchone()
        if(res is None):
            cursor.execute("INSERT INTO status VALUES (%s, %s);", ("topHash", topHash) )
        else:
            cursor.execute("UPDATE status SET value = %s WHERE key = %s;", (topHash, "topHash",))
        g.connectionToDb.commit()
        cursor.close()

    def getTopHash(self):
        cursor = get_cursor()
        cursor.execute("SELECT value FROM status WHERE key = %s;", ("topHash", ))
        res = cursor.fetchone()
        topHash = None
        if(res is not None):
            topHash = res[0]
        cursor.close()
        return topHash

    def getStatus(self):
        return {"Current Blockchain Height": self.getTopHeight(), "Max Sum Of Difficulties": self.getMaxSumOfDifficulty(), "Tophash": self.getTopHash()}

    def getTopHeight(self):
        return self.getBlock(self.getTopHash()).height

    def makeBlock(self, block_json):
        return Block.buildFromJson(block_json)

    def getBlock(self, hash):
        cursor = get_cursor()
        cursor.execute( "SELECT block FROM blocks WHERE hash = %s;" , (hash, ) )
        res = cursor.fetchone()
        if(res is None):
            print('Blockchain.getBlock() is returning None for')
            print('hash:', hash)
            return None
        block = pickle.loads(res[0])
        cursor.close()
        return block

    def getPreviousBlock(self, block):
        #print('getPreviousBlock()')
        if(block.previousHash=='0'*64):
            # block is genesisBlock
            return None
        else:
            #self.getBlock(block.previousHash).printBlock()
            return self.getBlock(block.previousHash)

    def getPreviousHash(self, hash):
        if(hash=='0'*64):
            return None
        else:
            block = self.getBlock(hash)
            if block is None:
                return None
            return self.getBlock(hash).previousHash

    def findHeight(self, hash):
        block = self.getBlock(hash)
        height = 0
        genesisPreviousHash = '0'*64
        previousBlock = self.getPreviousBlock(block)
        if previousBlock is None:
            # block is genesisBlock
            return 0
        else:
            return previousBlock.height + 1

    def findSumOfDifficulty(self,hash):
        block = self.getBlock(hash)
        genesisPreviousHash = '0'*64
        if(block.previousHash == genesisPreviousHash):
            return 0
        else:
            return (self.getPreviousBlock(block)).sumOfDifficulty+len(block.hash)-len((block.hash).lstrip('0'))

    def getMaxSumOfDifficulty(self):
        topHash=self.getTopHash()
        return self.findSumOfDifficulty(topHash)

    def setMaxSumOfDifficulty(self,newMaxSumOfDiff):
        self.maxSumOfDifficulty=newMaxSumOfDiff

    def addBlock(self, block):
        if isinstance(block, Block):
            if block.verify():
                previousBlock = self.getPreviousBlock(block)
                if previousBlock is None:
                    print("\tBlockchain.addBlock():\n\tNo previous block for block with previousHash:", block.previousHash)
                    return
                else:
                    block.setHeight( previousBlock.height + 1 )
                    block.setSumOfDifficulty(previousBlock.sumOfDifficulty + len(block.hash)-len((block.hash).lstrip('0')))
                    cursor = get_cursor()
                    cursor.execute('INSERT INTO blocks VALUES (%s,%s);', (block.hash, pickle.dumps(block)))
                    newSumOfDifficulty=self.findSumOfDifficulty(block.hash)
                    newHeight = block.height
                    if(self.getMaxSumOfDifficulty() < newSumOfDifficulty):
                        self.storeTopHash(block.hash)
                        self.setMaxSumOfDifficulty(newSumOfDifficulty)
                    g.connectionToDb.commit()
                    print('Added block:')
                    block.printBlock()
            else:
                print('Block not verified')
                block.printBlock()

    def buildTestBlockchain(self, numberOfBlocks):
        topBlock = self.getBlock(self.getTopHash())
        for iter in range(1,numberOfBlocks+1):
            nextBlock = Block({"Data": "Block number " + str(iter)}, topBlock.hash, difficulty=2, mine=True)
            self.addBlock(nextBlock)
            topBlock = nextBlock

    def generateBlocks(self, numberOfBlocks):
        topBlock = self.getBlock(self.getTopHash())
        topBlocktemp = self.getBlock(self.getTopHash())
        for iter in range(1,numberOfBlocks+1):
            nextBlock = Block({"Data": "Block number " + str(iter+topBlock.height)}, topBlocktemp.hash, difficulty=2, mine=True)
            self.addBlock(nextBlock)
            topBlocktemp = nextBlock

    def generateBlocksWithPrefix(self, numberOfBlocks,prefix):
        topBlock = self.getBlock(self.getTopHash())
        topBlocktemp = self.getBlock(self.getTopHash())
        for iter in range(1,numberOfBlocks+1):
            nextBlock = Block({prefix +" : " + "Data": "Block number " + str(iter+topBlock.height)}, topBlocktemp.hash, difficulty=2, mine=True)
            self.addBlock(nextBlock)
            topBlocktemp = nextBlock

#def __init__(self, data, previousHash, difficulty=1, nonce=0, mine=False):
    def inducefork(self,numberOfBlocks,hash,prefix):
        block = self.getBlock(hash)
        if block is None:
            print ('hash not found in inducefork() method')
            return
        blocktemp = self.getBlock(hash)
        for iter in range(1,numberOfBlocks+1):
            nextBlock = Block({prefix + " : " + "Data": "Block number " + str(iter+block.height)}, blocktemp.hash, difficulty=2, mine=True)
            self.addBlock(nextBlock)
            blocktemp = nextBlock

    def getTopChainNumber(self, number_of_hashes_to_send):
        # TODO handle no such block in db
        topHash = self.getTopHash()
        block = self.getBlock(topHash)
        topHashChain = {0: topHash}
        for iter in range(1, number_of_hashes_to_send):
            if(block.previousHash=='0'*64):
                break
            block = self.getPreviousBlock(block)
            topHashChain[iter] = block.hash
        return topHashChain

    def getTopChainHash(self, last_hash_in_chain):
        # TODO handle no such block in db
        topHash = self.getTopHash()
        block = self.getBlock(topHash)
        topHashChain = {0: topHash}
        count = 0
        while(block.hash!=last_hash_in_chain):
            count += 1
            if block.previousHash=='0'*64:
                break
            block = self.getPreviousBlock(block)
            topHashChain[count] = block.hash
        return topHashChain

    def jsonify(self):
        chain_to_send = []
        block = self.getBlock(self.getTopHash())
        chain_to_send.append(block.jsonify())
        genesisPreviousHash = '0'*64
        while(block.previousHash!=genesisPreviousHash):
            block = self.getBlock(block.previousHash)
            chain_to_send.append(block.jsonify())
        return chain_to_send

class Block:
    def __init__(self, data, previousHash, difficulty=1, nonce=0, mine=False):
        self.data = data
        self.difficulty = difficulty
        self.nonce = nonce
        self.previousHash = previousHash
        self.height = -1
        self.sumOfDifficulty = 0
        self.hash = self.hashBlock()
        if(mine):
            self.mineBlock()

    def setHeight(self, height):
        self.height = height
        return

    def setDifficulty(self, difficulty):
        self.difficulty = difficulty
        return

    def setSumOfDifficulty(self, sumOfDifficulty):
        self.sumOfDifficulty = sumOfDifficulty
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
        self.hash = self.hashBlock()
        return( (self.hash).startswith(prefix) )

    def printBlock(self):
        print("Block:\n\tData:\t\t", self.data)
        print("\tPrevious Hash:\t", self.previousHash[:10])
        print("\tNonce:\t\t", self.nonce)
        print("\tDifficulty:\t", self.difficulty)
        print("\tHash:\t\t", self.hash[:10])
        print("\tHeight:\t\t", self.height)
        print("\tSumOfDifficulty:", self.sumOfDifficulty)


    @staticmethod
    def generateGenesisBlock():
        block = Block({"Data": "Genesis Block"}, '0'*64, mine=False)
        block.difficulty = 0
        block.setHeight(0)
        block.mineBlock()
        block.setSumOfDifficulty(0)
        return block

    @staticmethod
    def buildFromJson(block_json):
        if( 'data' in block_json and
            'previousHash' in block_json and
            len(block_json['previousHash'])==64 and
            'difficulty' in block_json and
            'nonce' in block_json):
            if( 'mine' in block_json and
                block_json['mine']=='on'):
                block = Block(block_json['data'], block_json['previousHash'], difficulty=int(block_json['difficulty']), mine=True)
            else:
                block = Block(block_json['data'], block_json['previousHash'], difficulty=int(block_json['difficulty']), nonce=int(block_json['nonce']))
            return block
