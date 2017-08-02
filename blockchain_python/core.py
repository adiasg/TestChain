import hashlib
import json
import pickle
import sqlite3
from flask import g, Flask, current_app

class Node:
    def __init__(self, DbName, app):
        self.peerList = ["127.0.0.1"]
        self.blockchain = Blockchain(DbName, app)

    def getStatus(self):
        return self.blockchain.getStatus()

    def buildTestNode(self, numberOfBlocks):
        self.blockchain.buildTestBlockchain(numberOfBlocks)

class Blockchain:
    def __init__(self, DbName, app):
        self.connectionToDb = sqlite3.connect(DbName)
        self.cursor = self.connectionToDb.cursor()
        self.cursor.execute("DROP TABLE IF EXISTS test")
        self.cursor.execute("CREATE TABLE test(hash STRING, block STRING)")
        genesisBlock = Block.generateGenesisBlock()
        self.cursor.execute("INSERT INTO test VALUES (?, ?)", (genesisBlock.hash, pickle.dumps(genesisBlock)) )
        self.topHash = genesisBlock.hash
        self.blockchainLength = 0
        self.sumOfDifficuties = 0

    def getStatus(self):
        return {"Current Blockchain Length": self.blockchainLength, "Sum Of Difficulties": self.sumOfDifficuties}

    def buildTestBlockchain(self, numberOfBlocks):
        #print("buildTestBlockchain()")
        top_block = self.getBlock(self.topHash)
        top_block.printBlock()

        for iter in range(1,numberOfBlocks+1):
            next_block = Block({"Data": "Block number " + str(iter)}, top_block.hash)
            self.addBlock(next_block)
            top_block = next_block

    def getBlock(self, hash):
        return [ pickle.loads(row[1]) for row in self.cursor.execute( "SELECT * FROM test WHERE hash = ?" , (hash, ) ) ][0]

    def addBlock(self, block):
        # TODO Verify before adding
        #print("addBlock()")
        self.cursor.execute('INSERT INTO test VALUES (?,?)', (block.hash, pickle.dumps(block)))
        newHeight = self.findHeight(block.hash)
        if(newHeight > self.blockchainLength):
            self.topHash = block.hash
            self.blockchainLength = newHeight
        self.connectionToDb.commit()

    def findHeight(self, hash):
        #print("findHeight()")
        block = self.getBlock(hash)
        height = 0
        genesisPreviousHash = '0'*64
        while(block.previousHash!=genesisPreviousHash):
            block = self.getBlock(block.previousHash)
            height += 1
        print("Height:", height)
        return height

    def jsonify(self):
        chain_to_send = []
        block = self.getBlock(self.topHash)
        chain_to_send.append(block.jsonify())
        genesisPreviousHash = '0'*64
        while(block.previousHash!=genesisPreviousHash):
            block = self.getBlock(block.previousHash)
            chain_to_send.append(block.jsonify())

class Block:
    def __init__(self, data, previousHash, mine=True):
        self.data = data
        self.difficulty = 1
        self.nonce = 0
        self.previousHash = previousHash
        self.hash = self.hashBlock()
        if(mine):
            self.mineBlock()

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
        block.mineBlock()
        return block

    @staticmethod
    def buildFromJson(json_dict):
        block = Block(json_dict['data'], json_dict['previousHash'])
        block.difficulty = int(json_dict['difficulty'])
        block.nonce = int(json_dict['nonce'])
        return block
