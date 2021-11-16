from cryptography.fernet import Fernet
import struct

global encrypted_packet_fmt_string_structure

encrypted_packet_fmt_string_structure = "128p"

key = Fernet(open("key.pen", "r").read())

def encrypt(msg_bin_str):
    # encrypts binary string structure
    return key.encrypt(msg_bin_str)

def decrypt(encypted_msg_bin_str):
    # decrypts binary string structure
    return key.decrypt(encypted_msg_bin_str)


if __name__ == "__main__":
    x = "Secret Data"
    print(x)
    print(encrypt(x.encode()))
    print(decrypt(encrypt(x.encode())))

