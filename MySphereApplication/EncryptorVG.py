import base64


def encrypt(data="", key=""):
    key_bytes = key.encode()
    data_bytes = data.encode()

    encrypted = bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data_bytes)])
    return base64.a85encode(encrypted).decode()



