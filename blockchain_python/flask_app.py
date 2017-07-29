from flask import Flask
from flask import render_template
from flask import request
import test_blockchain
from core import Block
import json

app = Flask(__name__)

blockchain = test_blockchain.build_blockchain()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def status():
    return render_template('status.html', blockchain_length=len(blockchain))

@app.route('/blocks')
def send_blocks():
    return render_template('display_blockchain.html', blockchain=test_blockchain.jsonify(blockchain), block_display_order=['data', 'difficulty', 'nonce', 'previous_hash', 'hash'])

@app.route('/submit/block',  methods=['GET','POST'])
def submit_block():
    if request.method=='GET':
        return render_template('submit_block.html')
    else:
        try:
            block = Block.build_from_json(request.form)
            page = "Block recieved: " + block.stringify() + "<br>"
            page += "Block verification " +  ("SUCCESSFUL" if block.verify() else "FAILED") + "<br>"
            return page
        except:
            page = "Invalid request<br>"
            page += "request.form: " + json.dumps(request.form) + "<br>"
            return page

app.run(debug=True)
