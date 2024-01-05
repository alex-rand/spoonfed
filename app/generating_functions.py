import os
import io
import openai
import pandas as pd
import sqlite3
from datetime import datetime

def generate(controller, calling_frame):
  
    # Get all the user specifications from the calling frame, or from 'global' state
    with_audio = calling_frame.audio_checkbox_var.get()
    audio_source = calling_frame.audio_source_picklist.get()
    model = calling_frame.model_picklist.get()
    n_sentences = int(calling_frame.nsentences_picklist.get())
    learned_deck_tokens = controller.learned_deck_tokens
    new_deck_tokens = controller.new_deck_tokens
    
    # Generate sentences
    gpt_payload = gpt__generate_new_sentences(learned_deck_tokens, new_deck_tokens, n_sentences, model)
    
    print("gpt_payload:")
    print(gpt_payload)
    
    # Quality control and examine the generated sentences
    gpt_payload_enhanced = evaluate_gpt_response(gpt_payload, learned_deck_tokens, new_deck_tokens)
    
    # Flag sentences that don't meet the N+1 rule, or any other rule I haven't thought of yet
    gpt_payload_enhanced = flag_bad_sentences(gpt_payload_enhanced, "n+1 with rogue")
    
    # Apend to the database
    save_to_database("database.db", gpt_payload_enhanced, model, audio_source) 
    
    return(gpt_payload_enhanced)
   
   # Display the sentences and diagnostics in a new window

  # # Subset only the sentences that fit the criteria
  # keepers = gpt_payload_enhanced[gpt_payload_enhanced['meets_criteria'] == True]
    
  
    if with_audio:
    # narakeet functions
      pass

# Call OpenAI API
def gpt__generate_new_sentences(learned_deck_tokens, new_deck_tokens, n_sentences, model):
    openai.api_key = os.getenv("OPENAI_API_KEY") 
    # Join each list into a single string, with words separated by comma
    learned_deck_tokens_str = ", ".join(learned_deck_tokens)
    new_deck_tokens_str = ", ".join(new_deck_tokens)
   
    # Define the prompt for GPT 
    prompt =f""" 
      I need your help to output a .csv file containing new Hindi sentences based on a student's existing vocabulary.
      Your output must be only a .csv file, with no other content.  
      Imagine you are a Hindi teacher, helping a native English speaker who has just started learning Hindi. 
      So far the student has learned the following words, which we can call the 'learned words', and are as follows: 
      {learned_deck_tokens_str} 
      Today the student is trying to learn the following words, which we can call the 'new words', and are as follows; 
      {new_deck_tokens_str} 
      Please generate {n_sentences} new Hindi sentences and return them as a .csv file with a column titled 'sentence'. Each sentence must meet all of the following criteria:
      - Each sentence includes _exactly one_ of the 'new words' -- you are NOT ALLOWED to include more than one word from the list of 'new words';
      - All of the other words in each sentence (besides the exactly one 'new word') must already appear in the list of 'learned words';
      - Each sentence must include a subject, a verb, and an object. 
      Please use correct grammar and formal sentence structure when writing the sentences.
      Include as many of the words from the list of 'learned words' as you can in each sentence while still respecting the rules I mentioned above.
      Always respect Hindi's standard subject-object-verb structure.  
      The output format of the new sentences you generate should be a .csv with a column for the Hindi sentence, 
      a column for the English translation called 'translation', and a column called 'new_word' specifying which of the new words you've included in that sentence.  
      Remember: you must include exactly _one_ of the 'new words' in each sentence, and the rest of the words must all already be present in the 'learned words', except for the exceptions I mentioned above.
      The output MUST be a .csv file with one column exactly as specified above. 
      Do NOT say anything else, just output the raw .csv file and say nothing else. Do not wrap in ```, just output the raw .csv text.
      """ 
    messages = [
      {"role": "system", "content": f"You are a helpful assistant. Your response must be in .CSV format."},
      {"role": "user", "content": prompt},
    ] 
    
   # ### DELETE from here
   # import ast
   # # Open the file in read mode ('r')
   # with open('test-payload.txt', 'r') as f:
   #     # Read the entire file to a string
   #     test_payload = f.read()
   #     
   # gpt_payload = ast.literal_eval(test_payload)
   # 
   # return(gpt_payload)
  
    ###  /DELETE up to here
    response = openai.ChatCompletion.create(
     # model="gpt-3.5-turbo-0613",
      model=model,
      messages=messages,
      temperature=0.1,
      top_p=1.0,
      frequency_penalty=0.0,
      presence_penalty=0.0
    )
   
   
    generated_text = [
      choice.message["content"].strip() for choice in response["choices"]
    ]
    
    print("generated_text:")
    print(generated_text)
    
  #  generated_text_string = generated_text[0]
  #  print("generated_text_string:")
  #  print(generated_text_string)
  #  
  #  generated_text_trimmed = generated_text_string.strip()
  #  generated_text_trimmed = generated_text_trimmed[6:-3].strip()
  #  print("generated_text_trimmed:")
  #  print(generated_text_trimmed)
  # 
    return generated_text
 
 # This function quality-checks the GPT payload, then it generates some diagnostics about the content of each sentence
def evaluate_gpt_response(gpt_payload, known_vocab, new_vocab):
  
    # Check whether the GPT payload matches the formatting of a .csv file: If it works then load it as a .csv. If it doesn't then throw an informative error.
    try:
        gpt_payload = pd.read_csv(io.StringIO(gpt_payload[0]))
    except pd.errors.ParserError:
        raise ValueError("The GPT response string does not match the format of a CSV file.")
      
    print("de-csv'd payload:")
    print(gpt_payload)
    
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

    return(gpt_payload)
    
# The function checks if the sentence meets two criteria:
# 1. It contains exactly one word found in df['to_learn']
# 2. All other words already exist in df['learned_unique']
def flag_bad_sentences(df, condition):
    
    # Add the condition to the table, for recordkeeping purposes
    df['filter_condition'] = condition
    
    # Option 1: Only keep sentences that have exactly 1 word from the new sentences Anki deck
    if condition == "n+1 no rogue":
        
        df['meets_criteria'] = (df['n_new_words'] + df['n_rogue_words']) == 1
    
    # Option 2: Only keep sentences that have exactly one new word OR exactly one rogue word, not both. 
    elif condition == "n+1 with rogue":
        
        df['meets_criteria'] = ((df['n_new_words'] == 1) & (df['n_rogue_words'] == 0)) ^ ((df['n_new_words'] == 0) & (df['n_rogue_words'] == 1))        
    
    return(df)

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
        
