import os

def check():
    directory_path = '/Users/alex/Library/Application Support/Anki2/Alex/collection.media/'

    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        x = "The directory exists."
    else:
        x = "The directory does not exist."
    
    return(x)

def check():

    username = os.path.basename(os.path.expanduser('~'))
    print(username)

print(check())