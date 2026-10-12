import customtkinter
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from authentication import *
from EncrypterJSON import *
from DecryptorJSON import *
from PIL import Image
from pyzbar.pyzbar import decode
from PIL import Image, ImageTk
import cv2
import winsound
import time
import numpy as np
import random
import string
import threading
import os
import requests
import shutil
import json
from datetime import datetime, timedelta


from application_backend import *
from Server import *
from Qr_code_generator import *
from server_authentication import *


# Options: 'SystemAsterisk', 'SystemExclamation', 'SystemExit', 'SystemHand', 'SystemQuestion'

class user_interface:
    def __init__(self):
        self.root = customtkinter.CTk()
        self.geometry = self.root.geometry("1100x800")
        self.auth_status = None
        self.personalization_status = None
        self.user = ""
        self.user_key = ""
        self.user_id = ""
        self.user_age = ""
        self.user_profession = ""

        self.cap = None
        self.scanning = False
        self.line_y = 0
        self.direction = 1

        self.theme_color = "#fffbe6"
        # self.theme_color = "#f3e6ff"

        self.hover_theme = "#ebebeb"
        self.file_view_orientation = "Vertical"
        self.opened_folders = []
        self.opened_folder_name = []
        self.previous_opened_folder = []
        self.previous_opened_folder_name = []
        self.current_folder_id = ""
        self.selected_connection_file_id = ""
        self.selected_filename = ""



        self.friend_ms_data = []
        self.application_users = []
        self.available_connection_req_data = []
        self.friend_list = []
        self.friend_dic = {}
        self.email_friend = {}


        # New
        self.selected_path_id = ""
        self.right_selected_path_id = ""

        self.system_configuration()

    def system_configuration(self):
        customtkinter.set_appearance_mode("light")

    def user_info(self):
        # Read user.json file (contain user info,personalization status,)
        try:
            user_data = self.decryptJSON(filename="user.json", key=7)
            print(user_data)
        except:
            # File not there means need to be sign up
            self.user = False
            self.user_key = False
            print("Sign up before login")

    def encrytJSON(self,data,filename,key):
        # Save encrypted data
        save_encrypted_json(data,filename,key)

    def decryptJSON(self,filename,key):
        # Key used for encryption (must match)

        # Load and decrypt
        file_data = load_decrypted_json(filename,key)

        print("Decrypted user data:")
        # print(file_data)

        return file_data

    def qr_code_create(self,data,name=""):
        service = qr_code_service(data)
        service.create_qrcode(size=10, border=4,name=name)

    def create_mastercard(self,data,name,username):
        service = qr_code_service(data)
        service.create_qrcode(size=10, border=4, name=name)
        service.create_card(username=username,access="Private & Public",base="CD-2.png",logo_path="MysphereC1.png",qr_code_path=f"{name}.png")

    def read_qr_code(self,data):
        service = qr_code_service()
        decrypted_data = service.decrypt(data)
        readable_data = service.qr_code_formater(decrypted_data)

        # if readable_data == False:
        #     self.scanned_qr_code_status = False
        #
        # else:
        #

        return readable_data

    def authenticate(self):
        # Integrated
        # For the first time token will be treated as token.json
        self.backend = application_backend(token="")

        self.auth_status = self.backend.authenticate_signup()

        if self.auth_status == True:
            print("Auth")
            self.backend.token = "token.json"
            self.backend.create_service()
            print("ready to use the services")

        else:
            print("Network issue")

    def server_setup(self):
        self.server_backend = server(token="server_token.json")
        self.server_auth_status = self.server_backend.authenticate()

        self.server_backend.create_service()
        self.available_users_data = self.server_backend.read_userjson_server()

        print(self.available_users_data)

        for user_info in self.available_users_data:
            print(user_info)

    def check_friends(self):
        data = self.backend.view_app_users()

        return data

    def access_by_card(self,data):
        qr_type = data["Type"]


        if qr_type == "A":
            userid = data["user_id"]
            username = data["username"]
            userpassword = data["password"]
            content = data["content"]
            masterkey = data["masterkey"]

            # For Master Card
            # Validate password & username

            self.login_username.delete(0, END)
            self.login_passkey.delete(0, END)

            self.login_username.insert(0,username)
            self.login_passkey.insert(0, userpassword)

            self.user = self.login_username.get()
            self.user_key = self.login_passkey.get()
            print(f"Trying to access with : {self.user}, {self.user_key}")
            print()

            user_choice = messagebox.askokcancel(title="Access Alert",message=f"Do you want to access as {username}")
            print(user_choice)
            if user_choice == True:
                self.login_lable_pass.pack_forget()
                self.login_passkey.pack_forget()
                self.scanwithcard.pack_forget()
                self.lable_rember.pack_forget()
                self.login_sign_in.pack_forget()
                self.login_username.delete(0, END)

                self.root.focus_set()


                self.login_lable_name.configure(text="Masterkey")
                self.login_username.configure(placeholder_text="Key",show="*",font=("Oswald",14,"bold"))

                self.masterkey_attempt = 3
                def get_masterkey():
                    # global masterkey_attempt
                    # Getting the masterkey from name entry

                    usermasterkey = self.login_username.get()

                    if usermasterkey == masterkey:
                        self.user_masterkey = len(usermasterkey)
                        self.authenticate_login()

                    else:
                        self.login_username.delete(0, END)
                        self.masterkey_attempt -= 1
                        messagebox.showerror("Invalid", f"Invalid masterkey, You have {self.masterkey_attempt} left")

                        if self.masterkey_attempt == 0:
                            self.login_username.delete(0, END)
                            self.login_interface()
                            # self.login_username.delete(0, END)
                            # self.login_passkey.delete(0, END)

                        else:
                            pass

                self.login_submit.configure(width=500, command=get_masterkey)





            else:
                self.login_username.delete(0, END)
                self.login_passkey.delete(0, END)


        elif qr_type == "O":
            # For one-time

            pass

        elif qr_type == "T":
            # For time constraint
            # userid = data["user_id"]
            # username = data["username"]
            qr_id = data["qr_code_id"]
            start_time = data["start_time"]
            end_time = data["end_time"]
            content = data["content"]

            def check_qrcode_validty(timestamp):
                date_sep = timestamp.split("//")
                sep_date = date_sep[0].split("/")
                sep_time = date_sep[1].split("/")
                curt_date = current_date()
                curt_time = current_time()
                if (int(sep_date[2]) > int(curt_date[2])):  # checking of year
                    return True
                elif (int(sep_date[2]) == int(curt_date[2])):  # checking for month
                    if (int(sep_date[1]) > int(curt_date[1])):
                        return True
                    elif (int(sep_date[1]) == int(curt_date[1])):  # checking for date
                        if (int(sep_date[0]) > int(curt_date[0])):
                            return True
                        elif (int(sep_date[0]) == int(curt_date[0])):  # checking for hour
                            if (int(sep_time[0]) > int(curt_time[0])):
                                return True
                            elif (int(sep_time[0]) == int(curt_time[0])):  # checking for min
                                if (int(sep_time[1]) > int(curt_time[1])):
                                    return True
                                elif (int(sep_time[1]) == int(curt_time[1])):  # checking for sec
                                    if (int(sep_time[2]) > int(curt_time[2])):
                                        return True
                                    elif (int(sep_time[2]) == int(curt_time[2])):
                                        return True
                                    else:
                                        return False
                                else:
                                    return False
                            else:
                                return False
                        else:
                            return False
                    else:
                        return False
                else:
                    return False

            def current_date():
                x = datetime.now()

                date = x.strftime("%d")
                month = x.strftime("%m")
                year = x.strftime("%y")

                # full_date = f"{date}/{month}/{year}"
                full_date = [date, month, year]

                return full_date

            def current_time():
                x = datetime.now()

                hour = x.strftime("%H")
                min = x.strftime("%M")
                sec = x.strftime("%S")

                current_time = [hour, min, sec]
                return current_time

            # Checking qr code validity
            validity = check_qrcode_validty(timestamp=end_time)

            date_sep = end_time.split("//")
            sep_time = date_sep[1].split("/")

            date = date_sep[0]
            time = ":".join(sep_time)

            if validity == True:
                # Qr code is valid
                print(date,time)

                messagebox.showinfo(title="QR code info", message=f"    {content}      ")

                qr_code_data = content.split("&&")
                file_id = qr_code_data[0]
                file_name = qr_code_data[1]+".enc"
                # revealing the content
                def show():
                    path = self.backend.download_file(id=file_id, filename=file_name)

                    def open():
                        self.run_progress_bar()

                        os.startfile(path)
                        self.main_progressbar.pack_forget()

                    threading.Thread(target=open).start()

                threading.Thread(target=show).start()



            else:
                # Qr code is expired
                messagebox.showinfo(title="QR code info",message=f"     QR code is expired on {date} at {time}  ")


        elif qr_type == "M":
            pass

        else:
            messagebox.showerror("Invalid","Use your Master Card to access")

    def authenticate_login(self):
        access_container = []
        # Logging in after signing in
        if self.server_auth_status == True:
            for data in self.available_users_data:

                # print(data)

                userid = data["userid"]
                username = data["username"]
                userpassword = data["password"]
                token = data["token"]
                client_id = data["Client ID"]
                client_secret = data["Client secret"]

                if username == self.user and userpassword == self.user_key:
                    messagebox.showinfo("Login Successful", "You have successfully logged in!")
                    access_container.append(username)

                    if os.path.exists(f"{userid}_token.json"):
                        print("File exists!")

                        def run_backend():
                            # self.intermediate_interface()
                            self.backend = application_backend(token="")
                            self.backend.user_id = userid
                            self.backend.authenticate()
                            self.backend.token = f"{userid}_token.json"
                            # self.backend.create_service()
                            # self.backend.read_mysphere_vault()

                            # Updating user info to system configuration
                            self.user = username
                            self.user_key = userpassword
                            self.user_id = userid
                            self.user_masterkey = 7


                        # threading.Thread(target=run_backend).start()
                        run_backend()

                        self.intermediate_interface()

                        # self.mysphere_interface()

                        print("You are logged in")


                    else:
                        self.user = username
                        self.user_key = userpassword
                        self.user_id = userid
                        self.user_masterkey = 7

                        # Taking access as outsider (Accessing from different place)
                        self.access_from_outside(refresh_token=token,client_id=client_id,client_secret=client_secret)
                        # Updating user info to system configuration




                else:
                    pass

            # Checking the valid user
            if len(access_container)==1:
                # User logged
                pass

            else:
                # No user found
                messagebox.showerror("Invalid", "No user found with this credentials")
                self.login_username.delete(0, END)
                self.login_passkey.delete(0, END)


                self.root.focus_set()
        else:
            pass


        # To work on

    def access_from_outside(self,refresh_token,client_id,client_secret):

        # Creating temporary token for user to access
        def generate_new_token_json(client_id, client_secret, refresh_token, scopes=None):
            token_url = 'https://oauth2.googleapis.com/token'

            # Request payload
            payload = {
                'client_id': client_id,
                'client_secret': client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }

            # Make POST request to get new access token
            response = requests.post(token_url, data=payload)

            if response.status_code == 200:
                token_response = response.json()

                # Extract new access token
                access_token = token_response.get('access_token')

                # Calculate expiry (assuming 1 hour from now)
                expiry_time = (datetime.utcnow() + timedelta(
                    seconds=token_response.get('expires_in', 3600))).isoformat() + 'Z'

                # Prepare token.json structure
                token_json = {
                    "token": access_token,
                    "refresh_token": refresh_token,
                    "token_uri": token_url,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "scopes": ["https://www.googleapis.com/auth/drive.file"] + [
                        "https://www.googleapis.com/auth/drive"],
                    "expiry": expiry_time
                }



                return token_json

            else:
                print("Error refreshing token:", response.text)
                return None

        temp_token_json = generate_new_token_json(client_id=client_id,client_secret=client_secret,refresh_token=refresh_token)

        if temp_token_json:
            # Optionally save to a file
            with open('temp_token.json', 'w') as f:
                json.dump(temp_token_json, f, indent=4)

            print("temp_token.json created successfully!")

            def run_backend():
                self.backend = application_backend(token="")
                self.backend.user_id = self.user_id
                self.backend.token = "temp_token.json"

                # self.backend.create_service()
                # self.backend.read_mysphere_vault()

            run_backend()


            # threading.Thread(target=run_backend).start()

            print("You are temp. logged in")
            self.intermediate_interface()

            # self.mysphere_interface()


            # Delete the temp_token.json file
            # os.remove("temp_token.json")





        else:
            pass

    def login_interface(self):
        login = customtkinter.CTkImage(
            light_image=Image.open("Icons\login.png"),
            dark_image=Image.open("Icons\login.png"),
            size=(60, 60))
        signup = customtkinter.CTkImage(
            light_image=Image.open("Icons\signup.png"),
            dark_image=Image.open("Icons\signup.png"),
            size=(60, 60))

        for i in self.root.winfo_children():
            i.destroy()

        self.frame_1 = customtkinter.CTkFrame(self.root, fg_color=self.hover_theme)
        self.frame_1.pack(side="top", fill="both", expand=1)
        self.frame_1.pack_propagate(False)

        self.scanner_frame = customtkinter.CTkFrame(self.frame_1, fg_color="transparent",height=0,width=400,border_width=0)
        self.scanner_frame.pack(side="top",pady=10)
        self.scanner_frame.pack_propagate(False)

        frame_tool_left = customtkinter.CTkLabel(self.scanner_frame,width=40,fg_color="black",text="")
        # frame_tool_left.pack(side="left",fill="y",padx=5)


        self.video_label = customtkinter.CTkLabel(self.scanner_frame, text="",)
        self.video_label.pack(side="left",fill="both",expand=1)

        frame_tool_right = customtkinter.CTkLabel(self.scanner_frame, width=40,fg_color="black")
        # frame_tool_right.pack(side="right", fill="y",)

        self.frame_2 = customtkinter.CTkFrame(self.frame_1, fg_color="white", height=550, width=700,border_width=1)
        self.frame_2.pack(expand=True, anchor="center")
        self.frame_2.pack_propagate(False)

        mysphere = customtkinter.CTkImage(
            light_image=Image.open("Icons\\plane_logo.png"),
            dark_image=Image.open("Icons\\plane_logo.png"),
            size=(120, 120))

        lable_logo = customtkinter.CTkLabel(self.frame_2, fg_color="transparent", image=mysphere, text="",
                                            height=0)
        lable_logo.place(x=10, y=4)

        frame_3 = customtkinter.CTkFrame(self.frame_2, fg_color="white", height=600, width=400, border_width=0,border_color="black")
        frame_3.pack(expand=True, anchor="center",pady=20)
        frame_3.pack_propagate(False)



        emptyframe = customtkinter.CTkFrame(frame_3, fg_color="transparent", height=10)
        emptyframe.pack(side="top", fill="both")

        lable_logo = customtkinter.CTkLabel(frame_3, fg_color="transparent",image=login, text="",
                                            height=45)
        lable_logo.pack(side="top", fill="both", pady=10)

        lable_text1 = customtkinter.CTkLabel(frame_3, text="LOGIN", font=("Oswald", 25,),text_color="#071940")
        lable_text1.pack(side="top", fill="both", pady=5)

        lable_text2 = customtkinter.CTkLabel(frame_3, text="", font=("Aerial", 20, "bold"))
        # lable_text2.pack(side="top", fill="both", pady=5)

        self.login_lable_name = customtkinter.CTkLabel(frame_3, text="Name", font=("Oswald", 16,), anchor="w")
        self.login_lable_name.pack(side="top", fill="both", pady=10,padx=7)

        self.login_username = customtkinter.CTkEntry(frame_3, placeholder_text="Name", font=("Aerial", 14), height=35,
                                             border_width=0, fg_color=self.hover_theme)
        self.login_username.pack(side="top", fill="both")

        self.login_lable_pass = customtkinter.CTkLabel(frame_3, text="Password", font=("Oswald", 16,), anchor="w")
        self.login_lable_pass.pack(side="top", fill="both", pady=10,padx=7)

        self.login_passkey = customtkinter.CTkEntry(frame_3, placeholder_text="Password", font=("Aerial", 14), height=35,
                                             border_width=0, fg_color=self.hover_theme, show="•")
        self.login_passkey.pack(side="top", fill="both")

        emptyframe = customtkinter.CTkFrame(frame_3, fg_color="transparent", height=30)
        emptyframe.pack(side="top", fill="both")

        self.lable_rember = customtkinter.CTkFrame(frame_3, fg_color="transparent", height=50)
        self.lable_rember.pack(side="top", fill="both", pady=10)

        checkbox = customtkinter.CTkCheckBox(self.lable_rember, text="Remember me", font=("Aerial", 14,),
                                             corner_radius=5,border_width=2,height=5,checkbox_height=20,checkbox_width=20)
        checkbox.pack(side="left",padx=5)

        forget = customtkinter.CTkSwitch(self.lable_rember, text="Forget password ", font=("Aerial", 14,),button_color="#071940")
        forget.pack(side="right")

        frame_5 = customtkinter.CTkFrame(frame_3, fg_color="transparent")
        frame_5.pack(side="top", fill="both", pady=2)

        def submit():
            self.user = self.login_username.get()
            self.user_key = self.login_passkey.get()
            print(self.user, self.user_key)

            self.authenticate_login()





        self.login_submit = customtkinter.CTkButton(frame_5, text="Submit", font=("Aerial", 16, "bold"), height=45, width=300,
                                         corner_radius=5, command=submit,fg_color="#071940",text_color="white")
        self.login_submit.pack(side="left", expand=1, pady=15, padx=4)

        def close_scanner():
            self.scanning = False
            if self.cap:
                self.cap.release()

                self.scanner_frame.configure(height=0)
                self.video_label.pack_forget()

                self.cap = None

                self.root.update_idletasks()
            self.scanwithcard.configure(command=open_scanner)



        def open_scanner():
            self.scanner_frame.configure(height=200)
            self.video_label.pack(side="left", fill="both", expand=1)
            self.scanwithcard.configure(command=close_scanner)
            # self.frame_1.configure(fg_color="black")

            if not self.cap:
                self.cap = cv2.VideoCapture(0)

            self.scanning = True
            self.update_frame()



        self.scanwithcard = customtkinter.CTkButton(frame_5, text="Scan", font=("Aerial", 16, "bold"), height=45, width=200,
                                               corner_radius=5,fg_color="#64e320",text_color="white",command=open_scanner)
        self.scanwithcard.pack(side="left", expand=1, pady=15, padx=4)

        def sign_up():

            self.authenticate()


            self.login_username.focus()
            self.login_passkey.focus_set()
            self.root.focus_set()

            lable_text1.configure(text="SIGN UP",)
            self.login_lable_pass.configure(text="Create Password")
            lable_logo.configure(image=signup)
            self.login_passkey.configure(placeholder_text="Create Password (Atleast 8 character & Max. 10)")

            self.login_username.delete(0, END)
            self.login_passkey.delete(0, END)

            forget.pack_forget()
            self.scanwithcard.pack_forget()

            def switch():
                self.user = self.login_username.get()
                self.user_key = self.login_passkey.get()
                print(self.user, self.user_key)
                self.personalization_interface()

            self.login_submit.configure(width=500,command=switch)



            # Folder name or path
            users_folder = "MySphereUsers"

            # Create folder if it doesn't already exist
            if not os.path.exists(users_folder):
                os.makedirs(users_folder)
                print(f"Folder '{users_folder}' created!")

            else:
                print(f"Folder '{users_folder}' already exists.")



        self.login_sign_in = customtkinter.CTkButton(frame_3, text="Sign in", height=50, text_color="black",
                                          fg_color="transparent", hover="disable", font=("Aerial", 15), command=sign_up)
        self.login_sign_in.pack(side="top")



        # self.root.mainloop()
        pass

    def update_frame(self):
        scan_box_x = 170
        scan_box_y = 140
        scan_box_width = 300
        scan_box_height = 200

        if not self.scanning or not self.cap:
            return

        ret, frame = self.cap.read()
        if not ret:
            print("❌ Failed to grab frame.")
            return

        frame = cv2.flip(frame, 1)
        black_frame = np.zeros_like(frame)

        top_left = (scan_box_x, scan_box_y)
        bottom_right = (scan_box_x + scan_box_width, scan_box_y + scan_box_height)
        scan_area = frame[scan_box_y:scan_box_y + scan_box_height,
                          scan_box_x:scan_box_x + scan_box_width]
        black_frame[scan_box_y:scan_box_y + scan_box_height,
                    scan_box_x:scan_box_x + scan_box_width] = scan_area

        # cv2.rectangle(black_frame, top_left, bottom_right, (255, 255, 255), 0)

        if self.line_y >= scan_box_height - 5:
            self.direction = -1
        elif self.line_y <= 5:
            self.direction = 1
        self.line_y += self.direction * 5

        cv2.line(
            black_frame,
            (scan_box_x, scan_box_y + self.line_y),
            (scan_box_x + scan_box_width, scan_box_y + self.line_y),
            (0, 0, 255), 1
        )

        decoded_objects = decode(scan_area)
        for obj in decoded_objects:
            data = obj.data.decode('utf-8')
            print(f"📦 QR Code Data: {data}")

            self.readable_data = self.read_qr_code(data)

            self.scanning = False
            self.on_closing()

            if self.readable_data != False:
                print(self.readable_data)
                self.access_by_card(data=self.readable_data)

            else:
                messagebox.showerror("Invalid QR code","This QR code is not valid.")

            return

        rgb_frame = cv2.cvtColor(black_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)

        # Convert to CTkImage
        imgtk = customtkinter.CTkImage(img,size=(500, 400),)

        # Set image to label
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk,corner_radius=5)

        if self.scanning:
            self.root.after(30, self.update_frame)

    def update_frame_resize(self):
        scan_box_x = 95
        scan_box_y = 90
        scan_box_width = 446
        scan_box_height = 292

        if not self.scanning or not self.cap:
            return

        ret, frame = self.cap.read()
        if not ret:
            print("❌ Failed to grab frame.")
            return

        frame = cv2.flip(frame, 1)
        black_frame = np.zeros_like(frame)

        top_left = (scan_box_x, scan_box_y)
        bottom_right = (scan_box_x + scan_box_width, scan_box_y + scan_box_height)
        scan_area = frame[scan_box_y:scan_box_y + scan_box_height,
                          scan_box_x:scan_box_x + scan_box_width]
        black_frame[scan_box_y:scan_box_y + scan_box_height,
                    scan_box_x:scan_box_x + scan_box_width] = scan_area

        # cv2.rectangle(black_frame, top_left, bottom_right, (255, 255, 255), 0)

        if self.line_y >= scan_box_height - 5:
            self.direction = -1
        elif self.line_y <= 5:
            self.direction = 1
        self.line_y += self.direction * 5

        cv2.line(
            black_frame,
            (scan_box_x, scan_box_y + self.line_y),
            (scan_box_x + scan_box_width, scan_box_y + self.line_y),
            (0, 0, 255), 2
        )

        decoded_objects = decode(scan_area)
        for obj in decoded_objects:
            data = obj.data.decode('utf-8')
            print(f"📦 QR Code Data: {data}")
            self.readable_data = self.read_qr_code(data)

            self.scanning = False

            self.on_closing_mini_scanner()

            if self.readable_data != False:
                print(self.readable_data)
                self.access_by_card(data=self.readable_data)

            else:
                messagebox.showerror("Invalid QR code", "This QR code is not valid.")


            return

        rgb_frame = cv2.cvtColor(black_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)

        # Convert to CTkImage
        imgtk = customtkinter.CTkImage(img,size=(400, 300),)

        # Set image to label
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk,corner_radius=0)

        if self.scanning:
            self.root.after(30, self.update_frame_resize)

    def on_closing(self):
        self.scanning = False
        if self.cap:
            self.cap.release()
            # winsound.PlaySound("Systemhand", winsound.SND_ALIAS)
            if self.readable_data == False:
                for i in range(1,7):
                    winsound.Beep(500, 240)
            else:
                winsound.Beep(1200, 240)
            # self.scanner_frame.pack_forget()
            self.scanner_frame.configure(height=0)
            self.video_label.pack_forget()

            def open_scanner():
                self.scanner_frame.configure(height=200)
                self.video_label.pack(side="left", fill="both", expand=1)

                def close_scanner():
                    self.scanning = False
                    if self.cap:
                        self.cap.release()

                        self.scanner_frame.configure(height=0)
                        self.video_label.pack_forget()

                        self.cap = None

                        self.root.update_idletasks()
                    self.scanwithcard.configure(command=open_scanner)

                self.scanwithcard.configure(command=close_scanner)

                if not self.cap:
                    self.cap = cv2.VideoCapture(0)

                self.scanning = True
                self.update_frame()

            self.scanwithcard.configure(command=open_scanner)

            self.cap = None

            self.root.update_idletasks()

    def on_closing_mini_scanner(self):
        self.scanning = False
        if self.cap:
            self.cap.release()
            # winsound.PlaySound("Systemhand", winsound.SND_ALIAS)

            winsound.Beep(1200, 240)
            # self.scanner_frame.pack_forget()
            self.scanner_frame.configure(height=0)
            self.video_label.pack_forget()
            self.scanqr_frame.place_forget()

            def open_scanner():
                self.scanner_frame.configure(height=200)
                self.video_label.pack(side="left", fill="both", expand=1)

                def close_scanner():
                    self.scanning = False
                    if self.cap:
                        self.cap.release()

                        self.scanner_frame.configure(height=0)
                        self.video_label.pack_forget()

                        self.cap = None

                        self.root.update_idletasks()
                    self.scanwithcard.configure(command=open_scanner)

                self.scanwithcard.configure(command=close_scanner)

                if not self.cap:
                    self.cap = cv2.VideoCapture(0)

                self.scanning = True
                self.update_frame()

            # self.scanwithcard.configure(command=open_scanner)


            self.cap = None

            self.root.update_idletasks()

    def create_new_user(self):
        # User.json

        self.backend.user = self.user
        self.backend.user_key = self.user_key

        self.backend.application_setup()

        # Encrypting user file
        self.encrytJSON(user_data, f"MySphereUsers\\{self.backend.user_id}.json", 7)

        # Renaming token with userid
        os.rename("token.json", f"{self.backend.user_id}_token.json")

        def sound():
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
        threading.Thread(target=sound).start()

        self.user_age = self.user_age_entry.get()

        self.uploading_quick_start()


        def old_code():
            def generate_user_id(length):
                characters = string.ascii_letters + string.digits
                return ''.join(random.choices(characters, k=length))

            self.user_id = generate_user_id(length=7)
            print("Generated ID: ", self.user_id)

            user_data = {
                "userid": self.user_id,
                "username": self.user,
                "password": self.user_key,
                "personalization_status": True,
            }

            # Encrypting user file
            self.encrytJSON(user_data, f"MySphereUsers\\{self.user_id}.json", 7)

            # Renaming token with userid
            os.rename("token.json", f"{self.user_id}_token.json")

            # Redirecting to landing window

            def sound():
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)

            threading.Thread(target=sound).start()

            self.user_age = self.user_age_entry.get()

            self.uploading_quick_start()

    def open_file_dialog1(self,):
        filepath = filedialog.askopenfilename(
            title="Select a file to upload",
            filetypes=[("All Files", "*.*"), ("Text Files", "*.txt")]
        )
        if filepath:
            print("Selected file path:", filepath)

        self.backend.upload_file(filepath=filepath)

    # New
    def open_file_dialog(self,):

        user_choice = messagebox.askokcancel(title="Upload", message=f"Do you want to upload in {self.previous_opened_folder_name[-1]}")
        print(user_choice)

        if user_choice == True:
            filepath = filedialog.askopenfilename(
                title="Select a file to upload",
                filetypes=[("All Files", "*.*"), ("Text Files", "*.txt")]
            )
            try:
                if filepath:
                    print("Selected file path:", filepath)

                self.backend.upload_file(filepath=filepath, id=self.previous_opened_folder[-1])
                loaded_file = self.load_files(id=self.previous_opened_folder[-1])
                self.display_files(fileandfolder=loaded_file)


            except:
                messagebox.showerror(title="Error",message="Unable to upload")
                pass

        else:
            pass



    def download_file(self):
        if self.right_selected_path_id!="" and self.selected_filename!="":
            folder_path = filedialog.askdirectory(title="Select a folder to upload")

            try:
                if folder_path:
                    print("Selected file path:", folder_path)
                print(self.right_selected_path_id,self.selected_filename)
                self.backend.download_file_to_local(id=self.right_selected_path_id, filename=self.selected_filename+".enc", save_to=folder_path)

                self.displayarea_title.configure(text=self.previous_opened_folder_name[-1])

                self.selected_filename = ""
                self.right_selected_path_id = ""


            except:
                messagebox.showerror(title="Error",message="Unable to download file")
                pass

        else:
            messagebox.showerror(title="Invalid",message="Select file to download")

    def uploading_quick_start(self):
        # After submitting personalization form
        print(self.user_age,self.user_profession)
        for i in self.personalization_form.winfo_children():
            i.destroy()

        title_label = customtkinter.CTkLabel(self.personalization_form, padx=25,
                                             text="  Quickstart - Upload your documents",
                                             anchor="w", font=("Oswald", 18,), height=50,fg_color=self.theme_color)
        title_label.pack(side="top", fill="x", )

        footer = customtkinter.CTkFrame(self.personalization_form,height=40,fg_color=self.theme_color)
        footer.pack(side="bottom",fill="x")

        info = customtkinter.CTkLabel(footer,text="Uploading all the documents is not mandatory",font=("Aerial Rounded MT", 12,),padx=25)
        info.pack(side="left",fill="x")

        next_bt = customtkinter.CTkButton(footer, text="Next", fg_color="#38e84c", text_color="white",
                                            font=("Aerial Rounded MT", 12, "bold"), corner_radius=4,command=self.mysphere_interface)
        next_bt.pack(side="right", padx=20,pady=20)



        document_frame = customtkinter.CTkScrollableFrame(self.personalization_form,fg_color="transparent")
        document_frame.pack(side="top",fill="both",expand=1)

        def age_based_documents(age):
            a = ["Birth certificate", "Immunization records", "Health insurance card", "School admission papers",
                 "Parent/guardian ID", "Passport (if traveling)"]
            b = ["School/College ID", "Academic certificates", "Govt ID (Aadhaar/SSN)", "Exam admit cards",
                 "Extracurricular certificates", "Bank account info"]
            c = ["Govt-issued ID (Aadhaar", "(PAN, etc.)", "Degrees & transcripts", "Passport, Employment letters",
                 "Salary slips", "Bank documents", "Insurance papers", "Rent/ownership agreements", "Resume/CV"]
            d = ["All young adult documents", "Property documents", "Investment proofs, Loan papers",
                 "Insurance policies", "Child-related documents", "Will/Estate planning"]
            e = ["ID cards", "Pension documents", "Medical reports", "Will/Estate papers", "Insurance",
                 "Property papers"]
            if age <= 12 and age >= 0:
                print("#children#")
                return a
            elif age <= 22 and age >= 13:
                print("#teens/students#")
                return b
            elif age <= 35 and age >= 23:
                print("#young adults#")
                return c
            elif age <= 59 and age >= 36:
                print("#middle age#")
                return d
            elif age >= 60:
                print("#Seniors#")
                return e

        def profession_based_document(prof):
            a = ["Degrees/certifications", "Employment letters", "Tax returns", "Work portfolio", "Salary slips",
                 "Visa/passport"]
            b = ["Medical licenses", "Degrees", "Memberships (MCI, etc.)", "Insurance", "Clinic papers",
                 "Medical history"]
            c = ["Appointment orders", "Transfer/posting letters", "Pension forms", "ID proof", "Property declarations"]
            d = ["Degrees & licenses", "Research/publications", "Lesson plans", "Experience certificates"]
            e = ["Skill certificates", "ID proof", "Insurance (if applicable)", "License/registration"]
            f = ["Business license", "Tax records", "Invoices", "Work portfolio", "Payment/bank statements"]

            if prof.lower() == "it" or prof.lower() == "software":
                return a

            elif prof.lower() == "doctor" or prof.lower() == "Healthcare":
                return b
            elif prof.lower() == "government employee":
                return c
            elif prof.lower() == "teacher" or prof.lower() == "student":
                return d
            elif prof.lower() == "skilled tradespeople":
                return e
            elif prof.lower() == "freelancer" or prof.lower() == "self-employed":
                return f


        required_documents_by_age = age_based_documents(int(self.user_age))
        required_documents_by_profession = profession_based_document(self.user_profession)
        required_documents = required_documents_by_age + required_documents_by_profession
        print(required_documents)

        def view():
            for i in range(0, len(required_documents)):
                doc_name = required_documents[i]
                doc_frame = customtkinter.CTkFrame(document_frame, height=400, fg_color="transparent")
                doc_frame.pack(side="top", fill="x", pady=10)

                doc_label = customtkinter.CTkLabel(doc_frame, text=doc_name, fg_color=self.theme_color, height=50,
                                                   padx=10, corner_radius=10, font=("Aerial Rounded MT", 12,),
                                                   width=200, anchor="w")
                doc_label.pack(side="left", padx=5, pady=5, anchor="w")

                upload_bt = customtkinter.CTkButton(doc_frame, text="Upload", fg_color="#4287f5", text_color="white",
                                                    font=("Aerial Rounded MT", 12, "bold"), corner_radius=4,command=self.open_file_dialog)
                upload_bt.pack(side="left", padx=20)

        def horizontal_view(file_container=required_documents):
            # Parameters
            total_files = len(file_container)  # Change this to anything dynamically
            columns = 4  # Number of columns you want
            rows = (total_files + columns - 1) // columns  # Calculate needed rows

            # Make grid responsive
            for row in range(rows):
                document_frame.grid_rowconfigure(row, weight=1)
            for col in range(columns):
                document_frame.grid_columnconfigure(col, weight=1)

            # Create doc frame
            for i in range(0,total_files):
                doc_name = file_container[i]
                doc_frame = customtkinter.CTkFrame(document_frame, height=100, fg_color="transparent")
                # doc_frame.pack(side="top", fill="x", pady=10)
                doc_frame.grid(row=i // columns, column=i % columns, padx=5, pady=5,)

                doc_label = customtkinter.CTkLabel(doc_frame, text=doc_name, fg_color=self.theme_color, height=50,
                                                   padx=10, corner_radius=10, font=("Aerial Rounded MT", 12,),
                                                   width=200, anchor="w")
                doc_label.pack(side="left", padx=5, pady=5, anchor="w")

                upload_bt = customtkinter.CTkButton(doc_frame, text="Upload", fg_color="#4287f5", text_color="white",
                                                    font=("Aerial Rounded MT", 12, "bold"), corner_radius=4,command=self.open_file_dialog)
                upload_bt.pack(side="left", padx=20)



        horizontal_view()

    def personalization_interface(self):
        title_label = customtkinter.CTkLabel(self.root, text="Personalization window", font=("Aerial", 20, "bold"))
        # title_label.pack(side="top", pady=100)

        mysphere = customtkinter.CTkImage(
            light_image=Image.open("Icons\\plane_logo.png"),
            dark_image=Image.open("Icons\\plane_logo.png"),
            size=(100, 100))


        for i in self.root.winfo_children():
            i.destroy()

        self.root.configure(fg_color="#f7f7f7")

        self.personalization_form = customtkinter.CTkFrame(self.root,fg_color="white")
        self.personalization_form.pack(fill="both",expand=1,pady=70,padx=100,anchor="center")

        title_label = customtkinter.CTkLabel(self.personalization_form, padx=15, text="  Securely store and share your files, documents, and more — all in one place.",anchor="w",font=("Aerial Rounded MT",18,),height=50)
        title_label.pack(side="top",fill="x",)

        terms_and_condtion_frame = customtkinter.CTkFrame(self.personalization_form,corner_radius=0,fg_color="white")
        terms_and_condtion_frame.pack(side="left",fill="both")

        user_detail_frame = customtkinter.CTkFrame(self.personalization_form,width=600,corner_radius=0,fg_color="#fcfbd2",border_width=1)
        user_detail_frame.pack(side="left", fill="both",expand=1,padx=10,pady=10)
        user_detail_frame.pack_propagate()

        title_label = customtkinter.CTkLabel(user_detail_frame, padx=15,
                                             text="   This will help to personalize the application",
                                              font=("Oswald", 17,), height=50,anchor="w")
        title_label.pack(side="top", fill="x",padx=1,pady=1)



        your_age_label = customtkinter.CTkLabel(user_detail_frame,text="Your Age",font=("Aerial Rounded MT", 12,))
        your_age_label.pack(side="top",anchor="w",padx=27)

        self.user_age_entry = customtkinter.CTkEntry(user_detail_frame,placeholder_text="Fill your age",font=("Aerial Rounded MT", 12,),width=200,border_width=0,corner_radius=2,height=35)
        self.user_age_entry.pack(side="top",anchor="w",padx=26)

        your_occu_label = customtkinter.CTkLabel(user_detail_frame, text="Choose your profession", font=("Aerial Rounded MT", 12,))
        your_occu_label.pack(side="top", anchor="w", padx=27)

        def profession_callback(choice):
            self.user_profession = choice
            print("Profession", choice)

        def most_view_doc_combobox_callback(choice):
            print("Mostly used document", choice)

        def habit_combobox_callback(choice):
            print("Habit", choice)

        profession_combobox_var = customtkinter.StringVar(value="")
        profession_combobox = customtkinter.CTkComboBox(user_detail_frame, values=["Student", "Teacher","Doctor","IT","Government Employee","Skilled Tradespeople","Freelancers","Self-employed","Other"],command=profession_callback,variable=profession_combobox_var,width=200,border_width=0,dropdown_fg_color="white")
        profession_combobox.pack(side="top",anchor="w",padx=27)


        your_occu_label = customtkinter.CTkLabel(user_detail_frame, text="Which document you mostly use weekly/monthly",font=("Aerial Rounded MT", 12,))
        your_occu_label.pack(side="top", anchor="w", padx=27)

        most_view_doc_combobox_var = customtkinter.StringVar(value="")
        most_view_doc_combobox = customtkinter.CTkComboBox(user_detail_frame, values=["ID", "Aadhar Card", ],command=most_view_doc_combobox_callback, variable=most_view_doc_combobox_var,width=200, border_width=0, dropdown_fg_color="white")
        most_view_doc_combobox.pack(side="top", anchor="w", padx=27)


        your_habit_label = customtkinter.CTkLabel(user_detail_frame, text="Had you ever lost your document",font=("Aerial Rounded MT", 12,))
        your_habit_label.pack(side="top", anchor="w", padx=27)

        habit_combobox_var = customtkinter.StringVar(value="")
        habit_combobox = customtkinter.CTkComboBox(user_detail_frame, values=["Yes", "No", "May be"],command=habit_combobox_callback,variable=habit_combobox_var,width=200, border_width=0, dropdown_fg_color="white")
        habit_combobox.pack(side="top", anchor="w", padx=27)


        submit_bt = customtkinter.CTkButton(user_detail_frame,text="Confirm",command=self.create_new_user,font=("Aerial Rounded MT", 12,"bold"),height=30,fg_color="#1b58f2",width=200,corner_radius=4)


        self.user_age_entry.configure(state="disabled")
        profession_combobox.configure(state="disabled")
        most_view_doc_combobox.configure(state="disabled")
        habit_combobox.configure(state="disabled")




        t_and_c = """       Terms & Conditions – Your Data, Your Control\n
        1. Your Privacy Comes First\n
        We respect your privacy. Any files, documents, or data you upload are 100% yours. We do not sell, share, or misuse your personal information.\n
        2. How We Use Your Data\n
        Your data is used only to provide and improve the services offered in this application — like helping you store, manage, or share your files securely.\n
        We never use your data for personal gain, advertising, or unauthorized purposes.\n
        3. Your Rights\n
        - You can view, download, and delete your data anytime.\n
        - You can ask for complete deletion of your account and all associated files.\n
        - We’re committed to transparency — no hidden usage, no shady stuff.\n
        4. Data Security\n
        We use industry-standard encryption and protection methods to keep your data safe from unauthorized access.\n
        5. No Third-Party Tracking\n
        We do not include any third-party trackers or analytics that invade your privacy. Your usage stays between you and us.\n
        6. Updates to These Terms\n
        If we ever need to change anything, we’ll let you know in advance and give you a chance to review it before continuing to use the app."""

        user_termsandcondition = customtkinter.CTkLabel(terms_and_condtion_frame, text=t_and_c,font=("Aerial",11,),height=14,justify="left",pady=20,fg_color="white")
        user_termsandcondition.pack(side="top",anchor="w")

        sub_div_1 = customtkinter.CTkFrame(terms_and_condtion_frame,height=40,corner_radius=0,fg_color="transparent")
        sub_div_1.pack(fill="x",pady=20)

        def check():
            if accept_check.get()==1:
                start_personalizaton_bt.configure(state="normal")
            else:
                start_personalizaton_bt.configure(state="disabled")

                pass

        accept_check = customtkinter.CTkCheckBox(sub_div_1, text="I have reviewed the above detail & accept the terms & conditions", font=("Aerial", 12,"bold"),
                                             corner_radius=5, border_width=2, height=20, checkbox_height=20,
                                             checkbox_width=20,command=check)
        accept_check.pack(side="left", padx=20)

        def start_personization():
            user_grant = accept_check.get()

            if user_grant==1:
                accept_check.configure(state="disabled")
                self.user_age_entry.configure(state="normal")
                profession_combobox.configure(state="normal")
                most_view_doc_combobox.configure(state="normal")
                habit_combobox.configure(state="normal")
                submit_bt.pack(side="top", anchor="w", padx=27, pady=20)

            else:
                pass

        start_personalizaton_bt = customtkinter.CTkButton(sub_div_1,text="Start personalization",state="disabled",font=("Aerial",11,"bold"),command=start_personization,corner_radius=5,height=29,fg_color="#3bbf11",text_color="white")
        start_personalizaton_bt.pack(side="right",padx=46)

        sub_div_2 = customtkinter.CTkFrame(terms_and_condtion_frame, height=40, corner_radius=10,fg_color="white")
        sub_div_2.pack(side="bottom",fill="x", pady=10,padx=5)

        psit_citing = customtkinter.CTkButton(sub_div_2,text="Built in PSIT",text_color="white",corner_radius=4,border_color="red",font=("Oswald",12),fg_color="red",border_width=2,hover="disable")
        psit_citing.pack(side="left",padx=20,pady=10)

        psit_citing = customtkinter.CTkButton(sub_div_2, text="Powered by Google Drive API", text_color="white", corner_radius=4,
                                              border_color="#fae41e", font=("Oswald", 12), fg_color="#fae41e", border_width=2,
                                              hover="disable")
        # psit_citing.pack(side="left", padx=20)
        psit_citing = customtkinter.CTkButton(sub_div_2, text="Team Saksham", text_color="white", corner_radius=4,
                                              border_color="#02066e", font=("Oswald", 12), fg_color="#02066e", border_width=2,
                                              hover="disable")
        # psit_citing.pack(side="left", padx=20)

        logo = customtkinter.CTkLabel(sub_div_2,
                                      text="",
                                      font=("Oswald", 17,), anchor="w", image=mysphere)
        logo.pack(side="right", fill="x", padx=1, pady=1)




        self.root.mainloop()
        pass

    def load_files1(self,current_folder_id):
        # Load files/folder from cloud

        folders = self.backend.read_mysphere_vault()
        files = []

        for i in folders:
            name = i["name"]
            print(i)
            files.append(name)

        return files

    def display_files_old(self,fileandfolder):
        # Loading files from current folder id

        self.opened_folders.append(fileandfolder)

        folder_logo = customtkinter.CTkImage(
            light_image=Image.open("Icons\\folder.png"),
            dark_image=Image.open("Icons\\folder.png"),
            size=(15, 15))

        file_logo = customtkinter.CTkImage(
            light_image=Image.open("Icons\\file2.png"),
            dark_image=Image.open("Icons\\file2.png"),
            size=(15, 15))

        def vertical_view(file_container=fileandfolder):
            total_files = len(file_container)
            try:
                for i in self.folder_area_frame.winfo_children():
                    i.destroy()
            except:
                pass

            empty_frame = customtkinter.CTkFrame(self.display_area_frame, corner_radius=0, height=12,
                                                 fg_color="transparent")
            # empty_frame.pack(side="top", fill="x")
            i = 0
            for item in fileandfolder:
                # print(item)
                type = item["type"]
                ID = item["id"]
                name = item["name"]

                if type == "folder":

                    def open_it(x=ID,y=name):
                        # print(f"Folder {files[x]} is opened")
                        files = self.load_files(id=x)
                        # print("Newfiles",files,x)
                        self.display_files(fileandfolder=files)

                        # self.previous_opened_folder.append(ID)

                        self.displayarea_title.configure(text=y)
                        # self.opened_folder_name.append(y)
                        self.previous_opened_folder_name.append(y)

                    folder = customtkinter.CTkButton(self.folder_area_frame, text=name, image=folder_logo,
                                                     text_color="black", fg_color=self.theme_color,
                                                     font=("Aerial Rounded MT", 12,), height=5, corner_radius=5,
                                                     anchor="w",
                                                     hover_color=self.hover_theme, command=open_it)
                    folder.pack(side="top", anchor="w", padx=20, pady=2)



                elif type == "file":

                    def open_it(x=name):



                        def show_img():
                            path = self.backend.download_file(file_name=x)
                            def open():
                                # img = Image.open(path)
                                self.run_progress_bar()
                                # for i in range(101):
                                #     self.main_progressbar.set(i / 100)
                                #     # print(i)
                                #     # time.sleep(0.0000000000000000001)
                                # img.show()
                                os.startfile(path)
                                self.main_progressbar.pack_forget()

                            threading.Thread(target=open).start()


                        threading.Thread(target=show_img).start()

                        # print(f"Folder {files[x]} is opened")
                        # self.load_files("x")
                        # self.display_files()

                        # for i in self.folder_area_frame.winfo_children():
                        #     i.destroy()

                        # self.displayarea_title.configure(text=files[x])
                        # self.opened_folder_name.append(files[x])

                    file = customtkinter.CTkButton(self.folder_area_frame, text=name, image=file_logo,
                                                     text_color="black", fg_color=self.theme_color,
                                                     font=("Aerial Rounded MT", 12,), height=5, corner_radius=5,
                                                     anchor="w",
                                                     hover_color=self.hover_theme, command=open_it)
                    file.pack(side="top", anchor="w", padx=20, pady=2)

                i = i + 1

        def horizontal_view(file_container=fileandfolder):
            try:
                for i in self.folder_area_frame.winfo_children():
                    i.destroy()
            except:
                pass

            # Parameters
            total_files = len(file_container)  # Change this to anything dynamically
            columns = 5  # Number of columns you want
            rows = (total_files + columns - 1) // columns  # Calculate needed rows

            # Make grid responsive
            for row in range(rows):
                self.folder_area_frame.grid_rowconfigure(row, weight=1)
            for col in range(columns):
                self.folder_area_frame.grid_columnconfigure(col, weight=1)

            i = 0
            for item in fileandfolder:
                # print(item)
                type = item["type"]
                ID = item["id"]
                name = item["name"]

                if type == "folder":

                    def open_it(x=ID,y=name):
                        # print(f"Folder {files[x]} is opened")
                        files = self.load_files(id=x)

                        self.display_files(fileandfolder=files)
                        self.displayarea_title.configure(text=y)
                        self.previous_opened_folder_name.append(y)

                    folder = customtkinter.CTkButton(self.folder_area_frame, text=name, image=folder_logo,
                                                     text_color="black", fg_color=self.theme_color,
                                                     font=("Aerial Rounded MT", 12,), height=5, corner_radius=5,
                                                     anchor="w",
                                                     hover_color=self.hover_theme, command=open_it)
                    folder.grid(row=i // columns, column=i % columns, padx=5, pady=5, )



                elif type == "file":

                    def open_it(x=i):
                        # print(f"Folder {files[x]} is opened")
                        # self.load_files("x")
                        # self.display_files()

                        # for i in self.folder_area_frame.winfo_children():
                        #     i.destroy()

                        self.displayarea_title.configure(text=files[x])
                        self.opened_folder_name.append(files[x])

                    file = customtkinter.CTkButton(self.folder_area_frame, text=name, image=file_logo,
                                                     text_color="black", fg_color=self.theme_color,
                                                     font=("Aerial Rounded MT", 12,), height=5, corner_radius=5,
                                                     anchor="w",
                                                     hover_color=self.hover_theme, command=open_it)
                    file.grid(row=i // columns, column=i % columns, padx=5, pady=5, )

                i = i + 1

        if self.file_view_orientation == "Horizontal":
            horizontal_view()

        else:
            vertical_view()

    # New
    def display_files(self,fileandfolder):
        # Loading files from current folder id

        self.opened_folders.append(fileandfolder)

        folder_logo = customtkinter.CTkImage(
            light_image=Image.open("Icons\\folder.png"),
            dark_image=Image.open("Icons\\folder.png"),
            size=(15, 15))

        file_logo = customtkinter.CTkImage(
            light_image=Image.open("Icons\\file2.png"),
            dark_image=Image.open("Icons\\file2.png"),
            size=(15, 15))

        def vertical_view(file_container=fileandfolder):
            total_files = len(file_container)
            try:
                for i in self.folder_area_frame.winfo_children():
                    i.destroy()
            except:
                pass

            empty_frame = customtkinter.CTkFrame(self.display_area_frame, corner_radius=0, height=12,
                                                 fg_color="red")

            if self.previous_opened_folder[-1] == "":
                self.view_shared_with_me()

            else:
                pass
            # empty_frame.pack(side="top", fill="x")

            # empty_frame.place(x=10,y=150)

            # self.folder_area_frame.configure(fg_color="yellow")
            # self.folder_area_frame.pack_propagate(0)

            i = 0
            for item in fileandfolder:
                # print(item)
                type = item["type"]
                ID = item["id"]
                name = item["name"]


                if type == "folder":

                    def open_it(x=ID,y=name):
                        # print(f"Folder {files[x]} is opened")
                        files = self.load_files(id=x)
                        # print("Newfiles",files,x)
                        self.display_files(fileandfolder=files)
                        self.selected_path_id=x

                        # self.previous_opened_folder.append(ID)

                        self.displayarea_title.configure(text=y)
                        # self.opened_folder_name.append(y)
                        self.previous_opened_folder_name.append(y)

                    folder = customtkinter.CTkButton(self.folder_area_frame, text=name, image=folder_logo,
                                                     text_color="black", fg_color=self.theme_color,
                                                     font=("Aerial Rounded MT", 12,), height=5, corner_radius=5,
                                                     anchor="w",
                                                     hover_color=self.hover_theme, command=open_it)
                    folder.pack(side="top", anchor="w", padx=20, pady=2)

                    def on_right_click(event,id=ID,folder_name=name,count=i):
                        self.right_selected_path_id = id

                        self.displayarea_title.configure(text="Folder selected - "+folder_name)

                    folder.bind("<Button-3>", on_right_click)



                elif type == "file":


                    if (f"{self.user_id}" not in name) and ("_connection" not in name):
                        def open_it(x=name, id=ID):
                            self.selected_path_id = x

                            def show_img():
                                path = self.backend.download_file(id=id, filename=x)

                                def open():
                                    # img = Image.open(path)
                                    self.run_progress_bar()
                                    os.startfile(path)
                                    self.main_progressbar.pack_forget()

                                threading.Thread(target=open).start()

                            threading.Thread(target=show_img).start()

                            # print(f"Folder {files[x]} is opened")
                            # self.load_files("x")
                            # self.display_files()

                            # for i in self.folder_area_frame.winfo_children():
                            #     i.destroy()

                            # self.displayarea_title.configure(text=files[x])
                            # self.opened_folder_name.append(files[x])

                        if ".enc" in name:
                            filename = name.split(".enc")
                            name = filename[0]

                        else:
                            pass

                        file = customtkinter.CTkButton(self.folder_area_frame, text=name, image=file_logo,
                                                       text_color="black", fg_color=self.theme_color,
                                                       font=("Aerial Rounded MT", 12,), height=5, corner_radius=5,
                                                       anchor="w",
                                                       hover_color=self.hover_theme, command=open_it)
                        file.pack(side="top", anchor="w", padx=20, pady=2)

                        def on_right_click(event,id=ID, file_name=name, count=i):
                            # x = self.display_area_frame.winfo_x()
                            # y = self.display_area_frame.winfo_y()

                            self.right_selected_path_id = id
                            self.selected_filename = file_name

                            self.displayarea_title.configure(text="File selected - " + file_name)

                        file.bind("<Button-3>", on_right_click)


                i = i + 1

        def horizontal_view(file_container=fileandfolder):
            try:
                for i in self.folder_area_frame.winfo_children():
                    i.destroy()
            except:
                pass

            # Parameters
            total_files = len(file_container)  # Change this to anything dynamically
            columns = 5  # Number of columns you want
            rows = (total_files + columns - 1) // columns  # Calculate needed rows

            # Make grid responsive
            for row in range(rows):
                self.folder_area_frame.grid_rowconfigure(row, weight=1)
            for col in range(columns):
                self.folder_area_frame.grid_columnconfigure(col, weight=1)

            i = 0
            for item in fileandfolder:
                # print(item)
                type = item["type"]
                ID = item["id"]
                name = item["name"]

                if type == "folder":

                    def open_it(x=ID,y=name):
                        # print(f"Folder {files[x]} is opened")
                        files = self.load_files(id=x)
                        self.selected_path_id = x


                        self.display_files(fileandfolder=files)
                        self.displayarea_title.configure(text=y)
                        self.previous_opened_folder_name.append(y)

                    folder = customtkinter.CTkButton(self.folder_area_frame, text=name, image=folder_logo,
                                                     text_color="black", fg_color=self.theme_color,
                                                     font=("Aerial Rounded MT", 12,), height=5, corner_radius=5,
                                                     anchor="w",
                                                     hover_color=self.hover_theme, command=open_it)
                    folder.grid(row=i // columns, column=i % columns, padx=5, pady=5, )



                elif type == "file":

                    def open_it(x=i):
                        # print(f"Folder {files[x]} is opened")
                        # self.load_files("x")
                        # self.display_files()

                        # for i in self.folder_area_frame.winfo_children():
                        #     i.destroy()
                        self.selected_path_id = x

                        self.displayarea_title.configure(text=file[x])
                        self.opened_folder_name.append(file[x])

                    file = customtkinter.CTkButton(self.folder_area_frame, text=name, image=file_logo,
                                                     text_color="black", fg_color=self.theme_color,
                                                     font=("Aerial Rounded MT", 12,), height=5, corner_radius=5,
                                                     anchor="w",
                                                     hover_color=self.hover_theme, command=open_it)
                    file.grid(row=i // columns, column=i % columns, padx=5, pady=5, )

                i = i + 1

        if self.file_view_orientation == "Horizontal":
            horizontal_view()

        else:
            vertical_view()



    def display_back1(self):

        lenght_opened_folders = len(self.opened_folders)


        if lenght_opened_folders>0:
            self.opened_folders.pop()
            self.opened_folder_name.pop()
            files = self.opened_folders[-1]
            file_name = self.opened_folder_name[-1]

            self.opened_folders.append(files)

            folder_logo = customtkinter.CTkImage(
                light_image=Image.open("Icons\\folder.png"),
                dark_image=Image.open("Icons\\folder.png"),
                size=(15, 15))

            def vertical_view(file_container=files):
                total_files = len(file_container)
                try:
                    for i in self.folder_area_frame.winfo_children():
                        i.destroy()
                except:
                    pass

                empty_frame = customtkinter.CTkFrame(self.display_area_frame, corner_radius=0, height=12,
                                                     fg_color="transparent")
                # empty_frame.pack(side="top", fill="x")

                for i in range(0, total_files):
                    def open_it(x=i):
                        # print(f"Folder {files[x]} is opened")
                        self.load_files("x")
                        self.display_files()

                        # for i in self.folder_area_frame.winfo_children():
                        #     i.destroy()

                        self.displayarea_title.configure(text=files[x])
                        self.opened_folder_name.append(files[x])

                    folder = customtkinter.CTkButton(self.folder_area_frame, text=files[i], image=folder_logo,
                                                     text_color="black", fg_color=self.theme_color,
                                                     font=("Aerial Rounded MT", 12,), height=5, corner_radius=5,
                                                     anchor="w",
                                                     hover_color=self.hover_theme, command=open_it)
                    folder.pack(side="top", anchor="w", padx=20, pady=2)

            def horizontal_view(file_container=files):
                try:
                    for i in self.folder_area_frame.winfo_children():
                        i.destroy()
                except:
                    pass

                # Parameters
                total_files = len(file_container)  # Change this to anything dynamically
                columns = 5  # Number of columns you want
                rows = (total_files + columns - 1) // columns  # Calculate needed rows

                # Make grid responsive
                for row in range(rows):
                    self.folder_area_frame.grid_rowconfigure(row, weight=1)
                for col in range(columns):
                    self.folder_area_frame.grid_columnconfigure(col, weight=1)

                # Create buttons
                for i in range(0, total_files):
                    def open_it(x=i):
                        # print(f"Folder {files[i]} is opened")
                        self.load_files("x")
                        self.display_files()

                        # for i in self.folder_area_frame.winfo_children():
                        #     i.destroy()

                        self.displayarea_title.configure(text=files[x])
                        self.opened_folder_name.append(files[x])

                    folder = customtkinter.CTkButton(self.folder_area_frame, text=files[i], image=folder_logo,
                                                     text_color="black", fg_color=self.theme_color,
                                                     font=("Aerial Rounded MT", 12,), height=5, corner_radius=5,
                                                     anchor="w",
                                                     hover_color=self.hover_theme, command=open_it)

                    folder.grid(row=i // columns, column=i % columns, padx=5, pady=5, )

            if self.file_view_orientation == "Horizontal":
                horizontal_view()
                # print("Displayed file in H")
                print(self.opened_folders)
            else:
                vertical_view()
                print(self.opened_folders)
                # print("Displayed file in V")
        else:
            print("No more left")

    def display_back(self):

        if len(self.previous_opened_folder)>1:
            # Removing the last folder id
            self.previous_opened_folder.pop()
            previous_folder_id = self.previous_opened_folder[-1]

            print("Prev ID",previous_folder_id)
            self.previous_opened_folder_name.pop()
            previous_folder_name = self.previous_opened_folder_name[-1]

            self.displayarea_title.configure(text=previous_folder_name)

            loaded_file = self.load_files(id=previous_folder_id)
            self.display_files(fileandfolder=loaded_file)



        elif len(self.previous_opened_folder) == 1:
            # Parent folder
            loaded_file = self.load_files(id="")
            self.display_files(fileandfolder=loaded_file)

    def view_files(self):
        self.search_bar.configure(state="normal")
        self.search_bt.configure(state="normal")
        # self.clear_bt.configure(state="normal")

        self.new_file_bt.configure(state="normal")
        self.new_folder_bt.configure(state="normal")
        self.download_bt.configure(state="normal")
        self.upload2_bt.configure(state="normal")
        self.add_friend_bt.configure(state="normal")
        self.scanqr_bt.configure(state="normal")
        self.share_bt.configure(state="normal")
        self.copy_bt.configure(state="normal")
        self.rename_bt.configure(state="normal")
        self.createqr_bt.configure(state="normal")

        self.displayarea_title.configure(text="Folders")

        try:
            for i in self.container.winfo_children():
                i.destroy()
        except:
            pass

        self.folder_area_frame = customtkinter.CTkScrollableFrame(self.container, fg_color="white")
        self.folder_area_frame.pack(side="left", fill="both", expand=1)

        loaded_file = self.load_files(id="")
        # print("Loaded files",loaded_file)
        self.display_files(fileandfolder=loaded_file)

    def load_files(self,id):
        self.current_folder_id = id

        if id=="":
            folders = self.backend.read_mysphere_vault()
            if len(self.previous_opened_folder)==0:
                self.previous_opened_folder.append("")
                self.previous_opened_folder_name.append("Folder")

            else:
                pass

        else:
            folders = self.backend.read_current_dir(id)
            if self.previous_opened_folder[-1]==id:
                pass
            else:
                self.previous_opened_folder.append(id)
                # self.previous_opened_folder_name.append(id)
            pass

        L = []
        folder_file_dict = {}
        for items in folders:
            type = items["mimeType"]
            ID = items["id"]
            name = items["name"]

            # print(type,name,ID)

            if type=="application/vnd.google-apps.folder":
                # Folder
                folder_file_dict = {"type":"folder","id":ID,"name":name}
                # folder_file_dict.update({"type":"folder","id":ID,"name":name})

            else:
                # File
                folder_file_dict = {"type": "file", "id": ID, "name": name}
                # folder_file_dict.update({"type": "file", "id": ID, "name": name})

            L.append(folder_file_dict)
        print("Opened folders :",self.previous_opened_folder)
        return L

    def view_shared_with_me(self):
        folder_logo = customtkinter.CTkImage(
            light_image=Image.open("Icons\\folder.png"),
            dark_image=Image.open("Icons\\folder.png"),
            size=(15, 15))

        file_logo = customtkinter.CTkImage(
            light_image=Image.open("Icons\\file2.png"),
            dark_image=Image.open("Icons\\file2.png"),
            size=(15, 15))

        for user_folder in self.shared_with_me_data:
            print(user_folder)

            if user_folder in self.friend_list:

                user_name = self.email_friend[user_folder]
            else:
                user_name = ""

            print()
            if len(self.shared_with_me_data[user_folder]) > 0 and user_name!="":
                user_data = self.shared_with_me_data[user_folder]

                def open_it(foldername=user_name,file_data=user_data):
                    # print(f"Folder {files[x]} is opened")

                    try:
                        for i in self.folder_area_frame.winfo_children():
                            i.destroy()
                    except:
                        pass

                    for file_id in file_data:
                        # Create file
                        file_name = file_data[file_id]
                        print(file_id, file_name)

                        if (f"{self.user_id}" not in file_name) and ("_connection" not in file_name):

                            def open_file(x=file_name, id=file_id):
                                # self.selected_path_id = x

                                def show_img():
                                    path = self.backend.download_file(id=id, filename=x)

                                    def open():
                                        # img = Image.open(path)
                                        self.run_progress_bar()
                                        os.startfile(path)
                                        self.main_progressbar.pack_forget()

                                    threading.Thread(target=open).start()

                                threading.Thread(target=show_img).start()

                            if ".enc" in file_name:
                                filename = file_name.split(".enc")
                                name = filename[0]

                            else:
                                pass

                            file = customtkinter.CTkButton(self.folder_area_frame, text=name, image=file_logo,
                                                           text_color="black", fg_color=self.theme_color,
                                                           font=("Aerial Rounded MT", 12,), height=5, corner_radius=5,
                                                           anchor="w",
                                                           hover_color=self.hover_theme, command=open_file)
                            file.pack(side="top", anchor="w", padx=20, pady=2)

                            self.displayarea_title.configure(text=name)

                    # files = self.load_files(id=x)
                    # # print("Newfiles",files,x)
                    # self.display_files(fileandfolder=files)
                    # self.selected_path_id = x

                    # self.previous_opened_folder.append(ID)

                    # self.displayarea_title.configure(text=)
                    # self.opened_folder_name.append(y)
                    # self.previous_opened_folder_name.append(y)

                folder = customtkinter.CTkButton(self.folder_area_frame, text=user_name, image=folder_logo,
                                                 text_color="black", fg_color=self.theme_color,
                                                 font=("Aerial Rounded MT", 12,), height=5, corner_radius=5,
                                                 anchor="w",
                                                 hover_color=self.hover_theme,command=open_it)
                folder.pack(side="top", anchor="w", padx=20, pady=2)



            else:
                pass





    def my_profile(self):
        self.search_bar.configure(state="disabled")
        self.search_bt.configure(state="disabled")
        # self.clear_bt.configure(state="disabled")
        self.new_file_bt.configure(state="disabled")
        self.new_folder_bt.configure(state="disabled")
        self.download_bt.configure(state="disabled")
        self.upload2_bt.configure(state="disabled")
        self.add_friend_bt.configure(state="disabled")
        self.scanqr_bt.configure(state="disabled")
        self.share_bt.configure(state="disabled")
        self.copy_bt.configure(state="disabled")
        self.rename_bt.configure(state="disabled")
        self.createqr_bt.configure(state="disabled")

        self.displayarea_title.configure(text="My Profile")

        try:
            for i in self.container.winfo_children():
                i.destroy()
        except:
            pass

        try:
            mastercard_path = f"{self.user.title()}_master_card.png"
            x = 250
            my_card = customtkinter.CTkImage(
                light_image=Image.open(mastercard_path),
                dark_image=Image.open(mastercard_path),
                size=(x * 1.75, x))

            self.mastercard_status = True
            masterkey_text = self.user_masterkey * "•"

        except:
            x = 250
            my_card = customtkinter.CTkImage(
                light_image=Image.open("Username_master_card.png"),
                dark_image=Image.open("Username_master_card.png"),
                size=(x * 1.75, x))

            self.mastercard_status = False
            masterkey_text = self.user_masterkey * ""


        self.my_profile_frame = customtkinter.CTkFrame(self.container, fg_color="transparent")
        self.my_profile_frame.pack(side="top", fill="both", expand=1)

        detail_frame = customtkinter.CTkFrame(self.my_profile_frame,width=460,height=500,border_width=1,fg_color=self.theme_color,border_color="#faf0b9",corner_radius=15)
        detail_frame.pack(side="left",anchor="n",padx=20,pady=25)

        detail_frame.pack_propagate(0)


        header_title_frame = customtkinter.CTkFrame(detail_frame,height=35,fg_color="transparent")
        header_title_frame.pack(side="top",fill="x",padx=5,pady=5)

        label = customtkinter.CTkLabel(header_title_frame, text="Personal Credentials", font=("Aerial Rounded MT", 16,"bold"), width=80,
                                       height=40, anchor="w")
        label.pack(side="left", padx=15,pady=10)


        name_frame = customtkinter.CTkFrame(detail_frame, height=35,fg_color="transparent")
        name_frame.pack(side="top", fill="x", padx=5, pady=5)

        label = customtkinter.CTkLabel(name_frame,text="Name  ",font=("Aerial Rounded MT",13,"bold"),width=80,height=20,anchor="w")
        label.pack(side="left",padx=15)

        username = customtkinter.CTkLabel(name_frame,text=self.user,font=("Aerial Rounded MT",13,),height=20)
        username.pack(side="left",padx=0)


        userid_frame = customtkinter.CTkFrame(detail_frame,height=35,fg_color="transparent")
        userid_frame.pack(side="top", fill="x", padx=5, pady=5)

        label = customtkinter.CTkLabel(userid_frame, text="UserID  ", font=("Aerial Rounded MT", 13, "bold"),width=80,height=20,anchor="w")
        label.pack(side="left", padx=15)

        userid = customtkinter.CTkLabel(userid_frame, text=self.user_id, font=("Aerial Rounded MT", 13,),height=20)
        userid.pack(side="left", padx=0)


        password_frame = customtkinter.CTkFrame(detail_frame,height=35,fg_color="transparent")
        password_frame.pack(side="top", fill="x", padx=5, pady=5)

        label = customtkinter.CTkLabel(password_frame, text="Password  ", font=("Aerial Rounded MT", 13, "bold"), width=80,
                                       height=20,anchor="w")
        label.pack(side="left", padx=15)

        password = customtkinter.CTkLabel(password_frame, text=self.user_key, font=("Aerial Rounded MT", 13,), height=20)
        password.pack(side="left", padx=0)



        masterkey_frame = customtkinter.CTkFrame(detail_frame,height=35,fg_color="transparent")
        masterkey_frame.pack(side="top", fill="x", padx=5, pady=5)

        label = customtkinter.CTkLabel(masterkey_frame, text="Master-key  ", font=("Aerial Rounded MT", 13, "bold"),
                                       width=80,
                                       height=20,anchor="w")
        label.pack(side="left", padx=15)

        masterkey_label = customtkinter.CTkLabel(masterkey_frame, text=masterkey_text, font=("Aerial Rounded MT", 13,), height=20)
        masterkey_label.pack(side="left", padx=0)



        bt_frame = customtkinter.CTkFrame(detail_frame,height=35,fg_color="transparent")
        bt_frame.pack(side="top", fill="x", padx=5, pady=15)


        def change_password():
            messagebox.showinfo(title="Application Manager",message="Introducing this feature soon, currently under development")

        bt1 = customtkinter.CTkButton(bt_frame, text="Change password", width=125, font=("Aerial", 12, "bold"),
                                      text_color="white",corner_radius=4,height=28,fg_color="#79e03d",command=change_password)
        bt1.pack(side="left", fill="y", padx=14)

        def create_master_key():
            dialog = customtkinter.CTkInputDialog(text="Master Key:", title="Creating the Master_")
            masterkey = dialog.get_input()
            if masterkey == "" or masterkey.isspace():
                messagebox.showerror("No Entry", "No Entry")
            else:
                data = {
                    "Type": "A",
                    "user_id": self.user_id,
                    "username": self.user,
                    "password": self.user_key,
                    "content": "Dear, MySphere warden give me access",
                    "masterkey": f"{masterkey}"
                }
                print(masterkey)

                user_choice = messagebox.askokcancel(title="Alert",
                                                     message=f"Master once created cannot be changed again,\nDo you want to continue ?")
                # print(user_choice)

                if user_choice==True:
                    self.create_mastercard(data=data, name=self.user_id, username=self.user.title())

                    masterkey_text = len(masterkey) * "•"
                    masterkey_label.configure(text=masterkey_text)

                    mastercard_path = f"{self.user.title()}_master_card.png"

                    x = 250
                    my_card = customtkinter.CTkImage(
                        light_image=Image.open(mastercard_path),
                        dark_image=Image.open(mastercard_path),
                        size=(x * 1.75, x))

                    self.card_display_label.configure(image=my_card)

                    create_masterkey_bt.configure(state="disabled")


                else:
                    pass


        create_masterkey_bt = customtkinter.CTkButton(bt_frame, text="Create master key", width=125, font=("Aerial", 12, "bold"),
                                      text_color="white",corner_radius=4,height=28,fg_color="#f5c725",command=create_master_key,text_color_disabled="white")
        create_masterkey_bt.pack(side="left", fill="y")


        def checK_mastercard():
            if self.mastercard_status == True:
                create_masterkey_bt.configure(state="disabled")

            else:
                pass

        checK_mastercard()

        detail = "Dear User,\nWe prioritize your privacy and data security.All credentials and user data stored within this application are locally encrypted and never shared with third parties.Accessed only when necessary to provide services.\n\nYou can create the vault card the access your data from anywhere\n\n- Team MySphere"



        card_detail = customtkinter.CTkLabel(detail_frame, text=detail, fg_color="transparent",
                                             corner_radius=4, wraplength=400, justify="left", anchor="nw", pady=5,
                                             font=("Calibri", 14,"italic"))
        card_detail.pack(side="top", pady=5, fill="x",padx=15)







        card_display_area_frame = customtkinter.CTkFrame(self.my_profile_frame, border_width=0,
                                              fg_color="transparent",border_color="#faf0b9",corner_radius=10)
        card_display_area_frame.pack(side="left", anchor="n",fill="both", padx=90, pady=5,)

        card_usage_title = customtkinter.CTkLabel(card_display_area_frame, text="Your Vault Pass", text_color="black",
                                                  font=("Oswald", 24), anchor="w")
        card_usage_title.pack(side="top", fill="x",padx=38,pady=5)

        card_display_frame = customtkinter.CTkFrame(card_display_area_frame,width=500,height=310,fg_color="#f7f7f7",corner_radius=13,border_width=1,)
        card_display_frame.pack(side="top",pady=0) #2E2E2E
        card_display_frame.pack_propagate(False)



        self.card_display_label = customtkinter.CTkLabel(card_display_frame,text="",fg_color="transparent",image=my_card)
        self.card_display_label.pack(side="top",fill="both",padx=30,pady=30,expand=1)

        button_frame = customtkinter.CTkFrame(card_display_area_frame, height=40, fg_color="transparent",
                                                    corner_radius=0)
        button_frame.pack(side="top", pady=10,fill="x")


        def change_templates():
            messagebox.showinfo(title="Application Manager",message="Introducing this feature soon, currently under development")

        bt1 = customtkinter.CTkButton(button_frame,text="Templates",width=20,font=("Aerial",12,"bold"),text_color="white",command=change_templates)
        bt1.pack(side="left",fill="y")


        def download_card():
            if self.mastercard_status == True:
                mastercard_path = f"{self.user.title()}_master_card.png"

                def download_file(source_path):
                    if not os.path.isfile(source_path):
                        messagebox.showerror("Error", f"The file '{source_path}' does not exist.")
                        return

                    # Ask user for destination path
                    destination_path = filedialog.askdirectory(title="Select a folder to download")
                    if not destination_path:
                        messagebox.showinfo("Cancelled", "Copy operation cancelled.")
                        return

                    try:
                        shutil.copy2(source_path, destination_path)
                        messagebox.showinfo("Success", f"File copied to:\n{destination_path}")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to copy file:\n{e}")

                download_file(source_path=mastercard_path)

            else:
                messagebox.showwarning(title="No master found",message="Please create masterkey to download mastercard")

        bt2 = customtkinter.CTkButton(button_frame, text="Download", width=20,font=("Aerial",12,"bold"),text_color="white",command=download_card)
        bt2.pack(side="left", fill="y",padx=4)

        card_usage_title = customtkinter.CTkLabel(card_display_area_frame, text="How to use the card", text_color="black",
                                                  font=("Oswald", 16), anchor="w")
        card_usage_title.pack(side="top", fill="x", padx=5, pady=5)

        detail = "This is Mysphere Vault Key which makes you login in the device in which you are already signed in or trying to access in another device.\n\nStep 1 : Download the card or get the physical card\nStep 2 : Open MySphere desktop application\nStep 3 : Click on the SCAN button, in the login window & scan it\nStep 4 : Provide the master key if required*"

        card_detail = customtkinter.CTkLabel(card_display_area_frame, text=detail, fg_color="transparent",
                                                    corner_radius=4,wraplength=400,justify="left",anchor="nw",pady=5,font=("Calibri",14))
        card_detail.pack(side="top", pady=5,fill="x")

        card_usage_title = customtkinter.CTkLabel(card_display_area_frame, text="Never share your Master Key",
                                                  text_color="red",
                                                  font=("calibri", 14,"bold"), anchor="w")
        card_usage_title.pack(side="top", fill="x", padx=5, pady=2)













        pass

    def mysphere_interface1(self):
        for i in self.root.winfo_children():
            i.destroy()

        self.root.title("MySphere")
        self.root.configure(bg="#f0f0f0")


        # print(self.backend.myvault_space())

        user = customtkinter.CTkImage(
            light_image=Image.open("Icons\\user.png"),
            dark_image=Image.open("Icons\\user.png"),
            size=(30, 30))
        file = customtkinter.CTkImage(
            light_image=Image.open("Icons\\file.png"),
            dark_image=Image.open("Icons\\file.png"),
            size=(30, 30))
        upload = customtkinter.CTkImage(
            light_image=Image.open("Icons\\upload.png"),
            dark_image=Image.open("Icons\\upload.png"),
            size=(30, 30))

        inbox_logo = customtkinter.CTkImage(
            light_image=Image.open("Icons\\inbox.png"),
            dark_image=Image.open("Icons\\inbox.png"),
            size=(30, 30))

        setting_logo = customtkinter.CTkImage(
            light_image=Image.open("Icons\\setting.png"),
            dark_image=Image.open("Icons\\setting.png"),
            size=(30, 30))

        logout_logo = customtkinter.CTkImage(
            light_image=Image.open("Icons\\logout.png"),
            dark_image=Image.open("Icons\\logout.png"),
            size=(30, 30))

        drive_logo = customtkinter.CTkImage(
            light_image=Image.open("Icons\\googledrive.png"),
            dark_image=Image.open("Icons\\googledrive.png"),
            size=(50, 50))

        api_logo = customtkinter.CTkImage(
            light_image=Image.open("Icons\\api.png"),
            dark_image=Image.open("Icons\\api.png"),
            size=(50, 50))

        secure_logo = customtkinter.CTkImage(
            light_image=Image.open("Icons\\secure.png"),
            dark_image=Image.open("Icons\\secure.png"),
            size=(30, 30))

        h_view = customtkinter.CTkImage(
            light_image=Image.open("Icons\\gridview.png"),
            dark_image=Image.open("Icons\\gridview.png"),
            size=(20, 20))

        v_view = customtkinter.CTkImage(
            light_image=Image.open("Icons\\verticalview.png"),
            dark_image=Image.open("Icons\\verticalview.png"),
            size=(20, 20))

        forward = customtkinter.CTkImage(
            light_image=Image.open("Icons\\next.png"),
            dark_image=Image.open("Icons\\next.png"),
            size=(30, 30))

        backward = customtkinter.CTkImage(
            light_image=Image.open("Icons\\back.png"),
            dark_image=Image.open("Icons\\back.png"),
            size=(30, 30))

        mysphere = customtkinter.CTkImage(
            light_image=Image.open("Icons\\plane_logo.png"),
            dark_image=Image.open("Icons\\plane_logo.png"),
            size=(90, 95))

        share = customtkinter.CTkImage(
            light_image=Image.open("Icons\\share.png"),
            dark_image=Image.open("Icons\\share.png"),
            size=(20, 20))

        addfriend = customtkinter.CTkImage(
            light_image=Image.open("Icons\\addf.png"),
            dark_image=Image.open("Icons\\addf.png"),
            size=(20, 20))

        copy = customtkinter.CTkImage(
            light_image=Image.open("Icons\\copy.png"),
            dark_image=Image.open("Icons\\copy.png"),
            size=(20, 20))

        rename = customtkinter.CTkImage(
            light_image=Image.open("Icons\\rename.png"),
            dark_image=Image.open("Icons\\rename.png"),
            size=(20, 20))

        share = customtkinter.CTkImage(
            light_image=Image.open("Icons\\share.png"),
            dark_image=Image.open("Icons\\share.png"),
            size=(20, 20))

        createqr = customtkinter.CTkImage(
            light_image=Image.open("Icons\\qrcodeb.png"),
            dark_image=Image.open("Icons\\qrcodeb.png"),
            size=(20, 20))

        scanqr = customtkinter.CTkImage(
            light_image=Image.open("Icons\\scan.png"),
            dark_image=Image.open("Icons\\scan.png"),
            size=(20, 20))

        new_folder = customtkinter.CTkImage(
            light_image=Image.open("Icons\\createfolder.png"),
            dark_image=Image.open("Icons\\createfolder.png"),
            size=(20, 20))

        new_file = customtkinter.CTkImage(
            light_image=Image.open("Icons\\createfile.png"),
            dark_image=Image.open("Icons\\createfile.png"),
            size=(20, 20))

        upload2 = customtkinter.CTkImage(
            light_image=Image.open("Icons\\upload2.png"),
            dark_image=Image.open("Icons\\upload2.png"),
            size=(20, 20))

        download = customtkinter.CTkImage(
            light_image=Image.open("Icons\\download.png"),
            dark_image=Image.open("Icons\\download.png"),
            size=(20, 20))


        # upload = customtkinter.CTkImage(
        #     light_image=Image.open("Icons\\upload.png"),
        #     dark_image=Image.open("Icons\\upload.png"),
        #     size=(30, 30))

        # interface_container = customtkinter.CTkFrame(self.root,corner_radius=0, fg_color="transparent")
        # interface_container.pack(side="top", fill="both",expand=1)

        side_bar_frame = customtkinter.CTkFrame(self.root, width=250, corner_radius=0, fg_color="white")
        side_bar_frame.pack(side="left", fill="y")

        logo_header_frame = customtkinter.CTkFrame(side_bar_frame, height=50, corner_radius=0)
        logo_header_frame.pack(side="top", fill="x")

        logo = customtkinter.CTkLabel(logo_header_frame,text="",font=("Agency FB",29,"bold"),height=100,fg_color="white",image=mysphere)
        logo.pack(side="top",fill="both",expand=1)

        empty_frame = customtkinter.CTkFrame(side_bar_frame, corner_radius=0, height=12, fg_color="transparent")
        empty_frame.pack(side="top", fill="x")

        side_bar_menu = customtkinter.CTkFrame(side_bar_frame, fg_color="white", corner_radius=15,border_width=0)
        side_bar_menu.pack(side="top", fill="both",padx=5)

        storage_area = customtkinter.CTkFrame(side_bar_frame, fg_color=self.theme_color, corner_radius=15,border_width=2,border_color="#faf0b9")
        storage_area.pack(side="top", fill="x",padx=5,pady=5)
        storage_area.pack_propagate(False)

        footer = customtkinter.CTkFrame(side_bar_frame, fg_color=self.theme_color,corner_radius=15,border_width=2,border_color="#faf0b9")
        footer.pack(side="bottom", fill="both",expand=1,padx=5,pady=5)

        container_frame = customtkinter.CTkFrame(self.root, corner_radius=0,fg_color="#f0f0f0")
        container_frame.pack(side="left", fill="both", expand=1)

        menubar_frame = customtkinter.CTkFrame(container_frame, height=25, corner_radius=0, fg_color="white")
        menubar_frame.pack(side="top", fill="x")

        # Toolbar

        tool_bar_frame = customtkinter.CTkFrame(container_frame, height=50, corner_radius=0,fg_color=self.theme_color)
        tool_bar_frame.pack(side="top", fill="x", pady=5, padx=10)
        tool_bar_frame.pack_propagate(False)

        self.back_bt = customtkinter.CTkButton(tool_bar_frame, text="", image=backward,command=self.display_back,
                                                corner_radius=2, fg_color="transparent", width=30,hover_color=self.hover_theme)
        self.back_bt.pack(side="left", fill="both",padx=5,pady=5)

        self.next_bt = customtkinter.CTkButton(tool_bar_frame, text="", image=forward,
                                              corner_radius=2, fg_color="transparent", width=30,hover_color=self.hover_theme)
        self.next_bt.pack(side="left", fill="both",pady=5)

        self.search_bar = customtkinter.CTkEntry(tool_bar_frame,width=400,height=30,border_width=1,corner_radius=4,placeholder_text="Search File/Folder",fg_color="white",placeholder_text_color="black",)
        self.search_bar.pack(side="left",pady=5,padx=20)

        self.search_bt = customtkinter.CTkButton(tool_bar_frame,text="Search",width=100,height=30,fg_color="#4CAF50",hover_color="#45A049",font=("Aerial",12,"bold"),text_color="white",corner_radius=4)
        self.search_bt.pack(side="left",pady=5,padx=2)

        self.clear_bt = customtkinter.CTkButton(tool_bar_frame, text="Clear", width=80, height=30, fg_color="#F44336",hover_color="#D7372B",
                                            font=("Aerial", 12, "bold"), text_color="white", corner_radius=4)
        self.clear_bt.pack(side="left", pady=5, padx=2)

        suggestor = customtkinter.CTkFrame(tool_bar_frame,fg_color="transparent")
        suggestor.pack(side="left",fill="both",expand=1,padx=5,pady=10)

        self.main_progressbar = customtkinter.CTkProgressBar(suggestor,width=200,corner_radius=0,height=10,progress_color="#35c435",fg_color="#dcdedc")
        # self.main_progressbar.pack(side="left",fill="y",pady=7,padx=20)

        self.main_progressbar.set(0.0)

        sugg_label = customtkinter.CTkLabel(suggestor,text="Click anywhere to know about",font=("Aerial",12,"italic"),text_color="#5e5e5e")
        sugg_label.pack(side="right",fill="x",padx=20)





        self.display_area_frame = customtkinter.CTkFrame(container_frame, corner_radius=2,fg_color="white")
        self.display_area_frame.pack(side="top", fill="both", expand=1, padx=10)

        self.header_frame = customtkinter.CTkFrame(self.display_area_frame,corner_radius=0,fg_color="white")
        self.header_frame.pack(side="top",fill="x")


        self.displayarea_title = customtkinter.CTkLabel(self.header_frame, text="", font=("Oswald", 20,),
                                                        text_color="black", anchor="w", padx=30, fg_color="white",
                                                        corner_radius=0, height=50)
        self.displayarea_title.pack(side="left", fill="x", pady=0,expand=1)

        new_file_bt = customtkinter.CTkButton(self.header_frame, text="", image=new_file, width=0, height=10,
                                                fg_color=self.hover_theme)
        new_file_bt.pack(side="left", padx=2)

        new_folder_bt = customtkinter.CTkButton(self.header_frame, text="", image=new_folder, width=0, height=10,
                                                fg_color=self.hover_theme)
        new_folder_bt.pack(side="left", padx=2)

        download_bt = customtkinter.CTkButton(self.header_frame, text="", image=download, width=0, height=10,
                                                fg_color=self.hover_theme)
        download_bt.pack(side="left", padx=2)

        upload2_bt = customtkinter.CTkButton(self.header_frame, text="", image=upload2, width=0, height=10,
                                                fg_color=self.hover_theme)
        upload2_bt.pack(side="left", padx=2)

        def run_add_friend():
            users_dic = self.check_friends()


            self.displayarea_title.configure(text="Available user")

            try:
                for i in self.container.winfo_children():
                    i.destroy()
            except:
                pass

            user = customtkinter.CTkImage(
                light_image=Image.open("Icons\\user.png"),
                dark_image=Image.open("Icons\\user.png"),
                size=(20, 20))

            self.folder_area_frame = customtkinter.CTkScrollableFrame(self.container, fg_color="white")
            self.folder_area_frame.pack(side="left", fill="both", expand=1)



            for i in users_dic:
                print(i,users_dic[i])
                user_frame = customtkinter.CTkFrame(self.folder_area_frame,fg_color="transparent")
                user_frame.pack(side="top",fill="x")

                def add_to_friend(id=i,name=users_dic[i]):
                    print(f"Adding {id} to our friends")

                    def send_request():
                        # Create a connection.ms

                        x = datetime.now()
                        # "%#d %b %Y"
                        date = x.strftime("%#d")
                        month = x.strftime("%b")
                        year = x.strftime("%Y")

                        timestamp = f"{date} {month} {year}"

                        messagebox.showinfo(title="Info", message=f"Sending request to {name}")
                        content = f"{self.user} :: {timestamp} :: Hello, {name} i would like to connect with you"
                        file_id = self.backend.create_connection_file(content=content, friend_name=name, email_id=id)

                        data = {file_id: {"status": "pending", "email": id, "name": name}}
                        self.backend.write_into_friend_ms(content=data)

                    threading.Thread(target=send_request).start()



                label = customtkinter.CTkLabel(user_frame,text=users_dic[i],compound="left",padx=10,anchor="w",height=30,image=user,font=("Aerial Rounded MT",12,),width=200,fg_color=self.theme_color)
                label.pack(side="left",padx=15,pady=2)

                add = customtkinter.CTkButton(user_frame,text="Add",command=add_to_friend,font=("Aerial Rounded MT",12,"bold"),corner_radius=5,height=25,width=100)
                add.pack(side="left",padx=5,pady=2)


        def thread_add_friend():
            # run_add_friend()
            threading.Thread(target=run_add_friend).start()
            # self.run_progress_bar()
            # self.main_progressbar.set(0)


        add_friend_bt = customtkinter.CTkButton(self.header_frame, text="", image=addfriend, width=0, height=10,
                                                fg_color=self.hover_theme,command=thread_add_friend)
        add_friend_bt.pack(side="left",padx=2)


        def close_scanner():
            self.scanning = False
            if self.cap:
                self.cap.release()

                self.scanner_frame.configure(height=0)
                # self.scanqr_frame.configure(height=0)
                self.video_label.pack_forget()
                self.scanqr_frame.place_forget()

                self.cap = None

                self.root.update_idletasks()
            scanqr_bt.configure(command=scan_qr)


        def open_scanner():
            self.scanner_frame.configure(height=200,width=300)
            self.video_label.pack(side="top",fill="both",expand=1)
            scanqr_bt.configure(command=close_scanner)
            # self.frame_1.configure(fg_color="black")

            if not self.cap:
                self.cap = cv2.VideoCapture(0)

            self.scanning = True
            self.update_frame_resize()

        def scan_qr():
            x = scanqr_bt.winfo_x()
            y = scanqr_bt.winfo_y()
            print(x,y)

            self.scanqr_frame = customtkinter.CTkFrame(self.root,height=300,width=400,fg_color="black",corner_radius=0)
            self.scanqr_frame.place(x=(x-200),y=(y+140))

            self.scanner_frame = customtkinter.CTkFrame(self.scanqr_frame,height=200,width=300)
            self.scanner_frame.pack(side="top",fill="both",padx=2)
            self.scanner_frame.pack_propagate(False)


            self.video_label = customtkinter.CTkLabel(self.scanner_frame, text="",fg_color="black")
            self.video_label.pack(side="top", fill="both",expand=1)

            bt1 = customtkinter.CTkButton(self.scanqr_frame,text="From gallery")
            bt1.pack(side="top",pady=5)


            open_scanner()


        scanqr_bt = customtkinter.CTkButton(self.header_frame,text="",image=scanqr,width=0,height=10,
                                            fg_color=self.hover_theme,command=scan_qr)
        scanqr_bt.pack(side="left",padx=2)

        # To open qr code creator
        def open_create_qr():

            qr = customtkinter.CTkImage(
                light_image=Image.open("Icons\\sampleqrcode.png"),
                dark_image=Image.open("Icons\\sampleqrcode.png"),
                size=(140, 140))

            x = scanqr_bt.winfo_x()
            y = scanqr_bt.winfo_y()
            print(x, y)


            self.createqr_frame = customtkinter.CTkFrame(self.container,width=400, fg_color="transparent",
                                                       corner_radius=0)
            self.createqr_frame.pack(side="left",fill="both")

            self.createqr_frame.pack_propagate(0)

            title = customtkinter.CTkLabel(self.createqr_frame,text="Create QR code",font=("Oswald",18,),height=40,fg_color=self.theme_color)
            title.pack(side="top",fill="x")

            qrcode = customtkinter.CTkLabel(self.createqr_frame, image=qr,text="", font=("Oswald", 18,),
                                           height=150,width=150,fg_color=self.hover_theme )
            qrcode.pack(side="top",pady=10)

            title = customtkinter.CTkLabel(self.createqr_frame, text="Define your QR code type", font=("MS Aerial Rounded", 14,), height=40,
                                           fg_color="transparent",anchor="w",padx=20)
            title.pack(side="top", fill="x")

            def radiobutton_event():
                radio_bt = radio_var.get()

                if radio_bt == 1:
                    # For one-time accessible
                    try:
                        self.properties_frame.pack_forget()
                    except:
                        pass

                    self.properties_frame = customtkinter.CTkFrame(self.createqr_frame, fg_color="transparent")
                    self.properties_frame.pack(side="top", fill="x", padx=8, pady=20)

                    subdiv1 = customtkinter.CTkFrame(self.properties_frame, fg_color="transparent")
                    subdiv1.pack(side="top", fill="x", pady=5, padx=10)

                    def run_create_qr_func_one_time():

                        def generate_qr_id(length):
                            characters = string.ascii_letters + string.digits
                            return ''.join(random.choices(characters, k=length))

                        qr_code_id = generate_qr_id(length=5)
                        print("Generated QR ID: ", qr_code_id)

                        data = {"Type": "O",
                                "qr_code_id": qr_code_id,
                                "user_id": "NIL",
                                "username": "NIL",
                                "password": "NIL",
                                "content": "hello world",
                                }

                        print(data)

                        # self.qr_code_create(data=data)

                        # Now, Upload info abput this qrcode to mysphere vault

                        # vault_id = self.backend.vault_id
                        # self.backend.create_file(filename=f"{qr_code_id}.QR",content="",parent=vault_id)


                    create_bt = customtkinter.CTkButton(subdiv1, text="Create", width=160,
                                                        corner_radius=5,command=run_create_qr_func_one_time)
                    create_bt.pack(side="bottom", padx=2, pady=15, anchor="w")




                    pass

                elif radio_bt == 2:
                    # For multiuser
                    pass

                elif radio_bt == 3:
                    # For time constraint
                    try:
                        self.properties_frame.pack_forget()
                    except:
                        pass

                    self.properties_frame = customtkinter.CTkFrame(self.createqr_frame,fg_color="transparent")
                    self.properties_frame.pack(side="top",fill="x",padx=8,pady=20)

                    subdiv1 = customtkinter.CTkFrame(self.properties_frame,fg_color="transparent")
                    subdiv1.pack(side="top",fill="x",pady=5,padx=10)
                    subdiv2 = customtkinter.CTkFrame(self.properties_frame,fg_color="transparent")
                    subdiv2.pack(side="top", fill="x",pady=2,padx=10)

                    start_date = customtkinter.CTkEntry(subdiv1,placeholder_text="Start date (DD/MM/YY)")
                    # start_date.pack(side="left",padx=2)
                    self.end_date = customtkinter.CTkEntry(subdiv1,placeholder_text="End date (DD/MM/YY)",width=160)
                    self.end_date.pack(side="left",padx=2)

                    def run_create_qr_func_time_cons():

                        def generate_qr_id(length):
                            characters = string.ascii_letters + string.digits
                            return ''.join(random.choices(characters, k=length))

                        qr_code_id = generate_qr_id(length=5)
                        print("Generated QR ID: ", qr_code_id)

                        #DD/MM/YY - start
                        #DD/MM/YY/HH/MM/SS end

                        def current_date():
                            x = datetime.now()

                            date = x.strftime("%d")
                            month = x.strftime("%m")
                            year = x.strftime("%y")

                            full_date = f"{date}/{month}/{year}"

                            return full_date

                        start_date = current_date()
                        self.end_date = self.end_date.get()
                        self.end_time = self.end_time.get()

                        def format_time(time):
                            splitted_time = time.split(":")
                            formatted_time = "/".join(splitted_time)

                            return formatted_time

                        end_time = format_time(self.end_time)
                        print(end_time)


                        end_timestamp = f"{self.end_date}//{end_time}"

                        data = {"Type": "T",
                                "qr_code_id": qr_code_id,
                                "user_id": "NIL",
                                "username": "NIL",
                                "password": "NIL",
                                "start_time": start_date,
                                "end_time": end_timestamp,
                                "content": "txt{Hello world}",

                                }

                        self.qr_code_create(data=data)

                    create_bt = customtkinter.CTkButton(subdiv2, text="Create",command=run_create_qr_func_time_cons,width=160,corner_radius=5)
                    create_bt.pack(side="bottom", padx=2,pady=15,anchor="w")

                    start_time = customtkinter.CTkEntry(subdiv2, placeholder_text="Enter start time(HH:MM:SS)")
                    # start_time.pack(side="left",padx=2)
                    self.end_time = customtkinter.CTkEntry(subdiv2, placeholder_text="End time (HH:MM:SS)",width=160)
                    self.end_time.pack(side="left",padx=2)



                    pass

                elif radio_bt == 4:
                    # For single user
                    pass

                # print("radiobutton toggled, current value:", radio_var.get())

            radio_var = customtkinter.IntVar(value=0)

            onetime = customtkinter.CTkRadioButton(self.createqr_frame, text="One time accessible",
                                                         command=radiobutton_event, variable=radio_var, value=1, radiobutton_width=19,
                                                         radiobutton_height=19,border_width_unchecked=2,
                                                         border_width_checked=5,
                                                         fg_color="green",font=("Aerial",13,))
            onetime.pack(side="top", fill="x",padx=20)

            multi = customtkinter.CTkRadioButton(self.createqr_frame, text="Multiuser accessible",
                                                         command=radiobutton_event, variable=radio_var, value=2, radiobutton_width=19,
                                                         radiobutton_height=19,border_width_unchecked=2,
                                                         border_width_checked=5,
                                                         fg_color="green",font=("Aerial",13,))
            multi.pack(side="top", fill="x",padx=20)

            time_cons = customtkinter.CTkRadioButton(self.createqr_frame, text="Time constraint",
                                                         command=radiobutton_event, variable=radio_var, value=3 ,radiobutton_width=19,
                                                         radiobutton_height=19,border_width_unchecked=2,
                                                         border_width_checked=5,
                                                         fg_color="green",font=("Aerial",13,))
            time_cons.pack(side="top", fill="x",padx=20)

            single = customtkinter.CTkRadioButton(self.createqr_frame, text="Single user accessible",
                                                         command=radiobutton_event, variable=radio_var, value=4,
                                                         radiobutton_width=19,
                                                         radiobutton_height=19,border_width_unchecked=2,
                                                         border_width_checked=5,
                                                         fg_color="green",font=("Aerial",13,))
            single.pack(side="top", fill="x",padx=20)

        createqr_bt = customtkinter.CTkButton(self.header_frame, text="", image=createqr, width=0, height=10,fg_color=self.hover_theme
                                              ,command=open_create_qr)
        createqr_bt.pack(side="left",padx=2)

        rename_bt = customtkinter.CTkButton(self.header_frame, text="", image=rename, width=0, height=10,fg_color=self.hover_theme)
        rename_bt.pack(side="left",padx=2)

        copy_bt = customtkinter.CTkButton(self.header_frame, text="", image=copy, width=0, height=10,fg_color=self.hover_theme)
        copy_bt.pack(side="left",padx=2)

        share_bt = customtkinter.CTkButton(self.header_frame, text="", image=share, width=0, height=10,fg_color=self.hover_theme)
        share_bt.pack(side="left",padx=2)



        orientation_frame = customtkinter.CTkFrame(self.header_frame, width=100, fg_color="white",)
        orientation_frame.pack(side="left",fill="y",padx=20)

        def horizontal_view():
            self.file_view_orientation = "Horizontal"
            loaded_file = self.load_files(id=self.current_folder_id)
            self.display_files(fileandfolder=loaded_file)

        def vertical_view():
            self.file_view_orientation = "Vertical"
            loaded_file = self.load_files(id=self.current_folder_id)
            self.display_files(fileandfolder=loaded_file)

        self.horizontal_bt = customtkinter.CTkButton(orientation_frame, text="", command=horizontal_view,image=h_view,fg_color=self.hover_theme, width=0, height=10,hover_color=self.hover_theme)
        self.horizontal_bt.pack(side="left",padx=2)

        self.vertical_bt = customtkinter.CTkButton(orientation_frame, text="",command=vertical_view,image=v_view,fg_color=self.hover_theme,width=0, height=10,hover_color=self.hover_theme)
        self.vertical_bt.pack(side="left",padx=2)

        self.container = customtkinter.CTkFrame(self.display_area_frame, fg_color="transparent")
        self.container.pack(side="left", fill="both", expand=1)



        # Side bar buttons

        my_profile = customtkinter.CTkButton(side_bar_menu, text="My Profile", font=("Aerial Rounded MT",14,"bold"),
                                             corner_radius=2, height=31, fg_color=self.theme_color,image=user,text_color="black",anchor="w",hover_color=self.hover_theme,command=self.my_profile)
        my_profile.pack(side="top", fill="x", padx=20, pady=20)

        my_file = customtkinter.CTkButton(side_bar_menu, text="Files", font=("Aerial Rounded MT",13,"bold"), corner_radius=2,
                                          height=31, fg_color=self.theme_color,image=file,text_color="black",anchor="w",hover_color=self.hover_theme,command=self.view_files)
        my_file.pack(side="top", fill="x", padx=20, pady=5)

        upload_file = customtkinter.CTkButton(side_bar_menu, text="Upload", font=("Aerial Rounded MT",13,"bold"),
                                              corner_radius=2, height=31, fg_color=self.theme_color,image=upload,text_color="black",anchor="w",hover_color=self.hover_theme,command=self.open_file_dialog)
        upload_file.pack(side="top", fill="x", padx=20, pady=5)

        inbox = customtkinter.CTkButton(side_bar_menu, text="Inbox", font=("Aerial Rounded MT", 13, "bold"),
                                              corner_radius=2, height=31, fg_color=self.theme_color, image=inbox_logo,
                                              text_color="black", anchor="w", hover_color=self.hover_theme,command=self.inbox)
        inbox.pack(side="top", fill="x", padx=20, pady=5)

        setting = customtkinter.CTkButton(side_bar_menu, text="Setting", font=("Aerial Rounded MT", 13, "bold"),
                                        corner_radius=2, height=31, fg_color=self.theme_color, image=setting_logo,
                                        text_color="black", anchor="w", hover_color=self.hover_theme,command=self.setting)
        setting.pack(side="top", fill="x", padx=20, pady=5)


        def logout():
            # Log out from main interface
            for i in self.root.winfo_children():
                i.destroy()

            self.login_interface()

        Logout = customtkinter.CTkButton(side_bar_menu, text="Log Out", font=("Aerial Rounded MT", 13, "bold"),
                                              corner_radius=2, height=31, fg_color=self.theme_color, image=logout_logo,
                                              text_color="black", anchor="w", hover_color=self.hover_theme,command=logout)
        Logout.pack(side="top", fill="x", padx=21, pady=20)




        # Storage
        title = customtkinter.CTkLabel(storage_area,text="Space Usage",anchor="w",padx=10, font=("Aerial Rounded MT", 13, "bold"),)
        title.pack(side="top",fill="x",padx=5,pady=7)

        spacebar = customtkinter.CTkProgressBar(storage_area, orientation="horizontal",height=10,corner_radius=4,progress_color="#35c435",fg_color="#dcdedc")
        spacebar.pack(side="top",fill="x",padx=14,pady=4)

        spacebar.set(0.2)

        totalspace = customtkinter.CTkLabel(storage_area, text="Total Space : 5 GB (As per plan)*", padx=10,
                                           font=("Aerial Rounded MT", 11,"bold"),anchor="w" )
        totalspace.pack(side="top", fill="x", padx=5, pady=0)

        space_used = customtkinter.CTkLabel(storage_area, text="Space Used : \nSpace Available :", padx=12,
                                       font=("Aerial Rounded MT", 11,),justify="left",anchor="w")
        space_used.pack(side="top", fill="x", padx=5, pady=0)

        space_manage = customtkinter.CTkLabel(storage_area, text="Integrated with \nspace management", padx=12,
                                            font=("Aerial Rounded MT", 11,"italic"), justify="left", anchor="w")
        space_manage.pack(side="bottom", fill="x", padx=5, pady=5)











        # Footer
        citation_label = customtkinter.CTkButton(footer, text="Made in PSIT", text_color="red",
                                                 font=("Oswald", 12, "bold"), border_width=2, border_color="red",
                                                 corner_radius=19, fg_color="transparent", hover=False,)
        citation_label.pack(side="top", fill="x", padx=5, pady=5)

        developercitation = customtkinter.CTkLabel(footer, text="Saksham Developments",
                                                   font=("Aerial Rounded MT", 11), height=2)
        developercitation.pack(side="bottom", fill="x", padx=5, pady=5)

        googledrivecitation = customtkinter.CTkLabel(footer, text="", padx=12,
                                              font=("Aerial Rounded MT", 11, "italic"), justify="left", anchor="w",image=drive_logo)
        googledrivecitation.pack(side="left", fill="x", padx=5, pady=1)

        apicitation = customtkinter.CTkLabel(footer, text="", padx=12,
                                                     font=("Aerial Rounded MT", 11, "italic"), justify="left",
                                                     anchor="w", image=api_logo)
        apicitation.pack(side="left", fill="x", padx=20, pady=1)

        securecitation = customtkinter.CTkLabel(footer, text="", padx=22,
                                                     font=("Aerial Rounded MT", 11, "italic"), justify="left",
                                                     anchor="w", image=secure_logo,)
        securecitation.pack(side="left", fill="x", padx=20, pady=1)


        # Menubar

        empty_option = customtkinter.CTkButton(menubar_frame, text="", width=100, fg_color="transparent",
                                              text_color="black",state="disabled")
        empty_option.pack(side="left", fill="y", padx=25,)

        file_option = customtkinter.CTkButton(menubar_frame,text="File",width=70,fg_color="transparent",text_color="black",font=("Aerial Rounded MT", 12),hover="disabled")
        file_option.pack(side="left",fill="y",padx=5)

        upload_option = customtkinter.CTkButton(menubar_frame, text="Upload", width=70, fg_color="transparent",
                                              text_color="black",font=("Aerial Rounded MT", 12),hover="disabled")
        upload_option.pack(side="left", fill="y", padx=0)

        upload_option = customtkinter.CTkButton(menubar_frame, text="Inbox", width=70, fg_color="transparent",
                                                text_color="black",font=("Aerial Rounded MT", 12),hover="disabled")
        upload_option.pack(side="left", fill="y", padx=5)

        upload_option = customtkinter.CTkButton(menubar_frame, text="Setting", width=70, fg_color="transparent",
                                                text_color="black",font=("Aerial Rounded MT", 12),hover="disabled")
        upload_option.pack(side="left", fill="y", padx=5)

        help_option = customtkinter.CTkButton(menubar_frame, text="Help", width=70, fg_color="transparent",
                                                text_color="black", font=("Aerial Rounded MT", 12),hover="disabled")
        help_option.pack(side="left", fill="y", padx=5)

        contact_option = customtkinter.CTkButton(menubar_frame, text="Contact Developer", width=70, fg_color="transparent",
                                                text_color="black", font=("Aerial Rounded MT", 12),hover="disabled")
        contact_option.pack(side="left", fill="y", padx=5)

        update_option = customtkinter.CTkButton(menubar_frame, text="Update", width=70,
                                                 fg_color="transparent",
                                                 text_color="black", font=("Aerial Rounded MT", 12),hover="disabled")
        update_option.pack(side="left", fill="y", padx=5)

        logout_option = customtkinter.CTkButton(menubar_frame, text="Logout", width=70,
                                                fg_color="transparent",
                                                text_color="black", font=("Aerial Rounded MT", 12),hover="disabled")
        logout_option.pack(side="right", fill="y", padx=35)









        self.root.mainloop()

    def intermediate_interface(self):

        try:
            for i in self.root.winfo_children():
                i.destroy()
        except:
            pass

        # self.login_interface()

        self.application_starting_interface()

        self.progressbar.set(0)

        def subprocesses():
            try:
                # Preload service

                self.backend.create_service()
                self.progressbar.set(0.2)

                # Preload userlist
                def load_and_update_freindms():
                    try:
                        self.progressbar.set(0.3)
                        data = self.backend.read_and_update_friendms_file()
                        friend_status_list = data[0]
                        changes = data[1]
                        print("Changes in freindms", changes, friend_status_list)
                        self.progressbar.set(0.35)

                        # Getting the connected friend_list
                        for status_dic in friend_status_list:
                            # print(status_dic, "Available")
                            for item in status_dic:
                                file_id = item
                                args = status_dic[file_id]

                                status = args["status"]
                                email = args["email"]
                                name = args["name"]

                                if status == "True":
                                    self.friend_list.append(email)
                                    self.friend_dic.update({name:email})
                                    self.email_friend.update({email:name})

                        # Update the file if changes exist

                        if changes >= 1:
                            self.backend.update_friend_ms(content=friend_status_list)
                            self.progressbar.set(0.4)
                            pass

                        else:
                            self.progressbar.set(0.4)
                            pass

                    except:
                        friend_status_list = []
                        changes = 0

                    self.friend_ms_data = friend_status_list

                load_and_update_freindms()


                # Load shared with me
                def load_shared():
                    self.shared_with_me_data = self.backend.list_sharedwithme_files()

                load_shared()

                # Preload inbox service
                def load_inbox_assets():
                    try:
                        self.progressbar.set(0.45)
                        self.available_connection_req_data = self.backend.see_connection_request()
                        print(data)
                        self.progressbar.set(0.5)
                    except:
                        self.available_connection_req_data = []

                    self.application_users = self.backend.view_app_users()
                    self.progressbar.set(0.6)

                load_inbox_assets()


                for i in range(60,101):
                    self.progressbar.set(i / 100)
                    # print(i)
                    time.sleep(0.001)

                def sound():
                    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)

                threading.Thread(target=sound).start()
                self.mysphere_interface()


            except Exception as e:

                print("Error from subprocess",e)
                # self.message_label.configure(text="Network is not available", font=("Agency FB", 14, "bold"),text_color="red")

        threading.Thread(target=subprocesses).start()

    # New
    def mysphere_interface(self):
        for i in self.root.winfo_children():
            i.destroy()

        self.root.title("MySphere")
        self.root.configure(bg="#f0f0f0")

        user = customtkinter.CTkImage(
            light_image=Image.open("Icons\\user.png"),
            dark_image=Image.open("Icons\\user.png"),
            size=(30, 30))
        file = customtkinter.CTkImage(
            light_image=Image.open("Icons\\file.png"),
            dark_image=Image.open("Icons\\file.png"),
            size=(30, 30))
        upload = customtkinter.CTkImage(
            light_image=Image.open("Icons\\upload.png"),
            dark_image=Image.open("Icons\\upload.png"),
            size=(30, 30))

        inbox_logo = customtkinter.CTkImage(
            light_image=Image.open("Icons\\inbox.png"),
            dark_image=Image.open("Icons\\inbox.png"),
            size=(30, 30))

        setting_logo = customtkinter.CTkImage(
            light_image=Image.open("Icons\\setting.png"),
            dark_image=Image.open("Icons\\setting.png"),
            size=(30, 30))

        logout_logo = customtkinter.CTkImage(
            light_image=Image.open("Icons\\logout.png"),
            dark_image=Image.open("Icons\\logout.png"),
            size=(30, 30))

        drive_logo = customtkinter.CTkImage(
            light_image=Image.open("Icons\\googledrive.png"),
            dark_image=Image.open("Icons\\googledrive.png"),
            size=(50, 50))

        api_logo = customtkinter.CTkImage(
            light_image=Image.open("Icons\\api.png"),
            dark_image=Image.open("Icons\\api.png"),
            size=(50, 50))

        secure_logo = customtkinter.CTkImage(
            light_image=Image.open("Icons\\secure.png"),
            dark_image=Image.open("Icons\\secure.png"),
            size=(30, 30))

        h_view = customtkinter.CTkImage(
            light_image=Image.open("Icons\\gridview.png"),
            dark_image=Image.open("Icons\\gridview.png"),
            size=(20, 20))

        v_view = customtkinter.CTkImage(
            light_image=Image.open("Icons\\verticalview.png"),
            dark_image=Image.open("Icons\\verticalview.png"),
            size=(20, 20))

        forward = customtkinter.CTkImage(
            light_image=Image.open("Icons\\next.png"),
            dark_image=Image.open("Icons\\next.png"),
            size=(30, 30))

        backward = customtkinter.CTkImage(
            light_image=Image.open("Icons\\back.png"),
            dark_image=Image.open("Icons\\back.png"),
            size=(30, 30))

        mysphere = customtkinter.CTkImage(
            light_image=Image.open("Icons\\plane_logo.png"),
            dark_image=Image.open("Icons\\plane_logo.png"),
            size=(90, 95))

        share = customtkinter.CTkImage(
            light_image=Image.open("Icons\\share.png"),
            dark_image=Image.open("Icons\\share.png"),
            size=(20, 20))

        addfriend = customtkinter.CTkImage(
            light_image=Image.open("Icons\\addf.png"),
            dark_image=Image.open("Icons\\addf.png"),
            size=(20, 20))

        copy = customtkinter.CTkImage(
            light_image=Image.open("Icons\\copy.png"),
            dark_image=Image.open("Icons\\copy.png"),
            size=(20, 20))

        rename = customtkinter.CTkImage(
            light_image=Image.open("Icons\\rename.png"),
            dark_image=Image.open("Icons\\rename.png"),
            size=(20, 20))

        share = customtkinter.CTkImage(
            light_image=Image.open("Icons\\share.png"),
            dark_image=Image.open("Icons\\share.png"),
            size=(20, 20))

        createqr = customtkinter.CTkImage(
            light_image=Image.open("Icons\\qrcodeb.png"),
            dark_image=Image.open("Icons\\qrcodeb.png"),
            size=(20, 20))

        scanqr = customtkinter.CTkImage(
            light_image=Image.open("Icons\\scan.png"),
            dark_image=Image.open("Icons\\scan.png"),
            size=(20, 20))

        new_folder = customtkinter.CTkImage(
            light_image=Image.open("Icons\\createfolder.png"),
            dark_image=Image.open("Icons\\createfolder.png"),
            size=(20, 20))

        new_file = customtkinter.CTkImage(
            light_image=Image.open("Icons\\createfile.png"),
            dark_image=Image.open("Icons\\createfile.png"),
            size=(20, 20))

        upload2 = customtkinter.CTkImage(
            light_image=Image.open("Icons\\upload2.png"),
            dark_image=Image.open("Icons\\upload2.png"),
            size=(20, 20))

        download = customtkinter.CTkImage(
            light_image=Image.open("Icons\\download.png"),
            dark_image=Image.open("Icons\\download.png"),

            size=(20, 20))
        folder_logo = customtkinter.CTkImage(
            light_image=Image.open("Icons\\folder.png"),
            dark_image=Image.open("Icons\\folder.png"),
            size=(15, 15))

        file_logo = customtkinter.CTkImage(
            light_image=Image.open("Icons\\file2.png"),
            dark_image=Image.open("Icons\\file2.png"),
            size=(15, 15))

        # upload = customtkinter.CTkImage(
        #     light_image=Image.open("Icons\\upload.png"),
        #     dark_image=Image.open("Icons\\upload.png"),
        #     size=(30, 30))

        # interface_container = customtkinter.CTkFrame(self.root,corner_radius=0, fg_color="transparent")
        # interface_container.pack(side="top", fill="both",expand=1)

        side_bar_frame = customtkinter.CTkFrame(self.root, width=250, corner_radius=0, fg_color="white")
        side_bar_frame.pack(side="left", fill="y")

        logo_header_frame = customtkinter.CTkFrame(side_bar_frame, height=50, corner_radius=0)
        logo_header_frame.pack(side="top", fill="x")

        logo = customtkinter.CTkLabel(logo_header_frame, text="", font=("Agency FB", 29, "bold"), height=100,
                                      fg_color="white", image=mysphere)
        logo.pack(side="top", fill="both", expand=1)

        empty_frame = customtkinter.CTkFrame(side_bar_frame, corner_radius=0, height=12, fg_color="transparent")
        empty_frame.pack(side="top", fill="x")

        side_bar_menu = customtkinter.CTkFrame(side_bar_frame, fg_color="white", corner_radius=15, border_width=0)
        side_bar_menu.pack(side="top", fill="both", padx=5)

        storage_area = customtkinter.CTkFrame(side_bar_frame, fg_color=self.theme_color, corner_radius=15,
                                              border_width=2, border_color="#faf0b9")
        storage_area.pack(side="top", fill="x", padx=5, pady=5)
        storage_area.pack_propagate(False)

        footer = customtkinter.CTkFrame(side_bar_frame, fg_color=self.theme_color, corner_radius=15, border_width=2,
                                        border_color="#faf0b9")
        footer.pack(side="bottom", fill="both", expand=1, padx=5, pady=5)

        container_frame = customtkinter.CTkFrame(self.root, corner_radius=0, fg_color="#f0f0f0")
        container_frame.pack(side="left", fill="both", expand=1)

        menubar_frame = customtkinter.CTkFrame(container_frame, height=25, corner_radius=0, fg_color="white")
        menubar_frame.pack(side="top", fill="x")

        # Toolbar

        tool_bar_frame = customtkinter.CTkFrame(container_frame, height=50, corner_radius=0,
                                                fg_color=self.theme_color)
        tool_bar_frame.pack(side="top", fill="x", pady=5, padx=10)
        tool_bar_frame.pack_propagate(False)

        self.back_bt = customtkinter.CTkButton(tool_bar_frame, text="", image=backward, command=self.display_back,
                                               corner_radius=2, fg_color="transparent", width=30,
                                               hover_color=self.hover_theme)
        self.back_bt.pack(side="left", fill="both", padx=5, pady=5)

        self.next_bt = customtkinter.CTkButton(tool_bar_frame, text="", image=forward,
                                               corner_radius=2, fg_color="transparent", width=30,
                                               hover_color=self.hover_theme)
        self.next_bt.pack(side="left", fill="both", pady=5)

        self.search_bar = customtkinter.CTkEntry(tool_bar_frame, width=400, height=30, border_width=1, corner_radius=4,
                                            placeholder_text="Search File/Folder", fg_color="white",
                                            placeholder_text_color="black", )
        self.search_bar.pack(side="left", pady=5, padx=20)

        self.search_bt = customtkinter.CTkButton(tool_bar_frame, text="Search", width=100, height=30, fg_color="#4CAF50",
                                            hover_color="#45A049", font=("Aerial", 12, "bold"), text_color="white",
                                            corner_radius=4,text_color_disabled="white")
        self.search_bt.pack(side="left", pady=5, padx=2)

        self.clear_bt = customtkinter.CTkButton(tool_bar_frame, text="Clear", width=80, height=30, fg_color="#F44336",
                                           hover_color="#D7372B",
                                           font=("Aerial", 12, "bold"), text_color="white", corner_radius=4,text_color_disabled="white" )
        self.clear_bt.pack(side="left", pady=5, padx=2)

        suggestor = customtkinter.CTkFrame(tool_bar_frame, fg_color="transparent")
        suggestor.pack(side="left", fill="both", expand=1, padx=5, pady=10)

        self.main_progressbar = customtkinter.CTkProgressBar(suggestor, width=200, corner_radius=0, height=10,
                                                             progress_color="#35c435", fg_color="#dcdedc")
        # self.main_progressbar.pack(side="left",fill="y",pady=7,padx=20)

        self.main_progressbar.set(0.0)

        sugg_label = customtkinter.CTkLabel(suggestor, text="Click anywhere to know about",
                                            font=("Aerial", 12, "italic"), text_color="#5e5e5e")
        sugg_label.pack(side="right", fill="x", padx=20)

        self.display_area_frame = customtkinter.CTkFrame(container_frame, corner_radius=2, fg_color="white")
        self.display_area_frame.pack(side="top", fill="both", expand=1, padx=10)

        self.header_frame = customtkinter.CTkFrame(self.display_area_frame, corner_radius=0, fg_color="white")
        self.header_frame.pack(side="top", fill="x")

        self.displayarea_title = customtkinter.CTkLabel(self.header_frame, text="", font=("Oswald", 20,),
                                                        text_color="black", anchor="w", padx=30, fg_color="white",
                                                        corner_radius=0, height=50)
        self.displayarea_title.pack(side="left", fill="x", pady=0, expand=1)

        def add_file():

            file_frame = customtkinter.CTkFrame(self.folder_area_frame, height=12, border_width=0,
                                                fg_color=self.theme_color)
            file_frame.pack(side="left", padx=20, pady=2)

            file_log = customtkinter.CTkLabel(file_frame, image=file_logo, text="",
                                              text_color="black", fg_color=self.theme_color,
                                              font=("Aerial Rounded MT", 12,), height=5, corner_radius=5,
                                              anchor="w")
            file_log.pack(side="left")
            text_name = customtkinter.CTkEntry(file_frame, font=("Aerial Rounded MT", 12,), height=5,
                                               border_width=0, fg_color=self.theme_color, width=125)
            text_name.pack(side="left")
            text_name.focus()

            self.search_bar.configure(state="disabled")
            self.search_bt.configure(state="disabled")
            # self.clear_bt.configure(state="disabled")
            self.new_file_bt.configure(state="disabled")
            self.new_folder_bt.configure(state="disabled")
            self.download_bt.configure(state="disabled")
            self.upload2_bt.configure(state="disabled")
            self.add_friend_bt.configure(state="disabled")
            self.scanqr_bt.configure(state="disabled")
            self.share_bt.configure(state="disabled")
            self.copy_bt.configure(state="disabled")
            self.rename_bt.configure(state="disabled")
            self.createqr_bt.configure(state="disabled")

            def on_enter_key(event=None):

                entry_text = text_name.get()
                # print("Entered:", entry_text)

                if "." in entry_text:
                    list = entry_text.split(".")

                else:
                    list = [entry_text,"txt"]

                folder_id = self.previous_opened_folder

                if entry_text == "" or entry_text.isspace():
                    messagebox.showwarning("Invalid", "Empty file name ")
                    file_frame.forget()

                else:
                    if folder_id[-1] == '':
                        req_folderid = self.backend.service.get_folder("MySphere Vault")
                        # print(req_folderid)
                        self.backend.service.create_file(file_name=list[0], content="", parent=req_folderid,
                                                         type=list[1])
                    else:
                        req_folderid = folder_id[-1]
                        # print(req_folderid)
                        self.backend.service.create_file(file_name=list[0], content="", parent=req_folderid,
                                                         type=list[1])

                    loaded_file = self.load_files(id=req_folderid)
                    self.display_files(fileandfolder=loaded_file)

                self.search_bar.configure(state="normal")
                self.search_bt.configure(state="normal")
                # self.clear_bt.configure(state="normal")

                self.new_file_bt.configure(state="normal")
                self.new_folder_bt.configure(state="normal")
                self.download_bt.configure(state="normal")
                self.upload2_bt.configure(state="normal")
                self.add_friend_bt.configure(state="normal")
                self.scanqr_bt.configure(state="normal")
                self.share_bt.configure(state="normal")
                self.copy_bt.configure(state="normal")
                self.rename_bt.configure(state="normal")
                self.createqr_bt.configure(state="normal")

            text_name.bind("<Return>", on_enter_key)

            def on_backspace(event):
                entry_text = text_name.get()
                if entry_text == "":
                    file_frame.pack_forget()

                    self.search_bar.configure(state="normal")
                    self.search_bt.configure(state="normal")
                    # self.clear_bt.configure(state="normal")
                    self.new_file_bt.configure(state="normal")
                    self.new_folder_bt.configure(state="normal")
                    self.download_bt.configure(state="normal")
                    self.upload2_bt.configure(state="normal")
                    self.add_friend_bt.configure(state="normal")
                    self.scanqr_bt.configure(state="normal")
                    self.share_bt.configure(state="normal")
                    self.copy_bt.configure(state="normal")
                    self.rename_bt.configure(state="normal")
                    self.createqr_bt.configure(state="normal")

                    return "break"

            text_name.bind("<BackSpace>", on_backspace)

        self.new_file_bt = customtkinter.CTkButton(self.header_frame, text="", image=new_file, width=0, height=10,
                                                   fg_color=self.hover_theme, command=add_file)
        self.new_file_bt.pack(side="left", padx=2)

        self.new_file_bt.pack_propagate(0)

        def add_folder():

            file_frame = customtkinter.CTkFrame(self.folder_area_frame, height=12, border_width=0,
                                                fg_color=self.theme_color)
            file_frame.pack(side="left", padx=20, pady=2)

            file_log = customtkinter.CTkLabel(file_frame, image=folder_logo, text="",
                                              text_color="black", fg_color=self.theme_color,
                                              font=("Aerial Rounded MT", 12,), height=5, corner_radius=5,
                                              anchor="w")
            file_log.pack(side="left")
            text_name = customtkinter.CTkEntry(file_frame, font=("Aerial Rounded MT", 12,), height=5,
                                               border_width=0, fg_color=self.theme_color, width=120)
            text_name.pack(side="left")
            text_name.focus()
            self.search_bar.configure(state="disabled")
            self.search_bt.configure(state="disabled")
            # self.clear_bt.configure(state="disabled")
            self.new_file_bt.configure(state="disabled")
            self.new_folder_bt.configure(state="disabled")
            self.download_bt.configure(state="disabled")
            self.upload2_bt.configure(state="disabled")
            self.add_friend_bt.configure(state="disabled")
            self.scanqr_bt.configure(state="disabled")
            self.share_bt.configure(state="disabled")
            self.copy_bt.configure(state="disabled")
            self.rename_bt.configure(state="disabled")
            self.createqr_bt.configure(state="disabled")

            def on_enter_key(event=None):
                entry_text = text_name.get()

                if entry_text == "" or entry_text.isspace():
                    messagebox.showwarning("Invalid", "EMPTY FOLDER NAME ")
                    file_frame.forget()

                # print("Entered:", entry_text)
                else:
                    folder_id = self.previous_opened_folder

                    if folder_id[-1] == '':
                        req_folderid = self.backend.service.get_folder("MySphere Vault")
                        print(req_folderid)
                        self.backend.service.create_folder(folder=entry_text, parent=req_folderid, )

                    else:
                        req_folderid = folder_id[-1]
                        print(req_folderid)
                        self.backend.service.create_folder(folder=entry_text, parent=req_folderid, )

                    loaded_file = self.load_files(id=req_folderid)
                    self.display_files(fileandfolder=loaded_file)

                self.search_bar.configure(state="normal")
                self.search_bt.configure(state="normal")
                # self.clear_bt.configure(state="normal")
                self.new_file_bt.configure(state="normal")
                self.new_folder_bt.configure(state="normal")
                self.download_bt.configure(state="normal")
                self.upload2_bt.configure(state="normal")
                self.add_friend_bt.configure(state="normal")
                self.scanqr_bt.configure(state="normal")
                self.share_bt.configure(state="normal")
                self.copy_bt.configure(state="normal")
                self.rename_bt.configure(state="normal")
                self.createqr_bt.configure(state="normal")

            text_name.bind("<Return>", on_enter_key)

            def on_backspace(event):
                entry_text = text_name.get()
                if entry_text == "":
                    file_frame.pack_forget()

                    self.search_bar.configure(state="normal")
                    self.search_bt.configure(state="normal")
                    # self.clear_bt.configure(state="normal")
                    self.new_file_bt.configure(state="normal")
                    self.new_folder_bt.configure(state="normal")
                    self.download_bt.configure(state="normal")
                    self.upload2_bt.configure(state="normal")
                    self.add_friend_bt.configure(state="normal")
                    self.scanqr_bt.configure(state="normal")
                    self.share_bt.configure(state="normal")
                    self.copy_bt.configure(state="normal")
                    self.rename_bt.configure(state="normal")
                    self.createqr_bt.configure(state="normal")

                    return "break"

            text_name.bind("<BackSpace>", on_backspace)

        self.new_folder_bt = customtkinter.CTkButton(self.header_frame, text="", image=new_folder, width=0,
                                                     height=10,
                                                     fg_color=self.hover_theme, command=add_folder)
        self.new_folder_bt.pack(side="left", padx=2)

        self.new_folder_bt.pack_propagate(0)

        self.download_bt = customtkinter.CTkButton(self.header_frame, text="", image=download, width=0, height=10,
                                                   fg_color=self.hover_theme,command=self.download_file)
        self.download_bt.pack(side="left", padx=2)

        self.download_bt.pack_propagate(0)

        self.upload2_bt = customtkinter.CTkButton(self.header_frame, text="", image=upload2, width=0, height=10,
                                                  fg_color=self.hover_theme, command=self.open_file_dialog)
        self.upload2_bt.pack(side="left", padx=2)

        self.upload2_bt.pack_propagate(0)



        def run_add_friend():
            users_dic = self.check_friends()

            self.displayarea_title.configure(text="Available user")

            try:
                for i in self.container.winfo_children():
                    i.destroy()
            except:
                pass

            user = customtkinter.CTkImage(
                light_image=Image.open("Icons\\user.png"),
                dark_image=Image.open("Icons\\user.png"),
                size=(20, 20))

            self.folder_area_frame = customtkinter.CTkScrollableFrame(self.container, fg_color="white")
            self.folder_area_frame.pack(side="left", fill="both", expand=1)

            for i in users_dic:
                print(i, users_dic[i])
                user_frame = customtkinter.CTkFrame(self.folder_area_frame, fg_color="transparent")
                user_frame.pack(side="top", fill="x")

                # name = users_dic[i]

                if i in self.friend_list:
                    # Already present
                    label = customtkinter.CTkLabel(user_frame, text=users_dic[i], compound="left", padx=10, anchor="w",
                                                   height=30, image=user, font=("Aerial Rounded MT", 12,), width=200,
                                                   fg_color=self.theme_color)
                    label.pack(side="left", padx=15, pady=2)

                    add = customtkinter.CTkButton(user_frame, text="Connected",
                                                  font=("Aerial Rounded MT", 12, "bold"), corner_radius=5, height=25,
                                                  width=100,state="disabled",text_color_disabled="white")
                    add.pack(side="left", padx=5, pady=2)
                    pass


                elif users_dic[i]==self.user:
                    pass


                else:
                    def add_to_friend(id=i, name=users_dic[i]):
                        print(f"Adding {id} to our friends")

                        def send_request():
                            # Create a connection.ms

                            x = datetime.now()
                            # "%#d %b %Y"
                            date = x.strftime("%#d")
                            month = x.strftime("%b")
                            year = x.strftime("%Y")

                            timestamp = f"{date} {month} {year}"

                            messagebox.showinfo(title="Info", message=f"Sending request to {name}")
                            content = f"{self.user} :: {timestamp} :: Hello, {name} i would like to connect with you"
                            file_id = self.backend.create_connection_file(content=content, friend_name=name,
                                                                          email_id=id)

                            data = {file_id: {"status": "pending", "email": id, "name": name}}
                            self.backend.write_into_friend_ms(content=data)

                        threading.Thread(target=send_request).start()

                    label = customtkinter.CTkLabel(user_frame, text=users_dic[i], compound="left", padx=10,
                                                   anchor="w",
                                                   height=30, image=user, font=("Aerial Rounded MT", 12,),
                                                   width=200,
                                                   fg_color=self.theme_color,)
                    label.pack(side="left", padx=15, pady=2)

                    add = customtkinter.CTkButton(user_frame, text="Add", command=add_to_friend,
                                                  font=("Aerial Rounded MT", 12, "bold"), corner_radius=5,
                                                  height=25,
                                                  width=100,text_color="white")
                    add.pack(side="left", padx=5, pady=2)
                    self.vertical_bt.configure(state="disabled")
                    self.horizontal_bt.configure(state="disabled")
                    self.search_bar.configure(state="disabled")
                    self.search_bt.configure(state="disabled")
                    # self.clear_bt.configure(state="disabled")
                    self.new_file_bt.configure(state="disabled")
                    self.new_folder_bt.configure(state="disabled")
                    self.download_bt.configure(state="disabled")
                    self.upload2_bt.configure(state="disabled")
                    self.add_friend_bt.configure(state="disabled")
                    self.scanqr_bt.configure(state="disabled")
                    self.share_bt.configure(state="disabled")
                    self.copy_bt.configure(state="disabled")
                    self.rename_bt.configure(state="disabled")
                    self.createqr_bt.configure(state="disabled")

                    # if name==self.user:
                    #     pass
                    #
                    # else:
                    #
                    #     def add_to_friend(id=i, name=users_dic[i]):
                    #         print(f"Adding {id} to our friends")
                    #
                    #         def send_request():
                    #             # Create a connection.ms
                    #
                    #             x = datetime.now()
                    #             # "%#d %b %Y"
                    #             date = x.strftime("%#d")
                    #             month = x.strftime("%b")
                    #             year = x.strftime("%Y")
                    #
                    #             timestamp = f"{date} {month} {year}"
                    #
                    #             messagebox.showinfo(title="Info", message=f"Sending request to {name}")
                    #             content = f"{self.user} :: {timestamp} :: Hello, {name} i would like to connect with you"
                    #             file_id = self.backend.create_connection_file(content=content, friend_name=name,
                    #                                                           email_id=id)
                    #
                    #             data = {file_id: {"status": "pending", "email": id, "name": name}}
                    #             self.backend.write_into_friend_ms(content=data)
                    #
                    #         threading.Thread(target=send_request).start()
                    #
                    #     label = customtkinter.CTkLabel(user_frame, text=users_dic[i], compound="left", padx=10,
                    #                                    anchor="w",
                    #                                    height=30, image=user, font=("Aerial Rounded MT", 12,),
                    #                                    width=200,
                    #                                    fg_color=self.theme_color, text_color="white")
                    #     label.pack(side="left", padx=15, pady=2)
                    #
                    #     add = customtkinter.CTkButton(user_frame, text="Add", command=add_to_friend,
                    #                                   font=("Aerial Rounded MT", 12, "bold"), corner_radius=5,
                    #                                   height=25,
                    #                                   width=100)
                    #     add.pack(side="left", padx=5, pady=2)






        def thread_add_friend():
            # run_add_friend()
            threading.Thread(target=run_add_friend).start()
            # self.run_progress_bar()
            # self.main_progressbar.set(0)

        self.add_friend_bt = customtkinter.CTkButton(self.header_frame, text="", image=addfriend, width=0,
                                                     height=10,
                                                     fg_color=self.hover_theme, command=thread_add_friend)
        self.add_friend_bt.pack(side="left", padx=2)

        self.add_friend_bt.pack_propagate(0)

        def close_scanner():
            self.scanning = False
            if self.cap:
                self.cap.release()

                self.scanner_frame.configure(height=0)
                # self.scanqr_frame.configure(height=0)
                self.video_label.pack_forget()
                self.scanqr_frame.place_forget()

                self.cap = None

                self.root.update_idletasks()
            self.scanqr_bt.configure(command=scan_qr)

        def open_scanner():
            self.scanner_frame.configure(height=200, width=300)
            self.video_label.pack(side="top", fill="both", expand=1)
            self.scanqr_bt.configure(command=close_scanner)
            # self.frame_1.configure(fg_color="black")

            if not self.cap:
                self.cap = cv2.VideoCapture(0)

            self.scanning = True
            self.update_frame_resize()

        def scan_qr():
            x = self.scanqr_bt.winfo_x()
            y = self.scanqr_bt.winfo_y()
            print(x, y)

            self.scanqr_frame = customtkinter.CTkFrame(self.root, height=300, width=400, fg_color="black",
                                                       corner_radius=0)
            self.scanqr_frame.place(x=(x - 200), y=(y + 140))

            self.scanner_frame = customtkinter.CTkFrame(self.scanqr_frame, height=200, width=300)
            self.scanner_frame.pack(side="top", fill="both", padx=2)
            self.scanner_frame.pack_propagate(False)

            self.video_label = customtkinter.CTkLabel(self.scanner_frame, text="", fg_color="black")
            self.video_label.pack(side="top", fill="both", expand=1)

            bt1 = customtkinter.CTkButton(self.scanqr_frame, text="From gallery")
            bt1.pack(side="top", pady=5)

            open_scanner()

        self.scanqr_bt = customtkinter.CTkButton(self.header_frame, text="", image=scanqr, width=0, height=10,
                                                 fg_color=self.hover_theme, command=scan_qr)
        self.scanqr_bt.pack(side="left", padx=2)

        self.scanqr_bt.pack_propagate(0)

        # To open qr code creator
        def open_create_qr():

            if self.right_selected_path_id!="":

                qr = customtkinter.CTkImage(
                    light_image=Image.open("Icons\\sampleqrcode.png"),
                    dark_image=Image.open("Icons\\sampleqrcode.png"),
                    size=(140, 140))

                x = self.scanqr_bt.winfo_x()
                y = self.scanqr_bt.winfo_y()
                print(x, y)

                self.createqr_frame = customtkinter.CTkFrame(self.container, width=400, fg_color="transparent",
                                                             corner_radius=0)
                self.createqr_frame.pack(side="left", fill="both")

                self.createqr_frame.pack_propagate(0)

                title = customtkinter.CTkLabel(self.createqr_frame, text="Create QR code", font=("Oswald", 18,),
                                               height=40, fg_color=self.theme_color)
                title.pack(side="top", fill="x")

                qrcode = customtkinter.CTkLabel(self.createqr_frame, image=qr, text="", font=("Oswald", 18,),
                                                height=150, width=150, fg_color=self.hover_theme)
                qrcode.pack(side="top", pady=10)

                title = customtkinter.CTkLabel(self.createqr_frame, text="Define your QR code type",
                                               font=("MS Aerial Rounded", 14,), height=40,
                                               fg_color="transparent", anchor="w", padx=20)
                title.pack(side="top", fill="x")

                def radiobutton_event():
                    radio_bt = radio_var.get()

                    if radio_bt == 1:
                        # For one-time accessible
                        try:
                            self.properties_frame.pack_forget()
                        except:
                            pass

                        self.properties_frame = customtkinter.CTkFrame(self.createqr_frame, fg_color="transparent")
                        self.properties_frame.pack(side="top", fill="x", padx=8, pady=20)

                        subdiv1 = customtkinter.CTkFrame(self.properties_frame, fg_color="transparent")
                        subdiv1.pack(side="top", fill="x", pady=5, padx=10)

                        def run_create_qr_func_one_time():

                            def generate_qr_id(length):
                                characters = string.ascii_letters + string.digits
                                return ''.join(random.choices(characters, k=length))

                            qr_code_id = generate_qr_id(length=5)
                            print("Generated QR ID: ", qr_code_id)

                            data = {"Type": "O",
                                    "qr_code_id": qr_code_id,
                                    "user_id": "NIL",
                                    "username": "NIL",
                                    "password": "NIL",
                                    "content": "hello world",
                                    }

                            print(data)

                            # self.qr_code_create(data=data)

                            # Now, Upload info abput this qrcode to mysphere vault

                            # vault_id = self.backend.vault_id
                            # self.backend.create_file(filename=f"{qr_code_id}.QR",content="",parent=vault_id)

                        create_bt = customtkinter.CTkButton(subdiv1, text="Create", width=160,
                                                            corner_radius=5, command=run_create_qr_func_one_time)
                        create_bt.pack(side="bottom", padx=2, pady=15, anchor="w")

                        pass

                    elif radio_bt == 2:
                        # For multiuser
                        pass

                    elif radio_bt == 3:
                        # For time constraint
                        try:
                            self.properties_frame.pack_forget()
                        except:
                            pass

                        self.properties_frame = customtkinter.CTkFrame(self.createqr_frame, fg_color="transparent")
                        self.properties_frame.pack(side="top", fill="x", padx=8, pady=20)

                        subdiv1 = customtkinter.CTkFrame(self.properties_frame, fg_color="transparent")
                        subdiv1.pack(side="top", fill="x", pady=5, padx=10)
                        subdiv2 = customtkinter.CTkFrame(self.properties_frame, fg_color="transparent")
                        subdiv2.pack(side="top", fill="x", pady=2, padx=10)

                        start_date = customtkinter.CTkEntry(subdiv1, placeholder_text="Start date (DD/MM/YY)")
                        # start_date.pack(side="left",padx=2)
                        self.end_date = customtkinter.CTkEntry(subdiv1, placeholder_text="End date (DD/MM/YY)",
                                                               width=160)
                        self.end_date.pack(side="left", padx=2)

                        def run_create_qr_func_time_cons():

                            def generate_qr_id(length):
                                characters = string.ascii_letters + string.digits
                                return ''.join(random.choices(characters, k=length))

                            qr_code_id = generate_qr_id(length=5)
                            print("Generated QR ID: ", qr_code_id)

                            # DD/MM/YY - start
                            # DD/MM/YY/HH/MM/SS end

                            def current_date():
                                x = datetime.now()

                                date = x.strftime("%d")
                                month = x.strftime("%m")
                                year = x.strftime("%y")

                                full_date = f"{date}/{month}/{year}"

                                return full_date

                            start_date = current_date()
                            self.end_date = self.end_date.get()
                            self.end_time = self.end_time.get()

                            def format_time(time):
                                splitted_time = time.split(":")
                                formatted_time = "/".join(splitted_time)

                                return formatted_time

                            end_time = format_time(self.end_time)
                            print(end_time)

                            end_timestamp = f"{self.end_date}//{end_time}"

                            data = {"Type": "T",
                                    "qr_code_id": qr_code_id,
                                    "user_id": "NIL",
                                    "username": "NIL",
                                    "password": "NIL",
                                    "start_time": start_date,
                                    "end_time": end_timestamp,
                                    "content": f"{self.right_selected_path_id}&&{self.selected_filename}",

                                    }

                            print(data)



                            self.qr_code_create(data=data,name=qr_code_id)

                            path = qr_code_id+".png"

                            qr = customtkinter.CTkImage(
                                light_image=Image.open(path),
                                dark_image=Image.open(path),
                                size=(140, 140))

                            qrcode.configure(image=qr)

                            print("Edit permission")

                            # Share with anyone permission
                            self.backend.share_anyone(id=self.right_selected_path_id)


                            # Update it to rose

                        create_bt = customtkinter.CTkButton(subdiv2, text="Create",
                                                            command=run_create_qr_func_time_cons, width=160,
                                                            corner_radius=5)
                        create_bt.pack(side="bottom", padx=2, pady=15, anchor="w")

                        start_time = customtkinter.CTkEntry(subdiv2, placeholder_text="Enter start time(HH:MM:SS)")
                        # start_time.pack(side="left",padx=2)
                        self.end_time = customtkinter.CTkEntry(subdiv2, placeholder_text="End time (HH:MM:SS)",
                                                               width=160)
                        self.end_time.pack(side="left", padx=2)

                        pass

                    elif radio_bt == 4:
                        # For single user
                        pass

                    # print("radiobutton toggled, current value:", radio_var.get())

                radio_var = customtkinter.IntVar(value=0)

                onetime = customtkinter.CTkRadioButton(self.createqr_frame, text="One time accessible",
                                                       command=radiobutton_event, variable=radio_var, value=1,
                                                       radiobutton_width=19,
                                                       radiobutton_height=19, border_width_unchecked=2,
                                                       border_width_checked=5,
                                                       fg_color="green", font=("Aerial", 13,))
                onetime.pack(side="top", fill="x", padx=20)

                multi = customtkinter.CTkRadioButton(self.createqr_frame, text="Multiuser accessible",
                                                     command=radiobutton_event, variable=radio_var, value=2,
                                                     radiobutton_width=19,
                                                     radiobutton_height=19, border_width_unchecked=2,
                                                     border_width_checked=5,
                                                     fg_color="green", font=("Aerial", 13,))
                multi.pack(side="top", fill="x", padx=20)

                time_cons = customtkinter.CTkRadioButton(self.createqr_frame, text="Time constraint",
                                                         command=radiobutton_event, variable=radio_var, value=3,
                                                         radiobutton_width=19,
                                                         radiobutton_height=19, border_width_unchecked=2,
                                                         border_width_checked=5,
                                                         fg_color="green", font=("Aerial", 13,))
                time_cons.pack(side="top", fill="x", padx=20)


                def close_create_qr():
                    self.createqr_frame.pack_forget()
                    self.createqr_bt.configure(command=open_create_qr)
                    pass

                self.createqr_bt.configure(command=close_create_qr)

                single = customtkinter.CTkRadioButton(self.createqr_frame, text="Single user accessible",
                                                      command=radiobutton_event, variable=radio_var, value=4,
                                                      radiobutton_width=19,
                                                      radiobutton_height=19, border_width_unchecked=2,
                                                      border_width_checked=5,
                                                      fg_color="green", font=("Aerial", 13,))
                single.pack(side="top", fill="x", padx=20)



            else:
                messagebox.showerror(title="Invalid",message="Please select file or folder to create qr")

        self.createqr_bt = customtkinter.CTkButton(self.header_frame, text="", image=createqr, width=0, height=10,
                                                   fg_color=self.hover_theme
                                                   , command=open_create_qr)
        self.createqr_bt.pack(side="left", padx=2)
        self.createqr_bt.pack_propagate(0)


        def file_rename():
            dialog = customtkinter.CTkInputDialog(text="New Name:", title="Rename ")
            entry_text = dialog.get_input()
            if entry_text == "" or entry_text.isspace():
                messagebox.showwarning("Invalid", "no entry ")

            # print("Entered:", entry_text)
            else:
                self.backend.rename(id=self.selected_path_id, name=entry_text+".enc")
                folder_id = self.previous_opened_folder[-1]

                loaded_file = self.load_files(id=folder_id)
                self.display_files(fileandfolder=loaded_file)

        def rename_message():
            messagebox.showinfo(title="Application Manager",message="Cannot use this feature now, work in progress")

        self.rename_bt = customtkinter.CTkButton(self.header_frame, text="", image=rename, width=0, height=10,
                                                 fg_color=self.hover_theme,command=rename_message)
        self.rename_bt.pack(side="left", padx=2)

        self.copy_bt = customtkinter.CTkButton(self.header_frame, text="", image=copy, width=0, height=10,
                                               fg_color=self.hover_theme)
        self.copy_bt.pack(side="left", padx=2)


        def open_share():
            if self.right_selected_path_id!="":
                self.createqr_frame = customtkinter.CTkFrame(self.container, width=400, fg_color="transparent",
                                                             corner_radius=0)
                self.createqr_frame.pack(side="left", fill="both")

                self.createqr_frame.pack_propagate(0)

                title = customtkinter.CTkLabel(self.createqr_frame, text="Share with your friend", font=("Oswald", 18,),
                                               height=40, fg_color=self.theme_color)
                title.pack(side="top", fill="x")

                title = customtkinter.CTkLabel(self.createqr_frame, text="Sharing file", font=("Aerial", 12,"bold"),
                                               height=40, fg_color="transparent",anchor="w",padx=10)
                title.pack(side="top", fill="x")

                file_id_entry = customtkinter.CTkEntry(self.createqr_frame,border_width=1,corner_radius=5,fg_color=self.hover_theme)
                file_id_entry.pack(side="top",fill="x",padx=5,pady=5)

                file_id_entry.insert(0,self.selected_filename)
                file_id_entry.configure(state="disabled",)

                name_container_frame = customtkinter.CTkScrollableFrame(self.createqr_frame, fg_color="transparent",
                                                             corner_radius=0)
                name_container_frame.pack(side="top",fill="both")

                sharing_people = []


                for friend in self.friend_dic:
                    check_var = customtkinter.StringVar(value="off")

                    def make_checkbox_event(name,var):
                        def toggle():
                            if var.get() == "on":
                                if name not in sharing_people:
                                    # email_add = self.friend_dic[name]
                                    sharing_people.append(name)
                                    print(f"Added: {name}")
                                    print(sharing_people)
                                    return name
                            else:
                                if name in sharing_people:
                                    # email_add = self.friend_dic[name]
                                    sharing_people.remove(name)
                                    print(f"Removed: {name}")
                                    print(sharing_people)
                                    return name

                        return toggle

                    # Create the checkbox
                    friend_checkbox = customtkinter.CTkCheckBox(
                        name_container_frame,
                        text=f"{friend}",
                        font=("Aerial Rounded MT", 12),
                        command=make_checkbox_event(friend,check_var),
                        corner_radius=2,
                        variable=check_var,
                        onvalue="on", offvalue="off",
                        checkbox_height=20, checkbox_width=20,
                        fg_color="purple", checkmark_color="white", border_width=2,
                    )
                    friend_checkbox.pack(side="top", fill="both", padx=14, pady=5)

                def close_share():
                    self.createqr_frame.pack_forget()
                    self.share_bt.configure(command=open_share)
                    pass

                self.share_bt.configure(command=close_share)


                def share_with_friend():
                    messagebox.showinfo(title="Info",message=f"Sharing file {self.selected_filename}")

                    if len(sharing_people)>=1:
                        for name in sharing_people:
                            email_add = self.friend_dic[name]
                            print("Sharing to :", email_add)

                            self.backend.share_with_friend(fileid=self.right_selected_path_id,email_add=email_add,role="reader")

                            # Work in process
                            def send():
                                x = datetime.now()
                                # "%#d %b %Y"
                                date = x.strftime("%#d")
                                month = x.strftime("%b")
                                year = x.strftime("%Y")

                                timestamp = f"{date} {month} {year}"
                                connection_file_id = self.backend.get_connection_file_id(email_id=email_add)

                                # messagebox.showinfo(title="Info", message=f"Adding new friend as {friend_name}")
                                message = f"{self.selected_filename} is shared to you"
                                content = f"{self.user} :: {timestamp} :: {message}"
                                self.backend.write_connection_file(content=content, id=connection_file_id)
                                print(content)

                                print("Shared successfully")

                            # threading.Thread(target=send).start()
                            # send()


                    else:
                        messagebox.showerror(title="Add friend",message="Add friend to share file")

                def run_share_with_friend():
                    threading.Thread(target=share_with_friend).start()


                share_bt = customtkinter.CTkButton(self.createqr_frame,text="Share",font=("Aerial Rounded MT", 13, "bold"),command=run_share_with_friend)
                share_bt.pack(side="bottom",fill="x",padx=5,pady=10)


            else:
                messagebox.showerror(title="Invalid", message="Please select file or folder to share")









        self.share_bt = customtkinter.CTkButton(self.header_frame, text="", image=share, width=0, height=10,
                                                fg_color=self.hover_theme,command=open_share)
        self.share_bt.pack(side="left", padx=2)

        orientation_frame = customtkinter.CTkFrame(self.header_frame, width=100, fg_color="white", )
        orientation_frame.pack(side="left", fill="y", padx=20)

        def horizontal_view():
            messagebox.showinfo(title="Application Manager",message="Cannot use this feature now, work in progress")
            # self.file_view_orientation = "Horizontal"
            # loaded_file = self.load_files(id=self.current_folder_id)
            # self.display_files(fileandfolder=loaded_file)

        def vertical_view():
            self.file_view_orientation = "Vertical"
            loaded_file = self.load_files(id=self.current_folder_id)
            self.display_files(fileandfolder=loaded_file)

        self.horizontal_bt = customtkinter.CTkButton(orientation_frame, text="", command=horizontal_view,
                                                     image=h_view, fg_color=self.hover_theme, width=0, height=10,
                                                     hover_color=self.hover_theme)
        self.horizontal_bt.pack(side="left", padx=2)

        self.vertical_bt = customtkinter.CTkButton(orientation_frame, text="", command=vertical_view, image=v_view,
                                                   fg_color=self.hover_theme, width=0, height=10,
                                                   hover_color=self.hover_theme)
        self.vertical_bt.pack(side="left", padx=2)

        self.container = customtkinter.CTkFrame(self.display_area_frame, fg_color="transparent")
        self.container.pack(side="left", fill="both", expand=1)

        # Side bar buttons

        my_profile = customtkinter.CTkButton(side_bar_menu, text="My Profile",
                                             font=("Aerial Rounded MT", 14, "bold"),
                                             corner_radius=2, height=31, fg_color=self.theme_color, image=user,
                                             text_color="black", anchor="w", hover_color=self.hover_theme,
                                             command=self.my_profile)
        my_profile.pack(side="top", fill="x", padx=20, pady=20)

        my_file = customtkinter.CTkButton(side_bar_menu, text="Files", font=("Aerial Rounded MT", 13, "bold"),
                                          corner_radius=2,
                                          height=31, fg_color=self.theme_color, image=file, text_color="black",
                                          anchor="w", hover_color=self.hover_theme, command=self.view_files)
        my_file.pack(side="top", fill="x", padx=20, pady=5)

        upload_file = customtkinter.CTkButton(side_bar_menu, text="Upload", font=("Aerial Rounded MT", 13, "bold"),
                                              corner_radius=2, height=31, fg_color=self.theme_color, image=upload,
                                              text_color="black", anchor="w", hover_color=self.hover_theme,
                                              command=self.open_file_dialog)
        upload_file.pack(side="top", fill="x", padx=20, pady=5)

        inbox = customtkinter.CTkButton(side_bar_menu, text="Inbox", font=("Aerial Rounded MT", 13, "bold"),
                                        corner_radius=2, height=31, fg_color=self.theme_color, image=inbox_logo,
                                        text_color="black", anchor="w", hover_color=self.hover_theme,
                                        command=self.inbox)
        inbox.pack(side="top", fill="x", padx=20, pady=5)

        setting = customtkinter.CTkButton(side_bar_menu, text="Setting", font=("Aerial Rounded MT", 13, "bold"),
                                          corner_radius=2, height=31, fg_color=self.theme_color, image=setting_logo,
                                          text_color="black", anchor="w", hover_color=self.hover_theme,
                                          command=self.setting)
        setting.pack(side="top", fill="x", padx=20, pady=5)

        def logout():
            # Log out from main interface
            for i in self.root.winfo_children():
                i.destroy()

            self.login_interface()

        Logout = customtkinter.CTkButton(side_bar_menu, text="Log Out", font=("Aerial Rounded MT", 13, "bold"),
                                         corner_radius=2, height=31, fg_color=self.theme_color, image=logout_logo,
                                         text_color="black", anchor="w", hover_color=self.hover_theme,
                                         command=logout)
        Logout.pack(side="top", fill="x", padx=21, pady=20)

        # Storage
        title = customtkinter.CTkLabel(storage_area, text="Space Usage", anchor="w", padx=10,
                                       font=("Aerial Rounded MT", 13, "bold"), )
        title.pack(side="top", fill="x", padx=5, pady=7)

        spacebar = customtkinter.CTkProgressBar(storage_area, orientation="horizontal", height=10, corner_radius=4,
                                                progress_color="#35c435", fg_color="#dcdedc")
        spacebar.pack(side="top", fill="x", padx=14, pady=4)

        spacebar.set(0.2)

        totalspace = customtkinter.CTkLabel(storage_area, text="Total Space : 5 GB (As per plan)*", padx=10,
                                            font=("Aerial Rounded MT", 11, "bold"), anchor="w")
        totalspace.pack(side="top", fill="x", padx=5, pady=0)

        space_used = customtkinter.CTkLabel(storage_area, text="Space Used : \nSpace Available :", padx=12,
                                            font=("Aerial Rounded MT", 11,), justify="left", anchor="w")
        space_used.pack(side="top", fill="x", padx=5, pady=0)

        space_manage = customtkinter.CTkLabel(storage_area, text="Integrated with \nspace management", padx=12,
                                              font=("Aerial Rounded MT", 11, "italic"), justify="left", anchor="w")
        space_manage.pack(side="bottom", fill="x", padx=5, pady=5)

        # Footer
        citation_label = customtkinter.CTkButton(footer, text="Made in PSIT", text_color="red",
                                                 font=("Oswald", 12, "bold"), border_width=2, border_color="red",
                                                 corner_radius=19, fg_color="transparent", hover=False, )
        citation_label.pack(side="top", fill="x", padx=5, pady=5)

        developercitation = customtkinter.CTkLabel(footer, text="Saksham Developments",
                                                   font=("Aerial Rounded MT", 11), height=2)
        developercitation.pack(side="bottom", fill="x", padx=5, pady=5)

        googledrivecitation = customtkinter.CTkLabel(footer, text="", padx=12,
                                                     font=("Aerial Rounded MT", 11, "italic"), justify="left",
                                                     anchor="w", image=drive_logo)
        googledrivecitation.pack(side="left", fill="x", padx=5, pady=1)

        apicitation = customtkinter.CTkLabel(footer, text="", padx=12,
                                             font=("Aerial Rounded MT", 11, "italic"), justify="left",
                                             anchor="w", image=api_logo)
        apicitation.pack(side="left", fill="x", padx=20, pady=1)

        securecitation = customtkinter.CTkLabel(footer, text="", padx=22,
                                                font=("Aerial Rounded MT", 11, "italic"), justify="left",
                                                anchor="w", image=secure_logo, )
        securecitation.pack(side="left", fill="x", padx=20, pady=1)

        # Menubar

        empty_option = customtkinter.CTkButton(menubar_frame, text="", width=100, fg_color="transparent",
                                               text_color="black", state="disabled")
        empty_option.pack(side="left", fill="y", padx=25, )

        file_option = customtkinter.CTkButton(menubar_frame, text="File", width=70, fg_color="transparent",
                                              text_color="black", font=("Aerial Rounded MT", 12), hover="disabled",command=self.view_files)
        file_option.pack(side="left", fill="y", padx=5)

        upload_option = customtkinter.CTkButton(menubar_frame, text="Upload", width=70, fg_color="transparent",
                                                text_color="black", font=("Aerial Rounded MT", 12),
                                                hover="disabled",command=self.open_file_dialog)
        upload_option.pack(side="left", fill="y", padx=0)

        upload_option = customtkinter.CTkButton(menubar_frame, text="Inbox", width=70, fg_color="transparent",
                                                text_color="black", font=("Aerial Rounded MT", 12),
                                                hover="disabled",command=self.inbox)
        upload_option.pack(side="left", fill="y", padx=5)

        upload_option = customtkinter.CTkButton(menubar_frame, text="Setting", width=70, fg_color="transparent",
                                                text_color="black", font=("Aerial Rounded MT", 12),
                                                hover="disabled",command=self.setting)
        upload_option.pack(side="left", fill="y", padx=5)

        def show_help():
            messagebox.showinfo(title="Help",message="Adding help soon.")

        help_option = customtkinter.CTkButton(menubar_frame, text="Help", width=70, fg_color="transparent",
                                              text_color="black", font=("Aerial Rounded MT", 12), hover="disabled",command=show_help)
        help_option.pack(side="left", fill="y", padx=5)


        def open_dev_chat():
            self.inbox()


        contact_option = customtkinter.CTkButton(menubar_frame, text="Contact Developer", width=70,
                                                 fg_color="transparent",
                                                 text_color="black", font=("Aerial Rounded MT", 12),
                                                 hover="disabled",command=open_dev_chat)
        contact_option.pack(side="left", fill="y", padx=5)


        def update():
            messagebox.showinfo(title="Update",message="No update for now")


        update_option = customtkinter.CTkButton(menubar_frame, text="Update", width=70,
                                                fg_color="transparent",
                                                text_color="black", font=("Aerial Rounded MT", 12),
                                                hover="disabled",command=update)
        update_option.pack(side="left", fill="y", padx=5)


        logout_option = customtkinter.CTkButton(menubar_frame, text="Logout", width=70,
                                                fg_color="transparent",
                                                text_color="black", font=("Aerial Rounded MT", 12),
                                                hover="disabled",command=logout)
        logout_option.pack(side="right", fill="y", padx=35)







        self.root.mainloop()

    def load_dev_chat(self,):
        label_header.configure(image=mysphere, text="   Developer", compound="left", pady=10, padx=10)
        try:
            for i in message_panel.winfo_children():
                i.destroy()
        except:
            pass

        messages = []
        # "Server :: 18 May 2025 :: Hello, User myself rosy I will be taking care of data.It my promise you will never loss your data & If you have request you are free to write down. Soon i will resolve it"]
        # '''Server :: 18 May 2025 :: Hello, Garvit! I'm Rosy, and I’ll be taking care of your data.I promise you’ll never lose a thing — your information is safe with me.If you have any requests or changes, feel free to write them down.I'll make sure they’re resolved or modified as soon as possible.''']

        title = "You are currently on application helpdesk, For any query chat further"

        dev_chat_label = customtkinter.CTkLabel(message_panel, text=title, fg_color="#c9e4de", pady=5, padx=10,
                                                font=("Aerial Rounded MT", 10,))
        dev_chat_label.pack(side="top", pady=5, padx=5)

        prev_date = ""
        for message in messages:
            splitted_message = message.split(" :: ")
            message_from = splitted_message[0]
            time_stamp = splitted_message[1]
            message_detail = splitted_message[2]

            if message_from == "Server":

                if prev_date != time_stamp:
                    date_label = customtkinter.CTkLabel(message_panel, text=time_stamp, fg_color="#c9e4de", pady=5,
                                                        padx=10, font=("Aerial Rounded MT", 10,))
                    date_label.pack(side="top", pady=5, padx=5)
                else:
                    pass

                prev_date = time_stamp

                message_frame = customtkinter.CTkLabel(message_panel, text=message_detail, fg_color="#faf4b7",
                                                       font=("Aerial", 12,),
                                                       padx=10, corner_radius=10, width=300, anchor="w", justify="left",
                                                       wraplength=350, pady=10)
                message_frame.pack(side="top", padx=5, pady=20, anchor="w")

            else:
                pass



    def inbox(self):
        self.search_bar.configure(state="disabled")
        self.search_bt.configure(state="disabled")
        # self.clear_bt.configure(state="disabled")
        self.new_file_bt.configure(state="disabled")
        self.new_folder_bt.configure(state="disabled")
        self.download_bt.configure(state="disabled")
        self.upload2_bt.configure(state="disabled")
        self.add_friend_bt.configure(state="disabled")
        self.scanqr_bt.configure(state="disabled")
        self.share_bt.configure(state="disabled")
        self.copy_bt.configure(state="disabled")
        self.rename_bt.configure(state="disabled")
        self.createqr_bt.configure(state="disabled")

        verified = customtkinter.CTkImage(
            light_image=Image.open("Icons\\verifiedblue.png"),
            dark_image=Image.open("Icons\\verifiedblue.png"),
            size=(15, 15))

        verifiedg = customtkinter.CTkImage(
            light_image=Image.open("Icons\\verifiedg.png"),
            dark_image=Image.open("Icons\\verifiedg.png"),
            size=(15, 15))

        rose = customtkinter.CTkImage(
            light_image=Image.open("Icons\\rose.png"),
            dark_image=Image.open("Icons\\rose.png"),
            size=(30, 30))

        mysphere = customtkinter.CTkImage(
            light_image=Image.open("Icons\\Mysphere logo.png"),
            dark_image=Image.open("Icons\\Mysphere logo.png"),
            size=(30, 30))

        user_logo = customtkinter.CTkImage(
            light_image=Image.open("Icons\\user.png"),
            dark_image=Image.open("Icons\\user.png"),
            size=(30, 30))


        self.displayarea_title.configure(text="Inbox")

        try:
            for i in self.container.winfo_children():
                i.destroy()
        except:
            pass

        self.inbox_frame = customtkinter.CTkFrame(self.container, fg_color="transparent")
        self.inbox_frame.pack(side="top", fill="both", expand=1)

        self.vertical_bt.configure(state="disabled")
        self.horizontal_bt.configure(state="disabled")

        user_panel = customtkinter.CTkFrame(self.inbox_frame, width=200, corner_radius=4,border_width=0,fg_color="white")
        user_panel.pack(side="left", fill="y", padx=5, pady=5)

        chat_frame = customtkinter.CTkFrame(self.inbox_frame, width=200, corner_radius=4,border_width=0,fg_color="white")
        chat_frame.pack(side="left", fill="both", expand=1, padx=5, pady=5)

        chat_header_frame = customtkinter.CTkFrame(chat_frame, corner_radius=2,border_width=1,height=42,fg_color="transparent")
        chat_header_frame.pack(side="top", fill="x", padx=0, pady=0)
        chat_header_frame.pack_propagate(False)

        label_header = customtkinter.CTkLabel(chat_header_frame,text="",height=32,fg_color=self.theme_color,anchor="w")
        label_header.pack(side="left",fill="both",expand=1)


        message_panel = customtkinter.CTkScrollableFrame(chat_frame, corner_radius=0,border_width=0,fg_color="#ffffff")
        message_panel.pack(side="top", fill="both", expand=1, padx=0, pady=0)

        self.text_area_frame = customtkinter.CTkFrame(chat_frame,fg_color="transparent")
        self.text_area_frame.pack(side="bottom",fill="x")

        def load_text_area():
            text_area = customtkinter.CTkTextbox(self.text_area_frame, corner_radius=10, height=100, border_width=1,
                                                 font=("Aerial", 14))
            text_area.pack(side="left", fill="both", expand=1, pady=20)

            bt_frame = customtkinter.CTkFrame(self.text_area_frame, width=70, fg_color="transparent")
            bt_frame.pack(side="left", fill="y", pady=20)

            # templ_frame = customtkinter.CTkScrollableFrame(chat_frame, height=40, orientation="horizontal")
            # templ_frame.pack(side="bottom", fill="x")

            def send_message():
                # Getting the typed message
                message = text_area.get("0.0", "end")

                message_frame = customtkinter.CTkLabel(message_panel, text=message,
                                                       fg_color="#faf4b7", font=("Aerial", 12,),
                                                       padx=10, corner_radius=10, width=300, anchor="w",
                                                       justify="left", wraplength=350, pady=10)
                message_frame.pack(side="top", padx=5, pady=20, anchor="e")

                # Upload it on the connection file
                def send():
                    x = datetime.now()
                    # "%#d %b %Y"
                    date = x.strftime("%#d")
                    month = x.strftime("%b")
                    year = x.strftime("%Y")

                    timestamp = f"{date} {month} {year}"

                    # messagebox.showinfo(title="Info", message=f"Adding new friend as {friend_name}")
                    content = f"{self.user} :: {timestamp} :: {message}"
                    self.backend.write_connection_file(content=content, id=self.selected_connection_file_id)
                    print(content)

                threading.Thread(target=send).start()

            send_bt = customtkinter.CTkButton(bt_frame, text="Send", width=70,command=send_message )
            send_bt.pack(side="top", fill="x", padx=4, pady=2)

            def clear_message():
                text_area.delete("0.0", "end")

            self.clear_bt = customtkinter.CTkButton(bt_frame, text="Clear", width=70,command=clear_message )
            self.clear_bt.pack(side="top", fill="x", padx=4, pady=2)

            def open_templates():

                def close_templates():
                    template_bt.configure(command=open_templates)
                    templ_frame.pack_forget()

                template_bt.configure(command=close_templates)
                templ_frame = customtkinter.CTkScrollableFrame(chat_frame,height=40,orientation="horizontal",fg_color="white",scrollbar_fg_color="white",scrollbar_button_color="white")
                templ_frame.pack(side="bottom",fill="x")

                template = ["Request password change","Shared with me files/folder"]

                for message in template:
                    bt = customtkinter.CTkButton(templ_frame,text=message,corner_radius=5,text_color="black",fg_color=self.hover_theme,height=20)
                    bt.pack(side="left",fill="y",padx=10)

            template_bt = customtkinter.CTkButton(bt_frame, text="Templates", width=70,command=open_templates )
            template_bt.pack(side="top", fill="x", padx=4, pady=2)


            def attach_file():
                self.view_files()


            submit_bt = customtkinter.CTkButton(bt_frame, text="Attach", width=70,command=attach_file )
            submit_bt.pack(side="top", fill="x", padx=4, pady=2)

        load_text_area()



        receipents = customtkinter.CTkLabel(user_panel, text="Recipients", font=("Aerial Rounded MT", 15,"bold"), height=40,anchor="w",padx=20)
        receipents.pack(side="top", fill="x",padx=2)




        user_panel_sub_frame = customtkinter.CTkScrollableFrame(user_panel, width=200, corner_radius=0, border_width=0,
                                            fg_color="white",scrollbar_button_color=self.hover_theme,scrollbar_fg_color=self.hover_theme,scrollbar_button_hover_color="#d4d5d6")
        user_panel_sub_frame.pack(side="top", fill="both", padx=0, pady=0,expand=1)

        # Creating server operator
        operator_frame = customtkinter.CTkFrame(user_panel_sub_frame,corner_radius=4,border_width=0,fg_color=self.theme_color)
        operator_frame.pack(side="top", fill="x", padx=5, pady=2)

        img_frame = customtkinter.CTkLabel(operator_frame,text="",image=rose,fg_color=self.theme_color,padx=10)
        img_frame.pack(side="left",padx=5,pady=0)

        # Loading chat
        def load_chat():
            label_header.configure(image=rose,text="   Rose",compound="left",pady=10,padx=10)
            try:
                for i in message_panel.winfo_children():
                    i.destroy()
            except:
                pass

            for i in self.text_area_frame.winfo_children():
                i.destroy()

            load_text_area()


            messages = [
                # "Server :: 18 May 2025 :: Hello, User myself rosy I will be taking care of data.It my promise you will never loss your data & If you have request you are free to write down. Soon i will resolve it"]
                f'''Server :: 18 May 2025 :: Hello, {self.user.title()}! I'm Rosy, and I’ll be taking care of your data.I promise you’ll never lose a thing — your information is safe with me.If you have any requests or changes, feel free to write them down.I'll make sure they’re resolved or modified as soon as possible.''']

            prev_date = ""
            for message in messages:
                splitted_message = message.split(" :: ")
                message_from = splitted_message[0]
                time_stamp = splitted_message[1]
                message_detail = splitted_message[2]

                if message_from == "Server":

                    if prev_date!=time_stamp:
                        date_label = customtkinter.CTkLabel(message_panel, text=time_stamp, fg_color="#c9e4de",pady=5,padx=10,font=("Aerial Rounded MT", 10,))
                        date_label.pack(side="top", pady=5,padx=5)
                    else:
                        pass

                    prev_date = time_stamp

                    message_frame = customtkinter.CTkLabel(message_panel, text=message_detail, fg_color="#faf4b7",font=("Aerial", 12,),
                                                           padx=10, corner_radius=10,width=300,anchor="w",justify="left",wraplength=350,pady=10)
                    message_frame.pack(side="top", padx=5, pady=20, anchor="w")

                else:
                    pass

        server_oper = customtkinter.CTkButton(operator_frame,text="   Rose",height=35,corner_radius=4,image=verified,compound="right",font=("Aerial Rounded MT", 11,),command=load_chat,hover_color=self.hover_theme,fg_color=self.theme_color,text_color="black",anchor="w",width=250)
        server_oper.pack(side="top",fill="x",pady=0)



        developer_frame = customtkinter.CTkFrame(user_panel_sub_frame, corner_radius=4, border_width=0,
                                                fg_color=self.theme_color)
        developer_frame.pack(side="top", fill="x", padx=5, pady=2)

        img_frame = customtkinter.CTkLabel(developer_frame, text="", image=mysphere, fg_color=self.theme_color, padx=10)
        img_frame.pack(side="left", padx=5, pady=0)


        def load_dev_chat():
            label_header.configure(image=mysphere,text="   Developer",compound="left",pady=10,padx=10)
            try:
                for i in message_panel.winfo_children():
                    i.destroy()
            except:
                pass

            for i in self.text_area_frame.winfo_children():
                i.destroy()

            load_text_area()


            messages = []
                # "Server :: 18 May 2025 :: Hello, User myself rosy I will be taking care of data.It my promise you will never loss your data & If you have request you are free to write down. Soon i will resolve it"]
                # '''Server :: 18 May 2025 :: Hello, Garvit! I'm Rosy, and I’ll be taking care of your data.I promise you’ll never lose a thing — your information is safe with me.If you have any requests or changes, feel free to write them down.I'll make sure they’re resolved or modified as soon as possible.''']

            title = "You are currently on application helpdesk, For any query chat further"

            dev_chat_label = customtkinter.CTkLabel(message_panel, text=title, fg_color="#c9e4de", pady=5, padx=10,
                                                font=("Aerial Rounded MT", 10,))
            dev_chat_label.pack(side="top", pady=5, padx=5)

            prev_date = ""
            for message in messages:
                splitted_message = message.split(" :: ")
                message_from = splitted_message[0]
                time_stamp = splitted_message[1]
                message_detail = splitted_message[2]

                if message_from == "Server":

                    if prev_date!=time_stamp:
                        date_label = customtkinter.CTkLabel(message_panel, text=time_stamp, fg_color="#c9e4de",pady=5,padx=10,font=("Aerial Rounded MT", 10,))
                        date_label.pack(side="top", pady=5,padx=5)
                    else:
                        pass

                    prev_date = time_stamp

                    message_frame = customtkinter.CTkLabel(message_panel, text=message_detail, fg_color="#faf4b7",font=("Aerial", 12,),
                                                           padx=10, corner_radius=10,width=300,anchor="w",justify="left",wraplength=350,pady=10)
                    message_frame.pack(side="top", padx=5, pady=20, anchor="w")

                else:
                    pass


        developer = customtkinter.CTkButton(developer_frame, text="   Developer", height=35, corner_radius=4,
                                              image=verified, compound="right", font=("Aerial Rounded MT", 11,),
                                              command=load_dev_chat, hover_color=self.hover_theme,
                                              fg_color=self.theme_color, text_color="black", anchor="w", width=250)
        developer.pack(side="top", fill="x", pady=0)


        # Load sended request friend & friend
        def load_request():

            # dic = {'1qEHcn-ts32xXwcReKbzA4PV15WKUkgk1': {'status': 'pending', 'email': 'sakshamyadav260705@gmail.com', 'name': 'saksham yadav'}}
            for status_dic in self.friend_ms_data :
                print(status_dic,"Available")
                for item in status_dic:
                    file_id = item
                    args = status_dic[file_id]

                    status = args["status"]
                    email = args["email"]
                    name = args["name"]

                    friend_frame = customtkinter.CTkFrame(user_panel_sub_frame, corner_radius=4, border_width=0,
                                                             fg_color=self.theme_color)
                    friend_frame.pack(side="top", fill="x", padx=5, pady=2)

                    img_frame = customtkinter.CTkLabel(friend_frame, text="", image=user_logo,
                                                       fg_color=self.theme_color, padx=10)
                    img_frame.pack(side="left", padx=5, pady=0)

                    def load_chat(id=file_id,friend_name=name):
                        label_header.configure(image=user_logo, text=f"   {friend_name}", compound="left", pady=10, padx=10)
                        try:
                            for i in message_panel.winfo_children():
                                i.destroy()
                        except:
                            pass

                        for i in self.text_area_frame.winfo_children():
                            i.destroy()

                        load_text_area()

                        print(f"loading chat for {id}")
                        data = self.backend.read_connection_file(id=id)
                        self.selected_connection_file_id = id
                        prev_date = ""
                        for message in data:

                            splitted_message = message.split(" :: ")
                            message_from = splitted_message[0]
                            time_stamp = splitted_message[1]
                            message_detail = splitted_message[2]

                            if message_from == friend_name:

                                if prev_date != time_stamp:
                                    date_label = customtkinter.CTkLabel(message_panel, text=time_stamp,
                                                                        fg_color="#c9e4de", pady=5, padx=10,
                                                                        font=("Aerial Rounded MT", 10,))
                                    date_label.pack(side="top", pady=5, padx=5)
                                else:
                                    pass

                                prev_date = time_stamp

                                message_frame = customtkinter.CTkLabel(message_panel, text=message_detail,
                                                                       fg_color="#faf4b7", font=("Aerial", 12,),
                                                                       padx=10, corner_radius=10, width=300, anchor="w",
                                                                       justify="left", wraplength=350, pady=10)
                                message_frame.pack(side="top", padx=5, pady=20, anchor="w")

                            else:
                                if prev_date != time_stamp:
                                    date_label = customtkinter.CTkLabel(message_panel, text=time_stamp,
                                                                        fg_color="#c9e4de", pady=5, padx=10,
                                                                        font=("Aerial Rounded MT", 10,))
                                    date_label.pack(side="top", pady=5, padx=5)
                                else:
                                    pass

                                prev_date = time_stamp

                                message_frame = customtkinter.CTkLabel(message_panel, text=message_detail,
                                                                       fg_color="#c9f0c0", font=("Aerial", 12,),
                                                                       padx=10, corner_radius=10, width=300, anchor="w",
                                                                       justify="left", wraplength=350, pady=20)
                                message_frame.pack(side="top", padx=5, pady=20, anchor="e")



                                pass

                        pass

                    friend = customtkinter.CTkButton(friend_frame, text="   "+name.title(), height=35,
                                                        corner_radius=4,
                                                        image=verifiedg, compound="right",
                                                        font=("Aerial Rounded MT", 11,),
                                                        command=load_chat, hover_color=self.hover_theme,
                                                        fg_color=self.theme_color, text_color="black", anchor="w",
                                                        width=250)
                    friend.pack(side="top", fill="x", pady=0)


            # try:
            #     self.available_connection_req_data = self.backend.see_connection_request()
            #     print(data)
            # except:
            #     self.available_connection_req_data = []
            #
            #
            # self.application_users = self.backend.view_app_users()

            for status_dic in self.available_connection_req_data:
                for item in status_dic:
                    file_id = item
                    args = status_dic[file_id]

                    # status = args["status"]
                    email = args["email id"]
                    name = args["name"]

                    username = self.application_users[email]

                    if email not in self.friend_list:
                        friend_frame = customtkinter.CTkFrame(user_panel_sub_frame, corner_radius=4, border_width=0,
                                                              fg_color=self.theme_color)
                        friend_frame.pack(side="top", fill="x", padx=5, pady=2)

                        img_frame = customtkinter.CTkLabel(friend_frame, text="", image=user_logo,
                                                           fg_color=self.theme_color, padx=10)
                        img_frame.pack(side="left", padx=5, pady=0)

                        def load_chat(id=file_id, friend_name=username, email_id=email):
                            label_header.configure(image=user_logo, text=f"   {friend_name}", compound="left", pady=10,
                                                   padx=10)
                            try:
                                for i in message_panel.winfo_children():
                                    i.destroy()
                            except:
                                pass

                            print(f"loading chat for {id}")
                            data = self.backend.read_connection_file(id=id)
                            self.selected_connection_file_id = id
                            lenght = len(data)
                            prev_date = ""
                            for message in data:

                                splitted_message = message.split(" :: ")
                                message_from = splitted_message[0]
                                time_stamp = splitted_message[1]
                                message_detail = splitted_message[2]

                                if message_from == friend_name:

                                    if prev_date != time_stamp:
                                        date_label = customtkinter.CTkLabel(message_panel, text=time_stamp,
                                                                            fg_color="#c9e4de", pady=5, padx=10,
                                                                            font=("Aerial Rounded MT", 10,))
                                        date_label.pack(side="top", pady=5, padx=5)
                                    else:
                                        pass

                                    prev_date = time_stamp

                                    message_frame = customtkinter.CTkLabel(message_panel, text=message_detail,
                                                                           fg_color="#faf4b7", font=("Aerial", 12,),
                                                                           padx=10, corner_radius=10, width=300,
                                                                           anchor="w",
                                                                           justify="left", wraplength=350, pady=10)
                                    message_frame.pack(side="top", padx=5, pady=20, anchor="w")

                                else:
                                    if prev_date != time_stamp:
                                        date_label = customtkinter.CTkLabel(message_panel, text=time_stamp,
                                                                            fg_color="#c9e4de", pady=5, padx=10,
                                                                            font=("Aerial Rounded MT", 10,))
                                        date_label.pack(side="top", pady=5, padx=5)
                                    else:
                                        pass

                                    prev_date = time_stamp

                                    message_frame = customtkinter.CTkLabel(message_panel, text=message_detail,
                                                                           fg_color="#c9f0c0", font=("Aerial", 12,),
                                                                           padx=10, corner_radius=10, width=300,
                                                                           anchor="w",
                                                                           justify="left", wraplength=350, pady=20)
                                    message_frame.pack(side="top", padx=5, pady=20, anchor="e")

                                    pass

                            if lenght == 1:
                                # Condition : Where as a user we received a friend request from another uesr
                                title = "Look like a new friend request, Do you want to add to friend list"

                                request_label = customtkinter.CTkLabel(message_panel, text=title,
                                                                       fg_color="#c9e4de", pady=5, padx=10,
                                                                       font=("Aerial Rounded MT", 10,))
                                request_label.pack(side="top", pady=5, padx=5)

                                for i in self.text_area_frame.winfo_children():
                                    i.destroy()

                                bt_frame = customtkinter.CTkFrame(self.text_area_frame, width=70,
                                                                  fg_color="transparent")
                                bt_frame.pack(side="top", fill="y", pady=20)

                                def add_to_friend():
                                    for i in self.text_area_frame.winfo_children():
                                        i.destroy()

                                    load_text_area()

                                    message_detail = "Yes, Ofcourse!"

                                    message_frame = customtkinter.CTkLabel(message_panel, text=message_detail,
                                                                           fg_color="#c9f0c0", font=("Aerial", 12,),
                                                                           padx=10, corner_radius=10, width=300,
                                                                           anchor="w",
                                                                           justify="left", wraplength=350, pady=20)
                                    message_frame.pack(side="top", padx=5, pady=20, anchor="e")

                                    request_label.pack_forget()

                                    # Update changes to connection file

                                    def add_request():
                                        # Adding in friend.ms file

                                        x = datetime.now()
                                        # "%#d %b %Y"
                                        date = x.strftime("%#d")
                                        month = x.strftime("%b")
                                        year = x.strftime("%Y")

                                        timestamp = f"{date} {month} {year}"

                                        messagebox.showinfo(title="Info", message=f"Adding new friend as {friend_name}")
                                        content = f"{self.user} :: {timestamp} :: {message_detail}"
                                        self.backend.write_connection_file(content=content, id=id)
                                        print(content)

                                        data = {id: {"status": "True", "email": email_id, "name": friend_name}}
                                        self.backend.write_into_friend_ms(content=data)
                                        print(data)

                                    threading.Thread(target=add_request).start()

                                accept_bt = customtkinter.CTkButton(bt_frame, text="Accept & Add", width=70,
                                                                    command=add_to_friend)
                                accept_bt.pack(side="left", fill="x", pady=2)

                                def reject_request():
                                    for i in self.text_area_frame.winfo_children():
                                        i.destroy()

                                    # load_text_area()

                                    message_detail = "No, Sorry"

                                    message_frame = customtkinter.CTkLabel(message_panel, text=message_detail,
                                                                           fg_color="#faf4b7", font=("Aerial", 12,),
                                                                           padx=10, corner_radius=10, width=300,
                                                                           anchor="w",
                                                                           justify="left", wraplength=350, pady=20)
                                    message_frame.pack(side="top", padx=5, pady=20, anchor="e")

                                    request_label.pack_forget()

                                    # Update changes to connection file
                                    def cancel_request():
                                        # Adding in friend.ms file

                                        x = datetime.now()
                                        # "%#d %b %Y"
                                        date = x.strftime("%#d")
                                        month = x.strftime("%b")
                                        year = x.strftime("%Y")

                                        timestamp = f"{date} {month} {year}"

                                        content = f"{self.user} :: {timestamp} :: {message_detail}"
                                        self.backend.write_connection_file(content=content, id=id)
                                        print(content)

                                    threading.Thread(target=cancel_request).start()

                                cancel_bt = customtkinter.CTkButton(bt_frame, text="Reject", width=70,
                                                                    command=reject_request)
                                cancel_bt.pack(side="left", fill="x", padx=4, pady=2)

                        friend = customtkinter.CTkButton(friend_frame, text="   " + username.title(), height=35,
                                                         corner_radius=4,
                                                         image=verifiedg, compound="right",
                                                         font=("Aerial Rounded MT", 11,),
                                                         command=load_chat, hover_color=self.hover_theme,
                                                         fg_color=self.theme_color, text_color="black", anchor="w",
                                                         width=250)
                        friend.pack(side="top", fill="x", pady=0)

                    else:
                        pass


        def load_request_from_other():

            try:
                data = self.backend.see_connection_request()

            except:
                data = []

            print(data)


            users = self.backend.view_app_users()

            for status_dic in data:
                for item in status_dic:
                    file_id = item
                    args = status_dic[file_id]

                    # status = args["status"]
                    email = args["email id"]
                    name = args["name"]

                    username = users[email]

                    friend_frame = customtkinter.CTkFrame(user_panel_sub_frame, corner_radius=4, border_width=0,
                                                             fg_color=self.theme_color)
                    friend_frame.pack(side="top", fill="x", padx=5, pady=2)

                    img_frame = customtkinter.CTkLabel(friend_frame, text="", image=user_logo,
                                                       fg_color=self.theme_color, padx=10)
                    img_frame.pack(side="left", padx=5, pady=0)

                    def load_chat(id=file_id,friend_name=username):
                        label_header.configure(image=user_logo, text=f"   {friend_name}", compound="left", pady=10, padx=10)
                        try:
                            for i in message_panel.winfo_children():
                                i.destroy()
                        except:
                            pass

                        print(f"loading chat for {id}")
                        data = self.backend.read_connection_file(id=id)

                        prev_date = ""
                        for message in data:

                            splitted_message = message.split(" :: ")
                            message_from = splitted_message[0]
                            time_stamp = splitted_message[1]
                            message_detail = splitted_message[2]

                            if message_from == friend_name:

                                if prev_date != time_stamp:
                                    date_label = customtkinter.CTkLabel(message_panel, text=time_stamp,
                                                                        fg_color="#c9e4de", pady=5, padx=10,
                                                                        font=("Aerial Rounded MT", 10,))
                                    date_label.pack(side="top", pady=5, padx=5)
                                else:
                                    pass

                                prev_date = time_stamp

                                message_frame = customtkinter.CTkLabel(message_panel, text=message_detail,
                                                                       fg_color="#faf4b7", font=("Aerial", 12,),
                                                                       padx=10, corner_radius=10, width=300, anchor="w",
                                                                       justify="left", wraplength=350, pady=10)
                                message_frame.pack(side="top", padx=5, pady=20, anchor="w")

                            else:
                                if prev_date != time_stamp:
                                    date_label = customtkinter.CTkLabel(message_panel, text=time_stamp,
                                                                        fg_color="#c9e4de", pady=5, padx=10,
                                                                        font=("Aerial Rounded MT", 10,))
                                    date_label.pack(side="top", pady=5, padx=5)
                                else:
                                    pass

                                prev_date = time_stamp

                                message_frame = customtkinter.CTkLabel(message_panel, text=message_detail,
                                                                       fg_color="#faf4b7", font=("Aerial", 12,),
                                                                       padx=10, corner_radius=10, width=300, anchor="w",
                                                                       justify="left", wraplength=350, pady=20)
                                message_frame.pack(side="top", padx=5, pady=20, anchor="e")

                                pass

                        pass

                    friend = customtkinter.CTkButton(friend_frame, text="   "+username.title(), height=35,
                                                        corner_radius=4,
                                                        image=verifiedg, compound="right",
                                                        font=("Aerial Rounded MT", 11,),
                                                        command=load_chat, hover_color=self.hover_theme,
                                                        fg_color=self.theme_color, text_color="black", anchor="w",
                                                        width=250)
                    friend.pack(side="top", fill="x", pady=0)


        threading.Thread(target=load_request).start()
        # threading.Thread(target=load_request_from_other).start()

        # load_request_from_other()
        # load_request()

    def setting(self):

        mysphere = customtkinter.CTkImage(
            light_image=Image.open("Icons\\plane_logo.png"),
            dark_image=Image.open("Icons\\plane_logo.png"),
            size=(295, 295))

        self.displayarea_title.configure(text="Setting")

        try:
            for i in self.container.winfo_children():
                i.destroy()
        except:
            pass

        self.setting_frame = customtkinter.CTkFrame(self.container, fg_color="transparent")
        self.setting_frame.pack(side="top", fill="both", expand=1)

        self.vertical_bt.configure(state="disabled")
        self.horizontal_bt.configure(state="disabled")

        setting_panel1 = customtkinter.CTkFrame(self.setting_frame,width=400,corner_radius=7,border_width=0,fg_color="transparent",border_color="#faf0b9")
        setting_panel1.pack(side="left",fill="y",padx=5,pady=5)
        setting_panel1.pack_propagate(False)

        setting_panel2 = customtkinter.CTkFrame(self.setting_frame,corner_radius=0,fg_color="white")
        setting_panel2.pack(side="left", fill="both",expand=1,padx=5,pady=5)

        logo = customtkinter.CTkLabel(setting_panel2,image=mysphere,text="")
        logo.pack(anchor="center",pady=150)



        system_configuration_frame = customtkinter.CTkFrame(setting_panel1, corner_radius=7, border_width=2,
                                                fg_color=self.theme_color, border_color="#faf0b9",height=400,)
        system_configuration_frame.pack(side="top", fill="x", padx=10, pady=10)
        system_configuration_frame.pack_propagate(False)

        config_label = customtkinter.CTkLabel(system_configuration_frame, text="System Configuration",
                                                font=("Aerial Rounded MT", 13, "bold"), justify="left",
                                                anchor="w",fg_color="transparent",padx=15,pady=5)
        config_label.pack(side="top", fill="x", padx=2, pady=2)

        fontsize_label = customtkinter.CTkLabel(system_configuration_frame, text="Edit font size",
                                                 font=("Aerial Rounded MT", 11,),padx=5)
        fontsize_label.pack(side="top", anchor="w", padx=15)


        def slider_event(value):
            print(value)

        slider = customtkinter.CTkSlider(system_configuration_frame, from_=10, to=15, command=slider_event,width=170,number_of_steps=5,button_color="green",progress_color="green")
        slider.pack(side="top", anchor="w", padx=12,pady=1)

        confirm_bt = customtkinter.CTkButton(system_configuration_frame,text="Apply",width=80,corner_radius=2,height=10,font=("Aerial", 11,"bold"),text_color="white")
        confirm_bt.pack(side="top",anchor="w",padx=17,pady=10)



        color_label = customtkinter.CTkLabel(system_configuration_frame, text="Edit Accent Color",
                                                 font=("Aerial Rounded MT", 11,), padx=5)
        color_label.pack(side="top", anchor="w", padx=15,pady=7)

        pastel_colors = [
            "#fffbe6",  # Light pastel yellow (original)
            "#ffe6eb",  # Light pastel pink
            "#e6f7ff",  # Light pastel blue
            "#e6fff2",  # Light pastel green
            "#f3e6ff",  # Light pastel purple
            "#fff0e6"  # Light pastel peach
        ]
        
        for label in range(0,5):
            if pastel_colors[label]==self.theme_color:
                border_color = "red"
                border_width = 2
            else:
                border_color = "black"
                border_width = 1

            color_label = customtkinter.CTkButton(system_configuration_frame, text="",
                                                 font=("Aerial Rounded MT", 11,),height=30,width=30,fg_color=pastel_colors[label],border_width=border_width,corner_radius=1,border_color=border_color)
            color_label.pack(side="top", anchor="w", padx=17, pady=2)

        confirm_bt = customtkinter.CTkButton(system_configuration_frame, text="Apply", width=80, corner_radius=2,
                                             height=10, font=("Aerial", 11, "bold"), text_color="white")
        confirm_bt.pack(side="top", anchor="w", padx=17, pady=10)




        system_configuration_frame2 = customtkinter.CTkFrame(setting_panel1, corner_radius=7, border_width=2,
                                                            fg_color=self.theme_color, border_color="#faf0b9",
                                                            height=400, )
        system_configuration_frame2.pack(side="top", fill="both", padx=10, pady=10)
        system_configuration_frame2.pack_propagate(False)

        empty_frame = customtkinter.CTkFrame(system_configuration_frame2, corner_radius=0, height=12,
                                             fg_color="transparent")
        empty_frame.pack(side="top", fill="x",pady=5,padx=5)

        def sound_checkbox_event():
            print("checkbox toggled, current value:", sound_check_var.get())

        sound_check_var = customtkinter.StringVar(value="on")
        sound_checkbox = customtkinter.CTkCheckBox(system_configuration_frame2, text="Use Sound/Notification while using application",font=("Aerial Rounded MT", 12,), command=sound_checkbox_event,corner_radius=2,
                                             variable=sound_check_var, onvalue="on", offvalue="off",checkbox_height=20,checkbox_width=20,fg_color="purple",checkmark_color="white",border_width=2,)
        sound_checkbox.pack(side="top", fill="both", padx=14, pady=5)


        def space_checkbox_event():
            print("checkbox toggled, current value:", sound_check_var.get())

        space_usage_check_var = customtkinter.StringVar(value="on")
        space_usage_checkbox = customtkinter.CTkCheckBox(system_configuration_frame2, text="Show space usage in sidebar",font=("Aerial Rounded MT", 12,), command=space_checkbox_event,corner_radius=2,
                                             variable=space_usage_check_var, onvalue="on", offvalue="off",checkbox_height=20,checkbox_width=20,fg_color="purple",checkmark_color="white",border_width=2)
        space_usage_checkbox.pack(side="top", fill="both", padx=14, pady=1)


    def application_starting_interface(self):
        logo = customtkinter.CTkImage(
            light_image=Image.open("Icons\\plane_logo.png"),
            dark_image=Image.open("Icons\\plane_logo.png"),
            size=(350, 350))

        self.root.configure(fg_color="white")
        logo_frame = customtkinter.CTkFrame(self.root,height=500,width=700,border_width=1,fg_color="white")
        logo_frame.pack(side="top",pady=100)

        label = customtkinter.CTkLabel(logo_frame,text="",image=logo)
        label.pack(side="top",fill="both",)

        self.progressbar = customtkinter.CTkProgressBar(self.root,width=700 ,corner_radius=0, height=20,
                                                   progress_color="#35c435", fg_color="#dcdedc")
        self.progressbar.pack(side="top",)

        self.progressbar.set(0.01)

        self.message_label = customtkinter.CTkLabel(self.root, text="",)
        self.message_label.pack(side="top", fill="both", )

    def run_progress_bar(self):
        # self.main_progressbar.start()
        self.main_progressbar.pack(side="left",fill="y",pady=7,padx=20)

        for i in range(101):
            self.main_progressbar.set(i / 100)
            print(i)
            # time.sleep(0.00001)



    def run(self):
        # Login
        def open_server():
            try:
                self.server_setup()
                for i in range(101):
                    self.progressbar.set(i / 100)
                    # print(i)
                    time.sleep(0.00001)

                def sound():
                    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)

                threading.Thread(target=sound).start()
                self.login_interface()

            except:
                self.message_label.configure(text="Network is not available",font=("Agency FB",14,"bold"),text_color="red")



        threading.Thread(target=open_server).start()

        # self.login_interface()

        self.application_starting_interface()



        # Authentication
        # Condition : (If user.json file is empty and authentication status is False) or for checkups
        # self.authenticate()



        # Personalization
        # Condition : If the personalization status is False & authentication status is False



        # Otherwise directs login interface then comes to main(home)
        # title_label = customtkinter.CTkLabel(self.root,text="Main window",font=("Aerial",20,"bold"))
        # title_label.pack(side="top",pady=100)

        self.root.mainloop()

        pass



App = user_interface()
App.run()
# App.user_info()
# App.personalization_interface()
# App.mysphere_interface()

