from flask import render_template
from flask_app import app
import test_main
import full_run


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Alex'}
    return render_template('index.html', title='Anaplan-Python Connector Flask App', user=user)


@app.route("/test_main")
def test_main_route_def():
    data = test_main.main()
    return render_template('test_main.html', data=data)


@app.route("/full_run_simdata")
def full_run_simdata():
    df_predictions, pred_file_upload_response, post_import_file_response, model_timestamp_file_upload_response, \
    model_timestamp_post_import_file_response = full_run.main(sim_data=True, verbose=True, dry_run=True)

    full_run_data = {'df_predictions': df_predictions.to_html(),
                     'pred_file_upload_response': pred_file_upload_response,
                     'post_import_file_response_code': post_import_file_response.json()['status']['code'],
                     'post_import_file_response_message': post_import_file_response.json()['status']['message'],
                     'model_timestamp_file_upload_response': model_timestamp_file_upload_response,
                     'model_timestamp_post_import_file_response_code': model_timestamp_post_import_file_response.json()['status']['code'],
                     'model_timestamp_post_import_file_response_message': model_timestamp_post_import_file_response.json()['status']['message']
                     }

    return render_template('full_run.html', tables=[df_predictions.to_html()], full_run_data=full_run_data)
