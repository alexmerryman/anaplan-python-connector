import base64
import sys
import json

#from flask import Flask

#app = Flask(__name__)

#@app.route('/')
#def hello_world():
#username = 'Anthony.Severini@teklink.com'
#password = "Steelerssoccera1219_1"
#user = 'Basic ' + str(base64.b64encode((f'{username}:{password}').encode('utf-8')).decode('utf-8'))
#    return("Hello, World!")`

# This script runs your selected export. Run 'exportStatus.py' to retrieve
# the task metadata for the export task.

# This script assumes you know your workspaceGuid, modelGuid, and export
# metadata.
# If you do not have this information, please run 'getWorkspaces.py',
# 'getModels.py', and 'getExports.py' and retrieve this information from the
# resulting json files.

# If you are using certificate authentication, this script assumes you have
# converted your Anaplan certificate to PEM format, and that you know the
# Anaplan account email associated with that certificate.

# This script uses Python 3 and assumes that you have the following modules
# installed: requests, base64, json

import requests
import base64
import sys
import json

# Insert your workspace Guid
wGuid = '8a81b08e4f6d2b43014fbe11122a160c'
# Insert your model Guid
mGuid = '96339A3A48394142A3E70E057F75480E'
# Insert the Anaplan account email being used
username = 'Anthony.Severini@teklink.com'
# Replace with your export metadata
exportData = {
  "id" : "116000000000",
  "name" : "PYC01:Export Test - Test.xls",
  "exportType" : "GRID_CURRENT_PAGE"
}
# If using basic auth, insert your password. Otherwise, remove this line.
password = 'Steelerssoccera1219_1'

user = 'Basic ' + str(base64.b64encode((f'{username}:{password}'
                                        ).encode('utf-8')).decode('utf-8'))

url = (f'https://api.anaplan.com/1/3/workspaces/{wGuid}/models/{mGuid}/' +
       f'exports/{exportData["id"]}/tasks')

postHeaders = {
    'Authorization': user,

    'Content-Type': 'application/json'
}

# Runs an export request, and returns task metadata to 'postExport.json'
postExport = requests.post(url,
                           headers=postHeaders,
                           data=json.dumps({'localeName': 'en_US'}))

conn = AnaplanConnection(anaplan.generate_authorization("Basic",user, password), wGuid, mGuid)

print(postExport.status_code)
print(postExport.text)
with open('postExport.json', 'wb') as f:
    f.write(postExport.text.encode('utf-8'))

print(postExport.text)

download = get_file(conn)