# Simple script to download files from Azure Blob Storage using their latest Python SDK
# Configured to write to a shared folder for use in SILDC - SICTM
# Requires python 3.6 or above
import os
import json
import argparse
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient

# Initialize argument parser
description = "Internal SICTM utility to download Azure Blobs from Storage Account"
parser = argparse.ArgumentParser(description=description)
parser.add_argument("-c", "--config", help="Script configuration file path")
parser.add_argument("-d", "--decrement-days", help="Amount of days decremented from current date", default=1, type=int)
parser.add_argument("-t", "--config-template", help="Generates a configuration template file", action='store_true')
args = parser.parse_args()

# Sets default config file path
__config_file_path = "./config.json"

# Generates configuration template if requested
if args.config_template:
    with open(__config_file_path, 'w') as json_file:
        template = '{"connection_string": "","blob_container": "","blob_folder": "","blob_file": "","local_folder": ""}'
        json_file.write(template)
    print('Template file created at ' + __config_file_path)
    exit(0)

# Sets default config file path
__config_days_decremented = 1

# Overrides default config file path if --config is provided
if args.config:
    __config_file_path = args.config

# Overrides default amount of days decremented if --decrement-days is provided
if args.decrement_days:
    __config_days_decremented = args.decrement_days

# Loads configuration file
with open(__config_file_path, 'r') as json_file:
    __config = json.load(json_file)

# Storage account connection string
MY_CONNECTION_STRING = __config['connection_string']

# Blob container
MY_BLOB_CONTAINER = __config['blob_container']

# Blob folder
MY_BLOB_FOLDER = __config['blob_folder']

# Blob file
MY_BLOB_FILE = __config['blob_file']

# Local folder
LOCAL_BLOB_PATH = __config['local_folder']


class AzureBlobFileDownloader:
    def __init__(self):
        print("Intializing AzureBlobFileDownloader")

        # Initialize the connection to Azure storage account
        self.blob_service_client = BlobServiceClient.from_connection_string(MY_CONNECTION_STRING)
        self.my_container = self.blob_service_client.get_container_client(MY_BLOB_CONTAINER)

    def save_blob(self, file_name, chunks):
        # Get full path to the file
        # To avoid loading incomplete files, they are downloaded with a custom extension
        downloading_file_path = os.path.join(LOCAL_BLOB_PATH, file_name+".downloading")
        downloaded_file_path = os.path.join(LOCAL_BLOB_PATH, file_name)

        # Create local folders for nested blobs
        os.makedirs(os.path.dirname(downloading_file_path), exist_ok=True)

        # Write to local file by chunks to avoid out of memory errors
        with open(downloading_file_path, "wb") as file:
            for chunk in chunks:
                file.write(chunk)

        # After being fully downloaded, the file is then renamed back to the original format
        os.rename(downloading_file_path, downloaded_file_path)

        # Append to list of downloaded blobs
        downloaded_files_path = os.path.join(LOCAL_BLOB_PATH, "downloaded_files.txt")
        with open(downloaded_files_path, "a") as file:
            file.write("\n" + file_name)

    def download_blobs(self, path=""):
        # Fetch blob list based on supplied path
        # List is based on expression match, so be careful with nested blobs
        my_blobs = self.my_container.list_blobs(path)

        # Fetches local list to avoid re-downloading blobs
        downloaded_blobs = os.listdir(LOCAL_BLOB_PATH)
        for blob in my_blobs:
            # Fetches only the file name from a specific folder
            clean_blob = blob.name.replace(MY_BLOB_FOLDER, "")
            if clean_blob in downloaded_blobs:
                continue

            print(clean_blob)

            # Fetches chunk iterable
            chunks = self.my_container.get_blob_client(blob).download_blob().chunks()

            # Saves blob locally
            self.save_blob(clean_blob, chunks)


if __name__ == '__main__':

    # The script is set to download the file generated in the morning databricks extractions for the day
    # -d argument may be provided to (re)download skipped days
    yesterday = datetime.now() - timedelta(__config_days_decremented)

    # Formats data as expected for SILDC
    data_formated = "%s%s%s000000" % (str(yesterday.year), str(yesterday.month).zfill(2), str(yesterday.day).zfill(2))

    # Initialize class and download files
    azure_blob_file_downloader = AzureBlobFileDownloader()
    azure_blob_file_downloader.download_blobs(f"{__config['blob_folder']}{__config['blob_file'].replace('{{date}}', data_formated)}")
