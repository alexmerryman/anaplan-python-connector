import os
import json
import requests
import numpy as np
import pandas as pd
import datetime
import time
import anaplan_connect_helper_functions
import model_covid
import flask_app_helper_functions

from app_classes import AnaplanUserAuthToken

# TODO: Import logging -- to track errors, notes, comments, timestamps, values, etc


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

    cred_path = "creds.json"
    if not os.path.isfile(cred_path):
        print('ERROR: No file called `creds.json` found in the path.')
        return None
    else:
        creds = json.load(open(cred_path,))
        return creds


# Reference: https://anaplanauthentication.docs.apiary.io/#reference
def generate_auth_token(verbose=False):
    creds = load_creds()
    email = creds['username']
    pwd = creds['password']

    if verbose:
        print("Generating Anaplan API authorization token...")
    token_generated = anaplan_connect_helper_functions.anaplan_create_token(email, pwd)
    token_auth_user = anaplan_connect_helper_functions.generate_token_auth_user(email, pwd, token=token_generated)

    return token_generated, token_auth_user


def write_token_file(token_generated, token_auth_user, verbose=False):
    # TODO: Write to subdirectory, instead of main directory?
    if verbose:
        print("Saving token locally...")
    with open("token.json", "wb") as token_outfile:
        # print(token_generated.content)
        token_outfile.write(token_generated.content)

    if verbose:
        print("Saving token auth user locally...")
    with open("token_auth_user.txt", "w") as token_auth_user_outfile:
        token_auth_user_outfile.write(token_auth_user)


def read_token_file(verbose=False):
    if verbose:
        print("Attempting to read token from saved file...")

    token_path = "token.json"
    if not os.path.isfile(token_path):
        print(f"ERROR: No file called `{token_path}` found in the path.")
        token_generated = None
    else:
        with open(token_path) as token_json:
            token_generated = json.load(token_json)
        print(f"Successfully read {token_path} from local file.")

    token_auth_user_path = "token_auth_user.txt"
    if not os.path.isfile(token_auth_user_path):
        print(f"ERROR: No file called `{token_auth_user_path}` found in the path.")
        token_auth_user = None
    else:
        with open(token_auth_user_path) as token_auth_user_txt:
            token_auth_user = token_auth_user_txt.read()
        print(f"Successfully read {token_auth_user_path} from local file.")

    return token_generated, token_auth_user


def full_token_credentialing(expiry_buffer=180, verbose=False):
    try:
        token_generated, token_auth_user = read_token_file(verbose=verbose)
    except Exception as e:
        print(f"Unable to load token_generated, token_auth_user from local file (exception {e}); generating new ones...")
        token_generated, token_auth_user = generate_auth_token(verbose=verbose)
        if verbose:
            print("Writing token and auth user to local files (token.json, token_auth_user.txt)...")
        write_token_file(token_generated, token_auth_user, verbose=verbose)

    if (not token_generated) or (not token_auth_user):
        if verbose:
            print("Either token_generated or token_auth_user are None -- generating new token & auth user...")
        token_generated, token_auth_user = generate_auth_token(verbose=verbose)

        if verbose:
            print("Writing token and auth user to local files (token.json, token_auth_user.txt)...")
        write_token_file(token_generated, token_auth_user, verbose=verbose)
        token_generated = token_generated.json()

    TokenObj = AnaplanUserAuthToken(token_generated, expiry_buffer=expiry_buffer)
    TokenObj.auth_token_string = token_auth_user

    if verbose:
        print(f"Token expires at: {TokenObj.expiry_formatted()} ({TokenObj.expiry_sec()} epoch time).")
        print(f"It is currently: {int(time.time())} (epoch time).")
        print(f"Token expires in {TokenObj.remaining_sec()} seconds.")

    if TokenObj.expired_status() is True:
        if verbose:
            print(f"Token has expired, or will expire soon. Generating a new token...")
        token_generated, token_auth_user = generate_auth_token(verbose=verbose)
        write_token_file(token_generated, token_auth_user, verbose=verbose)
        token_generated = token_generated.json()
        TokenObj = AnaplanUserAuthToken(token_generated, expiry_buffer=expiry_buffer)
    else:
        if verbose:
            print(f"You have {TokenObj.remaining_sec()/60.} min to use this token.")

    return TokenObj


def anaplan_get_user_trigger_status(TokenObj, creds, verbose=False):
    wGuid = creds['san-diego-demo']['workspace_id']
    mGuid = creds['san-diego-demo']['model_id']
    user_trigger_file_id = creds['san-diego-demo']['user_trigger_file_id']

    if verbose:
        print('Getting user trigger status chunk metadata...')
    chunk_metadata_response, chunk_metadata_json = anaplan_connect_helper_functions.get_chunk_metadata(wGuid, mGuid,
                                                                                                       user_trigger_file_id,
                                                                                                       TokenObj.auth_token_string)
    if verbose:
        print(chunk_metadata_json)

    if verbose:
        print('Getting user trigger status chunk data...')
        print('Total number of chunks: {}'.format(len(chunk_metadata_json['chunks'])))

    # if len(chunk_metadata_json['chunks']) == 1:
    chunk_data_response, chunk_data_text = anaplan_connect_helper_functions.get_chunk_data(wGuid, mGuid,
                                                                                           user_trigger_file_id,
                                                                                           chunk_metadata_json['chunks'][0]['id'],
                                                                                           TokenObj.auth_token_string)
    chunk_data_parsed = anaplan_connect_helper_functions.parse_chunk_data(chunk_data_text)

    # print(chunk_data_text)
    # print(chunk_data_parsed)
    # print(chunk_data_parsed[1][1])

    # user_trigger_status == True if user has clicked the button in Anaplan; otherwise, False
    user_trigger_status = chunk_data_parsed[1][1] == 'true'

    if user_trigger_status:
        user_trigger_status_message = "An Anaplan user has triggered a button in Anaplan to execute the full run."
    else:
        user_trigger_status_message = "No Anaplan user action detected to execute the full run."

    return user_trigger_status, user_trigger_status_message


def anaplan_get_export_params(TokenObj, creds, verbose=False):
    wGuid = creds['san-diego-demo']['workspace_id']  # TODO: Get this from user input via list_workspaces
    mGuid = creds['san-diego-demo']['model_id']  # TODO: Get this from user input via list_models
    param_export_id = creds['san-diego-demo']['params_export_id']   # TODO: Get this from user input via list_exports

    # if verbose:
    #     print('Getting params export data from Anaplan...')
    # # ref: https://community.anaplan.com/t5/Best-Practices/RESTful-API-Best-Practices/ta-p/33579 (https://vimeo.com/318242332)
    # anaplan_param_export_response, anaplan_param_export_data_json = anaplan_connect_helper_functions.get_export_data(
    #     wGuid, mGuid, param_export_id, TokenObj.auth_token_string)
    # if verbose:
    #     print(anaplan_param_export_data_json['exportMetadata']['headerNames'])
    #     print(anaplan_param_export_data_json['exportMetadata']['dataTypes'])
    #     print(anaplan_param_export_data_json['exportMetadata']['rowCount'])
    #     print(anaplan_param_export_data_json['exportMetadata']['exportFormat'])
    #     print(anaplan_param_export_data_json['exportMetadata']['delimiter'])

    # if verbose:
    #     print('Creating params export task (POST)...')
    # anaplan_param_export_task_response, anaplan_param_export_task_json = anaplan_connect_helper_functions.post_export_task(wGuid, mGuid, param_export_id, TokenObj.auth_token_string)

    # Then, get all chunks
    if verbose:
        print('Getting params file info (chunk metadata) from Anaplan...')
    chunk_metadata_response, chunk_metadata_json = anaplan_connect_helper_functions.get_chunk_metadata(wGuid, mGuid, param_export_id, TokenObj.auth_token_string)
    if verbose:
        print(chunk_metadata_json)

    if verbose:
        print('Getting params chunk data from Anaplan...')
        print('Total number of chunks: {}'.format(len(chunk_metadata_json['chunks'])))

    if len(chunk_metadata_json['chunks']) == 1:
        chunk_data_response, chunk_data_text = anaplan_connect_helper_functions.get_chunk_data(wGuid, mGuid,
                                                                                               param_export_id, chunk_metadata_json['chunks'][0]['id'],
                                                                                               TokenObj.auth_token_string)
        chunk_data_parsed = anaplan_connect_helper_functions.parse_chunk_data(chunk_data_text)

        return chunk_data_parsed

    else:
        all_param_chunk_data = []
        for c in chunk_metadata_json['chunks']:
            chunk_data_response, chunk_data_text = anaplan_connect_helper_functions.get_chunk_data(wGuid, mGuid, param_export_id, c['id'], TokenObj.auth_token_string)
            chunk_data_parsed = anaplan_connect_helper_functions.parse_chunk_data(chunk_data_text)
            all_param_chunk_data.append(chunk_data_parsed)

        return all_param_chunk_data


def anaplan_get_export_historical_df(TokenObj, creds, verbose=False):
    wGuid = creds['san-diego-demo']['workspace_id']
    mGuid = creds['san-diego-demo']['model_id']
    df_export_id = creds['san-diego-demo']['df_export_id']

    # if verbose:
    #     print('Getting historical DF export data from Anaplan')
    # # ref: https://community.anaplan.com/t5/Best-Practices/RESTful-API-Best-Practices/ta-p/33579 (https://vimeo.com/318242332)
    # anaplan_historical_df_export_response, anaplan_historical_df_export_data_json = anaplan_connect_helper_functions.get_export_data(
    #     wGuid, mGuid, df_export_id, TokenObj.auth_token_string)
    #
    # if verbose:
    #     print('Creating historical DF export task (POST)...')
    # anaplan_historical_df_export_task_response, anaplan_historical_df_export_task_json = anaplan_connect_helper_functions.post_export_task(wGuid, mGuid, df_export_id, TokenObj.auth_token_string)

    # Then, get all chunks
    if verbose:
        print('Getting historical DF file info (chunk metadata) from Anaplan...')
    chunk_metadata_response, chunk_metadata_json = anaplan_connect_helper_functions.get_chunk_metadata(wGuid, mGuid, df_export_id, TokenObj.auth_token_string)

    if verbose:
        print(chunk_metadata_json)

    if verbose:
        print('Getting historical DF chunk data from Anaplan...')
        print('Total number of chunks: {}'.format(len(chunk_metadata_json['chunks'])))

    if len(chunk_metadata_json['chunks']) == 1:
        chunk_data_response, chunk_data_text = anaplan_connect_helper_functions.get_chunk_data(wGuid, mGuid,
                                                                                               df_export_id,
                                                                                               chunk_metadata_json['chunks'][0]['id'],
                                                                                               TokenObj.auth_token_string)
        chunk_data_parsed = anaplan_connect_helper_functions.parse_chunk_data(chunk_data_text)
        historical_df = pd.DataFrame(chunk_data_parsed[1:], columns=chunk_data_parsed[0])

        return historical_df

    else:
        all_historical_df_chunk_data = []
        for c in chunk_metadata_json['chunks']:
            if verbose:
                print('Chunk name, ID:', c['name'], ',', c['id'])
            chunk_data_response, chunk_data_text = anaplan_connect_helper_functions.get_chunk_data(wGuid, mGuid, df_export_id, c['id'], TokenObj.auth_token_string)
            chunk_data_parsed = anaplan_connect_helper_functions.parse_chunk_data(chunk_data_text)
            if verbose:
                print(chunk_data_parsed)
            all_historical_df_chunk_data.append(chunk_data_parsed)

        historical_df = pd.DataFrame(all_historical_df_chunk_data[1:], columns=all_historical_df_chunk_data[0])  # TODO: This is untested for num chunks > 1, and likely does not work

        return historical_df


def process_historical_df(df_historical):
    df_historical['time_obs'] = df_historical['time_obs'].astype(int)
    df_historical['death_rate'] = df_historical['death_rate'].astype(float)
    df_historical['ln_death_rate'] = np.log(df_historical['death_rate'])
    df_historical['group'] = 'all'
    df_historical['intercept'] = 1.0  # TODO: Default to 1.0?

    return df_historical


def parse_params_chunk_data(params_chunk_data):
    # First element in params_chunk_data list is the header row; can ignore
    params_chunk_data = params_chunk_data[1:]

    # Param values are exported as strings; cast all as float (they should all be float)
    # TODO: What if some params are not float? e.g. unbounded, np.inf, etc?
    params = {}
    for i in params_chunk_data:
        params[i[0]] = float(i[1])

    return params


def process_params(params):
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

    return fe_init, re_init, fe_gprior, re_gprior, fe_bounds, re_bounds


def validate_params(params):
    # TODO: make sure the params are in the proper format to plug into model_covid.py (all are present, values cast as floats, etc)
    return None


def validate_df(df_historical):
    # TODO: make sure the df is in the proper format to plug into model_covid.py (proper shape, column names, etc)
    return None


def simulate_data():
    # Create example data -- both death rate and log death rate
    np.random.seed(1234)

    df_historical = pd.DataFrame()
    df_historical['time_obs'] = np.arange(30)
    df_historical['death_rate'] = np.exp(.1 * (df_historical['time_obs'] - 20)) / (
                1 + np.exp(.1 * (df_historical['time_obs'] - 20))) + \
                                  np.random.normal(0, 0.1, size=30).cumsum()
    df_historical['ln_death_rate'] = np.log(df_historical['death_rate'])
    df_historical['group'] = 'all'
    df_historical['intercept'] = 1.0
    fe_init = [0, 0, 1.]
    fe_gprior = [[0, np.inf], [0, np.inf], [1., np.inf]]
    fe_bounds = [[0., 100.], [0., 100.], [0., 100.]]

    sim_data_dict = {
        'df_historical': df_historical,
        'fe_init': fe_init,
        'fe_gprior': fe_gprior,
        'fe_bounds': fe_bounds}

    return sim_data_dict


def make_temp_directory(verbose=False):
    tmp_path = os.path.join(os.getcwd(), "tmp")

    # TODO: Refactor using: from pathlib import Path, Path(OI_path).mkdir(parents=True, exist_ok=True)

    try:
        os.makedirs(tmp_path)
        if verbose:
            print("`/tmp` directory successfully created.")
    except OSError:
        if verbose:
            print("`/tmp` directory already exists.")
        pass  # tmp_path directory already exists

    return tmp_path


def filesize_to_chunks(filepath):
    file_size = os.path.getsize(filepath) / 1000000.
    print(f"File is: {file_size} MB")
    if file_size < 10:
        print(f"File small enough for 1 chunk of data ({filepath}).")
    else:
        print(f"File must be split into 2+ chunks of data ({filepath}).")
        # TODO: In case file_size > 10 MB and must be split into 2+ chunks of data
        pass

    return file_size


def put_post_data(tmp_path, filename, data_df, workspace_id, model_id, put_destination_id, post_destination_id, TokenObj, verbose=False):
    """
    # TODO: Check whether tmp directory exists -- if not, create it.

    Save data to tmp directory as CSV.
    Get file_size to determine how many chunks to break it up into.
    Read data as basic/encoded (for upload as octet-stream).
    Put (upload) data to specified workspace/model.
    Post (import) data to specified workspace/model.

    :param tmp_path:
    :param filename (str): The name you wish to save/import the data as -- NTOE: This must be the EXACT name as the file you are overwriting in Anaplan.
    :param data_df (DataFrame): The data you wish to import.
    :param workspace_id:
    :param model_id:
    :param destination_id:
    :param TokenObj:
    :param verbose:
    :return:
    """
    pred_filename = "Covid_Predictions.csv"  # This must the be exact name of the file currently in Anaplan which you are replacing/updating
    # Save predictions DF locally as CSV
    if verbose:
        print('Saving predictions DF as a CSV locally...')
    data_tmp_filepath = os.path.join(tmp_path, filename)
    pd.DataFrame.to_csv(data_df, data_tmp_filepath, index=False)

    file_size = filesize_to_chunks(data_tmp_filepath)
    # TODO: Break into chunks if necessary

    data_file = open(data_tmp_filepath, 'r').read().encode('utf-8')

    # --- Initiate the upload ---
    if verbose:
        print('Uploading data to Anaplan...')
    put_upload_response = anaplan_connect_helper_functions.put_upload_file(workspace_id,
                                                                                 model_id,
                                                                                 put_destination_id,
                                                                                 data_file,
                                                                                 TokenObj.auth_token_string)

    # --- Execute the import ---
    if verbose:
        print('Importing uploaded data DF to Anaplan...')
    post_import_response, post_import_data = anaplan_connect_helper_functions.post_upload_file(workspace_id,
                                                                                                         model_id,
                                                                                                         post_destination_id,
                                                                                                         TokenObj.auth_token_string)

    return put_upload_response, post_import_response, post_import_data


def validate_data_import():
    # TODO
    pass


def anaplan_reset_user_trigger_status(TokenObj, creds, verbose=False):

    # TODO: Just execute the import action "User Trigger Fill"?

    # tmp_path = "tmp"
    # filename = "user_trigger_export_csv"
    # data_df = pd.DataFrame({'1':}) # TODO
    workspace_id = creds['san-diego-demo']['workspace_id']
    model_id = creds['san-diego-demo']['model_id']
    put_destination_id = creds['san-diego-demo']['user_trigger_file_id']
    post_destination_id = creds['san-diego-demo']['user_trigger_import_id']

    post_import_reset_trigger_response, post_import_reset_trigger_data = anaplan_connect_helper_functions.post_upload_file(workspace_id, model_id, post_destination_id, TokenObj.auth_token_string)

    # put_upload_response, \
    #     post_import_response, post_import_data = put_post_data(tmp_path, filename, data_df, workspace_id, model_id,
    #                                                            put_destination_id, post_destination_id, TokenObj,
    #                                                            verbose=verbose)

    return post_import_reset_trigger_response, post_import_reset_trigger_data


def full_run_main(num_time_predict=30, dry_run=True, verbose=False):
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
    :param dry_run: (bool) Whether to execute a dry_run or not -- dry_run will run with verbose=True and sim_data=True
    :param verbose: (bool) Whether to print each step to the console as it's being executed.
    :return:
    """
    if verbose:
        print('Loading Anaplan credential from creds.json...')
    creds = load_creds()

    wGuid = creds['san-diego-demo']['workspace_id']
    mGuid = creds['san-diego-demo']['model_id']

    if verbose:
        print("Getting authorization token (either saved locally or generating a new one)...")
    TokenObj = full_token_credentialing()

    if verbose:
        print('Getting params from Anaplan...')
    params_chunks_unparsed = anaplan_get_export_params(TokenObj, creds, verbose=verbose)
    params = parse_params_chunk_data(params_chunks_unparsed)
    if verbose:
        print('Processing params...')
    fe_init, re_init, fe_gprior, re_gprior, fe_bounds, re_bounds = process_params(params)

    if dry_run:
        if verbose:
            print('dry_run=True passed, using simulated data...')
        sim_data_dict = simulate_data()
        df_historical = sim_data_dict['df_historical']
        fe_init = sim_data_dict['fe_init']
        fe_gprior = sim_data_dict['fe_gprior']
        fe_bounds = sim_data_dict['fe_bounds']

    else:
        if verbose:
            print('Getting historical DF from Anaplan...')
        df_historical = anaplan_get_export_historical_df(TokenObj, creds, verbose=verbose)

        if verbose:
            print('Processing historical DF...')
        df_historical = process_historical_df(df_historical)

    # if not validate_params(params):
    #     # TODO: Raise an exception/alert to the user if the params are in an invalid format
    #     raise

    # if not validate_df(df_historical):
    #     # TODO: Raise an exception/alert to the user if the DF is in an invalid format
    #     raise

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
        'fe_init': fe_init,
        'fe_gprior': fe_gprior,
        'fe_bounds': fe_bounds,
        'num_time_predict': num_time_predict
    }

    if verbose:
        print('Fitting model to parameters, generating predictions...')
    model, df_predictions = model_covid.fit_model_predict(model_args_dict, verbose=verbose, charts=False)

    # invert ln(death rate) to get predicted actual death rate
    df_predictions['death_rate'] = np.exp(df_predictions['prediction_ln_death_rate'])

    # TODO: Add `group` ('all'), `intercept` (1.0) columns to df_predictions -- first change format in Anaplan to ensure compatibility on upload/import?
    # TODO: Keep only the actual death rate column (not `prediction_ln_death_rate`) -- must change file schema in Anaplan first
    # df_predictions = df_predictions[['time_pred', 'death_rate']]

    # Test to verify the file was correctly uploaded to Anaplan -- first row should contain this nonsensical value
    df_predictions.at[0, 'death_rate'] = -111

    if not dry_run:
        tmp_path = make_temp_directory(verbose=verbose)

        # =============== Predictions DF ===============
        pred_filename = "Covid_Predictions.csv"

        predictions_put_id = creds['san-diego-demo']['predictions_file_id']
        predictions_post_id = creds['san-diego-demo']['predictions_import_id']

        pred_put_upload_response, \
            pred_post_import_response, pred_post_import_data = put_post_data(tmp_path,
                                                                             pred_filename,
                                                                             df_predictions,
                                                                             wGuid,
                                                                             mGuid,
                                                                             predictions_put_id,
                                                                             predictions_post_id,
                                                                             TokenObj,
                                                                             verbose=verbose)

        # TODO: Once import is complete, delete the .\temp directory?

        # TODO: Check whether the import action was successful, how many rows uploaded/ignored, failure dump, etc

        # =============== Model Run Timestamp ===============
        model_run_timestamp = datetime.datetime.now().strftime('%m/%d/%Y')
        model_run_df = pd.DataFrame([model_run_timestamp], columns=['date'])
        model_run_filename = "date_model_ran.csv"

        model_run_timestamp_put_id = creds['san-diego-demo']['model_run_timestamp_file_id']
        model_run_timestamp_post_id = creds['san-diego-demo']['model_run_timestamp_import_id']

        model_run_put_upload_response, \
            model_run_post_import_response, model_run_post_import_data = put_post_data(tmp_path,
                                                                                       model_run_filename,
                                                                                       model_run_df,
                                                                                       wGuid,
                                                                                       mGuid,
                                                                                       model_run_timestamp_put_id,
                                                                                       model_run_timestamp_post_id,
                                                                                       TokenObj,
                                                                                       verbose=verbose)

    else:
        print("dry_run=True passed, not actually uploading/importing (PUT/POST) to Anaplan.")
        pred_put_upload_response = None
        pred_post_import_response = None
        model_run_put_upload_response = None
        model_run_post_import_response = None

    return df_historical, df_predictions, pred_put_upload_response, pred_post_import_response, model_run_put_upload_response, model_run_post_import_response


def full_run_main_loop(timeout_min=5, num_time_predict=30, dry_run=False, verbose=False):
    time_begin = time.time()
    timeout_time = time_begin + (timeout_min*60)

    TokenObj = full_token_credentialing()
    creds = load_creds()

    user_trigger_status, user_trigger_status_message = anaplan_get_user_trigger_status(TokenObj, creds)

    print("Timeout?", timeout_time >= time.time())
    print("User trigger status:", user_trigger_status)
    while timeout_time >= time.time() and not user_trigger_status:  # Stay in loop until timeout, or user_trigger_status == True
        TokenObj = full_token_credentialing()
        user_trigger_status, user_trigger_status_message = anaplan_get_user_trigger_status(TokenObj, creds)

    print("Condition(s) passed to break while loop; executing full_run_main...")
    df_historical, df_predictions, pred_file_upload_response, post_import_file_response, model_timestamp_file_upload_response, model_timestamp_post_import_file_response = full_run_main(num_time_predict=num_time_predict, dry_run=dry_run, verbose=verbose)

    print("Resetting user trigger status to False...")
    post_import_reset_trigger_response, post_import_reset_trigger_data = anaplan_reset_user_trigger_status(TokenObj, creds, verbose=verbose)
    print(post_import_reset_trigger_response)
    print(post_import_reset_trigger_data)

    return df_historical, df_predictions, pred_file_upload_response, post_import_file_response, model_timestamp_file_upload_response, model_timestamp_post_import_file_response


# if __name__ == "__main__":
#     # TODO: Use argparse library to enable args from CLI?
#     main(sim_data=False, verbose=True, dry_run=False)
