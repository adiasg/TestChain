import unittest
import test
from test import printBlock

peer1 = '172.32.0.4'
peer2 = '172.32.0.5'

class SimpleLaggingTestCase(unittest.TestCase):
    def setUp(self):
        self.peer1 = peer1
        self.peer2 = peer2

        self.data1 = {}
        self.data1['prefix'] = "TEST-SIMPLE-LAGGING "
        self.data1['hash'] = ""
        self.data1['numberOfBlocks'] = 32
        self.data1['reset'] = True

        self.data2 = {}
        self.data2['prefix'] = "TEST-SIMPLE-LAGGING "
        self.data2['hash'] = ""
        self.data2['numberOfBlocks'] = 48
        self.data2['reset'] = True

        generateBlocksResponse1 = test.generateBlocks(self.peer1, '5000', self.data1)
        generateBlocksResponse2 = test.generateBlocks(self.peer2, '5000', self.data2)

        '''
        topBlock1 = test.getTopBlock(self.peer1, '5000')
        topBlock2 = test.getTopBlock(self.peer2, '5000')
        print("topBlock1:")
        printBlock(topBlock1)
        print("topBlock2:")
        printBlock(topBlock2)
        '''

    def test_sync(self):
        #print("################### Syncing ###################")
        test.initiateSync(self.peer1, '5000', self.peer2)
        topBlock1 = test.getTopBlock(self.peer1, '5000')
        topBlock2 = test.getTopBlock(self.peer2, '5000')
        #print("topBlock1:")
        #printBlock(topBlock1)
        #print("topBlock2:")
        #printBlock(topBlock2)
        self.assertEqual(topBlock1['hash'], topBlock2['hash'])

class SimpleLeadingTestCase(unittest.TestCase):
    def setUp(self):
        self.peer1 = peer1
        self.peer2 = peer2

        self.data1 = {}
        self.data1['prefix'] = "TEST-SIMPLE-LEADING "
        self.data1['hash'] = ""
        self.data1['numberOfBlocks'] = 25
        self.data1['reset'] = True

        self.data2 = {}
        self.data2['prefix'] = "TEST-SIMPLE-LEADING "
        self.data2['hash'] = ""
        self.data2['numberOfBlocks'] = 14
        self.data2['reset'] = True

        generateBlocksResponse1 = test.generateBlocks(self.peer1, '5000', self.data1)
        generateBlocksResponse2 = test.generateBlocks(self.peer2, '5000', self.data2)

        '''
        topBlock1 = test.getTopBlock(self.peer1, '5000')
        topBlock2 = test.getTopBlock(self.peer2, '5000')
        print("topBlock1:")
        printBlock(topBlock1)
        print("topBlock2:")
        printBlock(topBlock2)
        '''

    def test_sync(self):
        #print("################### Syncing ###################")
        test.initiateSync(self.peer1, '5000', self.peer2)
        topBlock1 = test.getTopBlock(self.peer1, '5000')
        topBlock2 = test.getTopBlock(self.peer2, '5000')
        #print("topBlock1:")
        #printBlock(topBlock1)
        #print("topBlock2:")
        #printBlock(topBlock2)
        self.assertEqual(topBlock1['hash'], topBlock2['hash'])

class ForkedButLeadingTestCase(unittest.TestCase):
    def setUp(self):
        self.peer1 = peer1
        self.peer2 = peer2

        self.data1 = {}
        self.data1['prefix'] = "TEST-FORKED-LEADING "
        self.data1['hash'] = ""
        self.data1['numberOfBlocks'] = 20
        self.data1['reset'] = True

        self.data2 = {}
        self.data2['prefix'] = "TEST-FORKED-LEADING "
        self.data2['hash'] = ""
        self.data2['numberOfBlocks'] = 20
        self.data2['reset'] = True

        generateBlocksResponse1 = test.generateBlocks(self.peer1, '5000', self.data1)
        generateBlocksResponse2 = test.generateBlocks(self.peer2, '5000', self.data2)

        self.data1 = {}
        self.data1['prefix'] = "TEST-FORKED-LEADING LEAD "
        self.data1['hash'] = ""
        self.data1['numberOfBlocks'] = 24
        self.data1['reset'] = False

        self.data2 = {}
        self.data2['prefix'] = "TEST-FORKED-LEADING LAG "
        self.data2['hash'] = ""
        self.data2['numberOfBlocks'] = 13
        self.data2['reset'] = False

        generateBlocksResponse1 = test.generateBlocks(self.peer1, '5000', self.data1)
        generateBlocksResponse2 = test.generateBlocks(self.peer2, '5000', self.data2)

    def test_sync(self):
        test.initiateSync(self.peer1, '5000', self.peer2)
        topBlock1 = test.getTopBlock(self.peer1, '5000')
        topBlock2 = test.getTopBlock(self.peer2, '5000')
        self.assertEqual(topBlock1['hash'], topBlock2['hash'])

class ForkedButLaggingTestCase(unittest.TestCase):
    def setUp(self):
        self.peer1 = peer1
        self.peer2 = peer2

        self.data1 = {}
        self.data1['prefix'] = "TEST-FORKED-LAGGING "
        self.data1['hash'] = ""
        self.data1['numberOfBlocks'] = 20
        self.data1['reset'] = True

        self.data2 = {}
        self.data2['prefix'] = "TEST-FORKED-LAGGING "
        self.data2['hash'] = ""
        self.data2['numberOfBlocks'] = 20
        self.data2['reset'] = True

        generateBlocksResponse1 = test.generateBlocks(self.peer1, '5000', self.data1)
        generateBlocksResponse2 = test.generateBlocks(self.peer2, '5000', self.data2)

        self.data1 = {}
        self.data1['prefix'] = "TEST-FORKED-LAGGING LAG "
        self.data1['hash'] = ""
        self.data1['numberOfBlocks'] = 17
        self.data1['reset'] = False

        self.data2 = {}
        self.data2['prefix'] = "TEST-FORKED-LAGGING LEAD "
        self.data2['hash'] = ""
        self.data2['numberOfBlocks'] = 39
        self.data2['reset'] = False

        generateBlocksResponse1 = test.generateBlocks(self.peer1, '5000', self.data1)
        generateBlocksResponse2 = test.generateBlocks(self.peer2, '5000', self.data2)

    def test_sync(self):
        test.initiateSync(self.peer1, '5000', self.peer2)
        topBlock1 = test.getTopBlock(self.peer1, '5000')
        topBlock2 = test.getTopBlock(self.peer2, '5000')
        self.assertEqual(topBlock1['hash'], topBlock2['hash'])

if __name__ == '__main__':
    unittest.main()
