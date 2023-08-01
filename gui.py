import tkinter as tk
import pandas as pd
from pandastable import Table
from PIL import ImageTk, Image
from google_api_functions import *
from openai_api_functions import * 
from anki_connect_functions import * 
from data_cleaning_functions import * 
from sqlite_functions import * 

def generate_sentences():
    
    # Load known and unknown cards from Anki
    known_vocab = load_known_vocab()
    new_vocab = load_new_vocab()
    
    # Remove any words that already exist in known vocab
    new_vocab = new_vocab[~new_vocab.isin(known_vocab)]
    
    gpt_payload = gpt__generate_new_sentences(known_vocab, new_vocab, 10)
    gpt_payload_enhanced = evaluate_gpt_response(gpt_payload, known_vocab, new_vocab)
    gpt_payload_enhanced = flag_bad_sentences(gpt_payload_enhanced, "n+1 with rogue")

    # display the sentences
    display_sentences(gpt_payload_enhanced)

def display_sentences(df):
    table_frame = tk.Frame(root)
    table_frame.grid(row=1, column=0, columnspan=2, sticky='nsew')

    table = Table(table_frame, dataframe=df, showtoolbar=True, showstatusbar=True)
    table.show()

root = tk.Tk()
root.grid_rowconfigure(1, weight=1)  # make row 1 expandable
root.grid_columnconfigure(0, weight=1)  # make column 0 expandable
root.grid_columnconfigure(1, weight=1)  # make column 1 expandable

generate_button = tk.Button(root, text="Generate sentences", command=generate_sentences)
generate_button.grid(row=0, column=1)

# load spinner image
spinner_image = ImageTk.PhotoImage(Image.open("assets/loading.gif"))
# create label with spinner image, but don't grid it yet
spinner_label = tk.Label(root, image=spinner_image)

root.mainloop()
