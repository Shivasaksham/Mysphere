from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload

import io
from io import BytesIO



class API_service:
    def __init__(self,token=""):
        self.token_path = token
        self.creds = Credentials.from_authorized_user_file(self.token_path)
        self.service = build('drive', 'v3', credentials=self.creds)
        pass

    def build_service(self):
        try:
            self.creds = Credentials.from_authorized_user_file(self.token_path)
            self.service = build('drive', 'v3', credentials=self.creds)
        except:
            print("")

    def is_network_available(self, test_url="https://www.googleapis.com", timeout=3):
        try:
            response = requests.get(test_url, timeout=timeout)
            return response.status_code == 200
        except requests.RequestException:
            return False


    def my_info(self):
        # Get information about the user
        about = self.service.about().get(fields="user").execute()
        # Print user information
        user_info = about.get('user', {})

        # print("User Information:")
        # print(f"User ID: {user_info.get('permissionId')}")
        # print(f"Display Name: {user_info.get('displayName')}")
        # print(f"Email Address: {user_info.get('emailAddress')}")


        return [user_info.get('displayName'),user_info.get('emailAddress')]

    def get_folder_size(self, folder_id):
        """
        Calculates the total size of all files inside a given Google Drive folder (recursively).

        Returns size in bytes.
        """
        total_size = 0
        page_token = None
        query = f"'{folder_id}' in parents and trashed = false"

        try:
            while True:
                response = self.service.files().list(
                    q=query,
                    fields="nextPageToken, files(id, name, mimeType, size)",
                    pageToken=page_token
                ).execute()

                for file in response.get('files', []):
                    if file['mimeType'] == 'application/vnd.google-apps.folder':
                        # Recursive call for subfolder
                        total_size += self.get_folder_size(file['id'])
                    else:
                        file_size = int(file.get('size', 0))
                        total_size += file_size

                page_token = response.get('nextPageToken', None)
                if not page_token:
                    break

        except Exception as e:
            print(f"Error while calculating folder size: {e}")

        return total_size

    def get_drive_storage_info(self,):
        """
        Fetches total, used, and remaining storage from Google Drive.
        """
        try:
            response = self.service.about().get(fields="storageQuota").execute()
            quota = response.get('storageQuota', {})

            total = int(quota.get('limit', 0))
            used = int(quota.get('usage', 0))
            used_in_drive = int(quota.get('usageInDrive', 0))
            remaining = total - used if total else None  # None means unlimited

            return {
                "total": total,
                "used": used,
                "used_in_drive": used_in_drive,
                "remaining": remaining
            }
        except Exception as e:
            print(f"Error getting storage info: {e}")
            return None

    def read_folder(self):
        # List folders
        results = self.service.files().list(q="mimeType='application/vnd.google-apps.folder'",fields="files(id, name)").execute()
        return results.get('files', [])

    def get_folder(self,name):
        folders = self.read_folder()
        folder_id = []
        for folder in folders:
            # print(folder)
            if folder["name"] == name:
                folder_id.append(folder["id"])

            else:
                pass

        return folder_id[0]

    def get_file(self, name,type=""):
        if type=="":
            folders = self.list_files()
        else:
            folders = self.list_files(type="root")


        folder_id = []
        for folder in folders:
            # print(folder)
            if folder["name"] == name:
                folder_id.append(folder["id"])

            else:
                pass

        return folder_id[0]


    def list_sub_files(self,folder_id):
        results = self.service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name, parents)").execute()
        return results.get('files', [])

    def list_sub_file_name(self,folder_id):
        results = self.service.files().list(q=f"'{folder_id}' in parents", fields="files(name)").execute()
        files = results.get('files', [])
        file_name = []
        for i in files:
            file_name.append(i["name"])


        return file_name

    def list_files(self,type=""):
        if type=="":
            results = self.service.files().list(fields="files(id, name, parents)").execute()
            files = results.get('files', [])

            return files

        elif type=="root":
            query = "'me' in owners and trashed = false"
            results = self.service.files().list(
                q=query,
                fields="files(id, name, parents)"

            ).execute()

            # fields = "files(id, name, mimeType, owners(displayName, emailAddress), modifiedTime)"

            files = results.get('files', [])

            return files






    def find(self,name):
        try:
            file = self.get_file(name=name)
            if len(file)>=1:
                return True

            else:
                return False

        except:
            return False

    def find_parent(self,name,type=None):
        result = self.find(name=name)
        if result==True:
            if type=="folder" or type=="" or type==None:
                id = self.get_folder(name=name)
            elif type=="file":
                id = self.get_file(name=name)

            metadata = self.list_files()
            if id=="":
                return None

            else:
                parent = None
                for meta in metadata:
                    if meta["id"]==id:
                        parent = meta["parents"]

                        # print(meta["parents"])
                    else:
                        pass
                return parent[0]

        else:
            return None

    def find_file_in_folder(self, parent_folder_id, target_name, is_folder=False):
        try:
            mime_query = " and mimeType='application/vnd.google-apps.folder'" if is_folder else ""
            query = f"'{parent_folder_id}' in parents and name = '{target_name}' and trashed = false{mime_query}"

            response = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType, parents)"
            ).execute()

            files = response.get('files', [])
            if files:
                return files[0]  # Return the first match
            else:
                print(f"No file or folder named '{target_name}' found in folder ID '{parent_folder_id}'.")
                return False
        except Exception as e:
            print(f"Error searching for file: {e}")
            return None

    def get_name_by_id(self,file_id):
        try:
            file = self.service.files().get(fileId=file_id, fields="name, mimeType").execute()
            return file['name']
        except Exception as e:
            print(f"Error fetching name for ID {file_id}: {e}")
            return None

    def create_folder(self,folder,parent=""):
        if parent!="":

            try:
                folder_metadata = {
                    'name': folder,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [parent]
                }
            except:
                print("Invalid id")

        else:
            folder_metadata = {
                'name': folder,
                'mimeType': 'application/vnd.google-apps.folder',
            }

        # Create the folder
        prev_parent = self.find_parent(name=folder)
        # print(prev_parent)

        if (prev_parent==parent) or (prev_parent != None and parent==""):
            print("Folder already exist")
            pass

        else:
            Folder = self.service.files().create(body=folder_metadata, fields='id').execute()
            print(f'Folder created with ID: {Folder.get("id")}')



        # Folder = self.service.files().create(body=folder_metadata, fields='id').execute()
        # print(f'Folder created with ID: {Folder.get("id")}')

    def create_file(self,file_name, content, parent="",type=""):
        if type=="zip":
            try:
                file_metadata = {
                    'name': file_name,
                    'mimeType': 'application/zip',
                    'parents': [parent]
                }

                # Create a BytesIO object to represent the file content
                content_stream = io.BytesIO(content.encode())

                # Create a MediaIoBaseUpload object to upload the file content
                media = MediaIoBaseUpload(content_stream, mimetype='text/plain', resumable=True)

                # Create the file
                # file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                # print(f"File : {file_name} is created in {parent}")
                # return file

                prev_parent = self.find_parent(name=file_name,type="file")
                # print(prev_parent)

                if (prev_parent==parent) or (prev_parent != None and parent==""):
                    print("File already exist")
                    pass

                else:
                    file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                    print(f"File : {file_name} is created in {parent}")
                    return file



            except:
                print("Invalid id")

        elif parent!="" and type!="zip":
            file_metadata = {
                'name': file_name,
                'mimeType': 'text/plain',
                'parents': [parent],
            }

            # Create a BytesIO object to represent the file content
            content_stream = io.BytesIO(content.encode())

            # Create a MediaIoBaseUpload object to upload the file content
            media = MediaIoBaseUpload(content_stream, mimetype='text/plain', resumable=True)

            # Create the file
            # file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            # print(f"File : {file_name} is created. in sub ")
            #
            # return file

            prev_parent = self.find_parent(name=file_name,type="file")
            # print(prev_parent)

            if (prev_parent==parent) or (prev_parent != None and parent==""):
                print("File already exist")
                pass

            else:
                file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                print(f"File : {file_name} is created in {parent}")
                return file






        else:
            file_metadata = {
                'name': file_name,
                'mimeType': 'text/plain',

            }

            # Create a BytesIO object to represent the file content
            content_stream = io.BytesIO(content.encode())

            # Create a MediaIoBaseUpload object to upload the file content
            media = MediaIoBaseUpload(content_stream, mimetype='text/plain', resumable=True)

            # Create the file
            # file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            # print(f"File : {file_name} is created. ")
            #
            # return file

            prev_parent = self.find_parent(name=file_name,type="file")
            # print(prev_parent)

            if (prev_parent==parent) or (prev_parent != None and parent==""):
                print("File already exist")
                pass

            else:
                file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                print(f"File : {file_name} is created in {parent}")
                return file



    def add_content(self, file_id, additional_text):
        # Retrieve the current content of the text file
        file = self.service.files().get_media(fileId=file_id).execute()
        current_content = file.decode('utf-8')

        # Append the new text to the current content
        new_content = current_content + additional_text

        # Convert the new content to a BytesIO object
        media = MediaIoBaseUpload(BytesIO(new_content.encode('utf-8')), mimetype='text/plain')

        # Update the file's content with the combined text
        updated_file = self.service.files().update(fileId=file_id, media_body=media).execute()
        print("File updated successfully")
        # print(f'Text appended to file with ID {file_id} successfully.')


    def update_file(self,file_id, new_content):
        # Convert the new content to a BytesIO object
        media = MediaIoBaseUpload(BytesIO(new_content.encode('utf-8')), mimetype='text/plain')

        # Update the file's content with the combined text
        updated_file = self.service.files().update(fileId=file_id, media_body=media).execute()
        print("File updated successfully")
        # print(f'Text appended to file with ID {file_id} successfully.')


    def upload_file(self,file_path, folder_id=None):
        file_metadata = {'name': file_path.split('/')[-1]}  # Use the filename as the name in Drive

        if folder_id:
            file_metadata['parents'] = [folder_id]

        media = MediaFileUpload(file_path)
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f'File ID: {file["id"]} is uploaded.')

        return file['id']

    def delete(self,id):
        # Delete the folder/file itself
        self.service.files().delete(fileId=id).execute()

    def read_file(self,file_id):
        # Use files().get_media() to retrieve the file content
        request = self.service.files().get_media(fileId=file_id)

        # Use a BytesIO object to store the content
        content_stream = io.BytesIO()

        # Download the file content in chunks and write it to the BytesIO object
        downloader = MediaIoBaseDownload(content_stream, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

        # Reset the stream position to the beginning
        content_stream.seek(0)

        # Read the content from the BytesIO object
        content = content_stream.read()

        return content.decode()

    def share(self,file_id, email_address, role=""):
        if role in ["reader","writer","commenter"]:
            try:
                permission = {
                    'type': 'user',
                    'role': role,
                    'emailAddress': email_address
                }

                permission = self.service.permissions().create(fileId=file_id, body=permission, fields='id').execute()
                print(f'Shared file with ID {file_id} with user {email_address} successfully.')

            except:
                pass

        else:
            print("Invalid role")

    def upload_zip_file(self,filename,zip_file_path, folder_id=None):
        file_metadata = {'name': f'{filename}.zip'}  # Change the file name as needed

        if folder_id:
            file_metadata['parents'] = [folder_id]

        media = MediaFileUpload(zip_file_path, mimetype='application/zip')
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f'File ID: {file["id"]} is uploaded. ' )


    def Give_permission(self, file_id, email_address, role=""):
        permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email_address
        }

        # Create the permission
        self.service.permissions().create(
            fileId=file_id,
            body=permission,
            fields='id'
        ).execute()

        print(f'Permission granted to {email_address}')

    def remove_permission(self,file_id,permission_id):
        # Remove the permission
        self.service.permissions().delete(
            fileId=file_id,
            permissionId=permission_id
        ).execute()

        print(f'Permission with ID {permission_id} removed')

    def view_permission(self,file_id):
        try:
            # List the permissions for the file
            permissions = self.service.permissions().list(fileId=file_id,
                                                     fields='permissions(id, role, type, emailAddress)').execute()

            items = permissions.get('permissions', [])
            return items

        except Exception as e:
            print(f"An error occurred: {e}")


    def list_shared_with_me_files(self,):
        # Use the query to find files shared with the current user
        query = "sharedWithMe"
        results = self.service.files().list(q=query, fields="files(id, name,mimeType, owners(displayName, emailAddress))").execute()
        items = results.get('files', [])

        return items



        # if not items:
        #     print('No files found.')
        # else:
        #     print('Files:')
        #     for item in items:
        #         owner = item['owners']
        #
        #         print(f"{item['name']} ({item['id']})  {owner['displayName']} {owner['emailAddress']}")


    def list_shared_with_me_files_name(self,):
        # Use the query to find files shared with the current user
        query = "sharedWithMe"
        results = self.service.files().list(q=query, fields="files(name)").execute()
        items = results.get('files', [])

        file_name = []

        for files in items:
            file_name.append(files["name"])

        return file_name






















