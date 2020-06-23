from flask import Flask, render_template, request
from flask_app import app
import test_main
import full_run
import flask_app_helper_functions


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Alex'}

    return render_template('index.html', title='Anaplan-Python Connector Flask App', user=user)


@app.route("/test_main")
def test_main():
    data = test_main.main()

    return render_template('test_main.html', data=data)


@app.route("/generate_token")
def generate_token():
    TokenObj = full_run.full_token_credentialing()

    return render_template('auth_token.html',
                           creation_status=TokenObj.creation_status,
                           creation_status_message=TokenObj.creation_status_message,
                           remaining_time_seconds=round(TokenObj.remaining_sec()),
                           expiry_time_human_readable=TokenObj.expiry_formatted())


@app.route("/user_trigger_status")
def user_trigger_status():
    TokenObj = full_run.full_token_credentialing()
    creds = full_run.load_creds()
    user_trigger_status, user_trigger_status_message = full_run.anaplan_get_user_trigger_status(TokenObj, creds=creds)
    user_trigger_status = str(user_trigger_status).upper()

    return render_template('user_trigger_status.html', user_trigger_status=user_trigger_status, user_trigger_status_message=user_trigger_status_message)


@app.route("/workspaces/")  # TODO: Why doesn't route "/workspaces" work?
def workspaces():
    TokenObj = full_run.full_token_credentialing()
    avail_workspaces = flask_app_helper_functions.anaplan_list_workspaces(TokenObj.auth_token_string)

    return render_template('workspaces.html', avail_workspaces=avail_workspaces)


@app.route("/model_exports")
def model_exports():
    # Get params, historical df here?
    TokenObj = full_run.full_token_credentialing()
    model_exports = flask_app_helper_functions.anaplan_list_exports()  # TODO

    return render_template('model_exports.html', model_exports=model_exports)


# @app.route("/workspaces/models")
# def models():
#     selected_workspace = request.args.get('type')
#     print(selected_workspace)


@app.route("/full_run_simdata")
def full_run_simdata():
    # TODO: Cache the data in case user navigate away, it doesn't have to re-run/re-calculate everything?
    df_historical, df_predictions, pred_file_upload_response, post_import_file_response, \
    model_timestamp_file_upload_response, model_timestamp_post_import_file_response = full_run.full_run_main(num_time_predict=30, dry_run=True, verbose=True)

    full_run_data = {'df_historical': df_historical.to_html(),
                     'df_predictions': df_predictions.to_html(),
                     'pred_file_upload_response': "N/A",
                     'post_import_file_response_code': "N/A",
                     'post_import_file_response_message': "Executed dry_run, so no import attempted.",
                     'model_timestamp_file_upload_response': "N/A",
                     'model_timestamp_post_import_file_response_code': "N/A",
                     'model_timestamp_post_import_file_response_message': "Executed dry_run, so no import attempted."
                     }

    return render_template('full_run.html', tables=[df_historical.to_html(), df_predictions.to_html()], full_run_data=full_run_data)


@app.route("/full_run_main")
def full_run_main():
    # TODO: Cache the data in case user navigate away, it doesn't have to re-run/re-calculate everything?
    df_historical, df_predictions, pred_file_upload_response, post_import_file_response, \
    model_timestamp_file_upload_response, model_timestamp_post_import_file_response = full_run.full_run_main(num_time_predict=30, dry_run=False, verbose=True)  # TODO: Get num_time_predict from user input

    full_run_data = {'df_historical': df_historical.to_html(),
                     'df_predictions': df_predictions.to_html(),
                     'pred_file_upload_response': pred_file_upload_response,
                     'post_import_file_response_code': post_import_file_response.json()['status']['code'],
                     'post_import_file_response_message': post_import_file_response.json()['status']['message'],
                     'model_timestamp_file_upload_response': model_timestamp_file_upload_response,
                     'model_timestamp_post_import_file_response_code': model_timestamp_post_import_file_response.json()['status']['code'],
                     'model_timestamp_post_import_file_response_message': model_timestamp_post_import_file_response.json()['status']['message']
                     }

    return render_template('full_run.html', tables=[df_historical.to_html(), df_predictions.to_html()], full_run_data=full_run_data)  # tables=[df_predictions.to_html()],


@app.route("/monitor_anaplan")  # TODO: Should this route be linked to "/" so it executes immediately? Or require user input to begin?
def monitor_anaplan():
    # TODO: Create/use function in anaplan_connect_helper_functions -- monitor actions stream, and whenever one changes, execute full_run()
    # Will have to generate user auth token -- make sure to use this with the rest of the app? Don't regenerate every time.
    # Represent "button press" as a model action?
    # Possible to continuously monitor? Or instead, get a snapshot every X seconds? Take snapshot initially, then monitor every X seconds
    pass