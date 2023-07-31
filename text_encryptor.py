from cryptography.fernet import Fernet

# Generate a random encryption key
key = b'eXqe4xrjdstZTKe3nNNGP8ie8WMqhBZehXev8M1_OEQ='

# Prompt the user for their choice
choice = input("Choose a file to encrypt:\n1: heights\n2: distances\nEnter Choice: ")

# Validate the user's choice
while choice not in ['1', '2']:
    print("\nInvalid choice. Please enter only either 1 or 2")
    choice = input("Choose a file to encrypt:\n1: heights\n2: distances\nEnter Choice: ")
if choice == '1':
    choice = 'heights'
else:
    choice = 'distances'
# Create a Fernet cipher object with the key
cipher = Fernet(key)

# Path to the text file
text_file_path = f'C:/Users/nickf/Documents/Code/War Thunder Air Bot/sensitive/{choice}.txt'

# Read the contents of the text file
with open(text_file_path, 'rb') as file:
    text_data = file.read()

# Encrypt the text data
encrypted_data = cipher.encrypt(text_data)

# Path to save the encrypted text file
encrypted_text_file_path = f'C:/Users/nickf/Documents/Code/War Thunder Air Bot/data/{choice}_encrypted.txt'

# Write the encrypted data to the file
with open(encrypted_text_file_path, 'wb') as file:
    file.write(encrypted_data)

print(f"{choice} file encrypted and saved successfully.")
