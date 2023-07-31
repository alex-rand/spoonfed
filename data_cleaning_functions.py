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

def evaluate_gpt_response(gpt_payload, known_vocab, new_vocab):
    
    # Check whether the GPT payload matches the formatting of a .csv file: If it works then load it as a .csv. If it doesn't then throw an informative error.
    try:
        gpt_payload = pd.read_csv(io.StringIO(gpt_payload[0]))
    except pd.errors.ParserError:
        raise ValueError("The GPT response string does not match the format of a CSV file.")
    
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