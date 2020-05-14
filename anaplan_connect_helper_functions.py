import requests
import base64


def anaplan_basic_auth_user(user_email, user_pwd):
    basic_auth_user = 'Basic ' + str(base64.b64encode(f'{user_email}:{user_pwd}'.encode('utf-8')).decode('utf-8'))

    return basic_auth_user


def get_workspaces(user):
    """
    This script returns all workspaces the `user` has access to.

    If you are using certificate authentication, this script assumes you have converted your Anaplan certificate to
    PEM format, and that you know the Anaplan account email associated with that certificate.

    :param user: (str) Basic authorization user connection string.
    :return: (obj) Requests object containing workspace metadata.
    """
    getHeaders = {
        'Authorization': user
    }

    workspaces = requests.get('https://api.anaplan.com/1/3/workspaces',
                              headers=getHeaders)

    return workspaces


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

    model_info = requests.get(f'https://api.anaplan.com/1/3/models/{mGuid}',
                              headers=getHeaders)

    return model_info


def get_model_files(wGuid, mGuid, user):
    getHeaders = {
        'Authorization': user
    }

    model_files = requests.get(f'https://api.anaplan.com/1/3/workspaces/{wGuid}/' + f'models/{mGuid}/files',
                               headers=getHeaders)

    return model_files


def get_chunk_data(wGuid, mGuid, fileID, user):
    """
    Returns the metadata for each chunk in a file.

    :param wGuid:
    :param mGuid:
    :param fileID:
    :param user:
    :return:
    """
    getHeaders = {
        'Authorization': user
    }

    chunk_data = requests.get('https://api.anaplan.com/1/3/workspaces/'
                              + f'{wGuid}/models/{mGuid}/files/{fileID}' + '/chunks',
                              headers=getHeaders)

    return chunk_data


def get_imports(wGuid, mGuid, user):
    getHeaders = {
        'Authorization': user
    }

    model_imports = requests.get(f'https://api.anaplan.com/1/3/workspaces/{wGuid}/' + f'models/{mGuid}/imports',
                                 headers=getHeaders)

    return model_imports


def get_exports(wGuid, mGuid, user):
    getHeaders = {
        'Authorization': user
    }

    model_exports = requests.get(f'https://api.anaplan.com/1/3/workspaces/{wGuid}/' + f'models/{mGuid}/exports',
                                 headers=getHeaders)

    return model_exports


def get_actions(wGuid, mGuid, user):
    getHeaders = {
        'Authorization': user
    }

    model_actions = requests.get(f'https://api.anaplan.com/1/3/workspaces/{wGuid}/' + f'models/{mGuid}/actions',
                                 headers=getHeaders)

    return model_actions


def get_processes(wGuid, mGuid, user):
    getHeaders = {
        'Authorization': user
    }

    model_processes = requests.get(f'https://api.anaplan.com/1/3/workspaces/{wGuid}/' + f'models/{mGuid}/processes',
                                   headers=getHeaders)

    return model_processes

