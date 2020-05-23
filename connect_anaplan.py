import json
import os
import anaplan_connect_helper_functions
import pandas as pd

# Reference: HTTP Status Codes: https://www.restapitutorial.com/httpstatuscodes.html

# TODO: Describe creds.json schema
def load_creds():
    cred_path = "creds.json"
    if not os.path.isfile(cred_path):
        return None

    creds = json.load(open(cred_path,))
    return creds


# TODO: More robust credentialing, including refreshing the API token instead of re-generating it:

# creds = None
# # The file token.pickle stores the user's access and refresh tokens, and is
# # created automatically when the authorization flow completes for the first
# # time.
# if os.path.exists('token.pickle'):
#     with open('token.pickle', 'rb') as token:
#         creds = pickle.load(token)
# # If there are no (valid) credentials available, let the user log in.
# if not creds or not creds.valid:
#     if creds and creds.expired and creds.refresh_token:
#         creds.refresh(Request())
#     else:
#         flow = InstalledAppFlow.from_client_secrets_file(
#             'credentials.json', SCOPES)
#         creds = flow.run_local_server(port=0)
#     # Save the credentials for the next run
#     with open('token.pickle', 'wb') as token:
#         pickle.dump(creds, token)





# TODO: def main()
# if __name__ == '__main__':
#     main()

san_diego_demo_creds = load_creds()

# manually-generated token: eKZyS21T9Q18E+fUkB+J2g==.m8wRnYs0Sh8Cc/2O6+3yn0E9XpOvFK+C1ZlyBs+sVEKOcPJ8fsNB6oQFIu89E4nYDqwn78bgjKxov6O0vbMkde35/wk3+i0s6t91Ksr44inNc/Y1IANGO6F5ISEix+fJ5oAftTOHbtwzsCIaMaWXWWW+Sx/n3s53f84T7Z4+XdXEEOWIVsQEg5fMc3qDN5Jw3kfewKz24dNAkZK3KJCCN7PIdTs/ZpN9BYTQMLRPTSp7KjbDtM35l+79QmECp2azLWgEheju+pjGg9hjdtbjUO03lZswq8mH7ZCm/ZBdapThHnphyboPGYmUHVhjpL4pNgeaqon1V+k1/kzBLPgpNS8g/M+e2MlcxhhI1T9a3kDcMdDL5s3Al5TtWL0Vby6GTVF8qTfmeDpnq9BZwh7jYB0Twq3Ef3iKSNRmpV4zEjCTYQT7VfBBc++ib+/tuDvefeR4gJD1LjE81Zg+ivm2B0qwciwJm93y+5eMsEZOVApmeXX2rxVTXnGo+ahS2Uts.fAJyUL5OcWCi/7giyD8iCE+Ju0PjP+CQ8zZukoOsmnI=
AS_user_email = san_diego_demo_creds['username']
AS_user_pwd = san_diego_demo_creds['password']

wGuid = san_diego_demo_creds['san-diego-demo']['workspace_id']
mGuid = san_diego_demo_creds['san-diego-demo']['model_id']
anaplan_param_export_id = san_diego_demo_creds['san-diego-demo']['export_id']

# basic_auth_user = anaplan_connect_helper_functions.anaplan_basic_auth_user(AS_user_email, AS_user_pwd)

# TODO: Modularize this -- i.e. main() function should simply connect to Anaplan,
#  then function to get params from get_export,
#  function to run COVID projections w/ params,
#  function to import projections back into Anaplan
# Anaplan API v2.x require token-based authentication rather than basic user:pwd authentication
# (ref: https://anaplanauthentication.docs.apiary.io/#reference/authentication-token)


print('------------------- GENERATING AUTH TOKEN -------------------')
# TODO: Use refresh token method instead of generating new token each time? Are there limits to token generation and/or API calls?

# TODO: Fix token generation ?
manual_token = "eKZyS21T9Q18E+fUkB+J2g==.m8wRnYs0Sh8Cc/2O6+3yn0E9XpOvFK+C1ZlyBs+sVEKOcPJ8fsNB6oQFIu89E4nYDqwn78bgjKxov6O0vbMkde35/wk3+i0s6t91Ksr44inNc/Y1IANGO6F5ISEix+fJ5oAftTOHbtwzsCIaMaWXWWW+Sx/n3s53f84T7Z4+XdXEEOWIVsQEg5fMc3qDN5Jw3kfewKz24dNAkZK3KJCCN7PIdTs/ZpN9BYTQMLRPTSp7KjbDtM35l+79QmECp2azLWgEheju+pjGg9hjdtbjUO03lZswq8mH7ZCm/ZBdapThHnphyboPGYmUHVhjpL4pNgeaqon1V+k1/kzBLPgpNS8g/M+e2MlcxhhI1T9a3kDcMdDL5s3Al5TtWL0Vby6GTVF8qTfmeDpnq9BZwh7jYB0Twq3Ef3iKSNRmpV4zEjCTYQT7VfBBc++ib+/tuDvefeR4gJD1LjE81Zg+ivm2B0qwciwJm93y+5eMsEZOVApmeXX2rxVTXnGo+ahS2Uts.fAJyUL5OcWCi/7giyD8iCE+Ju0PjP+CQ8zZukoOsmnI="
token_auth_user = anaplan_connect_helper_functions.generate_token_auth_user(AS_user_email, AS_user_pwd, token=manual_token)
print(token_auth_user)

print('------------------- GETTING ALL WORKSPACES -------------------')
workspaces_response, workspaces_data_json = anaplan_connect_helper_functions.get_workspaces(token_auth_user)
print(workspaces_data_json)

print('------------------- GETTING MODEL INFO -------------------')
print('Model ID:', mGuid)
model_info_response, model_info_json = anaplan_connect_helper_functions.get_model_info(mGuid, token_auth_user)
print(model_info_json)

print('------------------- GETTING ALL MODEL EXPORTS -------------------')
model_exports_response, model_exports_json = anaplan_connect_helper_functions.get_model_exports(wGuid, mGuid, token_auth_user)
print(model_exports_json)

print('------------------- GETTING EXPORT DATA -------------------')
# ref: https://community.anaplan.com/t5/Best-Practices/RESTful-API-Best-Practices/ta-p/33579 (https://vimeo.com/318242332)
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
    chunk_data_parsed_array = anaplan_connect_helper_functions.parse_chunk_data(chunk_data_text)
    print(chunk_data_parsed_array)


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
