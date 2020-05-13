import base64
import sys
import json

#from flask import Flask

#app = Flask(__name__)

#@app.route('/')
#def hello_world():
username = 'Anthony.Severini@teklink.com'
password = "Steelerssoccera1219"
user = 'Basic ' + str(base64.b64encode((f'{username}:{password}').encode('utf-8')).decode('utf-8'))
#    return("Hello, World!")`