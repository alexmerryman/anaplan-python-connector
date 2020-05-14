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

auth_token = '5Y6tPNuDwSKzlJt9ulStGw==.n947r77aE06ho8E46m0iLm1Z0X/p29PfnXeTBXqc4kKCgp75K4yUTTtptgKQYH7q4AHgokvIdSEpOUdJkYaOBGypTRpo/qp71RZ6/96hxdqqzVZo5Ma8pfPOPZ/PzSdWk6jZUmHeQsdb6wa9pPUg23d3foNjpsD27UH0fVyTy0pszr5DTClPGq1wEBQhCHYCMkLVVXMJq1yUUDqFQVmQH4eyhat/guuEn0O1yVIlD9c6FyDwBcRL7nXRYRo+ZbWh/xSs8+/fOoNYW3z+9TMLNIUZyQziBK5cLt7Ym+UUczxhvAYvIwnB00vOlelMc4t4NAPwoyTG8eRVjjfDa7oZRIq0w7vfjgYMiy0oBWCr0GR9dfDakjV5r/eMt6W+GmDt+RI10XDO3zF+Q0kY5Opq4xChJ7qZ//uxR3yli5keObr1+Ev3/H0Ate3zeuXUvQGzQHeZzs+Ahtx5BzFZa0ghNL1CyyYZLcxNTmsfrugvYAm9roz6qMow5cfxlMNa0aPX.Chs5rJ+qifx+CTgBN7c601lkvwDVl94haeM5plraudk='
token_auth_user = f'AnaplanAuthToken {auth_token}'

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
    model_exports = anaplan_connect_helper_functions.get_exports(wGuid, mGuid, token_auth_user)
    model_exports_data = json.loads(model_exports.text)
except:
    print('ERROR: Unable to get model files.')
if model_exports.status_code == 200:
    print(model_exports_data)
else:
    print('Error: Status Code {}'.format(model_exports.status_code))


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
    print('ERROR: Unable to get model files.')
if chunk_metadata.status_code == 200:
    print(chunk_metadata_data)
else:
    print('Error: Status Code {}'.format(chunk_metadata.status_code))


print('------------------- CHUNK INFO -------------------')
for c in chunk_metadata_data['chunks']:
    print('Chunk name, ID:', c['name'], ',', c['id'])
PYC01_test_chunk_id = '0'
try:
    chunk_data = anaplan_connect_helper_functions.get_chunk_data(wGuid,
                                                                 mGuid,
                                                                 PYC01_test_file_id,
                                                                 PYC01_test_chunk_id,
                                                                 token_auth_user)
    print(chunk_data.url)
    chunk_data_data = json.loads(chunk_data.text)
except:
    print('ERROR: Unable to get specified chunk.')
if chunk_data.status_code == 200:
    print(chunk_data_data)
else:
    print('Error: Status Code {}'.format(chunk_data.status_code))




# print('--------------------------------------------------------------------------------')
# import requests
# PYC01_export_test_id = '116000000000'
#
# print(json.loads(requests.get(f'https://api.anaplan.com/1/3/workspaces/{wGuid}/models/{mGuid}/files/{PYC01_export_test_id}/chunks',
#                    headers={'Authorization': basic_auth_user})).text)



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
