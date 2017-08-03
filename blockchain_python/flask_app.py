from flask import Flask, render_template, request, redirect, url_for
from core import Block, Blockchain, Node
import json

app = Flask(__name__)

node = Node('test.db', app)
node.buildTestNode(10)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def status():
    return render_template('status.html', status_data=node.getStatus(), topHashList=node.scanTopHash())

@app.route('/blocks')
def blocks():
    return render_template('blocks.html', blockchain=node.blockchain.jsonify(), block_display_order=['data', 'difficulty', 'nonce', 'previousHash', 'hash', 'height'])

@app.route('/blocks/submit', methods=['GET','POST'])
def submitBlock():
    if request.method=='GET':
        return render_template('submit_block.html')
    else:
        try:
            block = Block.buildFromJson(request.form)
            if(block.verify()):
                node.blockchain.addBlock(block)
            elif(request.form['mine']=="on"):
                block.mineBlock()
                node.blockchain.addBlock(block)
            return render_template('blocks.html', heading="Block Added", blockchain=node.blockchain.jsonify(), block_display_order=['data', 'difficulty', 'nonce', 'previousHash', 'hash'])
        except:
            page = "Invalid request<br>"
            page += "request.form: " + json.dumps(request.form) + "<br>"
            return page

@app.route('/peerList')
def peerList():
    return render_template('peerList.html', peerList=node.peerList)

@app.route('/connect')
def peerConnect():
    node.peerConnect(request.remote_addr)
    return redirect(url_for('peerList'))

@app.route('/topHash', methods=['GET','POST'])
def topHash():
    if request.method=='GET':
        return render_template('topHash.html', topHash=node.getTopHash())
    else:
        return json.dumps({'topHash': node.getTopHash()})

app.run(debug=True)
