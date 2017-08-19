from flask import Flask, jsonify, g, request, abort, redirect, url_for
import json
import psycopg2
import sys
from core import Block, Blockchain, Node

app = Flask(__name__)

def connect_db():
    print('connect_db()')
    if not hasattr(g, 'connectionToDb'):
        connect_str = " dbname='myproject' user='myprojectuser' host='localhost' password='password' "
        g.connectionToDb = psycopg2.connect(connect_str)

with app.app_context():
    #print('app.app_context()')
    connect_db()
    node = Node()
    node.buildTestNode(20)
    g.connectionToDb.close()

@app.before_request
def beforeRequest():
    #print('@app.before_request')
    connect_db()

@app.teardown_appcontext
def teardownAppcontext(error):
    #print('@app.teardown_appcontext')
    if hasattr(g, 'connectionToDb'):
        g.connectionToDb.close()

@app.route('/', methods=['GET'])
def serve_index():
    return jsonify({'nodeDeclaration': node.getNodeDeclaration()})

@app.route('/status', methods=['GET'])
def serve_status():
    return jsonify(node.getStatus())

@app.route('/block/all', methods=['GET'])
def serve_block_all():
    return jsonify(node.getAllBlocks())

@app.route('/block/topHashChain', methods=['GET'])
def serve_block_topHashChain():
    return jsonify(node.getTopChainNumber(10))

@app.route('/block/request', methods=['POST'])
def serve_block():
    if not request.json or not 'hash' in request.json:
        abort(400)
    return jsonify(node.getBlock(request.json['hash']))

@app.route('/block/submit', methods=['POST'])
def serve_block_submit():
    # TODO verify json
    node.addBlock(request.json)
    return jsonify({'block':'received'})

@app.route('/connect', methods=['POST'])
def serve_connect():
    if not request.json or not 'nodeDeclaration' in request.json:
        abort(400)
    node.addPeer(request.remote_addr, request.json['nodeDeclaration'])
    return redirect(url_for('serve_index'))

@app.route('/connect/to', methods=['POST'])
def serve_connect_to():
    if not request.json or not 'peerIp' in request.json:
        abort(400)
    node.connectPeer(request.json['peerIp'])
    return jsonify({'status': 'recieved request'})

@app.route('/peerList', methods=['GET'])
def serve_peerList():
    return jsonify(node.getPeerList())

@app.route('/block/sync', methods=['POST'])
def serve_block_sync():
    print('serve_block_sync():')
    if request.json:
        print('request.json')
        if 'topHash' in request.json:
            #print('\trequest.json contains topHash')
            #print("\trequest.json['tophash']:", request.json['topHash'])
            return jsonify(node.receiveSync(request.remote_addr, request.json['topHash']))
        elif 'topHashChain' in request.json:
            #print('\trequest.json contains topHashChain')
            #print("\trequest.json['topHashChain']:", request.json['topHashChain'])
            return jsonify(node.receiveTopHashChain(request.remote_addr, request.json['topHashChain']))
    else:
        abort(400)

@app.route('/block/sync/initiate', methods=['POST'])
def serve_block_sync_initiate():
    if not request.json or not 'peerIp' in request.json:
        print('serve_block_sync_initiate returning 400')
        abort(400)
    #print('not 400')
    #print(request.json)
    #print(request.json['peerIp'])
    return jsonify(node.initiateSync(request.json['peerIp']))

if __name__ == '__main__':
    if(len(sys.argv)>1 and sys.argv[1]=='debug'):
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', debug=False)
