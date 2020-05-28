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


def anaplan_get_export_historical_df(auth_token, verbose=False):
    # TODO: try/except?
    if verbose:
        print('Loading Anaplan credential from creds.json')
    san_diego_demo_creds = load_creds()

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


def main(num_time_predict=30, sim_data=False, verbose=False, dry_run=False):
    """
    # TODO: Update these steps & docstring
    - Load credentials via load_creds()
    - Generate an auth token.

    - Run get_anaplan_params.py
    - Parse chunk_data_parsed_array (set var name = its accompanying value)
    - Plug vars into curvefit model (COVID deaths?)
    - Get resulting projections (as CSV?)
    - Import projections back into Anaplan.

    :param num_time_predict: (int) Time to predict out (ex: number of days).
    :param sim_data: (bool) Whether to use simulated data or real data from Anaplan.
    :param verbose: (bool) Whether to print each step to the console as it's being executed.
    :param dry_run: (bool) Whether to execute a dry_run or not -- dry_run will run with verbose=True and sim_data=True
    :return:
    """
    if verbose:
        print('Loading Anaplan credential from creds.json')
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

    if dry_run:
        sim_data = True
        verbose = True

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

    # Test to verify the file was correctly uploaded to Anaplan -- first row should contain this nonsensical value
    df_predictions.at[0, 'death_rate'] = -2222
    print(df_predictions.head())

    # pred_file_timestamp = datetime.datetime.now().strftime('%Y-%m-%d')
    # pred_filename = "covid_predictions_{TIME}.csv".format(TIME=pred_file_timestamp)
    pred_filename = "Covid_Predictions.csv"  # This must the be exact name of the file currently in Anaplan which you are replacing/updating
    # Save predictions df locally as CSV
    if verbose:
        print('Saving predictions df as a CSV locally...')
    pd.DataFrame.to_csv(df_predictions, pred_filename, index=False)

    # --- Import predictions csv into Anaplan ---
    # Note: To upload a file using the API, that file must already exist in Anaplan. If the file has not been
    # previously uploaded, you must upload it initially using the Anaplan user interface.
    # You can then carry out subsequent uploads of that file using the API.
    # Reference: https://anaplan.docs.apiary.io/#reference/upload-files

    # Notes on files uploaded/exported via API:
    # Private files are created when you use the Anaplan API to:
    # - Upload a file
    # - Run the export action
    #
    # Private files have these characteristics:
    # - A private import file can only be accessed by the user who originally uploaded the source file to the model.
    # - A private import file can only be accessed by the user who originally ran the export.
    # - Private files are stored in models and removed if not accessed at least once in 48 hours. If your private file no longer exists for a file Import Data Source or file Export Action, the default file is used instead.

    # TODO: Currently assuming the data to upload/import fits within 1 chunk (<10 MB)
    data_file = open(pred_filename, 'r').read().encode('utf-8')

    # --- Initiate the upload ---
    if verbose:
        print('Uploading predictions df to Anaplan...')
    pred_file_upload_response = anaplan_connect_helper_functions.put_upload_file(wGuid, mGuid, predictions_file_id, data_file, token_auth_user)
    print(pred_file_upload_response)

    # --- Execute the import ---
    if verbose:
        print('Importing uploaded predictions df to Anaplan...')
    post_import_file_response, post_import_file_data = anaplan_connect_helper_functions.post_upload_file(wGuid, mGuid, predictions_import_id, token_auth_user)
    print(post_import_file_response)
    print(post_import_file_data)

    # Once import is complete, delete the .\temp directory

    # TODO: Check whether the import action was successful, how many rows uploaded/ignored, failure dump, etc

    model_run_timestamp = datetime.datetime.now().strftime('%m/%d/%Y')
    model_run_df = pd.DataFrame([model_run_timestamp], columns=['date'])
    model_run_filename = "date_model_ran.csv"
    pd.DataFrame.to_csv(model_run_df, model_run_filename, index=False)

    model_timestamp_data_file = open(model_run_filename, 'r').read().encode('utf-8')

    model_run_timestamp_file_id = san_diego_demo_creds['san-diego-demo']['model_run_timestamp_file_id']
    model_run_timestamp_import_id = san_diego_demo_creds['san-diego-demo']['model_run_timestamp_import_id']

    # --- Initiate the upload ---
    if verbose:
        print('Uploading model timestamp to Anaplan...')
    model_timestamp_file_upload_response = anaplan_connect_helper_functions.put_upload_file(wGuid, mGuid, model_run_timestamp_file_id, model_timestamp_data_file, token_auth_user)
    print(model_timestamp_file_upload_response)

    # --- Execute the import ---
    if verbose:
        print('Importing uploaded model timestamp to Anaplan...')
    model_timestamp_post_import_file_response, model_timestamp_post_import_file_data = anaplan_connect_helper_functions.post_upload_file(wGuid, mGuid, model_run_timestamp_import_id, token_auth_user)
    print(model_timestamp_post_import_file_response)
    print(model_timestamp_post_import_file_data)


if __name__ == "__main__":
    # TODO: Use argparse to enable args from CLI?
    main(sim_data=False, verbose=True, dry_run=False)
