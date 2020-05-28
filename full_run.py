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
    "`project`": {
        "workspace_id": "xxxxxxxxxxxxxxxxxxx",
        "model_id": "xxxxxxxxxxxxxxxxxxx",
        "export_id": "xxxxxxxxxxxxxxxxxxx"
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


# TODO: More robust credentialing, including refreshing the API token instead of re-generating it:
# Use: The time.time() function returns the number of seconds since the epoch, as seconds.

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


def anaplan_get_export_params(auth_token, verbose=False):
    # TODO: try/except?
    if verbose:
        print('Loading Anaplan credential from creds.json')
    san_diego_demo_creds = load_creds()
    # san_diego_demo_email = san_diego_demo_creds['username']
    # san_diego_demo_pwd = san_diego_demo_creds['password']

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
    # if verbose:
    #     print(anaplan_param_export_task_json)
    #     print(anaplan_param_export_task_json['task']['taskId'])
    #     print(anaplan_param_export_task_json['task']['taskState'])

    # if verbose:
    #     print('------------------- GETTING EXPORT TASK DETAILS -------------------')
    # anaplan_param_export_task_details_response, anaplan_param_export_task_details_json = anaplan_connect_helper_functions.get_export_task_details(wGuid, mGuid, param_export_id, anaplan_param_export_task_json['task']['taskId'], auth_token)
    # if verbose:
    #     print(anaplan_param_export_task_details_json)
    #     print(anaplan_param_export_task_details_json['task']['taskState'])
    #
    # # Once 'taskState' == 'COMPLETE', run get_files()
    # if verbose:
    #     print('------------------- GETTING ALL MODEL FILES -------------------')
    # model_files__response, model_files_json = anaplan_connect_helper_functions.get_model_files(wGuid, mGuid, auth_token)
    # if verbose:
    #     print(model_files_json)

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


def anaplan_get_export_historical_df(auth_token, verbose=False):
    # TODO: try/except?
    if verbose:
        print('Loading Anaplan credential from creds.json')
    san_diego_demo_creds = load_creds()
    # san_diego_demo_email = san_diego_demo_creds['username']
    # san_diego_demo_pwd = san_diego_demo_creds['password']

    wGuid = san_diego_demo_creds['san-diego-demo']['workspace_id']
    mGuid = san_diego_demo_creds['san-diego-demo']['model_id']
    df_export_id = san_diego_demo_creds['san-diego-demo']['df_export_id']

    if verbose:
        print('------------------- GETTING HISTORICAL DF EXPORT DATA -------------------')
    # ref: https://community.anaplan.com/t5/Best-Practices/RESTful-API-Best-Practices/ta-p/33579 (https://vimeo.com/318242332)
    anaplan_historical_df_export_response, anaplan_historical_df_export_data_json = anaplan_connect_helper_functions.get_export_data(
        wGuid, mGuid, df_export_id, auth_token)

    if verbose:
        print('------------------- CREATING HISTORICAL DF (POST) EXPORT TASK -------------------')
    anaplan_historical_df_export_task_response, anaplan_historical_df_export_task_json = anaplan_connect_helper_functions.post_export_task(wGuid, mGuid, df_export_id, auth_token)

    # Then, get all chunks
    if verbose:
        print('------------------- GETTING HISTORICAL DF FILE INFO (CHUNK METADATA) -------------------')
    chunk_metadata_response, chunk_metadata_json = anaplan_connect_helper_functions.get_chunk_metadata(wGuid, mGuid, df_export_id, auth_token)
    if verbose:
        print(chunk_metadata_json)

    if verbose:
        print('------------------- GETTING HISTORICAL DF CHUNK DATA -------------------')
        print('Total number of chunks: {}'.format(len(chunk_metadata_json['chunks'])))

    if len(chunk_metadata_json['chunks']) == 1:
        chunk_data_response, chunk_data_text = anaplan_connect_helper_functions.get_chunk_data(wGuid, mGuid,
                                                                                               df_export_id, chunk_metadata_json['chunks'][0]['id'],
                                                                                               auth_token)
        chunk_data_parsed = anaplan_connect_helper_functions.parse_chunk_data(chunk_data_text)
        historical_df = pd.DataFrame(chunk_data_parsed[1:], columns=chunk_data_parsed[0])

        return historical_df

    else:
        all_historical_df_chunk_data = []
        for c in chunk_metadata_json['chunks']:
            if verbose:
                print('Chunk name, ID:', c['name'], ',', c['id'])
            chunk_data_response, chunk_data_text = anaplan_connect_helper_functions.get_chunk_data(wGuid, mGuid, df_export_id, c['id'], auth_token)
            # print(chunk_data.url)
            # print(chunk_data.status_code)
            # print(chunk_data_text)
            # historical_df = pd.DataFrame.from_records([r.split(',') for r in chunk_data_text[1:]], columns=chunk_data_text.split('\n')[0])
            chunk_data_parsed = anaplan_connect_helper_functions.parse_chunk_data(chunk_data_text)
            if verbose:
                print(chunk_data_parsed)
            all_historical_df_chunk_data.append(chunk_data_parsed)

        historical_df = pd.DataFrame(all_historical_df_chunk_data[1:], columns=all_historical_df_chunk_data[0])  # TODO: This is untested for num chunks > 1, and likely does not work

        return historical_df


def parse_params_chunk_data(params_chunk_data):
    # First element in params_chunk_data list is the header row; can ignore
    params_chunk_data = params_chunk_data[1:]

    # Param values are exported as strings; cast all as float
    params = {}
    for i in params_chunk_data:
        params[i[0]] = float(i[1])

    return params


def validate_params(params):
    # TODO: make sure the params are in the proper format to plug into model_covid.py (all are present, values cast as floats, etc)
    return None


def validate_df(df_historical):
    # TODO: make sure the df is in the proper format to plug into model_covid.py (proper shape, column names, etc)
    return None


# def anaplan_import_data(verbose=False):
#     # TODO: try/except?
#     if verbose:
#         print('Loading Anaplan credential from creds.json')
#     san_diego_demo_creds = load_creds()
#     san_diego_demo_email = san_diego_demo_creds['username']
#     san_diego_demo_pwd = san_diego_demo_creds['password']
#
#     wGuid = san_diego_demo_creds['san-diego-demo']['workspace_id']
#     mGuid = san_diego_demo_creds['san-diego-demo']['model_id']
#     import_id = san_diego_demo_creds['san-diego-demo']['import_id']
#     import_predictions_file_id = san_diego_demo_creds['san-diego-demo']['import_predictions_file_id']


def main(num_time_predict=30, sim_data=False, verbose=False, dry_run=False):
    """
    # TODO: Update these steps & docstring
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
    param_export_id = san_diego_demo_creds['san-diego-demo']['params_export_id']
    import_predictions_file_id = san_diego_demo_creds['san-diego-demo']['import_predictions_file_id']
    upload_file_import_id = san_diego_demo_creds['san-diego-demo']['upload_file_import_id']
    import_process_id = san_diego_demo_creds['san-diego-demo']['import_preds_process_id']

    # TODO: Store token somewhere, and if it expires, refresh it?
    token_generated = anaplan_connect_helper_functions.anaplan_create_token(san_diego_demo_email, san_diego_demo_pwd)
    token_auth_user = anaplan_connect_helper_functions.generate_token_auth_user(san_diego_demo_email, san_diego_demo_pwd, token=token_generated)

    if dry_run:
        sim_data = True

    if sim_data:
        if verbose:
            print('No data provided; using simulated data.')
        # Create example data -- both death rate and log death rate
        np.random.seed(1234)

        df_historical = pd.DataFrame()
        df_historical['time_obs'] = np.arange(30)
        df_historical['death_rate'] = np.exp(.1 * (df_historical['time_obs'] - 20)) / (1 + np.exp(.1 * (df_historical['time_obs'] - 20))) + \
                           np.random.normal(0, 0.1, size=30).cumsum()
        df_historical['ln_death_rate'] = np.log(df_historical['death_rate'])
        df_historical['group'] = 'all'
        df_historical['intercept'] = 1.0  # Default to 1.0 ?
        fe_init = [0, 0, 1.]
        fe_gprior = [[0, np.inf], [0, np.inf], [1., np.inf]]
        fe_bounds = [[0., 100.], [0., 100.], [0., 100.]]

        # pd.DataFrame.to_csv(df, "covid_sim_data.csv", index=False)

    else:  # if sim_data == False, connect to Anaplan to get 'real' data
        if verbose:
            print('Getting params from Anaplan...')
        params_chunks_unparsed = anaplan_get_export_params(token_auth_user, verbose=verbose)
        params = parse_params_chunk_data(params_chunks_unparsed)

        if verbose:
            print('Getting historical df from Anaplan...')
        df_historical = anaplan_get_export_historical_df(token_auth_user, verbose=verbose)

        df_historical['time_obs'] = df_historical['time_obs'].astype(int)
        df_historical['death_rate'] = df_historical['death_rate'].astype(float)
        df_historical['ln_death_rate'] = np.log(df_historical['death_rate'])
        df_historical['group'] = 'all'
        df_historical['intercept'] = 1.0  # TODO: Default to 1.0?
        # TODO: Make more flexible to take any number of params
        fe_init = [params['fe_init_1'], params['fe_init_2'], params['fe_init_3']]
        re_init = [params['re_init_1'], params['re_init_2'], params['re_init_3']]
        fe_gprior = [
            [params['fe_gprior_1_lower'], params['fe_gprior_1_upper']],
            [params['fe_gprior_2_lower'], params['fe_gprior_2_upper']],
            [params['fe_gprior_3_lower'], params['fe_gprior_3_upper']]
        ]
        re_gprior = [
            [params['re_gprior_1_lower'], params['re_gprior_1_upper']],
            [params['re_gprior_2_lower'], params['re_gprior_2_upper']],
            [params['re_gprior_3_lower'], params['re_gprior_3_upper']]
        ]
        fe_bounds = [
            [params['fe_bounds_1_lower'], params['fe_bounds_1_upper']],
            [params['fe_bounds_2_lower'], params['fe_bounds_2_upper']],
            [params['fe_bounds_3_lower'], params['fe_bounds_3_upper']]
        ]
        re_bounds = [
            [params['re_bounds_1_lower'], params['re_bounds_1_upper']],
            [params['re_bounds_2_lower'], params['re_bounds_2_upper']],
            [params['re_bounds_3_lower'], params['re_bounds_3_upper']]
        ]
        # model_options = params['options']  # TODO

    # if not validate_params(params):
    #     # TODO: Raise an exception/alert to the user if the params are in an invalid format
    #     raise

    # if not validate_df(df_historical):
    #     # TODO: Raise an exception/alert to the user if the DF is in an invalid format
    #     raise

    print(df_historical.head())
    model_args_dict = {
        'df': df_historical,
        'col_t': 'time_obs',
        'col_obs': 'ln_death_rate',
        'col_group': 'group',
        'col_covs': [['intercept'], ['intercept'], ['intercept']],
        'param_names': ['alpha', 'beta', 'p'],
        'link_fun': [lambda x: x, lambda x: x, lambda x: x],
        'var_link_fun': [lambda x: x, lambda x: x, lambda x: x],
        # 'fun': ln_gaussian_cdf,  # TODO -- must import ln_gaussian_cdf here? model_covid.py cannot parse a string value here -- must be the function/object from curvefit.core.functions
        'fe_init': fe_init, #[0, 0, 1.],
        'fe_gprior': fe_gprior, #[[0, np.inf], [0, np.inf], [1., np.inf]]
        'fe_bounds': fe_bounds,
        'num_time_predict': num_time_predict
    }

    if verbose:
        print('Fitting model to parameters, generating predictions...')
    model, df_predictions = model_covid.fit_model_predict(model_args_dict, verbose=verbose, charts=False)

    # invert ln(death rate) to get predicted actual death rate
    df_predictions['death_rate'] = np.exp(df_predictions['prediction_ln_death_rate'])

    # # Keep only the actual death rate column
    # df_predictions = df_predictions[['time_pred', 'death_rate']]

    # print(df_historical.head())
    # print(df_historical.tail())
    # print(num_time_predict)
    # print(df_predictions.head())
    # print(df_predictions.tail())

    # Test to verify the file was correctly uploaded to Anaplan
    df_predictions.at[0, 'death_rate'] = -999
    print(df_predictions.head())

    pred_file_timestamp = datetime.datetime.now().strftime('%Y-%m-%d')
    pred_filename = "covid_predictions_{TIME}.csv".format(TIME=pred_file_timestamp)
    # Save predictions df locally as CSV
    if verbose:
        print('Saving predictions df as a CSV locally...')
    pd.DataFrame.to_csv(df_predictions, pred_filename, index=False)

    # --- Import predictions csv into Anaplan ---
    # Note: To upload a file using the API, that file must already exist in Anaplan.
    # If the file has not been previously uploaded, you must upload it initially using the Anaplan user interface.
    # You can then carry out subsequent uploads of that file using the API.
    # Ref: https://anaplan.docs.apiary.io/#reference/upload-files

    # Notes on files uploaded/exported via API:
    # Private files are created when you use the Anaplan API to:
    # - Upload a file
    # - Run the export action
    #
    # Private files have these characteristics:
    # - A private import file can only be accessed by the user who originally uploaded the source file to the model.
    # - A private import file can only be accessed by the user who originally ran the export.
    # - Private files are stored in models and removed if not accessed at least once in 48 hours. If your private file no longer exists for a file Import Data Source or file Export Action, the default file is used instead.


    file_upload_metadata = {
        "id": import_predictions_file_id,
        "name": pred_filename,
        "chunkCount": 1,
        "delimiter": "",
        "encoding": "utf-8",
        "firstDataRow": 2,
        "format": "csv",
        "headerRow": 1,
        "separator": ","
    }

    data_file = open(pred_filename, 'r').read().encode('utf-8')

    # # --- Initiate the upload ---
    # if verbose:
    #     print('Uploading predictions df to Anaplan...')
    # pred_file_upload_response = anaplan_connect_helper_functions.put_upload_file(wGuid, mGuid, file_upload_metadata, data_file, token_auth_user)
    # print(pred_file_upload_response)
    #
    # # --- Execute the import ---
    # if verbose:
    #     print('Importing uploaded predictions df to Anaplan model...')
    # post_import_file_response, post_import_file_data = anaplan_connect_helper_functions.post_upload_file(wGuid, mGuid, upload_file_import_id, token_auth_user)
    # print(post_import_file_response)
    # print(post_import_file_data)




    # if verbose:
    #     print('Starting import process (to uploaded predictions df to Anaplan model)...')
    # post_import_process_response, post_import_process_data = anaplan_connect_helper_functions.post_import_process(wGuid, mGuid, import_process_id, token_auth_user)
    # print(post_import_process_response)
    # print(post_import_process_data)


    # Once import is complete, delete the .\temp directory

    # TODO: Check whether the import action was successful, how many rows uploaded/ignored, etc



if __name__ == "__main__":
    main(sim_data=False, verbose=True, dry_run=False)



# tokenval = "ENUOA0k7kpYVgQ9WYjrOQA==.kT6bkAURD/ALZV7id1XGDhY19vq9Z1iF4namAlUW0VfWqdZaSwn1sPW1drOYQMdepQGZhHywc2ffo/gjGUkclFQ28sgKQhwNz30GcWAqY8f3HvWyUmqN+zbvIt5tJLwayJtYNBOurRTcpqITo2kVeyrr8PZwTsqQ14CMv5a+ip58pfaREQsMGMicTbsaKfbBuY6NP5qUQK/5p3WsRjmqiyQPfofJFSDF6RoksVqVgi+B4xJ95uhbTZZiXfAYqgYebqY98zvg1zARVLV1BqIcRR2LBabJ4lz8lN0bL7xboWIf9JhU7OdAK4wCe4ykaV9TBXqYvhYVQx2JwnzMGyuMwwPQED6iwZjwjvnC55UaptGZ5b5hbUVRt68kqpkVuDAA24jKjjmx7/d2opKm4FoEHq/8H9pggx+FPm1iAu/3iizp680nurCjJWpj1U8/UYpfUu0wi6oGXDxLBK91bDWE+vAt65/GmeRU1D9stbJCRcncS5NfbK1aSa5KkA+XCKeg.RJ+NzsZAwxuuPWQCNHkYEVG58Q1uEyZx5EPl1aP/LPA="
# token_auth_user = anaplan_connect_helper_functions.anaplan_token_auth_user(tokenval)
# wGuid = "8a81b08e4f6d2b43014fbe11122a160c"
# mGuid = "96339A3A48394142A3E70E057F75480E"
#
# model_imports_response, model_imports_data = anaplan_connect_helper_functions.get_model_imports(wGuid, mGuid, token_auth_user)
# print(model_imports_response)
# print(model_imports_data)
# covid_preds_import_id = "112000000024"
#
# model_files_response, model_files_json = anaplan_connect_helper_functions.get_model_files(wGuid, mGuid, token_auth_user)
# print(model_files_json)
# covid_preds_file_id = "113000000022"

# put_import_file




# TODO: Set up Flask instance to run this from Anaplan -- trigger via button
