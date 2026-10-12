import base64


def decrypt(data="", key=""):
    key_bytes = key.encode()
    encrypted = base64.a85decode(data.encode())
    original = bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(encrypted)])
    return original.decode()