import json

def simple_decrypt(text, key):
    return ''.join(chr((ord(char) - key) % 256) for char in text)


def load_decrypted_json(filename, key):
    with open(filename, 'r', encoding='utf-8') as file:
        encrypted_str = file.read()

    decrypted_str = simple_decrypt(encrypted_str, key)
    return json.loads(decrypted_str)

def load_decrypted_text(text,key):
    encrypted_str = text
    decrypted_str = simple_decrypt(encrypted_str, key)
    return json.loads(decrypted_str)


