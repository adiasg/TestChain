from flask import jsonify, g
import hashlib
import json
import pickle
import psycopg2
import requests
import os

def get_cursor():
    return g.connectionToDb.cursor()

db_suffix = ""
if "db_suffix" in os.environ:
    db_suffix = os.environ.get('db_suffix')

class Node:
    def __init__(self):
        self.nodeDeclaration = {'isPeer': True}
        self.blockchain = Blockchain()
        peerList = [('172.24.0.2', '5000'), ('172.24.0.5', '5000'), ('172.32.0.2', '5000'), ('172.32.0.5', '5000'), ('10.4.7.216', '5000')]
        cursor = get_cursor()
        cursor.execute("DROP TABLE IF EXISTS peerList;")
        cursor.execute("CREATE TABLE peerList(peerIp cidr, portNo smallint);")
        for peerIp, portNo in peerList:
            print("peerIp, portNo", peerIp, portNo)
            cursor.execute("INSERT INTO peerList VALUES (%s, %s);", (peerIp, portNo))
        g.connectionToDb.commit()
        cursor.close()

    def getNodeDeclaration(self):
        return self.nodeDeclaration

    def getStatus(self):
        return self.blockchain.getStatus()

    def getPeerList(self):
        peerList = []
        cursor = get_cursor()
        cursor.execute("SELECT host(peerIp) FROM peerList;")
        peerListRows = cursor.fetchall()
        for peerIp in peerListRows:
            peerList.append(peerIp[0])
        print("peerList:", peerList)
        cursor.close()
        return peerList

    def getPeerPortNo(self, peerIp):
        return '5000'
        #cursor = get_cursor()
        #cursor.execute("SELECT portNo FROM peerList WHERE peerIp = %s;", (peerIp,))
        #portNo = cursor.fetchone()
        #cursor.close()
        #return portNo[0]

    def getTopHash(self):
        return self.blockchain.getTopHash()

    def buildTestNode(self, numberOfBlocks):
        self.blockchain.buildTestBlockchain(numberOfBlocks)

    def generateBlocks(self, numberOfBlocks, prefix, hash, reset=False):
        success_status = self.blockchain.generateBlocks(numberOfBlocks, prefix, hash, reset)
        topHash = self.getTopHash()
        if hash == "":
            return {'success': success_status, 'topHash': topHash, 'status': 'generated '+str(numberOfBlocks)+' blocks with prefix: '+prefix}
        else:
            return {'success': success_status, 'topHash': topHash, 'status': 'generated '+str(numberOfBlocks)+' blocks with prefix : '+prefix + ' starting from hash : '+hash}

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
        if(peerIp not in self.getPeerList()):
            hostIpList = self.getHostIps()
            if(peerIp not in hostIpList):
                url = 'http://'+peerIp+':'+str(self.getPeerPortNo(peerIp))+'/'
                peerDeclaration = requests.get(url,timeout=30).json()
                self.addPeer(peerIp, peerDeclaration['nodeDeclaration'])

    def addPeer(self, peerIp, peerDeclaration):
        if('isPeer' in peerDeclaration and peerDeclaration['isPeer'] is True):
            cursor = get_cursor()
            cursor.execute("INSERT INTO peerList(peerIp, portNo) VALUES (%s, %s);", (peerIp, 5432))
            g.connectionToDb.commit()
            cursor.close()

    def sendTopHashChain(self, peerIp, topHashChain):
        url = 'http://'+peerIp+':'+str(self.getPeerPortNo(peerIp))+'/block/sync'
        data = {'topHashChain': topHashChain}
        requests.post(url, json=data, timeout=30)

    def propogateBlock(self,block):
        for peerIp in self.getPeerList():
            url = 'http://'+peerIp+':'+str(self.getPeerPortNo(peerIp))+'/block/submit'
            data={'block':block}
            status = requests.post(url,json=data,timeout=30)
            print(status)

    def receiveSync(self, peerIp, peerTopHash):
        print('receiveSync()')
        print('\tpeerTopHash:', peerTopHash)
        if self.blockchain.getBlock(peerTopHash) is not None:
            print('\tblock in db')
            if self.blockchain.getTopHash()==peerTopHash:
                reply = {'status': 'synced'}
                return reply
            if self.blockchain.inLongestChain(peerTopHash):
                print('\tblock in longest chain')
                reply = {'status': 'leading'}
                reply['topHashChain'] = self.blockchain.getTopChainHash(peerTopHash)
                return reply
            else:
                print('\tblock in fork')
                reply = {'status': 'leading but forked'}
                intersectionHash = self.blockchain.findIntersection( self.blockchain.getTopHash(), peerTopHash )
                print('intersectionHash:', intersectionHash)
                reply['topHashChain'] = self.blockchain.getTopChainHash( intersectionHash )
                return reply
        else:
            print('\tblock not in db')
            reply = {'status': 'forked'}
            reply['topHash'] = self.blockchain.getTopHash()
            reply['topHashChain'] = self.blockchain.getTopChainNumber(40)
            return reply

    def initiateSync(self, peerIp):
        print('initiateSync()')
        if peerIp not in self.getHostIps():
            url = 'http://'+peerIp+':'+str(self.getPeerPortNo(peerIp))+'/block/sync'
            data = {'topHash': self.blockchain.getTopHash()}
            print("url:", url)
            status_response = requests.post(url, json=data, timeout=30).json()
            print('\tgot status_response:', status_response)
            if status_response is not None and 'status' in status_response:
                status = status_response['status']
                if(status=='synced'):
                    pass
                elif(status=='leading' and 'topHashChain' in status_response):
                    self.queryBlocksFromPeer(peerIp, status_response['topHashChain'])
                elif(status=='leading but forked' and 'topHashChain' in status_response):
                    self.queryBlocksFromPeer(peerIp, status_response['topHashChain'])
                elif(status=='forked' and 'topHash' in status_response and'topHashChain' in status_response):
                    if( self.blockchain.getBlock(status_response['topHash']) is None ):
                        self.queryBlocksFromPeer(peerIp, status_response['topHashChain'])
                        chainToSend = self.blockchain.getTopChainNumber(40)
                        self.sendTopHashChain(peerIp, chainToSend)
                    else:
                        intersectionHash = self.blockchain.findIntersection( self.blockchain.getTopHash(), status_response['topHash'] )
                        print('intersectionHash:', intersectionHash)
                        chainToSend = self.blockchain.getTopChainHash( intersectionHash )
                        self.sendTopHashChain(peerIp, chainToSend)
        return {'status': 'sync complete'}

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
        if(topHashChain=={}):
            return
        key=max(topHashChain, key=int)
        key = int(key)
        while(key>=0 and self.blockchain.getBlock(topHashChain[str(key)]) is not None):
            key = key-1
        while(key>=0):
            if( self.queryBlockFromPeer(peerIp, topHashChain[str(key)])==False ):
                break
            key = key-1

    def queryBlockFromPeer(self, peerIp, hash):
        print('queryBlockFromPeer()')
        url = 'http://'+peerIp+':'+str(self.getPeerPortNo(peerIp))+'/block/request'
        data = {'hash': hash}
        print(data)
        block_json = requests.post(url, json=data, timeout=30).json()
        block = Block.buildFromJson(block_json)
        if block is not None and self.blockchain.getBlock(block.hash) is None:
            #block.printBlock()
            print('Trying add block')
            self.blockchain.addBlock(block)
            return True
        else:
            return False

class Blockchain:
    def __init__(self):
        cursor = get_cursor()
        cursor.execute("DROP TABLE IF EXISTS blocks_"+db_suffix+";")
        cursor.execute("CREATE TABLE blocks_"+db_suffix+"(hash CHAR(64) PRIMARY KEY, block jsonb, time_of_insertion timestamp);")
        g.connectionToDb.commit()
        cursor.execute("DROP TABLE IF EXISTS status_"+db_suffix+";")
        cursor.execute("CREATE TABLE status_"+db_suffix+"(key text, value text);")
        g.connectionToDb.commit()
        genesisBlock = Block.generateGenesisBlock()
        cursor.execute("INSERT INTO blocks_"+db_suffix+"(hash, block, time_of_insertion) VALUES (%s, %s, now());", (genesisBlock.hash, genesisBlock.stringify()) )
        g.connectionToDb.commit()
        cursor.close()
        self.storeTopHash(genesisBlock.hash)

    def storeTopHash(self, topHash):
        cursor = get_cursor()
        cursor.execute("SELECT value FROM status_"+db_suffix+" WHERE key = %s;", ("topHash", ))
        res = cursor.fetchone()
        if(res is None):
            cursor.execute("INSERT INTO status_"+db_suffix+" VALUES (%s, %s);", ("topHash", topHash) )
        else:
            cursor.execute("UPDATE status_"+db_suffix+" SET value = %s WHERE key = %s;", (topHash, "topHash",))
        g.connectionToDb.commit()
        cursor.close()

    def getTopHash(self):
        cursor = get_cursor()
        cursor.execute("SELECT value FROM status_"+db_suffix+" WHERE key = %s;", ("topHash", ))
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
        cursor.execute( "SELECT block FROM blocks_"+db_suffix+" WHERE hash = %s;" , (hash, ) )
        res = cursor.fetchone()
        if(res is None):
            print('Blockchain.getBlock() is returning None for')
            print('hash:', hash)
            return None
        #print('Got res[0]:', res[0])
        block = Block.buildFromJson(res[0])
        block.setSumOfDifficulty(res[0]['sumOfDifficulty'])
        block.setHeight(res[0]['height'])
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

    def addBlock(self, block):
        if block.verify():
            #print("---------------------------------------------------------------")
            previousBlock = self.getPreviousBlock(block)
            if previousBlock is None:
                print("\tBlockchain.addBlock():\n\tNo previous block for block with previousHash:", block.previousHash)
                #print("---------------------------------------------------------------")
                return
            else:
                #print("Got previous block:")
                #previousBlock.printBlock()
                #print("Setting height:", previousBlock.height + 1)
                block.setHeight( previousBlock.height + 1 )
                block.setSumOfDifficulty(previousBlock.sumOfDifficulty + len(block.hash)-len((block.hash).lstrip('0')))
                cursor = get_cursor()
                #print('Adding block:')
                #print(block.stringify())
                cursor.execute("INSERT INTO blocks_"+db_suffix+"(hash, block, time_of_insertion) VALUES (%s,%s, now());", (block.hash, block.stringify()))
                newSumOfDifficulty = self.findSumOfDifficulty(block.hash)
                #print("Found newSumOfDifficulty:", newSumOfDifficulty)
                newHeight = block.height
                if(self.getMaxSumOfDifficulty() < newSumOfDifficulty):
                    #print('Storing topHash:', block.hash)
                    self.storeTopHash(block.hash)
                g.connectionToDb.commit()
                print('Added block:')
                block.printBlock()
                #print('Checking added block')
                #self.getBlock(block.hash).printBlock()
        else:
            print('Block not verified')
            block.printBlock()
        #print("---------------------------------------------------------------")

    def buildTestBlockchain(self, numberOfBlocks):
        topBlock = self.getBlock(self.getTopHash())
        for iter in range(1,numberOfBlocks+1):
            nextBlock = Block({"Data": "Block number " + str(iter)}, topBlock.hash, difficulty=2, mine=True)
            self.addBlock(nextBlock)
            topBlock = nextBlock

    def generateBlocks(self, numberOfBlocks, prefix, hash, reset=False):
        if(reset):
            cursor = get_cursor()
            cursor.execute("DROP TABLE IF EXISTS blocks_"+db_suffix+";")
            #cursor.execute("CREATE TABLE blocks_"+db_suffix+"(hash text, block jsonb);")
            cursor.execute("CREATE TABLE blocks_"+db_suffix+"(hash CHAR(64) PRIMARY KEY, block jsonb, time_of_insertion timestamp);")
            g.connectionToDb.commit()
            cursor.execute("DROP TABLE IF EXISTS status_"+db_suffix+";")
            cursor.execute("CREATE TABLE status_"+db_suffix+"(key text, value text);")
            g.connectionToDb.commit()
            genesisBlock = Block.generateGenesisBlock()
            cursor.execute("INSERT INTO blocks_"+db_suffix+"(hash, block, time_of_insertion) VALUES (%s, %s, now());", (genesisBlock.hash, genesisBlock.stringify()) )
            g.connectionToDb.commit()
            cursor.close()
            self.storeTopHash(genesisBlock.hash)
        if hash == "":
            topBlock = self.getBlock(self.getTopHash())
            #topBlocktemp = self.getBlock(self.getTopHash())
        else:
            topBlock = self.getBlock(hash)
            #topBlocktemp = self.getBlock(hash)
        if topBlock is None:
            return False
        for iter in range(numberOfBlocks):
            topBlock = Block({"Data": prefix + "Block number " + str(1+topBlock.height)}, topBlock.hash, difficulty=2, mine=True)
            self.addBlock(topBlock)
        return True

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

    def getTopChainHash(self, lastPreviousHash):
        # TODO handle no such block in db
        print('getTopChainHash()')
        print('lastPreviousHash:', lastPreviousHash)
        topHash = self.getTopHash()
        block = self.getBlock(topHash)
        topHashChain = {}
        count = 0
        while(block.hash!=lastPreviousHash and block.previousHash!='0'*64):
            print("block.hash", block.hash)
            topHashChain[count] = block.hash
            block = self.getPreviousBlock(block)
            count += 1
        return topHashChain

    def inLongestChain(self, hash):
        if(hash=='0'*64):
            return False
        currentHash = self.getTopHash()
        while(currentHash is not None):
            if(currentHash==hash):
                return True
            currentHash = self.getPreviousHash(currentHash)
        return False

    def findIntersection(self, hash1, hash2):
        block1 = self.getBlock(hash1)
        block2 = self.getBlock(hash2)
        if(block1 is None or block2 is None):
            return None
        if(block1.height>=block2.height):
            return self.findIntersectionUtil(block1, block2)
        else:
            return self.findIntersectionUtil(block2, block1)

    def findIntersectionUtil(self, block1, block2):
        # Assuming that block1.height >= block2.height
        while(block1.height!=block2.height):
            block1 = self.getPreviousBlock(block1)
        while(block1.hash!=block2.hash):
            block1 = self.getPreviousBlock(block1)
            block2 = self.getPreviousBlock(block2)
        return block1.hash

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
        self.difficulty = int(difficulty)
        self.nonce = int(nonce)
        self.previousHash = previousHash
        self.height = -1
        self.sumOfDifficulty = 0
        self.hash = self.hashBlock()
        if(mine):
            self.mineBlock()

    def setHeight(self, height):
        self.height = int(height)
        return

    def setDifficulty(self, difficulty):
        self.difficulty = int(difficulty)
        return

    def setSumOfDifficulty(self, sumOfDifficulty):
        self.sumOfDifficulty = int(sumOfDifficulty)
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
        block_json = {}
        block_json['data'] = self.data
        block_json['difficulty'] = self.difficulty
        block_json['nonce'] = self.nonce
        block_json['previousHash'] = self.previousHash
        block_json['height'] = self.height
        block_json['sumOfDifficulty'] = self.sumOfDifficulty
        return block_json

    def stringify(self):
        return json.dumps(self.jsonify())

    def verify(self):
        prefix = '0' * self.difficulty
        self.hash = self.hashBlock()
        return( (self.hash).startswith(prefix) )

    def printBlock(self):
        print("Block:")
        print("\tData:\t\t", self.data)
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
        #print('Got block_json:', block_json)
        if( 'data' in block_json and \
            'previousHash' in block_json and \
            len(block_json['previousHash'])==64 and \
            'difficulty' in block_json and \
            'nonce' in block_json):
            if( 'mine' in block_json and \
                block_json['mine']=='on'):
                #print('Mining block')
                block = Block(block_json['data'], block_json['previousHash'], difficulty=int(block_json['difficulty']), mine=True)
            else:
                #print('Not mining block')
                block = Block(block_json['data'], block_json['previousHash'], difficulty=int(block_json['difficulty']), nonce=int(block_json['nonce']))
            #print('Returning block:')
            #block.printBlock()
            return block
