import qrcode
import EncryptorVG
import DecryptorVG
from PIL import Image
from PIL import Image, ImageDraw, ImageFont


class qr_code_service:
    def __init__(self,data={}):
        self.data = data



    def read_data(self):
        embedded_string = ""

        for placeholder in self.data:
            # print(self.data[placeholder])
            embedded_string += self.data[placeholder]+"##"


        return embedded_string

    def encrypt(self,data):
        encrypted_data = EncryptorVG.encrypt(data=data,key="7")

        return encrypted_data

    def decrypt(self,data):
        try:
            decrypted_data = DecryptorVG.decrypt(data=data, key="7")

            return decrypted_data

        except:

            return None

    def qr_code_formater(self,data):
        try:
            splitted_data = data.split("##")

            if (splitted_data[0] == "T"):

                decode_data = {
                    "Type": "T",
                    "qr_code_id": splitted_data[1],
                    "user_id": splitted_data[2],
                    "username": splitted_data[3],
                    "password": splitted_data[4],
                    "start_time": splitted_data[5],
                    "end_time": splitted_data[6],
                    "content": splitted_data[-2],
                }

                return decode_data

            elif (splitted_data[0] == "M"):

                decode_data = {
                    "Type": "M",
                    "user_id": splitted_data[1],
                    "username": splitted_data[2],
                    "password": splitted_data[3],
                    "content": splitted_data[-2],
                }

                return decode_data

            elif (splitted_data[0] == "U"):

                decode_data = {
                    "Type": "U",
                    "user_id": splitted_data[1],
                    "username": splitted_data[2],
                    "password": splitted_data[3],
                    "content": splitted_data[-2],
                }

                return decode_data

            elif (splitted_data[0] == "A"):

                decode_data = {
                    "Type": "A",
                    "user_id": splitted_data[1],
                    "username": splitted_data[2],
                    "password": splitted_data[3],
                    "content": splitted_data[4],
                    "masterkey": splitted_data[-2]
                }

                return decode_data

            elif (splitted_data[0] == "O"):

                decode_data = {
                    "Type": "O",
                    "qr_code_id": splitted_data[1],
                    "user_id": splitted_data[2],
                    "username": splitted_data[3],
                    "password": splitted_data[4],
                    "content": splitted_data[5],
                }

                return decode_data



            else:
                print("Not defined type")

        except:
            return False

    def create_qrcode(self,size=int(),border=int(),properties=[],name=""):
        self.qr_type = self.data["Type"]

        # Create an instance of QRCode with the desired size
        qr = qrcode.QRCode(
            version=1,  # version=1 corresponds to a 21x21 size QR code
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=border,
        )

        if self.qr_type == "O":
            # Accessible for single time
            pass
        elif self.qr_type == "T":
            # Accessible within the given time frame
            pass
        elif self.qr_type == "M":
            # More than 1 user can access
            pass
        elif self.qr_type == "U":
            # Only for personal user / Single user accessible
            pass
        elif self.qr_type == "A":
            # Defined for application only
            self.qr_type = "MySphere_Access_Key"
            pass

        # Add data to the QRCode object
        content = self.read_data()
        data = self.encrypt(content)
        print(data)
        qr.add_data(data)
        qr.make(fit=True)

        # Create an image from the QRCode object
        img = qr.make_image(fill_color="black", back_color="white")

        if name=="":
            # Save the image
            img.save(f"{self.qr_type} Qrcode.png")
            print(f"Type {self.qr_type} QR code is generated")

        else:
            # Save the image
            img.save(f"{name}.png")
            print(f"Type {name} QR code is generated")

    def create_card(self,username, access, base, logo_path, qr_code_path):
        base_image = Image.open(base).convert("RGBA")

        # # Generate the QR code
        # qr = qrcode.make(qr_code_data)
        # qr = qr.resize((250, 250))

        qr = Image.open(qr_code_path)
        qr = qr.resize((250, 250))

        def template1():
            # Load and resize the logo
            logo = Image.open(logo_path).convert("RGBA")
            logo = logo.resize((270, 270))
            logo_position = (5, -1)

            qr_position = (730, 170)

            base_image.paste(logo, logo_position, logo)
            base_image.paste(qr, qr_position)

            # Draw text on the image
            draw = ImageDraw.Draw(base_image)

            try:
                font = ImageFont.truetype("DejaVuSans-Bold.ttf", 36, )
                small_font = ImageFont.truetype("DejaVuSans.ttf", 16)
                medium_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)

            except IOError:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()

            # Define text and position
            name_position = (70, 280)
            access_position = (70, 360)
            info_position = (70, 390)
            made_position = (70, 500)
            copyright_position = (70, 530)

            draw.text(name_position, username, font=font, fill="#D4AF37")
            draw.text(access_position, access + " access", font=medium_font, fill="white")
            draw.text(info_position, "Max storage : 5GB\nValidity : Not defined", font=small_font, fill="white")
            draw.text(made_position, "Made in PSIT", font=medium_font, fill="white")
            draw.text(copyright_position, "All copyright reserved", font=medium_font, fill="white")

            circle_radius = 15

            x = 330
            circle_positions = [(x + 550, 540),
                                (x + 590, 540),
                                (x + 630, 540)]

            colors = ["red", "green", "yellow"]

            for i in range(3):
                x, y = circle_positions[i]
                draw.ellipse((x - circle_radius, y - circle_radius, x + circle_radius, y + circle_radius),
                             fill=colors[i])

            # Save the result
            base_image.save(f"{username}_master_card.png")

        if base == "CD-2.png":
            template1()

        else:
            pass

data = {
    "Type":"A",
    "user_id":"000000",
    "username":"00000",
    "password":"0000",
    "content":"Dear, MySphere warden give me access",
    "masterkey":"0000"
}

# service = qr_code_service(data=data)
# service.create_qrcode(size=10,border=4,name="qr")

# service.create_card("Username","Private & Public","CD-2.png","MysphereC1.png","qr.png")

#
#
# # data = '''GSCij;,CU)!sAZ>'LYks6j*Sn'GP+Z=r1^U=\\rH>'F"^D!u)GV;Hm@-(I2(k>>l4M'''
# # data = service.decrypt(data)
# # print(service.qr_code_formater(data))
#
# data = '''FqbW#;.`]nAUP7,6rmP\?WL>H:0(:o5nk";"U"oA'Q[/Q72m%h:1Qk%;FOJ"5ZU<P;HXf4?9qI*>#H/;<)ca`6kg=>"U"oA'E'''
# data = service.decrypt(data)
#
# print(data)
#
# print(service.qr_code_formater(data))



