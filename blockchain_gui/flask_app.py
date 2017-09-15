from flask import Flask, render_template, jsonify, request
import json
import requests
import sys

app = Flask(__name__)

url = 'http://127.0.0.1:5000'

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/status')
def serve_status():
    data = requests.get(url+'/status', timeout=30).json()
    return render_template('status.html', status_data=data)

@app.route('/block/all')
def serve_block_all():
    data = requests.get(url+'/block/all', timeout=30).json()
    return render_template('block_display.html', blockchain=data, block_display_order=['data', 'difficulty', 'nonce', 'hash','previousHash',  'height', 'sumOfDifficulty'])



@app.route('/block/request', methods=['GET', 'POST'])
def serve_block_request():
    if(request.method == 'GET'):
        return render_template('block_request.html')
    else:
        block = requests.post(url+'/block/request', json=request.form, timeout=30).json()
        return render_template('message.html', message=block)

@app.route('/block/topHashChain')
def serve_block_topHashChain():
    data = requests.get(url+'/block/topHashChain', timeout=30).json()
    return render_template('message.html', message=data)

@app.route('/block/submit', methods=['GET', 'POST'])
def serve_block_submit():
    if(request.method == 'GET'):
        return render_template('block_submit.html')
    else:
        status = requests.post(url+'/block/submit', json=request.form, timeout=30).json()
        return render_template('message.html', message=status)

@app.route('/block/generateBlocks', methods=['GET', 'POST'])
def serve_block_generate():
    if(request.method == 'GET'):
        return render_template('block_generate.html')
    else:
        status = requests.post(url+'/block/generateBlocks', json=request.form, timeout=30).json()
        return render_template('message.html', message=status)

@app.route('/connect', methods=['GET', 'POST'])
def serve_connect():
    if(request.method == 'GET'):
        return render_template('connect.html')
    else:
        status = requests.post(url+'/connect/to', json=request.form, timeout=30).json()
        return render_template('message.html', message=status)

@app.route('/peerList')
def serve_peerList():
    data = requests.get(url+'/peerList', timeout=30).json()
    return render_template('peerList.html', peerList=data)

@app.route('/initiateSync', methods=['GET', 'POST'])
def serve_initiateSync():
    if(request.method == 'GET'):
        peerList = requests.get(url+'/peerList', timeout=30).json()
        print("peerList:", peerList)
        return render_template('initiateSync.html', peerList=peerList)
    else:
        print('form POSTed')
        print(request.form)
        print(request.form['peerIp'])
        print('request.form:',jsonify(request.form))
        data = {}
        data['peerIp'] = request.form['peerIp']
        print('data:', data)
        status = requests.post(url+'/block/sync/initiate', json=data, timeout=200).json()
        return render_template('message.html', message=status)

@app.route('/debug')
def serve_debug():
    return render_template('message.html', message="Debug page")

if __name__ == '__main__':
    if(len(sys.argv)>1 and sys.argv[1]=='debug'):
        app.run(port=5001, debug=True)
    else:
        app.run(host='0.0.0.0', port=5001, debug=False)
