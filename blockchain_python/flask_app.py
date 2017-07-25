from flask import Flask
from .blockchain_python import test_flask

app = Flask(__name__)

@app.route('/test')
def index():
    return test_flask()
