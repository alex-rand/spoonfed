import os
import requests
import random
import pandas as pd

# Randomly choose a Hindi voice from all available on Narakeet
def get_voice():
    all_hindi_voices = ['preeti', 'mehar', 'nitesh', 'sushma', 'amitabh', 'kareena', 'aditi']
    return random.choice(all_hindi_voices)

import os
import requests

# Get the filepath for the folder where Anki media files need to be stored
def get_anki_media_path(anki_profile_name):
    
    username = os.path.basename(os.path.expanduser('~'))

    # Return the path to the Anki collection media for the specified profile
    return f"/Users/{username}/Library/Application Support/Anki2/{anki_profile_name}/collection.media"

def call_narakeet_api(text, voice, language, anki_profile_name):
    
    # Define the endpoint and parameters for the API call
    url = f'https://api.narakeet.com/text-to-speech/mp3?voice={voice}&language={language}'
    
    options = {
        'headers': {
            'Accept': 'application/octet-stream',
            'Content-Type': 'text/plain',
            'x-api-key': os.getenv("NARAKEET_API_KEY")
        },
        'data': text.encode('utf8')
    }
    
    # Make the API call to get audio data
    audio_data = requests.post(url, **options).content
    
    # Get the save path from get_anki_media_path()
    directory_path = get_anki_media_path(anki_profile_name)

    # Use the first 10 characters of the text for the filename
    filename = f"{text[:10]}.mp3"

    # Join them to get the full save path
    save_path = os.path.join(directory_path, filename)  
    
    # Save the audio data to the specified path
    with open(save_path, 'wb') as f:
        f.write(audio_data)
    
    # Return the filename
    return filename

def generate_audio(df, language, anki_profile_name):
    
    # Apply the function to each row of the 'sentence' column.
    # This function saves audio to 
    df['audio'] = df['sentence'].apply(lambda x: call_narakeet_api(x, get_voice(), language, anki_profile_name))
    
    return df

# Sample usage:
# Assuming df is your dataframe
# updated_df = generate_audio_for_dataframe(df)
