import os
import openai

def get_new_sentences(df): 
  
  openai.api_key = os.getenv("OPENAI_API_KEY")

  response = openai.Completion.create(
    model="gpt-3.5-turbo-0613",
    prompt= """
    
    I need your help to generate a .csv file containing new Hindi sentences based on a student's existing vocabulary,
    Imagine you are a Hindi teacher, helping a native English speaker who has just started learning Hindi. 
    So far the student has learned the following words, which we can call the 'learned words':
    
    Today the student is trying to learn the following words, which we can call the 'new words':
       
    Please generate 100 new Hindi sentences that meet all of the following criteria:
    - Each sentence includes _exactly one_ of the 'new words', no more and no less;
    - All of the other words in each sentence (besides the one 'new word') must already appear in the 'learned words'. 
    However, for verbs that appear in 'learned words' you can use conjugations of those verbs that don't appear in 'learned words'. 
    Likewise, for nouns and adjectives in 'learned words' you can include gender versions that don't appear in 'learned words' yet. 

    The output format of the new sentences you generate should be a .csv with a column for the Hindi sentence, 
    a column for the English translation, and a column specifying which of the 'new words' you've included in that sentence. 
    
    Remember; you must include exactly _one_ of the 'new words' in each sentence, and the rest of the words must all already be present in the 'learned words', except for the exceptions I mentioned above.

    """
    temperature=1,
    max_tokens=64,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0
  )