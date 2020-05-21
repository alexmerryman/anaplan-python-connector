import json
import anaplan_connect_helper_functions
import pandas as pd

# Ref: HTTP Status Codes: https://www.restapitutorial.com/httpstatuscodes.html

# TODO: Refactor credentials -- put in cred.csv/json file, add that file to .gitignore
# Insert your workspace Guid
wGuid = '8a81b08e4f6d2b43014fbe11122a160c'

# Insert your model Guid
mGuid = '96339A3A48394142A3E70E057F75480E'

AS_user_email = 'Anthony.Severini@teklink.com'
AS_user_pwd = 'Steelerssoccera1219_1'
basic_auth_user = anaplan_connect_helper_functions.anaplan_basic_auth_user(AS_user_email, AS_user_pwd)

# TODO: Modularize this -- i.e. main() function should simply connect to Anaplan,
#  then function to get params from get_export,
#  function to run COVID projections w/ params,
#  function to import projections back into Anaplan
# Anaplan API v2.x require token-based authentication rather than basic user:pwd authentication
# (ref: https://anaplanauthentication.docs.apiary.io/#reference/authentication-token)


print('------------------- GENERATING AUTH TOKEN -------------------')
# TODO: Use refresh token method instead of generating new token each time? Are there limits to token generation and/or API calls?
token_auth_user = anaplan_connect_helper_functions.generate_token_auth_user(AS_user_email, AS_user_pwd)
print(token_auth_user)

print('------------------- GETTING ALL WORKSPACES -------------------')
workspaces_response, workspaces_data_json = anaplan_connect_helper_functions.get_workspaces(token_auth_user)
print(workspaces_data_json)

print('------------------- GETTING MODEL INFO -------------------')
print(f'Model ID: {mGuid}')
model_info_response, model_info_json = anaplan_connect_helper_functions.get_model_info(mGuid, token_auth_user)
print(model_info_json)

print('------------------- GETTING ALL MODEL EXPORTS -------------------')
model_exports_response, model_exports_json = anaplan_connect_helper_functions.get_model_exports(wGuid, mGuid, token_auth_user)
print(model_exports_json)

print('------------------- GETTING EXPORT DATA -------------------')
# TODO: blocked by inadequate schema in Anaplan (for test table)
# ref: https://community.anaplan.com/t5/Best-Practices/RESTful-API-Best-Practices/ta-p/33579 (https://vimeo.com/318242332)
anaplan_param_export_id = '116000000005'
anaplan_param_export_response, anaplan_param_export_data_json = anaplan_connect_helper_functions.get_export_data(wGuid, mGuid, anaplan_param_export_id, token_auth_user)
print(anaplan_param_export_data_json['exportMetadata']['headerNames'])
print(anaplan_param_export_data_json['exportMetadata']['dataTypes'])
print(anaplan_param_export_data_json['exportMetadata']['rowCount'])
print(anaplan_param_export_data_json['exportMetadata']['exportFormat'])
print(anaplan_param_export_data_json['exportMetadata']['delimiter'])

print('------------------- CREATING (POST) EXPORT TASK -------------------')
anaplan_param_export_task_response, anaplan_param_export_task_json = anaplan_connect_helper_functions.post_export_task(wGuid, mGuid, anaplan_param_export_id, token_auth_user)
print(anaplan_param_export_task_json)
print(anaplan_param_export_task_json['task']['taskId'])
print(anaplan_param_export_task_json['task']['taskState'])

print('------------------- GETTING EXPORT TASK DETAILS -------------------')
anaplan_param_export_task_details_response, anaplan_param_export_task_details_json = anaplan_connect_helper_functions.get_export_task_details(wGuid, mGuid, anaplan_param_export_id, anaplan_param_export_task_json['task']['taskId'], token_auth_user)
print(anaplan_param_export_task_details_json)
print(anaplan_param_export_task_details_json['task']['taskState'])

# Once 'taskState' == 'COMPLETE', run get_files()
print('------------------- GETTING ALL MODEL FILES -------------------')
model_files__response, model_files_json = anaplan_connect_helper_functions.get_model_files(wGuid, mGuid, token_auth_user)
print(model_files_json)
# Then, get all chunks

print('------------------- GETTING FILE INFO (CHUNK METADATA) -------------------')
chunk_metadata_response, chunk_metadata_json = anaplan_connect_helper_functions.get_chunk_metadata(wGuid, mGuid, anaplan_param_export_id, token_auth_user)
print(chunk_metadata_json)

print('------------------- GETTING CHUNK DATA -------------------')
for c in chunk_metadata_json['chunks']:
    print('Chunk name, ID:', c['name'], ',', c['id'])
    chunk_data_response, chunk_data_text = anaplan_connect_helper_functions.get_chunk_data(wGuid, mGuid, anaplan_param_export_id, c['id'], token_auth_user)
    # print(chunk_data.url)
    # print(chunk_data.status_code)
    # print(chunk_data_text)
    anaplan_connect_helper_functions.parse_chunk_data(chunk_data_text)


# print('------------------- ALL MODEL IMPORTS -------------------')
# model_files__response, model_imports_json = anaplan_connect_helper_functions.get_model_imports(wGuid, mGuid, token_auth_user)
# print(model_imports_json)
# print('------------------- MODEL ACTIONS -------------------')
# model_actions_response, model_actions_json = anaplan_connect_helper_functions.get_actions(wGuid, mGuid, basic_auth_user)
# print(model_actions_json)
#
# print('------------------- MODEL PROCESSES -------------------')
# model_processes_response, model_processes_json = anaplan_connect_helper_functions.get_processes(wGuid, mGuid, basic_auth_user)
# print(model_processes_json)
