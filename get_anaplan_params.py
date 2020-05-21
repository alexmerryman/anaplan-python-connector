import anaplan_connect_helper_functions


def main(user_email, user_pwd, wGuid, mGuid, export_id):
    print('------------------- GENERATING AUTH TOKEN -------------------')
    token_auth_user = anaplan_connect_helper_functions.generate_token_auth_user(user_email, user_pwd)

    print('------------------- CREATING (POST) EXPORT TASK -------------------')
    anaplan_param_export_task_response, anaplan_param_export_task_json = anaplan_connect_helper_functions.post_export_task(
        wGuid, mGuid, export_id, token_auth_user)
    # print(anaplan_param_export_task_json)
    print("Export Task Status: ", anaplan_param_export_task_json['task']['taskState'])
    if anaplan_param_export_task_json['task']['taskState'] == 'NOT_STARTED':
        print('------------------- GETTING EXPORT TASK DETAILS -------------------')
        anaplan_param_export_task_details_response, anaplan_param_export_task_details_json = anaplan_connect_helper_functions.get_export_task_details(
            wGuid, mGuid, export_id, anaplan_param_export_task_json['task']['taskId'], token_auth_user)

    print("Export Task Status:", anaplan_param_export_task_details_json['task']['taskState'])
    # TODO: Make sure anaplan_param_export_task_details_json['task']['taskState'] == 'COMPLETED' ?

    print('------------------- GETTING FILE INFO (CHUNK METADATA) -------------------')
    chunk_metadata_response, chunk_metadata_json = anaplan_connect_helper_functions.get_chunk_metadata(wGuid, mGuid,
                                                                                                       export_id,
                                                                                                       token_auth_user)

    print('------------------- GETTING CHUNK DATA -------------------')
    for c in chunk_metadata_json['chunks']:
        # print('Chunk name, ID:', c['name'], ',', c['id'])
        chunk_data_response, chunk_data_text = anaplan_connect_helper_functions.get_chunk_data(wGuid,
                                                                                               mGuid,
                                                                                               export_id,
                                                                                               c['id'],
                                                                                               token_auth_user)
        if chunk_data_response.status_code == 200:
            # print(chunk_data_text)
            chunk_data_parsed_array = anaplan_connect_helper_functions.parse_chunk_data(chunk_data_text)
        else:
            print("ERROR: Chunk Data Response Status Code:", chunk_data_response.status_code)

    return chunk_data_parsed_array


if __name__ == "__main__":
    chunk_data_parsed_array = main('Anthony.Severini@teklink.com', 'Steelerssoccera1219_1',
                                   '8a81b08e4f6d2b43014fbe11122a160c', '96339A3A48394142A3E70E057F75480E',
                                   '116000000005')
    print(chunk_data_parsed_array)
