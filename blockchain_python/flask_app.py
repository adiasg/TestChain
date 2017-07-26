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
    page = "Index page"
    return page

@app.route('/status')
def status():
    page = "Length of blockchain: " + str(len(blockchain)) + "\n" + "<br>"
    return page

@app.route('/blocks')
def send_blocks():
    return test_blockchain.jsonify(blockchain)

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
