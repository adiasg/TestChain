import hashlib

class Block:
    def __init__(self, data, previous_hash):
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.difficulty = 2
        self.hash = self.hash_block()
        if(self.previous_hash!='0'):
            self.mine_block()

    def hash_block(self):
        sha = hashlib.sha256()
        sha.update((str(self.data) + str(self.previous_hash) + str(self.nonce)).encode('utf-8'))
        return sha.hexdigest()

    def mine_block(self):
        prefix = '0' * self.difficulty
        while(not( ( self.hash ).startswith(prefix) )):
            self.nonce += 1
            self.hash = self.hash_block()
        return

    def print_block(self):
        print("Block:\n\tData:\t\t", self.data)
        print("\tPrevious Hash:\t", self.previous_hash[:10])
        print("\tNonce:\t\t", self.nonce)
        print("\tDifficulty:\t", self.difficulty)
        print("\tHash:\t\t", self.hash[:10])
        return

    @staticmethod
    def generate_genesis_block():
        return Block({"Data": "Genesis Block"}, '0')


blockchain = [Block.generate_genesis_block()]
top_block = blockchain[-1]
top_block.print_block()

for iter in range(10):
    next_block = Block({"Data": "Block number " + str(iter)}, top_block.hash)
    top_block = next_block
    top_block.print_block()