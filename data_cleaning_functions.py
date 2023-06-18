
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
