from core import *
import json
import requests
url='http://localhost:5000'
block = Block('some data','0'*64,2,0,True)
data1 = {'block.hash':block.hash}
requests.post(url,data1)


