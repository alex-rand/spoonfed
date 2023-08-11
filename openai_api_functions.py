import os
import openai
import pandas as pd
import numpy as np

def gpt__generate_new_sentences(known_words, new_words, n_sentences, model): 

  openai.api_key = os.getenv("OPENAI_API_KEY")

  # Join each list into a single string, with words separated by comma
  known_words_str = ", ".join(known_words)
  new_words_str = ", ".join(new_words)
  
  # Define the prompts for GPT
  system_prompt = "You are a helpful assistant."
    
  prompt =f"""
    
    I need your help to output a .csv file containing new Hindi sentences based on a student's existing vocabulary.
    Your output must be only a .csv file, with absolutely no other content. 
    
    Imagine you are a Hindi teacher, helping a native English speaker who has just started learning Hindi. 
    So far the student has learned the following words, which we can call the 'learned words', and are as follows:
    
    {known_words_str}
    
    Today the student is trying to learn the following words, which we can call the 'new words', and are as follows;
    
    {new_words_str}
       
    Please generate {n_sentences} new Hindi sentences and return them as a .csv file with a column titled 'sentence'. Each sentence must meet all of the following criteria:
    - Each sentence includes _exactly one_ of the 'new words' -- you are NOT ALLOWED to include more than one word from the list of 'new words';
    - All of the other words in each sentence (besides the exactly one 'new word') must already appear in the list of 'learned words';
    - Each sentence must include a subject, a verb, and an object.
    
    Please use correct grammar and formal sentence structure when writing the sentences.
    Include as many of the words from the list of 'learned words' as you can in each sentence while still respecting the rules I mentioned above.
    Always respect Hindi's standard subject-object-verb structure. 

    The output format of the new sentences you generate should be a .csv with a column for the Hindi sentence, 
    a column for the English translation, and a column specifying which of the 'new words' you've included in that sentence. 
    
    Remember: you must include exactly _one_ of the 'new words' in each sentence, and the rest of the words must all already be present in the 'learned words', except for the exceptions I mentioned above.
    The output MUST be a .csv file with one column exactly as specified above. 
    Do NOT say anything else, just output the raw .csv file and say nothing else.

    """
    
  messages = [
    {"role": "system", "content": f"{system_prompt}"},
    {"role": "user", "content": prompt},
  ]

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
  
  return generated_text
 
