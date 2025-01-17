import os
import requests
import random
import string
import logging
import pandas as pd
import random

def generate_audio(df, language, anki_profile_name, tts_api):
    
    # Strip HTML tags and Anki Cloze notation
    df['sentence_stripped'] = df['sentence'].str.replace(r'<span class="?[^"]*"?>{{c1::(.*?)::.*?}}</span>', r'\1', regex=True)
    df['sentence_stripped'] = df['sentence_stripped'].str.replace(r'<[^>]+>', '', regex=True)
    
    # If the above stripping functions failed then the audio generating functions will include Cloze or HTML nonsense, so stop.
    if df['sentence_stripped'].str.contains('c1').any():
        raise ValueError("The HTML or Anki Cloze structure returned by the language model is incorrect, so generated audio would be incorrect.")

    pd.set_option("display.max_rows", 1000)
    pd.set_option("display.expand_frame_repr", True)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', None) 
    
    # Generate an audio file for each row of the 'sentence' column,
    # and return a new column to the dataset with the audio file names. 

    if tts_api == "ElevenLabs":
        df['audio'] = df['sentence_stripped'].apply(lambda x: call_elevenlabs_api(x, language, anki_profile_name))
    elif tts_api == "Narakeet":
        df['audio'] = df['sentence_stripped'].apply(lambda x: call_narakeet_api(x, get_voice(), language, anki_profile_name))
    else:
        raise ValueError("Invalid TTS API selected. Choose 'ElevenLabs' or 'Narakeet'.")

    
    # Format the values in the audio column so that Anki will actually play them
    df['audio'] = df['audio'].apply(lambda x: f"[sound:{x}]")
    
    return df

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
    
    # Check if text is None or empty
    if not text:
        logging.error("No text provided for Narakeet API call.")
        return None

    try:
        # Define the endpoint and parameters for the API call
        url = f'https://api.narakeet.com/text-to-speech/mp3?voice={voice}&language={language}&voice-speed=.8'

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

        # Use the first 10 characters of the text for the filename,
        # unless the text field is empty, in which case just use a random string
        if text:
            filename = f"{text[:10]}-{random.randint(10000000, 99999999)}.mp3"
        else:
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            filename = f"{random_string}.mp3"

        # Join them to get the full save path
        save_path = os.path.join(directory_path, filename)  

        # Save the audio data to the specified path
        with open(save_path, 'wb') as f:
            f.write(audio_data)

        # Return the filename
        return filename

    except Exception as e:
        logging.error(f"An error occurred in call_narakeet_api: {str(e)}")
        return None
    
def call_elevenlabs_api(text, language, anki_profile_name):
    
    # Check if text is None or empty
    if not text:
        logging.error("No text provided for Elevenlabs API call.")
        return None
    
    try:
        if language == "French":
            voice = "r7gc4KEJhGwyEQx71Tx1"  # or Patrick: "XTyroWkQl32ZSd3rRVZ1"
        elif language != "French":
            voice = "GGs86ihiCGgvbv8vqV7h" # or OUxfKPssG0qAk5VQF8We for lowlex
            
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"

        # Build the payload
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": random.randint(30, 80)/100,  # Random integer stability between 50 and 70
                "similarity_boost": random.randint(30, 80)/100,  # Random integer similarity boost between 60 and 80
                "use_speaker_boost": True
            }
            
        }
        headers = {
            "Accept": "audio/mpeg",
            "xi-api-key": os.getenv("ELEVENLABS_API_KEY"),
            "Content-Type": "application/json",
        }
    
        response = requests.request("POST", url, json=payload, headers=headers)

        # Check the response status code
        if response.status_code != 200:
            logging.error(f"Failed to generate audio for text: {text[:50]}. Error: {response.text}")
            return None

        # Get the audio
        audio_data = response.content
        
        # If we're doing French, send the voice back to the Voice-to-Voice API to turn it into Alex
        if language == "French":
            
            url = "https://api.elevenlabs.io/v1/speech-to-speech/GGs86ihiCGgvbv8vqV7h" # send to Alex-Clone voice
    
            # Set up the multipart form data
            files = {
                'audio': ('input_audio.mp3', audio_data, 'audio/mpeg'),
               'model_id': (None, 'eleven_multilingual_sts_v2', 'text/plain')
            }
    
            headers = {
                "Accept": "audio/mpeg",
                "xi-api-key": os.getenv("ELEVENLABS_API_KEY"),
            }

            response = requests.post(
                url,
                files=files,
                headers=headers,
            )
            
            # Extract the Alex version of the French text
            audio_data = response.content
            

        # Get the save path from 
        directory_path = get_anki_media_path(anki_profile_name)

        # Use the first 10 characters of the text for the filename,
        # unless the text field is empty, in which case just use a random string
        if text:
            filename = f"{text[:10]}-{random.randint(10000000, 99999999)}.mp3"
        else:
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            filename = f"{random_string}.mp3"

        # Join them to get the full save path
        save_path = os.path.join(directory_path, filename)  

        # Save the audio data to the specified path
        with open(save_path, 'wb') as f:
            f.write(audio_data)

        # Return the filename
        return filename

    except Exception as e:
        logging.error(f"An error occurred in call_narakeet_api: {str(e)}")
        return None

