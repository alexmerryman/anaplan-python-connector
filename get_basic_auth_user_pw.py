import base64


def anaplan_basic_auth_user(user_email, user_pwd):
    basic_auth_user = 'Basic ' + str(base64.b64encode(f'{user_email}:{user_pwd}'.encode('utf-8')).decode('utf-8'))

    return basic_auth_user


if __name__ == '__main__':
    basic_user = anaplan_basic_auth_user()
