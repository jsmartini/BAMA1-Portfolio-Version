from cryptography.fernet import Fernet

key = Fernet.generate_key()


with open("key.pen", "wb") as f:
    f.write(key)

