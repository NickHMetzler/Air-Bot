from cryptography.fernet import Fernet
import os

# Allow the use of relative paths
os.chdir(os.path.dirname(__file__))
script_folder = os.path.dirname(__file__)
# Change the permissions of all files in the script's folder to allow all users to read and write to them
for file in os.listdir(script_folder):
    file_path = os.path.join(script_folder, file)
    os.chmod(file_path, 0o666)

# The decryption key (must match the key used for encryption)
key = b'eXqe4xrjdstZTKe3nNNGP8ie8WMqhBZehXev8M1_OEQ='

# Create a Fernet cipher object with the key
cipher = Fernet(key)

# Path to the directory containing encrypted image files
encrypted_image_folder_path = 'Encrypted_Images'

# Path to save the decrypted image files
decrypted_image_folder_path = 'Decrypted_Images'

input("Welcome to the Image Decryption Tool\n"
      "1. Place all files to be decrypted into the 'Encrypted_Images' folder\n"
      "2. Ensure that all files end with a lowercase .bin\n"
      "Press Enter to begin: ")

# Get a list of encrypted binary files in the directory
bin_files = [filename for filename in os.listdir(encrypted_image_folder_path) if filename.endswith('.bin')]

exception_flag = False

# Loop through each binary file and decrypt it
for bin_file in bin_files:
    try:
        # Read the contents of the binary file
        bin_file_path = os.path.join(encrypted_image_folder_path, bin_file)
        with open(bin_file_path, 'rb') as file:
            encrypted_data = file.read()

        # Decrypt the binary data
        decrypted_data = cipher.decrypt(encrypted_data)

        # Name the decrypted file with the original name and extension
        original_file_name = os.path.splitext(bin_file)[0] + '.png'
        decrypted_file_path = os.path.join(decrypted_image_folder_path, original_file_name)

        # Write the decrypted data to the file
        with open(decrypted_file_path, 'wb') as file:
            file.write(decrypted_data)

        print(f"File {bin_file} decrypted and saved successfully as {original_file_name}.")

    except Exception as e:
        exception_flag = True
        print(f"Error occurred while processing {bin_file}: {str(e)}")

if exception_flag is True:
    print("Error occurred in processing some files, please check the log above.")
else:
    print("All files decrypted to 'Decrypted_Images' folder")

input('Press Enter to close the program: ')
