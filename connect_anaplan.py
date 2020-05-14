#from flask import Flask

#app = Flask(__name__)

#@app.route('/')
#def hello_world():
#username = 'Anthony.Severini@teklink.com'
#password = "Steelerssoccera1219_1"
#user = 'Basic ' + str(base64.b64encode((f'{username}:{password}').encode('utf-8')).decode('utf-8'))
#    return("Hello, World!")`


import anaplan_connect_helper_functions

# Insert your workspace Guid
wGuid = '8a81b08e4f6d2b43014fbe11122a160c'

# Insert your model Guid
mGuid = '96339A3A48394142A3E70E057F75480E'

user_email = 'Anthony.Severini@teklink.com'
user_pwd = 'Steelerssoccera1219_1'
basic_auth_user = anaplan_connect_helper_functions.anaplan_basic_auth_user(user_email, user_pwd)

# TODO: redo exportData (below)
# Replace with your export metadata
exportData = {
    "id": "116000000000",
    "name": "PYC01:Export Test - Test.xls",
    "exportType": "GRID_CURRENT_PAGE"
}

url = (f'https://api.anaplan.com/1/3/workspaces/{wGuid}/models/{mGuid}/' + f'exports/{exportData["id"]}/tasks')

postHeaders = {
    'Authorization': basic_auth_user,
    'Content-Type': 'application/json'
}

print('------------------- WORKSPACES -------------------')
try:
    workspaces = anaplan_connect_helper_functions.get_workspaces(basic_auth_user)
except:
    print('ERROR: Unable to get workspaces.')
if workspaces.status_code == 200:
    print(workspaces.text)
else:
    print('Error: Status Code {}'.format(workspaces.status_code))


print('------------------- MODEL INFO -------------------')
try:
    model_info = anaplan_connect_helper_functions.get_model_info(mGuid, basic_auth_user)
except:
    print('ERROR: Unable to get model info.')
if model_info.status_code == 200:
    print(model_info.text)
else:
    print('Error: Status Code {}'.format(model_info.status_code))


print('------------------- MODEL FILES -------------------')
try:
    model_files = anaplan_connect_helper_functions.get_model_files(wGuid, mGuid, basic_auth_user)
except:
    print('ERROR: Unable to get model files.')
if model_files.status_code == 200:
    print(model_files.text)
else:
    print('Error: Status Code {}'.format(model_files.status_code))


print('------------------- FILE INFO -------------------')
fileID = '116000000000'
try:
    chunk_data = anaplan_connect_helper_functions.get_chunk_data(wGuid, mGuid, fileID, basic_auth_user)
except:
    print('ERROR: Unable to get model files.')
if chunk_data.status_code == 200:
    print(chunk_data.text)
else:
    print('Error: Status Code {}'.format(chunk_data.status_code))


print('------------------- MODEL IMPORTS -------------------')
try:
    model_imports = anaplan_connect_helper_functions.get_imports(wGuid, mGuid, basic_auth_user)
except:
    print('ERROR: Unable to get model files.')
if model_imports.status_code == 200:
    print(model_imports.text)
else:
    print('Error: Status Code {}'.format(model_imports.status_code))


print('------------------- MODEL EXPORTS -------------------')
try:
    model_exports = anaplan_connect_helper_functions.get_exports(wGuid, mGuid, basic_auth_user)
except:
    print('ERROR: Unable to get model files.')
if model_exports.status_code == 200:
    print(model_exports.text)
else:
    print('Error: Status Code {}'.format(model_exports.status_code))


print('------------------- MODEL ACTIONS -------------------')
try:
    model_actions = anaplan_connect_helper_functions.get_actions(wGuid, mGuid, basic_auth_user)
except:
    print('ERROR: Unable to get model files.')
if model_actions.status_code == 200:
    print(model_actions.text)
else:
    print('Error: Status Code {}'.format(model_actions.status_code))


print('------------------- MODEL PROCESSES -------------------')
try:
    model_processes = anaplan_connect_helper_functions.get_processes(wGuid, mGuid, basic_auth_user)
except:
    print('ERROR: Unable to get model files.')
if model_processes.status_code == 200:
    print(model_processes.text)
else:
    print('Error: Status Code {}'.format(model_processes.status_code))

# # Runs an export request, and returns task metadata to 'postExport.json'
# try:
#     postExport = requests.post(url,
#                                headers=postHeaders,
#                                data=json.dumps({'localeName': 'en_US'}))
# except:
#     print('ERROR: Post failed. Status code: {}.'.format(postExport.status_code))
#
# conn = AnaplanConnection(anaplan.generate_authorization("Basic", basic_auth_user, password), wGuid, mGuid)
#
#
# print(postExport.status_code)
# print(postExport.text)
# with open('postExport.json', 'wb') as f:
#     f.write(postExport.text.encode('utf-8'))
#
# print(postExport.text)
#
# download = get_file(conn)