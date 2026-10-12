from authentication import *
from API_services_backend import *
from cryptography.fernet import Fernet
import base64, hashlib
import os
import string
import random
import json
import time



class application_backend:
    def __init__(self,token=""):
        self.token = token
        self.user_id = "BmXD95a"
        self.user = ""      # Username
        self.user_key = "" # Password
        self.vault_id = ""
        self.user_json_file_id = ""
        self.fms_file_id = ""
        self.key = self.generate_manual_key("Mysphere1234")


        # self.authenticate()
        # self.create_service()
        # self.application_setup()


    def authenticate(self):
        auth = UserAuth(id=self.user_id,credential="credentials1.json")
        auth.authenticate()

        self.auth_status = auth.auth_status
        return self.auth_status

    def authenticate_signup(self):
        auth = UserAuth(id=self.user_id, credential="credentials1.json")
        auth.authenticate_signup()

        self.auth_status = auth.auth_status
        return self.auth_status

    def create_service(self,):
        self.service = API_service(token=self.token)

        try:
            self.vault_id = self.service.get_folder(name="MySphere Vault")
            print(self.vault_id)

            self.user_email_address = self.service.my_info()[1]

            self.user_json_file_id = self.service.get_file(name=f"{self.user_id}.json")
            print(self.user_json_file_id)

            # self.service.create_file(file_name=f"{self.user_id}friends.ms", content="", parent=self.vault_id)
            self.fms_file_id = self.service.get_file(name=f"{self.user_id}friends.ms")

            self.available_files = self.read_mysphere_vault()

        except:
            pass

    def application_setup(self):
        # Creating a setup for the application to run backend
        print("Starting application setup...")
        # Creating folder for Mysphere server
        self.service.create_folder(folder="MySphere Vault")

        self.vault_id = self.service.get_folder(name="MySphere Vault")
        print("USER MYSPHERE VAULT ID : ",self.vault_id)

        # Creating user info
        user_info = self.create_user_info()
        print("USER INFO ENCRYPTED","\n"+(user_info))

        # Creating file to store users credentials
        self.service.create_file(file_name=f"{self.user_id}.json", content=user_info, parent=self.vault_id)

        # Token file

        self.service.create_file(file_name=f"{self.user_id}Rose.cf", content="", parent=self.vault_id)
        self.service.create_file(file_name=f"{self.user_id}Dev.cf", content="", parent=self.vault_id)

        self.service.create_file(file_name=f"{self.user_id}friends.ms", content="", parent=self.vault_id)

        self.user_json_file_id = self.service.get_file(name=f"{self.user_id}.json")
        print("USER JSON FILE ID : ",self.user_json_file_id)

        # Sharing file with server
        self.share_to_server(file_id=self.vault_id,role="writer")

        pass

    def create_user_info(self):
        def generate_user_id(length):
            characters = string.ascii_letters + string.digits
            return ''.join(random.choices(characters, k=length))

        self.user_id = generate_user_id(length=7)
        print("Generated ID: ", self.user_id)

        self.user_email_address = self.service.my_info()[1]

        token_credentials = self.read_jsonfile(filename="token.json")
        refresh_token = token_credentials[0]
        client_id = token_credentials[1]
        client_secret = token_credentials[2]

        user_data = {
            "userid": self.user_id,
            "username": self.user,
            "password": self.user_key,
            "personalization_status": True,
            "Vault ID": self.vault_id,
            "Email ID": self.user_email_address,
            "token": refresh_token,
            "Client ID": client_id,
            "Client secret": client_secret,


        }

        print("USER INFO", "\n" + str(user_data))

        # Encrypting user file
        encrypted_user_data = self.encrypt_text(str(user_data))

        return encrypted_user_data

    def share_to_server(self,file_id,role):
        # Sharing folder/file with server
        self.service.share(file_id=file_id,email_address="go.mysphere@gmail.com",role=role)

    def write_file_into_user_json(self,data):
        self.service.update_file(file_id=self.user_json_file_id,new_content=data)

        # Onhold

    def read_jsonfile(self,filename):
        # Open and load the JSON file

        with open(filename, 'r') as file:
            data = json.load(file)

        return [data['refresh_token'],data["client_id"],data["client_secret"]]


    def generate_manual_key(self,password):
        # Convert password to bytes and hash it using SHA-256
        hashed = hashlib.sha256(password.encode()).digest()

        # Encode the hash in base64 (Fernet requires this format)
        key = base64.urlsafe_b64encode(hashed)

        return key

    def encrypt_file(self,file_path):

        # Creating folder to save uploading file
        os.makedirs("Upload", exist_ok=True)

        fernet = Fernet(self.key)
        with open(file_path, 'rb') as file:
            original_data = file.read()

        encrypted_data = fernet.encrypt(original_data)
        print(encrypted_data)

        # path = "C:/Python3.10/CV2/Image Processing/output_image2.jpg"
        path = file_path.split("/")[-1]

        self.uploading_file = "Upload\\"+path + ".enc"
        with open("Upload\\"+path + ".enc", 'wb') as enc_file:
            enc_file.write(encrypted_data)
        print(f"[+] Encrypted to: Upload\\{path}.enc")

    def decrypt_file(self,enc_path, output_folder="activated_file"):
        try:
            fernet = Fernet(self.key)
            print(f"Decrypting: {enc_path}")

            with open(enc_path, 'rb') as enc_file:
                encrypted_data = enc_file.read()

            decrypted_data = fernet.decrypt(encrypted_data)

            # Create output folder if it doesn't exist
            os.makedirs(output_folder, exist_ok=True)

            # Get original filename by removing .enc
            base_filename = os.path.basename(enc_path)
            if base_filename.endswith(".enc"):
                output_filename = base_filename[:-4]
            else:
                output_filename = base_filename + ".dec"

            output_path = os.path.join(output_folder, output_filename)

            with open(output_path, 'wb') as out_file:
                out_file.write(decrypted_data)

            print(f"[+] Decrypted to: {output_path}")

            return output_path

        except Exception as e:
            print(f"[!] Failed to decrypt: {e}")


    def decrypt_file_local(self,enc_path, output_folder):
        try:
            fernet = Fernet(self.key)
            print(f"Decrypting: {enc_path}")

            with open(enc_path, 'rb') as enc_file:
                encrypted_data = enc_file.read()

            decrypted_data = fernet.decrypt(encrypted_data)

            # Create output folder if it doesn't exist
            os.makedirs(output_folder, exist_ok=True)

            # Get original filename by removing .enc
            base_filename = os.path.basename(enc_path)
            if base_filename.endswith(".enc"):
                output_filename = base_filename[:-4]
            else:
                output_filename = base_filename + ".dec"

            output_path = os.path.join(output_folder, output_filename)

            with open(output_path, 'wb') as out_file:
                out_file.write(decrypted_data)

            print(f"[+] Decrypted to: {output_path}")

            return output_path

        except Exception as e:
            print(f"[!] Failed to decrypt: {e}")

    def encrypt_text(self,data):
        key = self.generate_manual_key("7")
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data.encode())

        encrypted_data = str(encrypted_data)[2:-1]

        return encrypted_data

    def decrypt_text(self,encrypted_data):
        key = self.generate_manual_key("7")
        fernet = Fernet(key)

        decrypted_data = fernet.decrypt(encrypted_data)

        return decrypted_data.decode()

    def download_file1(self,file_name, save_to='Download'):
        # After checking the download folder then add the file
        self.available_files = self.read_mysphere_vault()

        for file in self.available_files:
            filename = file["name"]

            if file_name == filename:
                file_id = file["id"]
                file_path = self.service.download(file_id=file_id,file_name=filename,save_to="Download")
                path = self.decrypt_file(file_path)

                return path

            else:
                pass

    def download_file(self,id,filename, save_to='Download'):
        # After checking the download folder then add the file

        file_path = self.service.download(file_id=id, file_name=filename, save_to="Download")
        path = self.decrypt_file(file_path)

        return path

    def download_file_to_local(self,id,filename, save_to):
        # After checking the download folder then add the file

        file_path = self.service.download(file_id=id, file_name=filename, save_to="Download")
        path = self.decrypt_file_local(file_path,save_to)

        return path

    def read_mysphere_vault(self):
        # Read the folder available in the vault
        folder = self.service.list_sub_files(folder_id=self.vault_id)
        return folder

    def read_current_dir(self,id):
        # read the current folder
        folder = self.service.list_sub_files(folder_id=id)
        return folder

    def upload_file(self,filepath,id=""):
        # Encrypt the file first

        encrypt = self.encrypt_file(file_path=filepath)
        if id=="":
            self.service.upload_file(file_path=self.uploading_file,folder_id=self.vault_id,)

        else:
            self.service.upload_file(file_path=self.uploading_file, folder_id=id)

    def delete_account(self):
        # Delete the account
        self.service.delete(id=self.vault_id)
        print("Your account is deleted")

    def delete_file(self,name):
        # Delete specific file

        for file in self.available_files:
            file_name = file["name"]

            if file_name == name:
                file_id = file["id"]
                self.service.delete(file_id)
                print(name,"is deleted successfully")

            else:
                pass

    def create_file(self,filename,content,parent):
        # Assigned
        self.service.create_file(file_name=filename,content=content,parent=parent)
        pass

    def create_folder(self,folder):
        # Assigned
        self.service.create_folder(folder=folder,parent="")
        pass

    def share_with_friend(self,fileid,email_add,role):
        # Assigned
        self.service.share(file_id=fileid,email_address=email_add,role=role)
        pass

    def add_friend(self):
        # Assigned
        pass

    def rename(self,id,name):
        self.service.rename_item(file_id=id,new_name=name)

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

    def read_userjson_server(self,id):
        # To read the data available in the userjson file in the server
        data = self.read_files_decrypted(id=id)

        user_info_list = []
        for info in data:
            user_info_list.append(eval(info))

        return user_info_list

    def view_app_users(self):

        user_application = self.service.list_shared_with_me_files()
        user_dic = {}
        for application in user_application:
            # print(application)
            if (application["name"] == "User.json") and ((application["owners"])[0]["emailAddress"]=="go.mysphere@gmail.com"):
                file_id = application["id"]

                # print((application["owners"])[0]["emailAddress"])
                data = self.read_userjson_server(id=file_id)

                for item in data:
                    name = item["username"]
                    email_id = item["Email ID"]

                    user_dic.update({email_id:name})

                return user_dic

            else:
                data = []

    def list_sharedwithme_files(self):
        shared_with_me_files = self.service.list_shared_with_me_files()

        user_dic = self.view_app_users()

        shared_with_me_files_list = {}


        dic = {'sigmasharmag5@gmail.com': {},
         'sakshamyadav260705@gmail.com': {'1ZeA5Eux-JHslsWeMCTvUw-Hq9vercLrQ': 'African Lion.jpg',
                                          '1weTrhlPZL_Sj_W3zHk3XqqTzUsD06q08DJoiiNJC1sA': 'hello1',
                                          '1nrsvhd0U67rXRfrKw2_6sk1kzoDzR1Ob': 'Developers_info.dcf',
                                          '1frtsEf_5yYSlkbTlnwj7vWqoVMPUv4cO': 'YADAVJI_SigmaBhaiya420.cb'}}

        for user in user_dic:
            file_list = {}
            container = {user:file_list}
            for file in shared_with_me_files:
                file_type = file["mimeType"]
                user_id = (file["owners"])[0]["emailAddress"]
                file_id = file["id"]
                file_name = file["name"]

                if user_id == user:
                    if "application / vnd.google - apps.folder" in file_type:
                        files = self.service.list_sub_file_name(folder_id=file_id)

                        if len(files)>0:
                            # Search sys folder
                            if "sys" in files:
                                # Add
                                item = {file_id: file_name}
                                file_list.update(item)
                                pass

                            else:
                                pass

                        else:
                            # Not a required folder for mysphere
                            pass


                    else:
                        # For file

                        if ".enc" in file_name:
                            # Mysphere file
                            item = {file_id: file_name}
                            file_list.update(item)
                            pass

                        else:
                            # Not a mysphere file testing
                            # item = {file_id: file_name}
                            # file_list.update(item)
                            pass

                else:
                    pass


            shared_with_me_files_list.update(container)

        # print("Mysphere files/folder",shared_with_me_files_list)



        return shared_with_me_files_list

    def write_into_friend_ms(self,content):
        data = self.encrypt_text(data=str(content))
        self.service.add_content(file_id=self.fms_file_id, additional_text=data + "\n")

    def update_friend_ms(self,content):
        c = 0
        for items in content:
            data = self.encrypt_text(data=str(items))
            if c == 0:
                self.service.update_file(file_id=self.fms_file_id, new_content=data + "\n")

            else:
                self.service.add_content(file_id=self.fms_file_id, additional_text=data + "\n")

            c = c + 1

    def read_friend_ms(self):
        data = self.read_files_decrypted(id=self.fms_file_id)

        return data

    def create_connection_file(self,content,friend_name,email_id):
        data = self.encrypt_text(data=str(content))
        self.service.create_file(file_name=f"{friend_name}_connection.ms", content=data+"\n", parent=self.vault_id)

        id = self.service.get_file(name=f"{friend_name}_connection.ms")

        self.service.share(file_id=id,email_address=email_id,role="writer")

        return id

    def read_and_update_friendms_file(self):
        data = self.read_friend_ms()

        # data = ["{'1qEHcn-ts32xXwcReKbzA4PV15WKUkgk1': {'status': 'pending', 'email': 'sakshamyadav260705@gmail.com', 'name': 'saksham yadav'}}"]
        # message1 = ['Garvit Sharma :: 28 Apr 2025 :: Hello, saksham yadav i would like to connect with you','Saksham :: 28 Apr 2025 :: No']

        updated_friend_ms_data = []

        changes = 0
        for file in data:
            field = eval(file)
            print(field)

            for item in field:
                file_id = item
                type = field[file_id]

                previous_status = type["status"]
                email_id = type["email"]
                name = type["name"]


                data = self.read_files_decrypted(id=file_id)

                # data = message1

                # "Yes, Ofcourse!"

                if len(data)>1:
                    message_split = data[1].split(" :: ")
                    reply = message_split[-1]
                    user_reply = reply.split(",")[0]


                    if user_reply == "Yes" and previous_status=="pending":
                        type["status"] = "True"
                        # print(field)

                        updated_friend_ms_data.append(field)
                        print(name, "accepted our request")
                        changes = changes+1

                    elif user_reply == "No" and previous_status=="pending":
                        type["status"] = "False"
                        # print(field)

                        # updated_friend_ms_data.append(field)
                        print(name,"rejected our request")

                        changes = changes+1

                        # Removing the file id key
                        # Delete the connection file

                    elif previous_status=="True":
                        updated_friend_ms_data.append(field)




                        pass

                else:
                    print("No update in friend list logs ")
                    updated_friend_ms_data.append(field)

        return updated_friend_ms_data,changes


    def see_connection_request(self):
        data = self.service.list_shared_with_me_files()

        connection_request_dic = []
        for file in data:
            if "_connection.ms" in file["name"]:

                user_id = (file["owners"])[0]["emailAddress"]
                file_id = file["id"]
                file_name = file["name"]

                request_args = {file_id:{"email id":user_id,"name":file_name}}

                connection_request_dic.append(request_args)
            else:
                pass


        return connection_request_dic

    def get_connection_file_id(self,email_id):
        data = self.service.list_shared_with_me_files()
        id = ""
        for file in data:
            if "_connection.ms" in file["name"]:

                user_id = (file["owners"])[0]["emailAddress"]
                file_id = file["id"]
                print(file)

                if user_id==email_id:
                    id = file_id

                    return id

                else:
                    pass

            else:
                pass



    def read_connection_file(self,id):

        data = self.read_files_decrypted(id=id)

        return data


    def write_connection_file(self,id,content):
        data = self.encrypt_text(data=str(content))
        self.service.add_content(file_id=id, additional_text=data + "\n")


    def delete_connection_file(self,file_id):
        data = self.read_mysphere_vault()

        if file_id=="":
            for items in data:
                if "_connection.ms" in items["name"]:
                    self.service.delete(id=items["id"])

                else:
                    pass

        else:
            for items in data:
                if items["id"]==file_id:
                    self.service.delete(id=items["id"])

                else:
                    pass

    def clear_friend_list(self):
        self.service.update_file(file_id=self.fms_file_id,new_content="")


    def myvault_space(self):
        space = self.service.get_folder_size(folder_id=self.vault_id)

        def format_gb(bytes_val):
            return f"{bytes_val / (1024 ** 3):.5f} GB"

        def fmt(b): return f"{b / (1024 ** 2):.5f} MB"

        size = fmt(space)

        return size

    def share_anyone(self,id):
        self.service.share_with_anyone(file_id=id)


































# app = application_backend("BmXD95a_token.json")
# app.authenticate()
# app.create_service()

# data = app.list_sharedwithme_files()
#
# for user_folder in data:
#     print()
#     if len(data[user_folder])>0:
#         user_data = data[user_folder]
#         print(user_folder)
#         for file_id in user_data:
#             file_name = user_data[file_id]
#             print(file_id, file_name)
#
#     else:
#         pass



# id = app.get_connection_file_id(email_id="sakshamyadav260705@gmail.com")
# print(id)
# #
# #
# space = app.myvault_space()
# print(space)
# print(app.read_friend_ms())

# data = app.read_and_update_friendms_file()
# friend_status = data[0]
# print(data)
# print(friend_status)
# print()




# app.delete_connection_file(file_id="")

# data = app.view_app_users()
# print(data)



# app.upload_file(filepath="Sample.png")
# app.delete_file(name="C:\\Python3.10\\mysphere\\MySphereGS\\Virtual Environment1\\Upload\\Sample.ms.enc")
# app.download_file(file_name='Sample.png.enc')

# app.delete_account()


# print(app.read_mysphere_vault())


# app.application_setup()

# data = b'gAAAAABoCNKSgAh1hGcbF14KMYP_LYBr5kYIhcK7okWtywD9mHZemzcmrfrT4AqEZTLPBaDV5sUIGU3NB3U1vw4FC_XZ74X1Pw=='

# print(app.decrypt_text(encrypted_data=data))
# print(type((data)))
# print(data)
# print(app.decrypt_text(encrypted_data=enc_data))
