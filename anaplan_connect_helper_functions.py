import requests
import base64
import json
import re


def anaplan_basic_auth_user(user_email, user_pwd):
    basic_auth_user = 'Basic ' + str(base64.b64encode('{}:{}'.format(user_email, user_pwd).encode('utf-8')).decode('utf-8'))

    return basic_auth_user


def anaplan_create_token(user_email, user_pwd):
    try:
        token = requests.post("https://auth.anaplan.com/token/authenticate",
                              data={'user': '{EMAIL}:{PWD}'.format(EMAIL=user_email, PWD=user_pwd)},
                              auth=(user_email, user_pwd))
    except Exception as e:
        token = None  # TODO?
        print("ERROR: Unable to create auth token", e)  # TODO: Refactor the try/except clauses in all helper functions like this

    return token


def anaplan_token_auth_user(token):
    token_auth_user = 'AnaplanAuthToken {}'.format(token)
    # print(token_auth_user)
    return token_auth_user


def generate_token_auth_user(user_email, user_pwd, token=None):
    if token and isinstance(token, str):
        token_val = token
        token_auth_user = anaplan_token_auth_user(token_val)
    else:
        token = anaplan_create_token(user_email, user_pwd)
        # print('TOKEN TEXT:', token.text)
        # print('TOKEN STATUS CODE:', token.status_code)
        if token.status_code == 201:
            try:
                token_json = token.json()
                token_val = str(token_json['tokenInfo']['tokenValue'])
            except Exception as e:
                token_val = None
                print("ERROR: Unable to jsonify token, and/or unable to retrieve ['tokenInfo']['tokenValue'] from token ({}).".format(e))
            token_auth_user = anaplan_token_auth_user(token_val)
        else:
            token_auth_user = None  # TODO
            print('ERROR: Auth token creation failed - status code:', token.status_code)

    return token_auth_user


def anaplan_token_refresh(token):
    # TODO: try/except, if/else error handling
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
        print(workspaces_response.headers)
        print(workspaces_response.url)
        # print(workspaces_response.status_code)
        workspaces_json = json.loads(workspaces_response.text)
    except Exception as e:
        workspaces_response = None  # TODO
        workspaces_json = None  # TODO
        print('ERROR: Unable to get workspaces via API:', e)

    if workspaces_response.status_code == 200:
        return workspaces_response, workspaces_json
    else:
        print('Error: Status Code {}'.format(workspaces_response.status_code))
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
        model_info_response = requests.get('https://api.anaplan.com/2/0/models/{}'.format(mGuid),
                                           headers=getHeaders)
        model_info_json = json.loads(model_info_response.text)
    except:
        model_info_response = None  # TODO
        model_info_json = None  # TODO
        print('ERROR: Unable to get model info via API.')

    if model_info_response.status_code == 200:
        return model_info_response, model_info_json
    else:
        print('Error: Status Code {}'.format(model_info_response.status_code))
        return None, None  # TODO


def get_model_imports(wGuid, mGuid, user):
    """
    Gets the metadata associated for all import actions in the specified model.

    :param wGuid:
    :param mGuid:
    :param user:
    :return:
    """
    getHeaders = {
        'Authorization': user
    }

    try:
        model_imports_response = requests.get('https://api.anaplan.com/2/0/workspaces/{WGUID}/models/{MGUID}/imports'.format(WGUID=wGuid, MGUID=mGuid),
                                              headers=getHeaders)
        model_imports_data = json.loads(model_imports_response.text)
    except:
        model_imports_response = None
        model_imports_data = None  # TODO
        print('ERROR: Unable to get model imports via API.')

    if model_imports_response.status_code == 200:
        return model_imports_response, model_imports_data
    else:
        print('Error: Status Code {}'.format(model_imports_response.status_code))
        return None, None  # TODO


def put_upload_file(wGuid, mGuid, file_id, data_file, user):
    """
    Sets up the upload action in Anaplan -- does not actually execute it.

    :param wGuid:
    :param mGuid:
    :param file_upload_metadata:
    :param data_file:
    :param user:
    :return:
    """
    headers = {
        'Authorization': user,
        'Content-Type': 'application/octet-stream'
    }

    try:
        # TODO: If file is broken into multiple chunks i (larger than 10MB), repeat put request for ".../chunks/{i}"
        put_import_file_response = requests.put('https://api.anaplan.com/2/0/workspaces/{WGUID}/models/{MGUID}/files/{FILEID}'.format(WGUID=wGuid, MGUID=mGuid, FILEID=file_id),
                                                headers=headers,
                                                data=data_file)
        if put_import_file_response.ok:
            print('SUCCESS! File Upload Successful (via Anaplan helper function `put_upload_file()`).')
        else:
            print('Something wrong with file upload (PUT request) - response: {}.'.format(put_import_file_response))
        # put_import_file_data = json.loads(put_import_file_response.text)
    except Exception as e:
        put_import_file_response = None
        put_import_file_data = None  # TODO
        print('ERROR: Unable to put file import via API ({})'.format(e))

    if put_import_file_response.status_code == 204:
        return put_import_file_response #, put_import_file_data
    else:
        print('Error: Status Code {}'.format(put_import_file_response.status_code))
        return None #, None  # TODO


def post_upload_file(wGuid, mGuid, import_id, user):
    """
    Triggers/executes the import action in Anaplan.

    :param wGuid:
    :param mGuid:
    :param import_id:
    :param user:
    :return:
    """
    headers = {
        'Authorization': user,
        'Content-Type': 'application/json'
    }

    try:
        post_import_file_response = requests.post(
            'https://api.anaplan.com/2/0/workspaces/{WGUID}/models/{MGUID}/imports/{IMPORTID}/tasks/'.format(WGUID=wGuid,
                                                                                                             MGUID=mGuid,
                                                                                                             IMPORTID=import_id),
                                                  headers=headers,
                                                  data=json.dumps({'localeName': 'en_US'}))
        # print(post_import_file_response.url)
        post_import_file_data = json.loads(post_import_file_response.text)
    except Exception as e:
        post_import_file_response = None
        post_import_file_data = None  # TODO
        print('ERROR: Unable to post/execute file import via API ({})'.format(e))

    if post_import_file_response.status_code == 200:
        return post_import_file_response, post_import_file_data
    else:
        print('Error: Status Code {}'.format(post_import_file_response.status_code))
        return None, None  # TODO


def post_import_process(wGuid, mGuid, process_id, user):
    headers = {
        'Authorization': user,
        'Content-Type': 'application/json'
    }

    try:
        post_import_process_response = requests.post(
            'https://api.anaplan.com/2/0/workspaces/{WGUID}/models/{MGUID}/processes/{PROCESSID}/tasks/'.format(WGUID=wGuid,
                                                                                                                MGUID=mGuid,
                                                                                                                PROCESSID=process_id),
            headers=headers,
            data=json.dumps({'localeName': 'en_US'}))

        print(post_import_process_response.url)
        post_import_process_data = json.loads(post_import_process_response.text)
    except Exception as e:
        post_import_process_response = None
        post_import_process_data = None  # TODO
        print('ERROR: Unable to post/execute file import via API ({})'.format(e))

    if post_import_process_response.status_code == 200:
        return post_import_process_response, post_import_process_data
    else:
        print('Error: Status Code {}'.format(post_import_process_response.status_code))
        return None, None  # TODO


def get_model_exports(wGuid, mGuid, user):
    getHeaders = {
        'Authorization': user
    }

    try:
        model_exports_response = requests.get('https://api.anaplan.com/2/0/workspaces/{WGUID}/models/{MGUID}/exports'.format(WGUID=wGuid, MGUID=mGuid),
                                              headers=getHeaders)
        model_exports_json = json.loads(model_exports_response.text)
    except:
        model_exports_response = None  # TODO
        model_exports_json = None  # TODO
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
        export_data_response = requests.get('https://api.anaplan.com/2/0/workspaces/{WGUID}/models/{MGUID}/exports/{EXPORTID}'.format(WGUID=wGuid, MGUID=mGuid, EXPORTID=exportId),
                                            headers=getHeaders)
        export_data_json = json.loads(export_data_response.text)
    except:
        export_data_response = None  # TODO
        export_data_json = None  # TODO
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
        post_export_task_response = requests.post('https://api.anaplan.com/2/0/workspaces/{WGUID}/models/{MGUID}/exports/{EXPORTID}/tasks'.format(WGUID=wGuid, MGUID=mGuid, EXPORTID=exportId),
                                                  headers=post_headers,
                                                  data=json.dumps({'localeName': 'en_US'}))
        post_export_task_json = json.loads(post_export_task_response.text)
    except:
        post_export_task_response = None  # TODO
        post_export_task_json = None  # TODO
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
        task_details_response = requests.get('https://api.anaplan.com/2/0/workspaces/{WGUID}/models/{MGUID}/exports/{EXPORTID}/tasks/{TASKID}'.format(WGUID=wGuid, MGUID=mGuid, EXPORTID=exportId, TASKID=taskId),
                                             headers=get_headers)

        task_details_json = json.loads(task_details_response.text)
    except:
        task_details_response = None  # TODO
        task_details_json = None  # TODO
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
        model_files_response = requests.get('https://api.anaplan.com/2/0/workspaces/{WGUID}/models/{MGUID}/files'.format(WGUID=wGuid, MGUID=mGuid),
                                            headers=getHeaders)
        model_files_json = json.loads(model_files_response.text)
    except:
        model_files_response = None  # TODO
        model_files_json = None  # TODO
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
        chunk_metadata_response = requests.get('https://api.anaplan.com/2/0/workspaces/{WGUID}/models/{MGUID}/files/{FILEID}/chunks'.format(WGUID=wGuid, MGUID=mGuid, FILEID=fileID),
                                               headers=getHeaders)
        chunk_metadata_json = json.loads(chunk_metadata_response.text)
    except:
        chunk_metadata_response = None  # TODO
        chunk_metadata_json = None  # TODO
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
        chunk_data_response = requests.get('https://api.anaplan.com/2/0/workspaces/{WGUID}/models/{MGUID}/files/{FILEID}/chunks/{CHUNKID}'.format(WGUID=wGuid, MGUID=mGuid, FILEID=fileID, CHUNKID=chunkID),
                                           headers=getHeaders)
        chunk_data_text = chunk_data_response.text
    except Exception as e:
        chunk_data_response = None  # TODO
        chunk_data_text = None  # TODO
        print('ERROR: Unable to get chunk data via API ({})'.format(e))

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

    except Exception as e:
        print('Error: Unable to parse params from Anaplan ({})'.format(e))
        chunk_data_parsed_array = None  # TODO?

    return chunk_data_parsed_array


def get_model_actions(wGuid, mGuid, user):
    getHeaders = {
        'Authorization': user
    }

    try:
        model_actions_response = requests.get('https://api.anaplan.com/2/0/workspaces/{WGUID}/models/{MGUID}/actions'.format(WGUID=wGuid, MGUID=mGuid),
                                              headers=getHeaders)
        model_actions_json = json.loads(model_actions_response.text)
    except:
        model_actions_response = None  # TODO
        model_actions_json = None  # TODO
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
        model_processes_response = requests.get('https://api.anaplan.com/2/0/workspaces/{WGUID}/models/{MGUID}/processes'.format(WGUID=wGuid, MGUID=mGuid),
                                                headers=getHeaders)
        model_processes_json = json.loads(model_processes_response.text)
    except:
        model_processes_response = None  # TODO
        model_processes_json = None  # TODO
        print('ERROR: Unable to get model processes via API.')

    if model_processes_response.status_code == 200:
        return model_processes_response, model_processes_json
    else:
        print('Error: Status Code {}'.format(model_processes_response.status_code))
        return None, None  # TODO
