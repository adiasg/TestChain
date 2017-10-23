import numpy as np

endpoints = {}
endpoints[15] = (1.06, 1.4)
endpoints[20] = (1.56, 2.53)
endpoints[25] = (2.1, 4.0)

d = {}

for k in endpoints.keys():
    d[k] = np.linspace(endpoints[k][0], endpoints[k][1], 5).round(2).tolist()[1:-1]

print(d)
