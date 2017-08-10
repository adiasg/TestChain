from flask import Flask, render_template, request, redirect, url_for, g
from core import Block, Blockchain, Node
import psycopg2
import json
import sys
import requests

app = Flask(__name__)

def connect_db():
    print('connect_db()')
    if not hasattr(g, 'connectionToDb'):
        connect_str = " dbname='myproject' user='myprojectuser' host='localhost' password='password' "
        g.connectionToDb = psycopg2.connect(connect_str)

with app.app_context():
    print('app.app_context()')
    connect_db()
    node = Node('test.db', app)
    node.buildTestNode(22)
    g.connectionToDb.close()

@app.before_request
def bef_req():
    print('@app.before_request')
    connect_db()

@app.teardown_appcontext
def test(error):
    print('@app.teardown_appcontext')
    if hasattr(g, 'connectionToDb'):
        g.connectionToDb.close()

@app.route('/', methods=['GET','POST'])
def index():
    if(request.method=='GET'):
        return render_template('index.html')
    else:
        return node.getNodeDeclaration()

@app.route('/debug', methods=['GET','POST'])
def debug():
    return "Debug page"

@app.route('/initiateSync', methods=['GET','POST'])
def initiateSync():
    if request.method=='GET':
        return render_template('initiateSync.html', peerList=node.peerList)
    else:
        return node.initiateSyncPeer(request.form['peerIp'], "None")

@app.route('/status')
def status():
    return render_template('status.html', status_data=node.getStatus(), peerState=node.scanPeerState())

@app.route('/blocks/display')
def blocksDisplay():
    return render_template('blocks_display.html', blockchain=node.blockchain.jsonify(), block_display_order=['data', 'difficulty', 'nonce', 'previousHash', 'hash', 'height'])

@app.route('/blocks/request', methods=['GET','POST'])
def blockRequest():
    if request.method=='GET':
        return render_template('block_request.html')
    else:
        return node.getBlock(request.form['hash'])

@app.route('/blocks/submit', methods=['GET','POST'])
def blockSubmit():
    if request.method=='GET':
        return render_template('submit_block.html')
    else:
        try:
            block = Block.buildFromJson(request.form)
            if(block.verify()):
                node.blockchain.addBlock(block)
            elif('mine' in request.form and request.form['mine']=="on"):
                block.mineBlock()
                node.blockchain.addBlock(block)
            else:
                return "Block not verified"
            return render_template('blocks_display.html', heading="Block Added", blockchain=node.blockchain.jsonify(), block_display_order=['data', 'difficulty', 'nonce', 'previousHash', 'hash'])
        except:
            page = "Invalid request<br>"
            page += "request.form: " + json.dumps(request.form) + "<br>"
            return page

@app.route('/blocks/sync', methods=['GET','POST'])
def syncBlocks():
    print("syncBlocks")
    if request.method=='POST':
        print("POST")
        ini_req = ""
        state = node.receiveSyncPeer(request.remote_addr, json.loads(request.data.decode('utf-8')))
        #if(json.loads(state)['state']=="ahead/forked"):
            #ini_req = node.initiateSyncPeer(request.remote_addr, "ahead/forked")
        return str(state) + str(ini_req)
    else:
        print("GET")
        return node.initiateSyncPeer(request.remote_addr, "None")

@app.route('/peerList')
def peerList():
    return render_template('peerList.html', peerList=node.peerList)

@app.route('/connect', methods=['GET','POST'])
def peerConnect():
    if request.method=='GET':
        # for connecting node who is viewing another peers '/connect' page to that peer
        node.peerConnect(request.remote_addr)
        return redirect(url_for('peerList'))
    else:
        node.peerConnect(request.remote_addr, request.form)
        return redirect(url_for('peerList'))

@app.route('/connect/to', methods=['GET','POST'])
def connectToPeer():
    if request.method=='GET':
        return render_template('connect_to.html')
    else:
        node.peerConnect(request.form['peerIp'])
        node.connectToPeer(request.form['peerIp'])
        return redirect(url_for('peerList'))

@app.route('/topHash', methods=['GET','POST'])
def topHash():
    if request.method=='GET':
        return render_template('topHash.html', topHash=node.getTopHash())
    else:
        return json.dumps({'topHash': node.getTopHash()})

@app.route('/topHash/chain', methods=['GET','POST'])
def topHashChain():
    if request.method=='GET':
        return render_template('topHashChain.html', topHashChain=node.getTopHashChain())
    else:
        return json.dumps(node.getTopHashChain())

if __name__ == '__main__':
    if(len(sys.argv)>1 and sys.argv[1]=='debug'):
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', debug=False)
