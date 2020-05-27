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
    "san-diego-demo": {
        "workspace_id": "xxxxxxxxxxxxxxxxxxx",
        "model_id": "xxxxxxxxxxxxxxxxxxx",
        "export_id": "xxxxxxxxxxxxxxxxxxx"
        }
    }

    Since `creds.json` is in .gitignore, create the file in your local copy of the project when you clone it.

    :return: creds (dict): Contains relevant credentials for logging into Anaplan and creating a token to access the API
    """
    cred_path = "creds.json"
    if not os.path.isfile(cred_path):
        print('ERROR: No file called `creds.json` found in the path.')
        return None

    creds = json.load(open(cred_path,))
    return creds


# TODO: More robust credentialing, including refreshing the API token instead of re-generating it:
# The time.time() function returns the number of seconds since the epoch, as seconds

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


def anaplan_connect_get_params(auth_token, verbose=False):
    # TODO: try/except?
    if verbose:
        print('Loading Anaplan credential from creds.json')
    san_diego_demo_creds = load_creds()
    # san_diego_demo_email = san_diego_demo_creds['username']
    # san_diego_demo_pwd = san_diego_demo_creds['password']

    wGuid = san_diego_demo_creds['san-diego-demo']['workspace_id']
    mGuid = san_diego_demo_creds['san-diego-demo']['model_id']
    param_export_id = san_diego_demo_creds['san-diego-demo']['export_id']

    # if verbose:
    #     print('------------------- GENERATING AUTH TOKEN -------------------')
    # # TODO: Store token somewhere, and if it expires, refresh it?
    # token_generated = anaplan_connect_helper_functions.anaplan_create_token(san_diego_demo_email, san_diego_demo_pwd)
    # if verbose:
    #     print(token_generated)
    # token_auth_user = anaplan_connect_helper_functions.generate_token_auth_user(san_diego_demo_email, san_diego_demo_pwd, token=token_generated)


    if verbose:
        print('IMPORTS')
    model_imports_response, model_imports_data = anaplan_connect_helper_functions.get_model_imports(wGuid, mGuid, auth_token)
    if verbose:
        print(model_imports_response)
        print(model_imports_data)


    if verbose:
        print('------------------- GETTING EXPORT DATA -------------------')
    # ref: https://community.anaplan.com/t5/Best-Practices/RESTful-API-Best-Practices/ta-p/33579 (https://vimeo.com/318242332)
    anaplan_param_export_response, anaplan_param_export_data_json = anaplan_connect_helper_functions.get_export_data(
        wGuid, mGuid, param_export_id, auth_token)
    if verbose:
        print(anaplan_param_export_data_json['exportMetadata']['headerNames'])
        print(anaplan_param_export_data_json['exportMetadata']['dataTypes'])
        print(anaplan_param_export_data_json['exportMetadata']['rowCount'])
        print(anaplan_param_export_data_json['exportMetadata']['exportFormat'])
        print(anaplan_param_export_data_json['exportMetadata']['delimiter'])

    if verbose:
        print('------------------- CREATING (POST) EXPORT TASK -------------------')
    anaplan_param_export_task_response, anaplan_param_export_task_json = anaplan_connect_helper_functions.post_export_task(wGuid, mGuid, param_export_id, auth_token)
    if verbose:
        print(anaplan_param_export_task_json)
        print(anaplan_param_export_task_json['task']['taskId'])
        print(anaplan_param_export_task_json['task']['taskState'])

    if verbose:
        print('------------------- GETTING EXPORT TASK DETAILS -------------------')
    anaplan_param_export_task_details_response, anaplan_param_export_task_details_json = anaplan_connect_helper_functions.get_export_task_details(wGuid, mGuid, param_export_id, anaplan_param_export_task_json['task']['taskId'], auth_token)
    if verbose:
        print(anaplan_param_export_task_details_json)
        print(anaplan_param_export_task_details_json['task']['taskState'])

    # Once 'taskState' == 'COMPLETE', run get_files()
    if verbose:
        print('------------------- GETTING ALL MODEL FILES -------------------')
    model_files__response, model_files_json = anaplan_connect_helper_functions.get_model_files(wGuid, mGuid, auth_token)
    if verbose:
        print(model_files_json)

    # TODO: The below steps are all that are necessary? Eliminate helper function steps above? How to verify
    #  connection is successful, connects to correct workspace/model, files are there, etc?
    # Then, get all chunks
    if verbose:
        print('------------------- GETTING FILE INFO (CHUNK METADATA) -------------------')
    chunk_metadata_response, chunk_metadata_json = anaplan_connect_helper_functions.get_chunk_metadata(wGuid, mGuid, param_export_id, auth_token)
    if verbose:
        print(chunk_metadata_json)

    if verbose:
        print('------------------- GETTING CHUNK DATA -------------------')
    all_chunk_data = []
    for c in chunk_metadata_json['chunks']:
        if verbose:
            print('Chunk name, ID:', c['name'], ',', c['id'])
        chunk_data_response, chunk_data_text = anaplan_connect_helper_functions.get_chunk_data(wGuid, mGuid, param_export_id, c['id'], auth_token)
        # print(chunk_data.url)
        # print(chunk_data.status_code)
        # print(chunk_data_text)
        chunk_data_parsed = anaplan_connect_helper_functions.parse_chunk_data(chunk_data_text)
        if verbose:
            print(chunk_data_parsed)
        all_chunk_data.append(chunk_data_parsed)

    return all_chunk_data


def parse_chunk_data(chunk_data):
    # TODO: Parse chunk data into individual params -- variables to plug into CurveFit model?
    return None


def validate_params(params):
    # TODO: make sure the df & other params are in the proper format to plug into model_covid.py
    return None


def anaplan_import_data(verbose=False):
    # TODO: try/except?
    if verbose:
        print('Loading Anaplan credential from creds.json')
    san_diego_demo_creds = load_creds()
    san_diego_demo_email = san_diego_demo_creds['username']
    san_diego_demo_pwd = san_diego_demo_creds['password']

    wGuid = san_diego_demo_creds['san-diego-demo']['workspace_id']
    mGuid = san_diego_demo_creds['san-diego-demo']['model_id']
    import_id = san_diego_demo_creds['san-diego-demo']['import_id']
    file_id = san_diego_demo_creds['san-diego-demo']['file_id']


def main(sim_data=False, verbose=False):
    # TODO: Take additional args? arg1, arg2, arg3, etc...
    # TODO: Add dry_run functionality?
    """
    # TODO: Update these steps:
    Run get_anaplan_params.py
    Parse chunk_data_parsed_array (set var name = its accompanying value)
    Plug vars into curvefit model (COVID deaths?)
    Get resulting projections (as CSV?)
    Import projections back into Anaplan.

    :param verbose:
    :param arg1:
    :param arg2:
    :param arg3:
    :param etc:
    :param sim_data:
    :return:
    """
    if verbose:
        print('Loading Anaplan credential from creds.json')
    san_diego_demo_creds = load_creds()
    san_diego_demo_email = san_diego_demo_creds['username']
    san_diego_demo_pwd = san_diego_demo_creds['password']

    wGuid = san_diego_demo_creds['san-diego-demo']['workspace_id']
    mGuid = san_diego_demo_creds['san-diego-demo']['model_id']
    param_export_id = san_diego_demo_creds['san-diego-demo']['export_id']
    import_id = san_diego_demo_creds['san-diego-demo']['import_id']
    file_id = san_diego_demo_creds['san-diego-demo']['file_id']

    token_generated = anaplan_connect_helper_functions.anaplan_create_token(san_diego_demo_email, san_diego_demo_pwd)
    token_auth_user = anaplan_connect_helper_functions.generate_token_auth_user(san_diego_demo_email, san_diego_demo_pwd, token=token_generated)

    if sim_data:
        if verbose:
            print('No data provided; using simulated data.')
        # Create example data -- both death rate and log death rate
        np.random.seed(1234)

        df = pd.DataFrame()
        df['time'] = np.arange(100)
        df['death_rate'] = np.exp(.1 * (df.time - 20)) / (1 + np.exp(.1 * (df.time - 20))) + \
                           np.random.normal(0, 0.1, size=100).cumsum()
        df['ln_death_rate'] = np.log(df['death_rate'])
        df['group'] = 'all'
        df['intercept'] = 1.0  # Default to 1.0 ?

    else:
        if verbose:
            print('Connecting to Anaplan to get data/params.')
        # get data from Anaplan
        chunks_unparsed = anaplan_connect_get_params(token_auth_user, verbose=verbose)
        params = parse_chunk_data(chunks_unparsed)

        df = params['df']  # TODO ? Ref CurveFit documentation to determine what parameters to pass/include
        df['ln_death_rate'] = np.log(df['death_rate'])  # TODO
        df['group'] = 'all'  # TODO
        df['intercept'] = 1.0  # Default to 1.0 ?  # TODO

    # if not validate_params(params):
    #     # TODO: something here to raise an exception/alert the user that the params are in an invalid format
    #     raise

    model_args_dict = {
        'df': df,
        'col_t': 'time',
        'col_obs': 'ln_death_rate',
        'col_group': 'group',
        'col_covs': [['intercept'], ['intercept'], ['intercept']],
        'param_names': ['alpha', 'beta', 'p'],
        'link_fun': [lambda x: x, lambda x: x, lambda x: x],
        'var_link_fun': [lambda x: x, lambda x: x, lambda x: x],
        # 'fun': ln_gaussian_cdf,  # TODO -- must import ln_gaussian_cdf here? model_covid.py cannot parse a string value here -- must be the function/object from curvefit.core.functions
        'fe_init': [0, 0, 1.],
        'fe_gprior': [[0, np.inf], [0, np.inf], [1., np.inf]]
    }

    model, predictions = model_covid.fit_model_predict(model_args_dict, verbose=verbose, charts=False)

    pred_timestamp = datetime.datetime.now().strftime('%Y-%m-%d')

    # Save predictions df locally as CSV
    pd.DataFrame.to_csv(predictions, "covid_predictions_{TIME}.csv".format(TIME=pred_timestamp), index=False)

    # Import predictions csv into Anaplan
    import_file = "*.csv"

    model_imports_response, model_imports_data = anaplan_connect_helper_functions.post_model_imports(wGuid, mGuid, file_id, token_auth_user)
    print(model_imports_response)
    print(model_imports_data)
    # Once import is complete, delete the .\temp directory



if __name__ == "__main__":
    main(sim_data=True, verbose=True)



# tokenval = "grgB1qsg0yQk9igW3cHfmA==.XCzGjQehSMhl/KIyBSWTe0VBr0eqyp+yVQzDCorn5lqatXqLH8I2APF8WrxY0x7qOnL6jjhth14sGSFAm9EBRj4K9RovsmvGeqEEo8Qn9L3CBV1OZ3C3vSFGxYZHKeDFFz0xA4xzMXvetPN35Xi4EIxoRc8ypYMUNo7zlIZrHkLYT7bMCW4PJBW19nllg5ZPjSE7EWQTjj2x+jQrWxRoza39Y6Pwtl9pMRq/W3Zfy2ExS6bWT+iWty2VGK0uSuwmA4nCW7Uae8t5ZOvfWKIyq8QUb3eovDzVg5rCT0cKTkfN5LWE2bvqzyOBIRzREhS3zbjrJaO+zJ6xcQv7e6D3M/t1v+csZIYP9M3a2hTFNchiix42asF1yfeGGojOyDd2QondpEF0qOOeoh+G5v2kxkUsGGPUbWeuOCldsmswH+zdl/wZYQSiycBvJA1HiawhTttx6I/n5eqCG8GDJHVYaZCsTzcr+UHXSPgMAEPaMrNIjZ7dL2/kITrDpGbLj+nB.DQIw0cO3YLxFsXlxiTfDC3mdN9kVm+XFUDvKahHwUVs="
# token_auth_user = anaplan_connect_helper_functions.anaplan_token_auth_user(tokenval)
# wGuid = "8a81b08e4f6d2b43014fbe11122a160c"
# mGuid = "96339A3A48394142A3E70E057F75480E"
#
# model_imports_response, model_imports_data = anaplan_connect_helper_functions.get_model_imports(wGuid, mGuid, token_auth_user)
# print(model_imports_response)
# print(model_imports_data)
#
# model_files_response, model_files_json = anaplan_connect_helper_functions.get_model_files(wGuid, mGuid, token_auth_user)
# print(model_files_json)
# # covid_preds_file_id = "113000000021"

# TODO: Set up Flask instance to run this from Anaplan -- trigger via button
