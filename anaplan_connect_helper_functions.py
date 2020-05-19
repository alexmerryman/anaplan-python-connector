import requests
import base64
import json
import re


def anaplan_basic_auth_user(user_email, user_pwd):
    basic_auth_user = 'Basic ' + str(base64.b64encode(f'{user_email}:{user_pwd}'.encode('utf-8')).decode('utf-8'))

    return basic_auth_user


def anaplan_create_token(user_email, user_pwd):
    try:
        token = requests.post("https://auth.anaplan.com/token/authenticate",
                              data={'user': f'{user_email}:{user_pwd}'},
                              auth=(user_email, user_pwd))
    except Exception as e:
        token = None  # TODO?
        print(f"ERROR: Unable to create auth token ({e}).")  # TODO: Refactor the try/except clauses in all helper functions like this

    return token


def anaplan_token_auth_user(token):
    token_auth_user = f'AnaplanAuthToken {token}'
    # print(token_auth_user)
    return token_auth_user


def generate_token_auth_user(user_email, user_pwd):
    token = anaplan_create_token(user_email, user_pwd)
    # print('TOKEN TEXT:', token.text)
    # print('TOKEN STATUS CODE:', token.status_code)
    if token.status_code == 201:
        try:
            token_json = token.json()
            token_val = str(token_json['tokenInfo']['tokenValue'])
        except:
            token_val = None
            print("ERROR: Unable to jsonify token, and/or unable to retrieve ['tokenInfo']['tokenValue'] from token")
        token_auth_user = anaplan_token_auth_user(token_val)
    else:
        print('ERROR: Auth token creation failed - status code:', token.status_code)

    return token_auth_user


def anaplan_token_refresh(token):
    # TODO
    r = requests.post("https://auth.anaplan.com/token/refresh",
                      data={'H'},
                      auth=())
    return r


def get_workspaces(user):
    """
    This script returns all workspaces which `user` has access to.

    If you are using certificate authentication, this script assumes you have converted your Anaplan certificate to
    PEM format, and that you know the Anaplan account email associated with that certificate.

    :param user: (str) Basic authorization user connection string.
    :return: (obj) Requests object containing workspace metadata.
    """
    getHeaders = {
        'Authorization': user
    }

    try:
        workspaces_response = requests.get('https://api.anaplan.com/2/0/workspaces',
                                           headers=getHeaders)
        # print(workspaces_response.status_code)
        workspaces_json = json.loads(workspaces_response.text)
    except:
        print('ERROR: Unable to get workspaces via API.')

    if workspaces_response.status_code == 200:
        return workspaces_response, workspaces_json
    else:
        print('Error: Status Code {}'.format(workspaces_json.status_code))
        return None, None  # TODO


def get_model_info(mGuid, user):
    """
    Returns model info for the selected model to a json array saved in a file 'modelInfo.json'.
    This script assumes you know the modelGuid. If you do not know it, please run 'getModels.py' first.

    :param mGuid: (str) Model ID.
    :param user: (str) Basic authorization user connection string.
    :return: (obj) Requests object containing model info for the selected model.
    """
    getHeaders = {
        'Authorization': user
    }

    try:
        model_info_response = requests.get(f'https://api.anaplan.com/2/0/models/{mGuid}',
                                           headers=getHeaders)
        model_info_json = json.loads(model_info_response.text)
    except:
        print('ERROR: Unable to get model info via API.')

    if model_info_response.status_code == 200:
        return model_info_response, model_info_json
    else:
        print('Error: Status Code {}'.format(model_info_response.status_code))
        return None, None  # TODO


def get_model_imports(wGuid, mGuid, user):
    getHeaders = {
        'Authorization': user
    }

    try:
        model_imports_response = requests.get(f'https://api.anaplan.com/2/0/workspaces/{wGuid}/models/{mGuid}/imports',
                                              headers=getHeaders)
        model_imports_data = json.loads(model_imports_response.text)
    except:
        print('ERROR: Unable to get model imports via API.')

    if model_imports_response.status_code == 200:
        return model_imports_response, model_imports_data
    else:
        print('Error: Status Code {}'.format(model_imports_response.status_code))
        return None, None  # TODO


def get_model_exports(wGuid, mGuid, user):
    getHeaders = {
        'Authorization': user
    }

    try:
        model_exports_response = requests.get(f'https://api.anaplan.com/2/0/workspaces/{wGuid}/models/{mGuid}/exports',
                                              headers=getHeaders)
        model_exports_json = json.loads(model_exports_response.text)
    except:
        print('ERROR: Unable to get model exports via API.')
    if model_exports_response.status_code == 200:
        return model_exports_response, model_exports_json
    else:
        print('Error: Status Code {}'.format(model_exports_response.status_code))
        return None, None  # TODO


def get_export_data(wGuid, mGuid, exportId, user):
    getHeaders = {
        'Authorization': user
    }

    try:
        export_data_response = requests.get(f'https://api.anaplan.com/2/0/workspaces/{wGuid}/models/{mGuid}/exports/{exportId}',
                                            headers=getHeaders)
        export_data_json = json.loads(export_data_response.text)
    except:
        print('ERROR: Unable to get export data via API.')

    if export_data_response.status_code == 200:
        return export_data_response, export_data_json
    else:
        print('Error: Status Code {}'.format(export_data_response.status_code))
        return None, None  # TODO


def post_export_task(wGuid, mGuid, exportId, user):
    post_headers = {'Authorization': user,
                    'Content-Type': 'application/json'
                    }
    try:
        post_export_task_response = requests.post(f'https://api.anaplan.com/2/0/workspaces/{wGuid}/models/{mGuid}/exports/{exportId}/tasks',
                                                  headers=post_headers,
                                                  data=json.dumps({'localeName': 'en_US'}))
        post_export_task_json = json.loads(post_export_task_response.text)
    except:
        print('ERROR: Unable to post export task via API.')

    if post_export_task_response.status_code == 200:
        return post_export_task_response, post_export_task_json
    else:
        print('Error: Status Code {}'.format(post_export_task_response.status_code))
        return None, None  # TODO


def get_export_task_details(wGuid, mGuid, exportId, taskId, user):
    get_headers = {'Authorization': user
                   }
    try:
        task_details_response = requests.get(f'https://api.anaplan.com/2/0/workspaces/{wGuid}/models/{mGuid}/exports/{exportId}/tasks/{taskId}',
                                             headers=get_headers)

        task_details_json = json.loads(task_details_response.text)
    except:
        print('ERROR: Unable to get export task details via API.')

    if task_details_response.status_code == 200:
        return task_details_response, task_details_json
    else:
        print('Error: Status Code {}'.format(task_details_response.status_code))
        return None, None  # TODO


def get_model_files(wGuid, mGuid, user):
    getHeaders = {
        'Authorization': user
    }

    try:
        model_files_response = requests.get(f'https://api.anaplan.com/2/0/workspaces/{wGuid}/models/{mGuid}/files',
                                            headers=getHeaders)
        model_files_json = json.loads(model_files_response.text)
    except:
        print('ERROR: Unable to get model files via API.')

    if model_files_response.status_code == 200:
        return model_files_response, model_files_json
    else:
        print('Error: Status Code {}'.format(model_files_response.status_code))
        return None, None  # TODO


# TODO: Refactor helper function argument names per PEP8
def get_chunk_metadata(wGuid, mGuid, fileID, user):
    """
    Returns the metadata for each chunk in a file.

    :param wGuid:
    :param mGuid:
    :param fileID:
    :param user:
    :return:
    """
    # TODO: Refactor helper function header variable name per PEP8
    getHeaders = {
        'Authorization': user
    }

    try:
        chunk_metadata_response = requests.get('https://api.anaplan.com/2/0/workspaces/'
                                               + f'{wGuid}/models/{mGuid}/files/{fileID}/chunks',
                                               headers=getHeaders)
        chunk_metadata_json = json.loads(chunk_metadata_response.text)
    except:
        print('ERROR: Unable to get file info (chunk metadata) via API.')

    if chunk_metadata_response.status_code == 200:
        return chunk_metadata_response, chunk_metadata_json
    else:
        print('Error: Status Code {}'.format(chunk_metadata_response.status_code))
        return None, None  # TODO


def get_chunk_data(wGuid, mGuid, fileID, chunkID, user):
    """
    Returns the metadata for each chunk in a file.

    :param wGuid:
    :param mGuid:
    :param fileID:
    :param chunkID:
    :param user:
    :return:
    """
    getHeaders = {
        'Authorization': user,
        'Accept': 'application/octet-stream'
    }

    try:
        chunk_data_response = requests.get('https://api.anaplan.com/2/0/workspaces/'
                                           + f'{wGuid}/models/{mGuid}/files/{fileID}/chunks/{chunkID}',
                                           headers=getHeaders)
        chunk_data_text = chunk_data_response.text
    except:
        print('ERROR: Unable to get chunk data via API.')

    if chunk_data_response.status_code == 200:
        return chunk_data_response, chunk_data_text
    else:
        print('Error: Status Code {}'.format(chunk_data_response.status_code))
        return None, None  # TODO


def parse_chunk_data(chunk_data):
    chunk_data_parsed_array = []
    try:
        chunk_data_newline_array = chunk_data.splitlines()
        for s in chunk_data_newline_array:
            chunk_data_parsed_array.append(s.split(','))

    except:
        chunk_data_parsed_array = None  # TODO?

    return chunk_data_parsed_array


def get_model_actions(wGuid, mGuid, user):
    getHeaders = {
        'Authorization': user
    }

    try:
        model_actions_response = requests.get(f'https://api.anaplan.com/2/0/workspaces/{wGuid}/models/{mGuid}/actions',
                                              headers=getHeaders)
        model_actions_json = json.loads(model_actions_response.text)
    except:
        print('ERROR: Unable to get model actions via API.')

    if model_actions_response.status_code == 200:
        return model_actions_response, model_actions_json
    else:
        print('Error: Status Code {}'.format(model_actions_response.status_code))
        return None, None  # TODO


def get_model_processes(wGuid, mGuid, user):
    getHeaders = {
        'Authorization': user
    }

    try:
        model_processes_response = requests.get(f'https://api.anaplan.com/2/0/workspaces/{wGuid}/models/{mGuid}/processes',
                                                headers=getHeaders)
        model_processes_json = json.loads(model_processes_response.text)
    except:
        print('ERROR: Unable to get model processes via API.')

    if model_processes_response.status_code == 200:
        return model_processes_response, model_processes_json
    else:
        print('Error: Status Code {}'.format(model_processes_response.status_code))
        return None, None  # TODO
