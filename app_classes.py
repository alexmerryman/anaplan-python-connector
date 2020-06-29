import datetime
import time


class AnaplanUserAuthToken:
    def __init__(self, token_json_obj, expiry_buffer=180):
        self.creation_status = token_json_obj['status']
        self.creation_status_message = token_json_obj['statusMessage']
        self.expiry_millisec = token_json_obj['tokenInfo']['expiresAt']
        self.id = token_json_obj['tokenInfo']['tokenId']
        self.token_value = token_json_obj['tokenInfo']['tokenValue']
        self.refresh_id = token_json_obj['tokenInfo']['refreshTokenId']
        self.expiry_buffer = expiry_buffer
        self.auth_token_string = ""

    # Anaplan API ['tokenInfo']['expiresAt'] is returned in milliseconds elapsed since epoch time -- divide by 1000 to get seconds
    # https://www.epochconverter.com/

    def expiry_sec(self):
        return self.expiry_millisec/1000.

    def remaining_sec(self):
        return self.expiry_sec() - int(time.time())

    def expiry_formatted(self):
        return datetime.datetime.fromtimestamp(self.expiry_sec()).strftime('%I:%M:%S %p, %m/%d/%Y')

    def expired_status(self):
        return self.remaining_sec() < self.expiry_buffer
