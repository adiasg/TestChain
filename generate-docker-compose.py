import sys

if(len(sys.argv)==2):
    node_range = int(sys.argv[1])
    print("Generating docker-compose.yml for "+str(node_range)+" nodes")
else:
    print("Run python3 generate-docker-compose.yml <number-of-nodes>")
    sys.exit(-1)

f = open('generated-docker-compose.yml', 'w')

f.write("version: '2'\n")
f.write("\n")
f.write("networks:\n")
f.write("   testchain_net:\n")
f.write("       ipam:\n")
f.write("           driver: default\n")
f.write("           config:\n")
f.write("               - subnet: 172.32.0.0/16\n")
f.write("\n")

f.write("services:\n")

f.write("   postgres:\n")
f.write("       restart: always\n")
f.write("       build: ./postgres\n")
f.write("       networks:\n")
f.write("           testchain_net:\n")
f.write("               ipv4_address: 172.32.0.2\n")
f.write("       ports:\n")
f.write("           - \"5432\"\n")
f.write("       depends_on:\n")
f.write("           - data\n")
f.write("\n")

f.write("   data:\n")
f.write("       image: postgres:9.6\n")
f.write("       networks:\n")
f.write("           testchain_net:\n")
f.write("               ipv4_address: 172.32.0.3\n")
f.write("       volumes:\n")
f.write("           - /var/lib/postgresql\n")
f.write("       command: \"true\"\n")

for iter in range(1,node_range+1):
    f.write("\n")
    f.write("   web"+str(iter)+":\n")
    f.write("       environment:\n")
    f.write("           - db_suffix=web"+str(iter)+"\n")
    f.write("#           - postgres_host=postgres\n")
    f.write("       restart: always\n")
    f.write("       build: ./blockchain_core\n")
    f.write("       ports:\n")
    f.write("           - \"5000\"\n")
    f.write("       command: python flask_app.py\n")
    f.write("       networks:\n")
    f.write("           testchain_net:\n")
    f.write("               ipv4_address: 172.32.0."+str(iter+3)+"\n")
    f.write("       depends_on:\n")
    f.write("           - postgres\n")
    f.write("\n")

f.close()
