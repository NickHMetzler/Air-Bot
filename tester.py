# Initialize variables to store the phrases


# Read from chat_phrases.txt and store in the chat_phrases list
with open("data/chat_phrases.txt", "r") as file:
    chat_phrases = file.read().splitlines()

# Read from pyrenees_phrases.txt and store in the pyrenees_phrases list
with open("data/pyrenees_phrases.txt", "r") as file:
    pyrenees_phrases = file.read().splitlines()

# Now you have the phrases in the variables, you can use them as needed
print("Chat Phrases:", chat_phrases)
print("Pyrenees Phrases:", pyrenees_phrases)