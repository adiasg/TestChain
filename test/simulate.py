import test
from test import printBlock, printTopBlocks, resetPeers, randomPeerPair, dataGenerateBlock, generate_coro, sync_coro, wait
from analyze import analyze
import asyncio
import random
import os

if __name__ == '__main__':
    number_of_peers = 10
    avg_inter_sync_time_per_peer = 6.0
    avg_inter_generate_block_time_per_peer = 10.0
    lambda_sync = number_of_peers * 1.0 / avg_inter_sync_time_per_peer
    lambda_generate = 1.0 / avg_inter_generate_block_time_per_peer
    simulation_time = number_of_peers*100

    peers = [ '172.32.0.'+str(4+x) for x in range(number_of_peers) ]

    resetPeers(peers)

    loop = asyncio.get_event_loop()
    future1 = asyncio.ensure_future( generate_coro(peers, lambda_generate) )
    future2 = asyncio.ensure_future( sync_coro(peers, lambda_sync) )
    #loop.run_until_complete( asyncio.gather(future1, future2) )
    loop.run_until_complete( wait(simulation_time) )

    printTopBlocks(peers)

    analyze(number_of_peers, lambda_sync, lambda_generate, simulation_time)
