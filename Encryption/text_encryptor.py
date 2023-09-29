from cryptography.fernet import Fernet
import os

# Allow the use of relative paths
os.chdir(os.path.dirname(__file__))
script_folder = os.path.dirname(__file__)
# Change the permissions of all files in the script's folder to allow all users to read and write to them
for file in os.listdir(script_folder):
    file_path = os.path.join(script_folder, file)
    os.chmod(file_path, 0o666)

# Generate a random encryption key
key = b'eXqe4xrjdstZTKe3nNNGP8ie8WMqhBZehXev8M1_OEQ='

# Path to the text file
text_file_path = 'Original_Text'

# Path to save the encrypted text file
encrypted_text_file_path = 'Encrypted_Text'

input("Welcome to the Text Encryption Tool\n1. Place all files to be encrypted into the 'Original_Text' folder\n2. Ensure that all files end with a lowercase .txt\nPress Enter to begin: ")
# Create a Fernet cipher object with the key
cipher = Fernet(key)

# Read the contents of the text file
with open(text_file_path, 'rb') as file:
    text_data = file.read()

# Encrypt the text data
encrypted_data = cipher.encrypt(text_data)

# Write the encrypted data to the file
with open(encrypted_text_file_path, 'wb') as file:
    file.write(encrypted_data)

print(f"All files encrypted and saved successfully to the 'Encrypted_Text' Folder.\nPress Enter to close program: ")
