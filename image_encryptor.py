# This file encrypts any images in the assets folder to a bin file located in assets/bin
# To encrypt an image, name it imagename.png and place it in the assets folder
# Then run this file
from cryptography.fernet import Fernet
import os

# Generate a random encryption key
key = b'eXqe4xrjdstZTKe3nNNGP8ie8WMqhBZehXev8M1_OEQ='

# Create a Fernet cipher object with the key
cipher = Fernet(key)

# Path to the directory containing PNG files
folder_path = r'C:\Users\nickf\Documents\Code\War Thunder Air Bot\assets'

# Path to save the encrypted PNG files
encrypted_image_folder_path = r'C:\Users\nickf\Documents\Code\War Thunder Air Bot\assets\temp'

# Get a list of PNG files in the directory
png_files = [filename for filename in os.listdir(folder_path) if filename.endswith('.png')]

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
        print(f"Error occurred while processing {png_file}: {str(e)}")

print("All images processed.")
