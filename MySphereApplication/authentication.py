import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class UserAuth:
    def __init__(self,id="",username="",credential=""):
        self.user_id = id
        self.username = username
        self.cred_path = credential
        self.scope = ["https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
        self.auth_status = False


    def authenticate(self):

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists(f"{self.user_id}_token.json"):
            creds = Credentials.from_authorized_user_file(f"{self.user_id}_token.json", self.scope)
            print("Already Authenticated")

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("Refreshing token")
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.cred_path, self.scope)
                creds = flow.run_local_server(port=0)

                # Save the credentials for the next run
                with open("token.json", "w") as token:
                    token.write(creds.to_json())

        else:
            print("No need to refresh")

        self.auth_status = True

    def authenticate_signup(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self.scope)
            print("Already Authenticated")

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.cred_path, self.scope)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        self.auth_status = True










# id = input("Enter your id : ")
# username = input("Enter your username : ")
# cred = "credentials.json"
#
# conn = Dev_environment(id=id,username=username,credential=cred)
# conn.authenticate()































