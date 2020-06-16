import os
import json
import requests
import numpy as np
import pandas as pd
import datetime
import anaplan_connect_helper_functions
import model_covid


def load_creds():
    """
    creds.json schema:
    {
    "username": "user@domain.com",
    "password": "password",
    "`project-name`": {
        "workspace_id": "xxxxxxxxxxxxxxxxxxx", -- easiest to get these id's from Postman
        "model_id": "xxxxxxxxxxxxxxxxxxx",
        "df_export_id": "xxxxxxxxxxxxxxxxxxx",
        "params_export_id": "xxxxxxxxxxxxxxxxxxx",
        "predictions_file_id": "xxxxxxxxxxxxxxxxxxx",
        "predictions_import_id": "xxxxxxxxxxxxxxxxxxx",
        }
    }

    Since `creds.json` is in .gitignore, create the file in your local copy of the project when you clone it.

    :return: creds (dict): Contains relevant credentials for logging into Anaplan and creating a token to access the API
    """

    # TODO: The user won't know export_id, file_id, or import_id's
    cred_path = "creds.json"
    if not os.path.isfile(cred_path):
        print('ERROR: No file called `creds.json` found in the path.')
        return None

    creds = json.load(open(cred_path,))
    return creds


def anaplan_get_export_params(auth_token, verbose=False):
    # TODO: try/except?
    if verbose:
        print('Loading Anaplan credential from creds.json')
    san_diego_demo_creds = load_creds()

    wGuid = san_diego_demo_creds['san-diego-demo']['workspace_id']
    mGuid = san_diego_demo_creds['san-diego-demo']['model_id']
    param_export_id = san_diego_demo_creds['san-diego-demo']['params_export_id']

    if verbose:
        print('------------------- GETTING PARAMS EXPORT DATA -------------------')
    # ref: https://community.anaplan.com/t5/Best-Practices/RESTful-API-Best-Practices/ta-p/33579 (https://vimeo.com/318242332)
    anaplan_param_export_response, anaplan_param_export_data_json = anaplan_connect_helper_functions.get_export_data(
        wGuid, mGuid, param_export_id, auth_token)
    # if verbose:
    #     print(anaplan_param_export_data_json['exportMetadata']['headerNames'])
    #     print(anaplan_param_export_data_json['exportMetadata']['dataTypes'])
    #     print(anaplan_param_export_data_json['exportMetadata']['rowCount'])
    #     print(anaplan_param_export_data_json['exportMetadata']['exportFormat'])
    #     print(anaplan_param_export_data_json['exportMetadata']['delimiter'])

    if verbose:
        print('------------------- CREATING PARAMS (POST) EXPORT TASK -------------------')
    anaplan_param_export_task_response, anaplan_param_export_task_json = anaplan_connect_helper_functions.post_export_task(wGuid, mGuid, param_export_id, auth_token)


    # Then, get all chunks
    if verbose:
        print('------------------- GETTING PARAMS FILE INFO (CHUNK METADATA) -------------------')
    chunk_metadata_response, chunk_metadata_json = anaplan_connect_helper_functions.get_chunk_metadata(wGuid, mGuid, param_export_id, auth_token)
    if verbose:
        print(chunk_metadata_json)

    if verbose:
        print('------------------- GETTING PARAMS CHUNK DATA -------------------')
        print('Total number of chunks: {}'.format(len(chunk_metadata_json['chunks'])))

    if len(chunk_metadata_json['chunks']) == 1:
        chunk_data_response, chunk_data_text = anaplan_connect_helper_functions.get_chunk_data(wGuid, mGuid,
                                                                                               param_export_id, chunk_metadata_json['chunks'][0]['id'],
                                                                                               auth_token)
        chunk_data_parsed = anaplan_connect_helper_functions.parse_chunk_data(chunk_data_text)
        # if verbose:
        #     print(chunk_data_parsed)

        return chunk_data_parsed

    else:
        all_param_chunk_data = []
        for c in chunk_metadata_json['chunks']:
            # if verbose:
            #     print('Chunk name, ID:', c['name'], ',', c['id'])
            chunk_data_response, chunk_data_text = anaplan_connect_helper_functions.get_chunk_data(wGuid, mGuid, param_export_id, c['id'], auth_token)
            # print(chunk_data.url)
            # print(chunk_data.status_code)
            # print(chunk_data_text)
            chunk_data_parsed = anaplan_connect_helper_functions.parse_chunk_data(chunk_data_text)
            # if verbose:
            #     print(chunk_data_parsed)
            all_param_chunk_data.append(chunk_data_parsed)

        return all_param_chunk_data


def main(verbose=True):
    san_diego_demo_creds = load_creds()
    san_diego_demo_email = san_diego_demo_creds['username']
    san_diego_demo_pwd = san_diego_demo_creds['password']

    wGuid = san_diego_demo_creds['san-diego-demo']['workspace_id']
    mGuid = san_diego_demo_creds['san-diego-demo']['model_id']
    predictions_file_id = san_diego_demo_creds['san-diego-demo']['predictions_file_id']
    predictions_import_id = san_diego_demo_creds['san-diego-demo']['predictions_import_id']

    # TODO: Store token somewhere, and if it expires, refresh it?
    token_generated = anaplan_connect_helper_functions.anaplan_create_token(san_diego_demo_email, san_diego_demo_pwd)
    token_auth_user = anaplan_connect_helper_functions.generate_token_auth_user(san_diego_demo_email, san_diego_demo_pwd, token=token_generated)

    params_chunks_unparsed = anaplan_get_export_params(token_auth_user, verbose=verbose)
    return params_chunks_unparsed
