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


