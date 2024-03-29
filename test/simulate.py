import test
from test import printBlock, printTopBlocks, resetPeers, randomPeerPair, dataGenerateBlock, generate_coro, sync_coro, wait
from analyze import analyze
import asyncio
import sys
import time

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Error! Give arguments:")
        print("\tNumber of peers")
        print("\tLambda sync")
        print("\tLambda generate")
        print("\tSimulation time")

    else:
        """
        number_of_peers = 10
        avg_inter_sync_time_per_peer = 10.0
        avg_inter_generate_block_time = 10.0
        lambda_sync = number_of_peers * 1.0 / avg_inter_sync_time_per_peer
        lambda_generate = 1.0 / avg_inter_generate_block_time
        simulation_time = number_of_peers*100
        """
        number_of_peers = int(sys.argv[1])
        lambda_sync = float(sys.argv[2])
        lambda_generate = float(sys.argv[3])
        simulation_time = float(sys.argv[4])

        peers = [ '172.32.0.'+str(4+x) for x in range(number_of_peers) ]

        time.sleep(60)
        resetPeers(peers)

        loop = asyncio.get_event_loop()
        future1 = asyncio.ensure_future( generate_coro(peers, lambda_generate) )
        future2 = asyncio.ensure_future( sync_coro(peers, lambda_sync) )
        #loop.run_until_complete( asyncio.gather(future1, future2) )
        loop.run_until_complete( wait(simulation_time) )

        printTopBlocks(peers)

        analyze(number_of_peers, lambda_sync, lambda_generate, simulation_time)
