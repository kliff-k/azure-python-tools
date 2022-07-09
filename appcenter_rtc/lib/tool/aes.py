import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util import Counter


class Cipher:
    """
    Basic AES cipher python implementation class
    """
    def __init__(self, key: str):
        """
        Sets the key used for the symmetric operations and the default block size
        :param key: Symmetric key
        """
        self.private_key = hashlib.sha256(key.encode()).digest()
        self.bs = AES.block_size

    def encrypt(self, data: str) -> bytes:
        """
        :param data: String to be encrypted
        """
        # Setup AES Cipher using private key, counter mode
        ctr = Counter.new(128, initial_value=163349233)
        cipher = AES.new(self.private_key, AES.MODE_CTR, counter=ctr)

        # Encrypt the data and convert to base64
        return base64.b64encode(cipher.encrypt(data.encode()))

    def decrypt(self, enc):
        """
        :param enc: String to be decrypted
        """
        # Convert encrypted data from base64
        enc = base64.b64decode(enc)

        # Setup AES Cipher using private key
        ctr = Counter.new(128, initial_value=163349233)
        cipher = AES.new(self.private_key, AES.MODE_CTR, counter=ctr)

        # Decrypt data and
        return cipher.decrypt(enc).decode("utf-8")
