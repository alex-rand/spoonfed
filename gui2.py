import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
import os
import sqlite3
import json
import urllib.request
import urllib.error
import re

# Main Application Class
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Main App")
        
        # Initialize the SQLite database
        self.setup_database()

        self.selected_user_id = None

        # Tell the app what frames exist. These are all classes we define below
        # representing different screens in the UX.
        self.frames = {}
        for F in (UserConfigFrame, LanguageConfigFrame, DeckDisplayFrame):
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

        # Create table for language configurations
        c.execute('''CREATE TABLE IF NOT EXISTS languages
                     (id INTEGER PRIMARY KEY, user_id INTEGER, configuration_name TEXT,
                     learned_deck TEXT, learned_deck_cards TEXT, learned_deck_fields TEXT, 
                     new_deck TEXT, new_deck_cards TEXT, new_deck_fields TEXT,
                     FOREIGN KEY(user_id) REFERENCES users(id))''')

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
       
# User Configuration Frame
class UserConfigFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_user_config_frame()
        self.load_all_saved_users()

    ### Create a window for selecting the user
    def create_user_config_frame(self):
        # Grid configuration
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        tk.Label(self, text="User Configuration", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)
        
        self.anki_profile_label = tk.Label(self, text="Anki Profile:")
        self.anki_profile_label.grid(row=1, column=0, sticky='w', padx=10, pady=5)
        
        # Dropdown for saved user profiles
        self.saved_users_var = tk.StringVar(self.controller)  # Use self.controller here
        self.saved_users_dropdown = ttk.Combobox(self, textvariable=self.saved_users_var)
        self.saved_users_dropdown.grid(row=1, column=1, padx=10, pady=5)

        # Button to select the user and proceed
        tk.Button(self, text="Continue", command=self.proceed_with_selected_user).grid(row=3, column=0, columnspan=2, pady=10)

        # Button to add a new user
        tk.Button(self, text="Add New User", command=self.add_new_user).grid(row=4, column=0, columnspan=2, pady=10)
    
    ### Populate a picklist with all existing user names in the database
    def load_all_saved_users(self):
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("SELECT profile_name FROM users")
        user_profiles = [row[0] for row in c.fetchall()]

        self.saved_users_dropdown["values"] = user_profiles    
        conn.close()

    ### Create a new user and append to the database
    def add_new_user(self):
        new_user = simpledialog.askstring("Input", "Enter new user profile name:")
        if new_user:
            # Update the configurations file immediately
            self.set_user_configuration(new_user)
            # Refresh the dropdown with the updated users list
            self.load_all_saved_users()

    def set_user_configuration(self, user_name):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # Insert or ignore (in case of duplicate profile_name)
        c.execute("INSERT OR IGNORE INTO users (profile_name) VALUES (?)", (user_name,))
        conn.commit()

        # Get the user ID of the selected/added user
        c.execute("SELECT id FROM users WHERE profile_name=?", (user_name,))
        self.selected_user_id = c.fetchone()[0]

        conn.close()
        
    ### Once a user is selected, proceed to the Configurations window
    def proceed_with_selected_user(self):
        selected_user = self.saved_users_var.get()
        if selected_user:
            # Set the user configuration and proceed to the language config screen
            self.set_user_configuration(selected_user)
            
            # Move to the Language Configuration frame
            self.controller.show_frame(LanguageConfigFrame)
            
# Language Configuration Frame
class LanguageConfigFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_language_config_frame()
        
    ### Create the language configurations window
    def create_language_config_frame(self):
        # Configure the outer rows and columns to absorb extra space
        self.rowconfigure(0, weight=1)
        self.rowconfigure(6, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(3, weight=1)

        # Create the label for "Language Configuration" in the center rows/columns
        tk.Label(self, text="Language Configuration", font=("Arial", 16)).grid(row=1, column=1, columnspan=2, pady=10)

        # Create the dropdown (combobox) for language configurations
        self.configuration_var = tk.StringVar(self.controller)
        self.dropdown = ttk.Combobox(self, textvariable=self.configuration_var)
        self.dropdown.grid(row=2, column=1, columnspan=2, pady=10, sticky="ew")

        # Create the "Add New Configuration" button
        tk.Button(self, text="Add New Configuration", command=self.add_new_configuration).grid(row=3, column=1, pady=10)

        # Create the "Delete Configuration" button
        tk.Button(self, text="Delete Configuration", command=self.delete_language_configuration).grid(row=3, column=2, pady=10)

        # Create the "Execute" button
        tk.Button(self, text="Load Decks", command=self.execute_ankiconnect).grid(row=4, column=1, columnspan=2, pady=10)

        # Create the "Back" button to return to the user config screen
        tk.Button(self, text="Back", command=self.back_to_user_config).grid(row=5, column=1, columnspan=2, pady=10)

    ### Go back to User Configuration window
    def back_to_user_config(self):
        self.controller.show_frame(UserConfigFrame)

    def load_language_configurations_to_dropdown(self):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # Access selected_user_id from the MainApp instance
        c.execute("SELECT configuration_name FROM languages WHERE user_id=?", (self.controller.selected_user_id,))
        configurations = [row[0] for row in c.fetchall()]
        self.dropdown["values"] = configurations

        if self.dropdown["values"]:
            self.configuration_var.set(self.dropdown["values"][0])
        else:
            self.configuration_var.set('')

        conn.close()

    def add_new_configuration(self):
        self.new_window = tk.Toplevel(self.controller)
        NewLanguageConfigurationWindow(self.new_window, self.controller, self)


    def delete_language_configuration(self):
        # Confirm the deletion
        answer = tk.messagebox.askyesno("Delete Configuration", "Are you sure you want to delete this language configuration?")
        if answer:
            configuration_name = self.configuration_var.get()
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
    
            try:
                # Delete the selected language configuration from the database
                c.execute("DELETE FROM languages WHERE configuration_name=? AND user_id=?", (configuration_name, self.selected_user_id))
                conn.commit()
            except sqlite3.Error as e:
                print(f"Error deleting configuration from database: {e}")
            finally:
                conn.close()
        
        # Refresh the dropdown to reflect the change
        print("NOW!")
        self.load_language_configurations_to_dropdown()

        # Set the selected value of the dropdown to the next available value
        if self.dropdown["values"]:
            self.configuration_var.set(self.dropdown["values"][0])
        else:
            self.configuration_var.set('')
            
    def tkraise(self, aboveThis=None):
        super().tkraise(aboveThis)
        self.load_language_configurations_to_dropdown()
        
    def execute_ankiconnect(self):
        self.controller.show_frame(DeckDisplayFrame)
            
##### This class implements the logic for adding a new language configuration to a user profile
class NewLanguageConfigurationWindow:
    def __init__(self, root, main_app, lang_config_frame):
        self.root = root
        self.main_app = main_app
        self.lang_config_frame = lang_config_frame  
        self.root.title("Add New Configuration")

        # Learned vocab section
        self.learned_frame = tk.LabelFrame(root, text="Learned Vocab", padx=10, pady=10)
        self.learned_frame.grid(row=0, column=0, padx=10, pady=10)

        tk.Label(self.learned_frame, text="Deck Name").pack(pady=5)
        self.learned_deck_entry = tk.Entry(self.learned_frame, width=30)
        self.learned_deck_entry.pack(pady=5)

        # Dynamic form for learned card types and fields
        self.learned_card_entries = []
        self.learned_field_entries = []
        self.add_learned_card_button = tk.Button(self.learned_frame, text="Add Card Type & Fields", command=self.add_learned_card_field)
        self.add_learned_card_button.pack(pady=10)

        # New vocab section
        self.new_frame = tk.LabelFrame(root, text="New Vocab", padx=10, pady=10)
        self.new_frame.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.new_frame, text="Deck Name").pack(pady=5)
        self.new_deck_entry = tk.Entry(self.new_frame, width=30)
        self.new_deck_entry.pack(pady=5)

        # Dynamic form for new card types and fields
        self.new_card_entries = []
        self.new_field_entries = []
        self.add_new_card_button = tk.Button(self.new_frame, text="Add Card Type & Fields", command=self.add_new_card_field)
        self.add_new_card_button.pack(pady=10)

        # Save Button
        tk.Button(root, text="Save Configuration", command=self.save_language_configuration).grid(row=1, columnspan=2, pady=20)

    def add_learned_card_field(self):
        frame = tk.Frame(self.learned_frame)
        frame.pack(pady=5, fill=tk.X)

        tk.Label(frame, text="Card Type:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        card_entry = tk.Entry(frame, width=20)
        card_entry.grid(row=0, column=1, padx=5, pady=5)
        self.learned_card_entries.append(card_entry)

        tk.Label(frame, text="Fields (comma separated):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        field_entry = tk.Entry(frame, width=20)
        field_entry.grid(row=1, column=1, padx=5, pady=5)
        self.learned_field_entries.append(field_entry)

    def add_new_card_field(self):
        frame = tk.Frame(self.new_frame)
        frame.pack(pady=5, fill=tk.X)

        tk.Label(frame, text="Card Type:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        card_entry = tk.Entry(frame, width=20)
        card_entry.grid(row=0, column=1, padx=5, pady=5)
        self.new_card_entries.append(card_entry)

        tk.Label(frame, text="Fields (comma separated):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        field_entry = tk.Entry(frame, width=20)
        field_entry.grid(row=1, column=1, padx=5, pady=5)
        self.new_field_entries.append(field_entry)

    def save_language_configuration(self):
        configuration_name = simpledialog.askstring("Input", "Enter name for this configuration:")
        if configuration_name:
            
            # Load all the user inputs
            learned_deck = self.learned_deck_entry.get()
            learned_deck_cards = ','.join([entry.get() for entry in self.learned_card_entries])
            learned_deck_fields = ','.join([entry.get() for entry in self.learned_field_entries])
            new_deck = self.new_deck_entry.get()
            new_deck_cards = ','.join([entry.get() for entry in self.new_card_entries])
            new_deck_fields = ','.join([entry.get() for entry in self.new_field_entries])
            
            # Connect to the database and append all the info
            conn = sqlite3.connect('database.db')
            c = conn.cursor()

            try:
                # Use self.main_app.selected_user_id to insert the new configuration
                c.execute("INSERT INTO languages (user_id, configuration_name, learned_deck, learned_deck_cards, learned_deck_fields, new_deck, new_deck_cards, new_deck_fields) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                          (self.main_app.selected_user_id, configuration_name, learned_deck, learned_deck_cards, learned_deck_fields, new_deck, new_deck_cards, new_deck_fields))

                conn.commit()
            except sqlite3.Error as e:
                print(f"Error saving configuration to database: {e}")
            finally:
                conn.close()

            # Refresh dropdown in LanguageConfigFrame
            self.lang_config_frame.load_language_configurations_to_dropdown()

            self.root.destroy()
            
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