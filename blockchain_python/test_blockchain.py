import json
from core import Block

def build_blockchain(verbose=False):
    blockchain = [Block.generate_genesis_block()]
    top_block = blockchain[-1]
    if(verbose):
        top_block.print_block()

    for iter in range(3):
        next_block = Block({"Data": "Block number " + str(iter)}, top_block.hash)
        blockchain.append(next_block)
        top_block = next_block
        if(verbose):
            top_block.print_block()

    return blockchain

def make_json(blockchain):
    chain_to_send = [block.jsonify() for block in blockchain]
    chain_to_send = json.dumps(chain_to_send)
    #print(chain_to_send)
    print("type(chain_to_send):", type(chain_to_send))
    return chain_to_send

def build_from_json(json_str):
    recv_chain = json.loads(json_str)
    #print(recv_chain)
    print("type(recv_chain):", type(recv_chain))
    block = Block.build_from_json(recv_chain[-1])
    block.print_block()
    return

def test_flask():
    blockchain = build_blockchain()
    return make_json(blockchain)

def jsonify(blockchain):
    return make_json(blockchain)
