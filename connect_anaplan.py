#from flask import Flask

#app = Flask(__name__)

#@app.route('/')
#def hello_world():
#username = 'Anthony.Severini@teklink.com'
#password = "Steelerssoccera1219_1"
#user = 'Basic ' + str(base64.b64encode((f'{username}:{password}').encode('utf-8')).decode('utf-8'))
#    return("Hello, World!")`

import json
import anaplan_connect_helper_functions

# Insert your workspace Guid
wGuid = '8a81b08e4f6d2b43014fbe11122a160c'

# Insert your model Guid
mGuid = '96339A3A48394142A3E70E057F75480E'

user_email = 'Anthony.Severini@teklink.com'
user_pwd = 'Steelerssoccera1219_1'
basic_auth_user = anaplan_connect_helper_functions.anaplan_basic_auth_user(user_email, user_pwd)

# Anaplan API v2.x require token-based authentication rather than basic user:pwd authentication
# (reference: https://anaplanauthentication.docs.apiary.io/#reference/authentication-token)
try:
    token = anaplan_connect_helper_functions.anaplan_create_token(user_email, user_pwd)
    # print('TOKEN TEXT:', token.text)
    # print('TOKEN STATUS CODE:', token.status_code)
except:
    token = None
    print('ERROR: Unable to create auth token.')
if token.status_code == 201:
    try:
        token_json = token.json()
        token_val = str(token_json['tokenInfo']['tokenValue'])
        token_auth_user = anaplan_connect_helper_functions.anaplan_token_auth_user(token_val)
    except:
        print('ERROR: Invalid token.')
else:
    print('ERROR: Auth token creation failed - status code:', token.status_code)

# TODO: redo exportData (below)
# Replace with your export metadata
exportData = {
    "id": "116000000000",
    "name": "PYC01:Export Test - Test.xls",
    "exportType": "GRID_CURRENT_PAGE"
}

url = (f'https://api.anaplan.com/2/0/workspaces/{wGuid}/models/{mGuid}/' + f'exports/{exportData["id"]}/tasks')

postHeaders = {
    'Authorization': basic_auth_user,
    'Content-Type': 'application/json'
}

print('------------------- WORKSPACES -------------------')
try:
    workspaces = anaplan_connect_helper_functions.get_workspaces(token_auth_user)
    workspaces_data = json.loads(workspaces.text)
except:
    print('ERROR: Unable to get workspaces.')
if workspaces.status_code == 200:
    print(workspaces_data)
else:
    print('Error: Status Code {}'.format(workspaces.status_code))


print('------------------- MODEL INFO -------------------')
try:
    model_info = anaplan_connect_helper_functions.get_model_info(mGuid, token_auth_user)
    model_info_data = json.loads(model_info.text)
except:
    print('ERROR: Unable to get model info.')
if model_info.status_code == 200:
    print(model_info_data)
else:
    print('Error: Status Code {}'.format(model_info.status_code))


print('------------------- MODEL EXPORTS -------------------')
try:
    model_exports = anaplan_connect_helper_functions.get_model_exports(wGuid, mGuid, token_auth_user)
    model_exports_data = json.loads(model_exports.text)
except:
    print('ERROR: Unable to get model files.')
if model_exports.status_code == 200:
    print(model_exports_data)
else:
    print('Error: Status Code {}'.format(model_exports.status_code))

# TODO: blocked by inadequate schema in Anaplan (for test table)
# ref: https://community.anaplan.com/t5/Best-Practices/RESTful-API-Best-Practices/ta-p/33579 (https://vimeo.com/318242332)
test_export_id = '116000000002'
test_export_data = anaplan_connect_helper_functions.get_export_data(wGuid, mGuid, test_export_id, token_auth_user)
print(json.loads(test_export_data.text))

# print('------------------- MODEL IMPORTS -------------------')
# try:
#     model_imports = anaplan_connect_helper_functions.get_imports(wGuid, mGuid, token_auth_user)
#     model_imports_data = json.loads(model_imports.text)
# except:
#     print('ERROR: Unable to get model files.')
# if model_imports.status_code == 200:
#     print(model_imports_data)
# else:
#     print('Error: Status Code {}'.format(model_imports.status_code))


print('------------------- MODEL FILES -------------------')
try:
    model_files = anaplan_connect_helper_functions.get_model_files(wGuid, mGuid, token_auth_user)
    model_files_data = json.loads(model_files.text)
except:
    print('ERROR: Unable to get model files.')
if model_files.status_code == 200:
    print(model_files_data)
else:
    print('Error: Status Code {}'.format(model_files.status_code))


print('------------------- FILE INFO (CHUNK METADATA) -------------------')
# for f in model_files_data:
#     if f['id'] == '':
PYC01_test_file_id = '116000000000'
print('FILE ID:', PYC01_test_file_id)
try:
    chunk_metadata = anaplan_connect_helper_functions.get_chunk_metadata(wGuid, mGuid, PYC01_test_file_id, token_auth_user)
    chunk_metadata_data = json.loads(chunk_metadata.text)
except:
    print('ERROR: Unable to get file info (chunk metadata).')
if chunk_metadata.status_code == 200:
    print(chunk_metadata_data)
else:
    print('Error: Status Code {}'.format(chunk_metadata.status_code))


print('------------------- CHUNK INFO -------------------')
for c in chunk_metadata_data['chunks']:
    print('Chunk name, ID:', c['name'], ',', c['id'])
    try:
        chunk_data = anaplan_connect_helper_functions.get_chunk_data(wGuid,
                                                                     mGuid,
                                                                     PYC01_test_file_id,
                                                                     c['id'],
                                                                     token_auth_user)
        # print(chunk_data.url)
        # print(chunk_data.status_code)
        # print(chunk_data.text)
        # print(type(chunk_data.text))
        chunk_data_text = chunk_data.text
    except:
        print('ERROR: Unable to get specified chunk.')
    if chunk_data.status_code == 200:
        print(chunk_data_text)
        anaplan_connect_helper_functions.parse_chunk_data(chunk_data_text)
    else:
        print('Error: Status Code {}'.format(chunk_data.status_code))





# print('------------------- MODEL ACTIONS -------------------')
# try:
#     model_actions = anaplan_connect_helper_functions.get_actions(wGuid, mGuid, basic_auth_user)
#     model_actions_data = json.loads(model_exports.text)
# except:
#     print('ERROR: Unable to get model files.')
# if model_actions.status_code == 200:
#     print(model_actions_data)
# else:
#     print('Error: Status Code {}'.format(model_actions.status_code))
#
#
# print('------------------- MODEL PROCESSES -------------------')
# try:
#     model_processes = anaplan_connect_helper_functions.get_processes(wGuid, mGuid, basic_auth_user)
#     model_processes_data = json.loads(model_processes.text)
# except:
#     print('ERROR: Unable to get model files.')
# if model_processes.status_code == 200:
#     print(model_processes_data)
# else:
#     print('Error: Status Code {}'.format(model_processes.status_code))


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
