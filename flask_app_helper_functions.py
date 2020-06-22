import anaplan_connect_helper_functions


def anaplan_list_workspaces(auth_token):
    workspaces_response, workspaces_json = anaplan_connect_helper_functions.get_workspaces(auth_token)
    # workspaces_dict = {}
    # for i in workspaces_json['workspaces']:
    #     workspaces_dict[i['name']] = i['id']
    return workspaces_json['workspaces']


def anaplan_list_models(workspace_id, auth_token):
    # TODO
    pass


def anaplan_list_exports(workspace_id, model_id, auth_token):
    model_exports_response, model_exports_json = anaplan_connect_helper_functions.get_model_exports(workspace_id, model_id, auth_token)
    return model_exports_json['exports']


def anaplan_list_files():
    pass


def anaplan_list_imports():
    pass


def anaplan_get_user_trigger_status(auth_token, creds, verbose=False):
    wGuid = creds['san-diego-demo']['workspace_id']
    mGuid = creds['san-diego-demo']['model_id']
    user_trigger_export_id = creds['san-diego-demo']['user_trigger_export_id']

    if verbose:
        print('------------------- GETTING PARAMS FILE INFO (CHUNK METADATA) -------------------')
    chunk_metadata_response, chunk_metadata_json = anaplan_connect_helper_functions.get_chunk_metadata(wGuid, mGuid,
                                                                                                       user_trigger_export_id,
                                                                                                       auth_token)
    if verbose:
        print(chunk_metadata_json)

    if verbose:
        print('------------------- GETTING PARAMS CHUNK DATA -------------------')
        print('Total number of chunks: {}'.format(len(chunk_metadata_json['chunks'])))

    # if len(chunk_metadata_json['chunks']) == 1:
    chunk_data_response, chunk_data_text = anaplan_connect_helper_functions.get_chunk_data(wGuid, mGuid,
                                                                                           user_trigger_export_id,
                                                                                           chunk_metadata_json['chunks'][0]['id'],
                                                                                           auth_token)
    chunk_data_parsed = anaplan_connect_helper_functions.parse_chunk_data(chunk_data_text)

    # print(chunk_data_text)
    # print(chunk_data_parsed)
    # print(chunk_data_parsed[1][1])

    user_trigger_status = chunk_data_parsed[1][1] == 'true'
    print("user_trigger_status == 'true'?\t", user_trigger_status == 'true')

    return user_trigger_status
    # TODO: Reset the state of the trigger to False
