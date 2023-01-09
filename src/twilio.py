from twilio.rest import Client


class TwilioClient:
    def __init__(self, config):
        self.to_num = config["TO_NUM"]
        self.from_num = config["FROM_NUM"]
        self.account_sid = config["ACCOUNT_SID"]
        self.auth_token = config["AUTH_TOKEN"]

    def send_message(self, message):
        client = Client(self.account_sid, self.auth_token)
        client.messages.create(to=self.to_num, from_=self.from_num, body=message)
