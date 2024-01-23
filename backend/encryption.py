import sys
import hashlib
import getpass
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA512
from Crypto.Random import get_random_bytes


def hash_this(input):

    h = hashlib.new("SHA256")


    h.update(input.encode())
    input_hash = h.hexdigest()

    return input_hash

def computeMasterKey(mp, ds):
    password = hash_this(mp)
    salt = hash_this(ds)
    key = PBKDF2(password, salt, 32, count=1000000, hmac_hash_module=SHA512)
    return key

def main():
    user_input = input("Give me something to hash: ")

    hashed_input = hash_this(user_input)
    print(hashed_input)



if __name__ == "__main__":
    main()

# print(h.digest()) # Raw bytes
# print(h.hexdigest()) # Hexadecimal output 