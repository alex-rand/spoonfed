import os
import io
import openai
import pandas as pd
import sqlite3
import csv
from datetime import datetime

def generate_text(calling_frame):

    # Get all the user specifications from the calling frame, or from 'global' state
    learned_deck_tokens = calling_frame.controller.learned_deck_tokens
    new_deck_tokens = calling_frame.controller.new_deck_tokens
    
    # Generate sentences
    gpt_payload = gpt__generate_new_sentences(calling_frame)
    
    # Quality control and examine the generated sentences
    gpt_payload_enhanced = evaluate_gpt_response(gpt_payload, learned_deck_tokens, new_deck_tokens)
    
    # Flag sentences that don't meet the specified rule, e.g. 'i+1 no rogue'
    gpt_payload_enhanced = flag_bad_sentences(gpt_payload_enhanced, calling_frame.selection_criterion_picklist.currentText())
    
    # Export for debugging 
    gpt_payload_enhanced.to_csv('test-payload-enhanced.csv', encoding='utf-8', index=False)

    # Apend to the database
  #  save_to_database("database.db", gpt_payload_enhanced, calling_frame.model_picklist.currentText(), audio_source) 
    
    return(gpt_payload_enhanced)
   
# Call OpenAI API
def gpt__generate_new_sentences(calling_frame):
    openai.api_key = os.getenv("OPENAI_API_KEY") 

    # Define the prompt for GPT 
    prompt = calling_frame.prompt
    

    
    # o1 can't take a system prompt, but other models take both system and user prompts
    if calling_frame.model_picklist.currentText() in ['o1-preview', 'o1-mini']:
        messages = [
            {"role": "user", "content": prompt},
        ]
    else:
        messages = [
            {"role": "system", "content": "You are a CSV generator to assist with creating tables for language learning. Your response must be in .CSV format with exactly 4 columns."},
            {"role": "user", "content": prompt},
        ]
    
    ### For debugging purposes, load a cached CSV so we don't call OpenAI a zillion times
  #  with open('test-payload.txt', 'r') as f:
  #      generated_text = f.read()
 #
  #  return(generated_text)
  
    response = openai.ChatCompletion.create(
      model=calling_frame.model_picklist.currentText(),
      messages=messages,
      temperature=1,
      top_p=1.0,
      frequency_penalty=0.0,
      presence_penalty=0.0
    )
   
    generated_text = [
      choice.message["content"].strip() for choice in response["choices"]
    ]

 #  # Export it for debugging purposes
    with open('test-payload.csv', 'w', encoding='utf-8') as f:
        # Write the CSV data to the file
        f.write(generated_text[0])
    
 #  # print(generated_text[0])
   
    return generated_text
 
# This function quality-checks the GPT payload, then it generates some diagnostics about the content of each sentence
def evaluate_gpt_response(gpt_payload, known_vocab, new_vocab):
    # Check whether the GPT payload matches the formatting of a .csv file: If it works then load it as a .csv. If it doesn't then throw an informative error.
    try:
        # Read the payload using the csv module to handle commas within quotes
        data = []
        reader = csv.reader(io.StringIO(gpt_payload[0]))
        for row in reader:
            data.append(row)

        # Convert the list of lists into a DataFrame
        gpt_payload = pd.DataFrame(data[1:], columns=data[0])
        
    except pd.errors.ParserError:
        raise ValueError("The GPT response string does not match the format of a CSV file.")
      
    # DEBUGGING
  # gpt_payload.to_csv('parsed-csv.csv', encoding='utf-8', index=False)
    
    # Count the total number of sentences in the payload
    gpt_payload['n_sentences'] = len(gpt_payload)
    
    # Convert the vocab lists to sets, as a way of removing duplicates and enabling efficient operations
    known_vocab_set = set(known_vocab.dropna())
    new_vocab_set = set(new_vocab.dropna())
    
    # Create an inner function to call on each returned sentence one at a time
    def count_word_types(sentence):
        
        # Unnest the sentence into a set
        sentence_words = set(sentence.split())
        
        # Count various word types
        n_words = len(sentence.split())
        n_known_words = len(sentence_words.intersection(known_vocab_set)) 
        n_new_words = len(sentence_words.intersection(new_vocab_set))
        n_rogue_words = len(sentence_words) - n_known_words - n_new_words

        return pd.Series([n_words, n_known_words, n_new_words, n_rogue_words])

    # Apply the function and assign results to new columns
    gpt_payload[['n_words', 'n_known_words', 'n_new_words', 'n_rogue_words']] = gpt_payload['sentence'].apply(count_word_types)
    
    # Do some adhoc correction of HTML tags, which GPT seems to predictably get wrong sometimes
    gpt_payload['sentence'] = gpt_payload['sentence'].str.replace(r'(<span class="[^"]*)&quot;([^"]*">)', r'\1"\2', regex=True)
    gpt_payload['sentence'] = gpt_payload['sentence'].str.replace(r'<span class=\\\\"target_verb\\\\">', '<span class="target_verb">', regex=False)

    return(gpt_payload)
    
# The function checks if the sentence meets two criteria:
# 1. It contains exactly one word found in df['to_learn']
# 2. All other words already exist in df['learned_unique']
def flag_bad_sentences(df, condition):
    
    # Add the condition to the table, for recordkeeping purposes
    df['filter_condition'] = condition
    
    # Option 1: Only keep sentences that have exactly 1 word from the new sentences Anki deck
    if condition == "n+1 no rogue":
        df['meets_criteria'] = ((df['n_new_words'] == 1) & (df['n_rogue_words'] == 0))
    
    # Option 2: Only keep sentences that have exactly one new word OR exactly one rogue word, not both. 
    elif condition == "n+1 with rogue":
        df['meets_criteria'] = (df['n_new_words'] + df['n_rogue_words'] == 1)
        
    elif condition == "n+2 no rogue":
        df['meets_criteria'] = ((df['n_new_words'] > 0) & (df['n_new_words'] <= 2) & (df['n_rogue_words'] == 0))
        
    elif condition == "n+2 with rogue":
        df['meets_criteria'] = ((df['n_new_words'] + df['n_rogue_words'] > 0) & (df['n_new_words'] + df['n_rogue_words'] <= 2))
    
    elif condition == "None":
        df['meets_criteria'] = True
        
    return df

# Function to call the other functions below
def save_to_database(db_name, dat, gpt_model, audio_provider):
    try:
        # Append metadata to the database and return the run_id
        run_id = append_run_entry(db_name, datetime.now().isoformat(), gpt_model, audio_provider)
        if run_id is None:
            raise Exception("Failed to append run entry.")

        # Append the enhanced gpt outputs to the database
        append_status = append_sentences(dat, run_id, db_name)
        if not append_status:
            raise Exception("Failed to append sentences to the database.")
    except Exception as e:
        print(f"Error in save_to_database: {e}")
        raise

# Append a few things to a 'metadata' table
def append_run_entry(db_file, timestamp, gpt_model, audio_provider):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute('''INSERT INTO runs(timestamp, gpt_model, audio_provider)
                     VALUES(?, ?, ?);''', (timestamp, gpt_model, audio_provider))
        conn.commit()
        run_id = c.lastrowid
        return run_id
    except sqlite3.Error as e:
        print(f"Database error in append_run_entry: {e}")
        return None
    finally:
        if conn:
            conn.close()

# Append the enhanced GPT response
def append_sentences(gpt_response, run_id, db_name: str = 'database.db'):
    try:
        gpt_response['run_id'] = run_id
        with sqlite3.connect(db_name) as conn:
            gpt_response.to_sql('gpt_responses', conn, if_exists='append', index=True, index_label='sentence_order')
        return True
    except Exception as e:
        print(f"Error in append_sentences: {e}")
        return False
        