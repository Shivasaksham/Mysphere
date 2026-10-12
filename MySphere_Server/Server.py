from authentication import *
from API_services import *
from cryptography.fernet import Fernet
import base64, hashlib
import os
import string
import random

import threading


'''
This class is created to serve as server for the MS application

1. On executing, It should starts with authentication & setting up the server database
   configuration for the first time & while running it after setup should only recheck the DB
   setup configuration ,if any file miss it should re-create it.
   
2. There should be some services available made using the API services for the functional and 
   operational usage for the server
   1. To read users info
   2. To update the user data in the server
   3. To add new user
   4. To delele user data
   5. To confirm user identity
   6. 
   
3. It will great, if server works itself & perform routine task periodically.
4. It should notify for incoming request or outgoing request wherever required.
5. All the data should be secure with end to end encryption by using fernet algorithm.


IMPORTANT DECLARATION
1. For available user detail (anyone type)
2. A dic {userid : vault id}






'''

class server:
    def __init__(self,token=""):
        self.token = token
        self.auth_status = False
        self.json_file_id = ""
        self.auto_check = True



        self.authenticate()
        self.create_service()

        pass

    def authenticate(self):
        print("SERVER INITIALIZED")
        print("Verifying Authentication.....")
        print()
        auth = UserAuth(credential="server_credentials.json")
        auth.authenticate()
        print("--------------------------------------------")

        self.auth_status = auth.auth_status

    def create_service(self):
        self.service = API_service(token=self.token)

        try:
            self.json_file_id = self.service.get_file(name="User.json")

        except:
            pass

    def server_setup(self):
        # Creating folder for Mysphere vault
        self.service.create_folder(folder="Server")

        id = self.service.get_folder(name="Server")
        print(id)

        # Creating file to store users credentials
        self.service.create_file(file_name="User.json",content="",parent=id)




        pass

    def read_user_acccont(self):
        # To check new

        self.vault_folders_id = []
        self.user_json_file_id = []

        user_application = self.service.list_shared_with_me_files()

        # available_user_id = self.available_users_id()

        print("AVAILABLE USER ACCOUNT (MYSPHERE SERVER)")
        print("--------------------------------------------")

        for application in user_application:
            # print(application)
            if application["name"] == "MySphere Vault":
                folder_id = application["id"]
                print((application["owners"])[0]["emailAddress"])
                self.vault_folders_id.append(folder_id)

            else:

                pass
        print("--------------------------------------------")
        print("Available account Id - ",self.vault_folders_id)

        # Adding new user if any exist
        for id in self.vault_folders_id:
            files = self.service.list_sub_files(folder_id=id)

            for file in files:
                if ".json" in file["name"]:  # Use userid as identifier
                    # print(file["id"])
                    id = file["id"]

                    data = self.read_files_encrypted(id=id)
                    print(data)


                    # Adding user data to our server
                    self.service.add_content(file_id=self.json_file_id,additional_text=data+"\n")

                else:
                    pass

    def check_new_account(self):
        # Checking for new user access request


        user_application = self.service.list_shared_with_me_files()
        available_vault_id = self.available_vault_id()
        # print(available_vault_id)
        new_vault_id = []
        user_account_id = {}
        user_rose_id = {}
        user_dev_file_id = {}

        for application in user_application:
            # print(application)
            if application["name"] == "MySphere Vault":
                folder_id = application["id"]
                account_id = (application["owners"])[0]["emailAddress"]
                print(account_id)

                if folder_id not in available_vault_id:

                    new_vault_id.append(folder_id)
                    user_account_id.update({folder_id:account_id})


                else:
                    pass

            else:
                pass

        if len(new_vault_id)>=1:
            print("Adding new user to server ...")
            # print(account_id)
            self.add_new_user(folder_id_list=new_vault_id,address=user_account_id)

        else:
            print("No new user found !")

    def add_new_user(self,folder_id_list,address):
        # Adding new user if any exist
        for vault_id in folder_id_list:
            files = self.service.list_sub_files(folder_id=vault_id)

            for file in files:
                if ".json" in file["name"]:  # Use userid as identifier
                    # print(file["id"])
                    id = file["id"]

                    data = self.read_files_encrypted(id=id)
                    print(data)

                    # Adding user data to our server
                    self.service.add_content(file_id=self.json_file_id, additional_text=data + "\n")



                else:
                    pass

            # Giving access to read our json file from server
            email_id = address[vault_id]
            self.service.share(file_id=self.json_file_id, email_address=email_id, role="reader")


    def generate_manual_key(self,password):
        # Convert password to bytes and hash it using SHA-256
        hashed = hashlib.sha256(password.encode()).digest()

        # Encode the hash in base64 (Fernet requires this format)
        key = base64.urlsafe_b64encode(hashed)

        return key

    def encrypt_text(self,data):
        # Algorithm for encrypting given the text
        # Remember to use the same key while decrypting the text

        # Only for id.JSON
        # The key should be same for the json file that is available in the user vault of each user

        key = self.generate_manual_key("7")
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data+",".encode())

        encrypted_data = str(encrypted_data)[2:-1]

        return encrypted_data

    def decrypt_text(self,encrypted_data):
        # Algorithm for decrypting given the text

        # Only for id.JSON
        # The key should be same for the json file that is available in the user vault of each user

        key = self.generate_manual_key("7")
        fernet = Fernet(key)

        decrypted_data = fernet.decrypt(encrypted_data)

        return decrypted_data.decode()

    def read_files_encrypted(self,id):
        # To read the content of the file without decrypting it
        # It will return only the raw data of the file
        data = self.service.read_file(file_id=id)

        return data

    def read_files_decrypted(self,id):
        # To read the file after decrypting it

        # TO REMEMBER : The format of the file should be like qwertyuioplkjhfda\nqazxswedcvfr\n
        # only such file will be decoded by the used algorithm

        data = self.service.read_file(file_id=id)
        # print(data)
        content = data[0:-1].split("\n")

        decrypted_data = []

        for line in content:
            decrypted_line = self.decrypt_text(encrypted_data=line)
            decrypted_data.append(decrypted_line)

        return decrypted_data

    def read_userjson_server(self,):
        # To read the data available in the userjson file in the server
        data = self.read_files_decrypted(id=self.json_file_id)

        user_info_list = []
        for info in data:
            user_info_list.append(info)


        return user_info_list

    def available_users_id(self):
        # To get the user ID
        data = self.read_userjson_server()

        user_id = []
        for field in data:
            id = (eval(field))["userid"]
            user_id.append(id)


        return user_id

    def available_username(self):
        # To get the username
        data = self.read_userjson_server()

        user_name = []
        for field in data:
            name = (eval(field))["username"]
            user_name.append(name)


        return user_name

    def available_vault_id(self):
        # To get the user ID
        try:
            data = self.read_userjson_server()
            vault_id = []
            for field in data:
                id = (eval(field))["Vault ID"]
                vault_id.append(id)
        except:
            vault_id = []


        return vault_id

    def fetch_userinfo(self,id):
        # To fetch all the info of the user by ID
        data = self.read_userjson_server()

        user_info = []
        for field in data:
            userid = (eval(field))["userid"]

            if userid == id:
                user_info.append((eval(field)))

            else:
                pass

        if len(user_info)==1:
            return user_info[0]

        else:
            return "No user available with this ID"

    def fetch_username(self,id):
        # To fetch the username by ID
        data = self.read_userjson_server()

        user_name = []

        for field in data:
            userid = (eval(field))["userid"]

            if userid == id:
                name = (eval(field))["username"]
                user_name.append(name)

            else:
                pass

        if len(user_name) == 1:
            return user_name[0]

        else:
            return "No user available with this ID"

    def delete_userjson_server(self):
        # For deleting the json file in the server
        self.service.delete(id=self.json_file_id)


    def auto_check_new_user(self):
        if self.auto_check == True:
            def watchman():
                self.check_new_account()
                self.auto_check_new_user()

            threading.Timer(10, watchman).start()
            # threading.Thread(target=watchman()).start()

        else:
            pass




server = server(token="token.json")
# server.server_setup()
# server.read_user_acccont()
# print(server.read_userjson_server())
# server.delete_userjson_server()
# server.check_new_account()
# server.auto_check_new_user()

# print(server.fetch_username(id='OzbxcxR'))
print(server.available_username())
# print(server.available_users_id())