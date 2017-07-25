import hashlib

class Block:
    def __init__(self, data, previous_hash):
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def hash_block(self):
        sha = hashlib.sha256()
        sha.update((str(self.data) + str(self.previous_hash)).encode('utf-8'))
        return sha.hexdigest()

    def print_block(self):
        print("Block:\n\tData:\t\t", self.data, "\n\tPrevious Hash:\t", self.previous_hash[:10], "\n\tHash:\t\t", self.hash[:10])
        return

    @staticmethod
    def generate_genesis_block():
        return Block({"Data": "Genesis Block"}, "0")


blockchain = [Block.generate_genesis_block()]
top_block = blockchain[-1]
top_block.print_block()

for iter in range(10):
    next_block = Block({"Data": "Block number " + str(iter)}, top_block.hash)
    top_block = next_block
    top_block.print_block()
