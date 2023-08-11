import os
import requests
import random
import logging

# Randomly choose a Hindi voice from all available on Narakeet
def get_voice():
    all_hindi_voices = ['preeti', 'mehar', 'nitesh', 'sushma', 'amitabh', 'kareena', 'aditi']
    return random.choice(all_hindi_voices)

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
    
    logging.info(f"Sending request to Narakeet for text: {text[:50]}...")  # Display only the first 50 characters of the text for brevity
    
    response = requests.post(url, **options)
    
    # Check the response status code
    if response.status_code != 200:
        logging.error(f"Failed to generate audio for text: {text[:50]}. Error: {response.text}")
        return None

    # Make the API call to get audio data
    audio_data = response.content
    
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
    
    # Generate an audio file for each row of the 'sentence' column,
    # and return a new column to the dataset with the audio file names. 
    df['audio'] = df['sentence'].apply(lambda x: call_narakeet_api(x, get_voice(), language, anki_profile_name))
    
    # Format the values in the audio column so that Anki will actually play them
    df['audio'] = df['audio'].apply(lambda x: f"[sound:{x}]")
    
    return df


# Sample usage:
# Assuming df is your dataframe
# updated_df = generate_audio_for_dataframe(df)
