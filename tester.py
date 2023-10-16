import os

folder_path = r'C:\Users\nickf\OneDrive\Documents\Code\Air_Bot\Air-Bot\assets\images\1440'

# Iterate through all files in the folder
for filename in os.listdir(folder_path):
    # Check if the file ends with ".png.crushed.png"
    if filename.endswith(".png.crushed.png"):
        # Generate the new filename by removing ".crushed" from the old filename
        new_filename = os.path.join(folder_path, filename.replace(".crushed.png", ""))
        
        # Rename the file
        os.rename(os.path.join(folder_path, filename), new_filename)
        print(f'Renamed: {filename} to {new_filename}')

print("Renaming process complete.")
