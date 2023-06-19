import io
import pandas as pd

def unnest_learned_words(df):

    # Remove leading and trailing whitespaces from the 'learned' and 'to_learn' columns
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    
    # Remove punctuation marks
    df = df.replace(r'[.,:!?]', '', regex=True).applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Unpack each row in the 'learned' column to get one word per row in a new DataFrame
    learned_unique_words = (df['learned'].str.split(expand=True)
                        .stack()
                        .reset_index(level=1, drop=True)
                        .to_frame('learned_unique'))

    # Remove duplicate words from the new 'learned' DataFrame
    learned_unique_words = learned_unique_words.drop_duplicates(subset=['learned_unique'], keep='first')

    # Merge the new 'learned' DataFrame back to the original one
    res = pd.concat([df.reset_index(drop=True), learned_unique_words.reset_index(drop=True)], axis=1)
    
    return(res)

def evaluate_gpt_response(known_vocab, new_vocab, gpt_payload):
    
  #  # Convert GPT response to a string if necessary, not a list.
  #  if isinstance(response_str, list):
  #      response_str = "\n".join(response_str)
  #      
  #  print(response_str)
    
   # Check whether the GPT payload matches the formatting of a .csv file: If it works then load it as a .csv. If it doesn't then throw an informative error.
    try:
        gpt_payload = pd.read_csv(io.StringIO(gpt_payload[0]))
    except pd.errors.ParserError:
        raise ValueError("The response string does not match the format of a CSV file.")
  
    # Create a new column in the 'response' df that flags, for each value in the 'sentence' column, 
    # whether that value meets the following 2 criteria:
    gpt_payload['meets_criteria'] = gpt_payload['sentence'].apply(lambda x: flag_bad_sentences(x, known_vocab, new_vocab))
    
   # Create a summary pandas table that contains the counts for each of true/false in the meets_criteria column. 
    response_diagnostics = gpt_payload['meets_criteria'].value_counts().rename_axis('meets_criteria').reset_index(name='counts')
    
    # Create a filtered version of the 'response' df which only keeps rows for which the value of meets_criteria is true
    response_validated = gpt_payload[gpt_payload['meets_criteria'] == True]

    return(gpt_payload, response_diagnostics, response_validated)
    
    
# The function checks if the sentence meets two criteria:
# 1. It contains exactly one word found in df['to_learn']
# 2. All other words already exist in df['learned_unique']
def flag_bad_sentences(sentence, known_vocab, new_vocab):

    known_vocab = set(known_vocab.dropna().tolist())
    new_vocab = set(new_vocab.dropna().tolist())
    
    sentence_words = set(sentence.split())
    
    # Condition 1: The sentence should contain exactly one word from to_learn_words
    condition_1 = len(sentence_words.intersection(new_vocab)) == 1
    
    # Condition 2: All other words should exist in learned_words
    condition_2 = sentence_words.difference(new_vocab).issubset(known_vocab)
    
    return condition_1 and condition_2
    
    
