import tkinter as tk
import os
import sqlite3
from user_config import UserConfigFrame
from language_config import LanguageConfigFrame
from decks_homepage import DecksHomepage
from iplusone import IPlusOneFrame

# Main Application Class
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Main App")
        
        # Initialize the SQLite database
        self.setup_database()

        # Initialize some 'global' variables to be made available across all frames of the app
        self.selected_user_id = None
        self.learned_deck_tokens = [],
        self.new_deck_tokens = []

        # Tell the app what frames exist. These are all classes we define below
        # representing different screens in the UX.
        self.frames = {}
        for F in (UserConfigFrame, LanguageConfigFrame, DecksHomepage, IPlusOneFrame):
            frame = F(parent=self, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        # Start by showing the first frame
        self.show_frame(UserConfigFrame)

    def show_frame(self, page_class):
        frame = self.frames[page_class]
        frame.tkraise()

    def setup_database(self):
        db_name = 'database.db'

        # Check if the database already exists
        if os.path.exists(db_name):
            return

        conn = sqlite3.connect(db_name)
        c = conn.cursor()

        # Create table for user configurations
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY, profile_name TEXT UNIQUE)''')

        # Create tables for language configurations
        c.execute('''
            CREATE TABLE IF NOT EXISTS language_configurations (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                configuration_name TEXT,
                configuration_language TEXT,
                learned_deck TEXT,
                new_deck TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS card_types (
                card_type_id INTEGER PRIMARY KEY,
                configuration_id INTEGER,
                card_type_name TEXT,
                FOREIGN KEY(configuration_id) REFERENCES language_configurations(id)
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS card_fields (
                field_id INTEGER PRIMARY KEY,
                card_type_id INTEGER,
                field_name TEXT,
                FOREIGN KEY(card_type_id) REFERENCES card_types(card_type_id)
            )
        ''')
        
        
        # Create table for runs
        c.execute('''CREATE TABLE IF NOT EXISTS runs
                     (run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      timestamp TEXT NOT NULL,
                      gpt_model TEXT,
                      audio_provider TEXT,
                      language_id INTEGER,
                      FOREIGN KEY(language_id) REFERENCES languages(id))''')

        # Create table for gpt_responses
        c.execute('''CREATE TABLE IF NOT EXISTS gpt_responses
                     (run_id INTEGER,
                      n_sentences INTEGER,
                      sentence_order INTEGER,
                      sentence TEXT,
                      translation TEXT,
                      new_word TEXT,
                      n_words INTEGER,
                      n_known_words INTEGER,
                      n_new_words INTEGER,
                      n_rogue_words INTEGER,
                      filter_condition TEXT,
                      meets_criteria BOOLEAN,
                      FOREIGN KEY(run_id) REFERENCES runs(run_id))''')

        conn.commit()
        conn.close()
       

class DeckDisplayFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
  #      self.create_deck_display_frame()

  #  def create_deck_display_frame(self):
        # Create and pack the scrollable tables for the 'learned' and 'new' decks
   #     self.learned_deck_table = self.create_scrollable_table("Learned Deck")
    #    self.new_deck_table = self.create_scrollable_table("New Deck")

        # Load the data for each table
 #       self.load_deck_data()
#
#    def create_scrollable_table(self, title):
#        frame = tk.LabelFrame(self, text=title)
#        frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
#
#        # Create a treeview with scrollbars
#        tree = ttk.Treeview(frame)
#        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
#        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
#        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
#
#        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
#        vsb.pack(side=tk.RIGHT, fill=tk.Y)
#        hsb.pack(side=tk.BOTTOM, fill=tk.X)
#
#        return tree
#
#    def load_deck_data(self):
#        # Load the 'learned' deck data
#        learned_data = load_vocab_from_deck(self.config['learned_deck'], self.config['learned_deck_cards'])
#        self.populate_table(self.learned_deck_table, learned_data)
#
#        # Load the 'new' deck data
#        new_data = load_vocab_from_deck(self.config['new_deck'], self.config['new_deck_cards'])
#        self.populate_table(self.new_deck_table, new_data)
#
#    def populate_table(self, table, data):
#        # Clear existing data
#        for i in table.get_children():
#            table.delete(i)
#        
#        # Populate the table with new data
#        for item in data:
#            table.insert('', 'end', values=item)
#    
#    def request(action, **params):
#        return {'action': action, 'params': params, 'version': 6}
#
#    # Function to send requests to Ankiconnect
#    def ankiconnect_invoke(action, **params):
#        requestJson = json.dumps(request(action, **params)).encode('utf-8')
#        try:
#            response = json.load(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8765', requestJson)))
#        except urllib.error.URLError as e:
#            raise Exception("Failed to establish connection with Anki. Make sure you have Anki open on your desktop.") from e
#        if len(response) != 2:
#            raise Exception('response has an unexpected number of fields')
#        if 'error' not in response:
#            raise Exception('response is missing required error field')
#        if 'result' not in response:
#            raise Exception('response is missing required result field')
#        if response['error'] is not None:
#            raise Exception(response['error'])
#        return response['result']
#
#
#    def load_vocab_from_deck(deck, card_types_and_fields):
#        """
#        Load vocabulary words from Anki cards based on specified deck, card types, and fields.
#
#        Parameters:
#        - deck (str): The name of the Anki deck.
#        - card_types_and_fields (dict): A dictionary where keys are card types and values are lists of fields.
#
#        Returns:
#        - pd.Series: A series of unique vocabulary words.
#        """
#
#        all_words = []
#
#        for card_type, fields in card_types_and_fields.items():
#            # Construct the query for the card type
#            query = f'"deck:{deck}" "note:{card_type}"'
#
#            # Retrieve note IDs for the card type
#            note_ids = ankiconnect_invoke('findNotes', query=query)
#
#            # Retrieve note content for the card type
#            note_content = pd.json_normalize(ankiconnect_invoke('notesInfo', notes=note_ids))
#
#            # Remove non-Devanagari text for all specified fields
#            for field in fields:
#                col_name = f"fields.{field}.value"
#                if col_name in note_content.columns:
#                    note_content[col_name] = note_content[col_name].astype(str).apply(remove_non_devanagari)
#
#            # Extract words from all specified fields
#            for field in fields:
#                col_name = f"fields.{field}.value"
#                if col_name in note_content.columns:
#                    words = (note_content[col_name].str.split(expand=True)
#                             .stack()
#                             .reset_index(level=1, drop=True))
#                    all_words.append(words)
#
#        # Combine all words and remove duplicates
#        combined = pd.concat(all_words, ignore_index=True).drop_duplicates(keep='first')
#
#        return combined
#
#    def remove_non_devanagari(text):
#        pattern = "[^\u0900-\u097F \n]"
#        return re.sub(pattern, '', text)
#
#    def create_new_card(dat, gpt_model, audio_provider):
#
#        # The AnkiConnect API needs a particular nestest structure to create a new note, 
#        # as documented under 'addNote' here: https://github.com/FooSoft/anki-connect 
#
#        # Define the fields for the Anki card
#        fields = {
#            'Front': dat['sentence'],
#            'Back': dat['translation'],
#            'Definition': dat['audio']
#        }
#
#        # Structure the note according to AnkiConnect's requirements
#        note = {
#            'deckName': "देवनागरी::मैंने सीखा",
#            'modelName': "Basic-10b04",
#            'fields': fields,
#            'tags': ["spoonfed", gpt_model, audio_provider]
#        }
#    
#        # Call
#        ankiconnect_invoke('addNote', note=note)


# Running the Application
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()