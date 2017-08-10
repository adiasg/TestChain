from flask import jsonify, g
import hashlib
import json
import pickle
import psycopg2
import netifaces
import requests

class UserDefinedError(Exception):
    def __init__(self, msg):
        self.msg = msg

def get_cursor():
    return g.connectionToDb.cursor()

class Node:
    def __init__(self):
        self.nodeDeclaration = {'isPeer': True}
        self.blockchain = Blockchain()
        self.peerList = []

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
        # TODO error handling, verify that block json is valid
        block = self.blockchain.makeBlock(block_json)
        if block is not None:
            self.blockchain.addBlock(block)

    def getHostIps(self):
        hostIpList = []
        interfaces = netifaces.interfaces()

        for interface in interfaces:
            ifaddress = netifaces.ifaddresses(interface)
            if(netifaces.AF_INET in ifaddress):
                link = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]
                hostIpList.append(link['addr'])
            if(netifaces.AF_INET6 in ifaddress):
                link = netifaces.ifaddresses(interface)[netifaces.AF_INET6][0]
                hostIpList.append(link['addr'])
        return hostIpList

    def connectPeer(self, peerIp, peerDeclaration):
        if(peerIp not in self.peerList):
            hostIpList = self.getHostIps()
            if(peerIp not in hostIpList):
                # TODO error handling
                if('isPeer' in peerDeclaration and peerDeclaration['isPeer'] is True):
                    self.peerList.append(peerIp)

    def recieveSync(self, peerIp, peerTopHash):
        if self.blockchain.getBlock(peerTopHash) is None:
            return {'status': 'lagging', 'topHash': self.blockchain.getTopHash()}
        else:
            return {'status': 'leading', 'topHashChain': self.blockchain.getTopChainHash(peerTopHash)}

    def initiateSync(self, peerIp):
        if peerIp not in self.getHostIps():
            url = 'http://'+peerIp+':5000/block/sync'
            data = {'topHash': self.blockchain.getTopHash()}
            # TODO this throws exception on timeout
            status_response = requests.get(url, json=data, timeout=5).json()
            if status_response is not None and 'status' in status_response:
                if status_response['status'] is 'lagging':
                    # TODO async post getTopChainHash(status_response['topHash']) to some endpoint
                    return {'status': 'Sync initiated'}
        return {'error': 'Node.initiateSync()'}

class Blockchain:
    def __init__(self):
        #print('Blockchain.__init__')
        cursor = get_cursor()
        cursor.execute("DROP TABLE IF EXISTS blocks;")
        cursor.execute("CREATE TABLE blocks(hash text, block bytea);")
        g.connectionToDb.commit()
        cursor.execute("DROP TABLE IF EXISTS tophash_store;")
        cursor.execute("CREATE TABLE tophash_store(tophash text, hash text);")
        g.connectionToDb.commit()
        genesisBlock = Block.generateGenesisBlock()
        #print('Generated genesis block')
        #genesisBlock.printBlock()
        cursor.execute("INSERT INTO blocks VALUES (%s, %s);", (genesisBlock.hash, pickle.dumps(genesisBlock)) )
        g.connectionToDb.commit()
        cursor.close()
        self.topHash = genesisBlock.hash
        self.storeTopHash(genesisBlock.hash)
        print('Comparing self.topHash and self.getTopHash()')
        print(self.topHash == self.getTopHash())
        print('self.topHash:', self.topHash)
        print('self.getTopHash():', self.getTopHash())
        self.sumOfDifficuties = 0

    def storeTopHash(self, topHash):
        cursor = get_cursor()
        cursor.execute("SELECT hash FROM tophash_store WHERE tophash = %s;", ("topHash", ))
        res = cursor.fetchone()
        if(res is None):
            cursor.execute("INSERT INTO tophash_store VALUES (%s, %s);", ("topHash", topHash) )
        else:
            cursor.execute("UPDATE tophash_store SET hash = %s WHERE tophash = %s;", (topHash, "topHash",))
        g.connectionToDb.commit()
        cursor.close()

    def getTopHash(self):
        cursor = get_cursor()
        cursor.execute("SELECT hash FROM tophash_store WHERE tophash = %s;", ("topHash", ))
        res = cursor.fetchone()
        topHash = None
        if(res is not None):
            topHash = res[0]
        cursor.close()
        return topHash

    def getStatus(self):
        return {"Current Blockchain Height": self.getTopHeight(), "Sum Of Difficulties": self.sumOfDifficuties, "Tophash": self.getTopHash()}

    def getTopHeight(self):
        return self.getBlock(self.getTopHash()).height

    def makeBlock(self, block_json):
        return Block.buildFromJson(block_json)

    def getBlock(self, hash):
        #print('Blockchain.getBlock()')
        #print('hash:', hash)
        try:
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
        except:
            raise UserDefinedError('error in Blockchain.getBlock()' + hash)

    def getPreviousBlock(self, block):
        if(block.previousHash!='0'*64):
            # TODO error handling
            return self.getBlock(block.previousHash)

    def getPreviousHash(self, hash):
        if(hash=='0'*64):
            # TODO not to send '0'*64, stop at genesisHash
            return None
        else:
            block = self.getBlock(hash)
            if(block==None):
                return None
            return self.getBlock(hash).previousHash

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

    def addBlock(self, block):
        print("addBlock()")
        #block.printBlock()
        try:
            if(block.verify()):
                previousBlock = self.getPreviousBlock(block)
                if(previousBlock is None):
                    print("No previous block for block with previousHash:", block.previousHash)
                else:
                    #print('Got previous height:', (self.getPreviousBlock(block)).height)
                    block.setHeight( previousBlock.height + 1 )
                    #print('The height is set as', block.height)
                    cursor = get_cursor()
                    cursor.execute('INSERT INTO blocks VALUES (%s,%s);', (block.hash, pickle.dumps(block)))
                    # TODO longest chain based on sumOfDifficuties
                    newHeight = self.findHeight(block.hash)
                    if(newHeight > self.getTopHeight()):
                        self.topHash = block.hash
                        self.storeTopHash(block.hash)
                        print('Comparing self.topHash and self.getTopHash()')
                        print(self.topHash == self.getTopHash())
                        print('self.topHash:', self.topHash)
                        print('self.getTopHash():', self.getTopHash())
                    g.connectionToDb.commit()
                    print('Added block with hash:', block.hash)
                    print('Block height:', block.height)
                    self.getBlock(block.hash).printBlock()
                    #block.printBlock()
            else:
                print('Block not verified')
                block.printBlock()
        except:
            raise UserDefinedError('error in Blockchain.addBlock()' + block.stringify())

    def buildTestBlockchain(self, numberOfBlocks):
        print("buildTestBlockchain()")
        topBlock = self.getBlock(self.getTopHash())

        for iter in range(1,numberOfBlocks+1):
            #print('iter:', iter, 'topHash:', self.topHash)
            nextBlock = Block({"Data": "Block number " + str(iter)}, topBlock.hash, mine=True)
            self.addBlock(nextBlock)
            topBlock = nextBlock

    def getTopChainNumber(self, number_of_hashes_to_send):
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
        topHash = self.getTopHash()
        block = self.getBlock(topHash)
        topHashChain = {0: topHash}
        count = 0
        while(block.hash!=last_hash_in_chain):
            print('from getthc')
            count += 1
            block.printBlock()
            if block.previousHash=='0'*64:
                break
            block = self.getPreviousBlock(block)
            topHashChain[count] = block.hash
        return topHashChain

    def jsonify(self):
        #print('Blockchain.jsonify()')
        chain_to_send = []
        block = self.getBlock(self.getTopHash())
        #print('block:')
        #block.printBlock()
        chain_to_send.append(block.jsonify())
        genesisPreviousHash = '0'*64
        while(block.previousHash!=genesisPreviousHash):
            # TODO error handling
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

    def setDifficulty(self, difficulty):
        self.difficulty = difficulty
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
            print('Block.buildFromJson() returning None for:', json_dict)
            return None
