# This file encrypts any images in the assets folder to a bin file located in assets/bin
# To encrypt an image, name it imagename.png and place it in the assets folder
# Then run this file
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

# Create a Fernet cipher object with the key
cipher = Fernet(key)

# Path to the directory containing PNG files
folder_path = 'Original_Images'

# Path to save the encrypted PNG files
encrypted_image_folder_path = 'Encrypted_Images'

input("Welcome to the Image Encryption Tool\n1. Place all files to be encrypted into the 'Original' folder\n2. Ensure that all files end with a lowercase .png\nPress Enter to begin: ")

# Get a list of PNG files in the directory
png_files = [filename for filename in os.listdir(folder_path) if filename.endswith('.png')]

exception_flag = False
# Loop through each PNG file
for png_file in png_files:
    try:
        # Read the contents of the PNG file
        png_file_path = os.path.join(folder_path, png_file)
        with open(png_file_path, 'rb') as file:
            image_data = file.read()

        # Encrypt the image data
        encrypted_data = cipher.encrypt(image_data)

        # Remove the extension from the PNG file name
        png_file_name = os.path.splitext(png_file)[0]

        # Name the encrypted file after the PNG file without the extension
        encrypted_file_path = os.path.join(encrypted_image_folder_path, png_file_name + '.bin')

        # Write the encrypted data to the file
        with open(encrypted_file_path, 'wb') as file:
            file.write(encrypted_data)

        print(f"Image {png_file} encrypted and saved successfully.")

    except Exception as e:
        exception_flag = True
        print(f"Error occurred while processing {png_file}: {str(e)}")

if exception_flag is True:
    print("Error occured in processing some images, please check the log above.")
else:
    print("All images processed to 'Encrypted' Folder")
input('Press enter to close program: ')
