from flask import Flask
from flask import render_template
from flask import request
from core import Block, Blockchain, Node
import json

app = Flask(__name__)

node = Node()
node.buildTestNode(10)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def status():
    return render_template('status.html', status_data=node.getStatus())

@app.route('/blocks')
def sendBlocks():
    return render_template('blocks.html', blockchain=node.blockchain.jsonify(), block_display_order=['data', 'difficulty', 'nonce', 'previousHash', 'hash'])

@app.route('/submit/block',  methods=['GET','POST'])
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

app.run(debug=True)
