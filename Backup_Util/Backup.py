import os
import shutil

# Allow the use of relative paths
os.chdir(os.path.dirname(__file__))
script_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Change the permissions of all files in the script's folder to allow all users to read and write to them
for file in os.listdir(script_folder):
    file_path = os.path.join(script_folder, file)
    os.chmod(file_path, 0o666)

# Define the source folders and files in the parent directory
source_folders = ["assets/images", "data"]
source_files = [".env"]

# Define the backup folder
backup_folder = os.path.join(os.getcwd(), "Persistent")

def backup_files():
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
    
    for folder in source_folders:
        source_path = os.path.join(script_folder, folder)
        backup_path = os.path.join(backup_folder, folder)

        if os.path.exists(backup_path):
            # If the backup directory already exists, remove it before copying
            shutil.rmtree(backup_path)
        
        shutil.copytree(source_path, backup_path)
    
    for file in source_files:
        source_path = os.path.join(script_folder, file)
        backup_path = os.path.join(backup_folder, file)
        shutil.copy(source_path, backup_path)
    
    input("Backup completed!\nPress Enter to Close: ")

def restore_files():
    if not os.path.exists(backup_folder):
        print("No backup found.")
        return

    for folder in source_folders:
        source_path = os.path.join(backup_folder, folder)
        dest_path = os.path.join(script_folder, folder)
        shutil.rmtree(dest_path)
        shutil.copytree(source_path, dest_path)
    
    for file in source_files:
        source_path = os.path.join(backup_folder, file)
        dest_path = os.path.join(script_folder, file)
        shutil.copy(source_path, dest_path)
    
    input("Files restored!\nPlease check that the Server IP in .env is correct.\nPress Enter to Close: ")


print("This backs up your important files for the bot to a folder called 'Persistent'. And replaces them when you update the bot")
print("Menu:\n1. Backup files to 'Persistent'\n2. Restore files from 'Persistent'\n3. Quit")
choice = input("Enter your choice (1/2/3): ")
    
if choice == '1':
    backup_files()
elif choice == '2':
    restore_files()
elif choice == '3':
    pass
else:
    print("Invalid choice. Please enter 1, 2, or 3.")
