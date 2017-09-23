import test
import time
import pandas

peer1 = '172.32.0.5'
peer2 = '172.32.0.5'
peer3 = '172.32.0.6'
defaultPortNo = '5000'

url1 = 'http://'+peer1+':'+defaultPortNo
url2 = 'http://'+peer2+':'+defaultPortNo
url3 = 'http://'+peer3+':'+defaultPortNo

data1 = {}
data1['prefix'] = 'TEST-BLOCK-GENERATE '
data1['hash'] = ''
data1['numberOfBlocks'] = 1
data1['difficulty'] = 4
data1['reset'] = False

columns = ['peerIp', 'numBlocks', 'difficulty', 'time']
data = []

for difficulty in range(6,7):
    print('Starting difficulty:', difficulty)
    data1['difficulty'] = difficulty
    for iter in range(2):
        start = time.time()
        test.generateBlocks(peer1, defaultPortNo, data1)
        end = time.time()
        elapsedTime = end - start
        data.append( [ peer1, data1['numberOfBlocks'], data1['difficulty'], elapsedTime ] )
        if iter % 5 == 0:
            print('Done with', iter, 'blocks')
    print('Finished difficulty:', difficulty)

df = pandas.DataFrame(data=data, columns=columns)
print(df)

print("Avg Time:", sum(df['time'])/len(df))
#df.to_csv('data/generateTime.csv', index=False)
