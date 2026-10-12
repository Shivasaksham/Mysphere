import json


def simple_encrypt(text, key):
    return ''.join(chr((ord(char) + key) % 256) for char in text)


def save_encrypted_json(data, filename, key):
    json_str = json.dumps(data)
    encrypted_str = simple_encrypt(json_str, key)

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(encrypted_str)

    print(f"Encrypted data saved to {filename}")

    return encrypted_str

def encrypted_data(data,key):
    json_str = json.dumps(data)
    encrypted_str = simple_encrypt(json_str, key)

    return encrypted_str


user_data = {
    "userid": "user123",
    "username": "john_doe",
    "password": "securepassword123",
    "personalization_status": True
}

