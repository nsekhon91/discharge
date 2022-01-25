import os

def create_folders(folder_name):
    if not os.path.isdir(folder_name):
        os.makedirs(folder_name)