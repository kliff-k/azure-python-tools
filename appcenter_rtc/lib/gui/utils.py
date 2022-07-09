import os
import json
import hashlib
import platform

from appcenter_rtc.config import data_paths
from appcenter_rtc.lib.tool.aes import Cipher


def check_user_data() -> bool:
    """
    Checks if local user data exists and is valid
    :return bool
    """
    # Checks if file exists, creates whole data path if possible
    if not os.path.exists(data_paths.local_data_file):
        os.makedirs(data_paths.local_data_folder, exist_ok=True)
        return False

    with open(data_paths.local_hash_file, 'r') as file:
        saved_hash = file.read()

    user_hash = hashlib.sha3_512(generate_encryption_key().encode()).hexdigest()

    # Checks if encryption key is valid for this system
    if saved_hash != user_hash:
        return False

    return True


def get_user_data() -> dict:
    """
    Fetches user credentials from encrypted local storage
    :return dict: User credentials dictionary
    """
    aes = Cipher(generate_encryption_key())
    with open(data_paths.local_data_file, 'rb') as file:
        data = json.loads(aes.decrypt(file.read()))

    return data


def generate_encryption_key() -> str:
    """
    Generates a persistent encryption key based on user login and machine specifications
    :return str: Encryption key string
    """
    return os.getlogin() + platform.node() + platform.system() + platform.machine()
