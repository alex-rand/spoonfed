import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
import os
import sqlite3

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Main App")
        
        # Initialize the SQLite database and tables if they don't exist
        self.setup_database()
        
        self.selected_user_id = None  # This will store the ID of the selected user

        # Create the user config frame and pack it immediately
        self.create_user_config_frame()
        self.load_all_saved_users()  # Call the function here
        self.user_config_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
    
        # Create the language config frame but don't pack it yet
        self.create_language_config_frame()
        
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

    ##### USER CONFIGURATION
    
    ### Create a window for selecting the user
    def create_user_config_frame(self):
        self.user_config_frame = tk.Frame(self.root)
        
        # Let the row and column of the main frame expand
        self.user_config_frame.grid_rowconfigure(0, weight=1)
        self.user_config_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(self.user_config_frame, text="User Configuration", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)
        
        self.anki_profile_label = tk.Label(self.user_config_frame, text="Anki Profile:")
        self.anki_profile_label.grid(row=1, column=0, sticky='w', padx=10, pady=5)
                
        # Dropdown for saved user profiles
        self.saved_users_var = tk.StringVar(self.root)
        self.saved_users_dropdown = ttk.Combobox(self.user_config_frame, textvariable=self.saved_users_var)
        self.saved_users_dropdown.grid(row=1, column=1, padx=10, pady=5)


        # Button to select the user and proceed
        tk.Button(self.user_config_frame, text="Select User and Proceed", command=self.proceed_with_selected_user).grid(row=3, column=0, columnspan=2, pady=10)

        # Button to add a new user
        tk.Button(self.user_config_frame, text="Add New User", command=self.add_new_user).grid(row=4, column=0, columnspan=2, pady=10)
    
    ### Populate a picklist with all existing user names in the database
    def load_all_saved_users(self):
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("SELECT profile_name FROM users")
        user_profiles = [row[0] for row in c.fetchall()]

        self.saved_users_dropdown["values"] = user_profiles    
        conn.close()
            
    ### Once a user is selected, proceed to the Configurations window
    def proceed_with_selected_user(self):
        selected_user = self.saved_users_var.get()
        if selected_user:
            # Set the user configuration and proceed to the language config screen
            self.set_user_configuration(selected_user)
            self.user_config_frame.pack_forget()
            self.language_config_frame.pack(pady=10, fill=tk.BOTH, expand=True)
            
            # Load the configurations into the dropdown
            self.load_language_configurations_to_dropdown()

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
    
    ##### LANGUAGE CONFIGURATION

    ### Create the language configurations window
    def create_language_config_frame(self):
        
        self.language_config_frame = tk.Frame(self.root)

        # Configure the outer rows and columns to absorb extra space
        self.language_config_frame.rowconfigure(0, weight=1)
        self.language_config_frame.rowconfigure(6, weight=1)
        self.language_config_frame.columnconfigure(0, weight=1)
        self.language_config_frame.columnconfigure(3, weight=1)

        # Create the label for "Language Configuration" in the center rows/columns
        tk.Label(self.language_config_frame, text="Language Configuration", font=("Arial", 16)).grid(row=1, column=1, columnspan=2, pady=10)

        # Create the dropdown (combobox) for language configurations
        self.configuration_var = tk.StringVar(self.root)
        self.dropdown = ttk.Combobox(self.language_config_frame, textvariable=self.configuration_var)
        self.load_language_configurations_to_dropdown()
        self.dropdown.grid(row=2, column=1, columnspan=2, pady=10, sticky="ew")

        # Create the "Add New Configuration" button
        tk.Button(self.language_config_frame, text="Add New Configuration", command=self.add_new_configuration).grid(row=3, column=1, pady=10)

        # Create the "Delete Configuration" button
        tk.Button(self.language_config_frame, text="Delete Configuration", command=self.delete_language_configuration).grid(row=3, column=2, pady=10)

        # Create the "Execute" button
        tk.Button(self.language_config_frame, text="Load Decks", command=self.load_decks).grid(row=4, column=1, columnspan=2, pady=10)

        # Create the "Back" button to return to the user config screen
        tk.Button(self.language_config_frame, text="Back", command=self.back_to_user_config).grid(row=5, column=1, columnspan=2, pady=10)

    ### Go back to User Configuration window
    def back_to_user_config(self):
        self.language_config_frame.pack_forget()
        self.user_config_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    def load_language_configurations_to_dropdown(self):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # Fetch language configurations specific to the selected user
        c.execute("SELECT configuration_name FROM languages WHERE user_id=?", (self.selected_user_id,))
        configurations = [row[0] for row in c.fetchall()]
        self.dropdown["values"] = configurations
        
        # Set the selected value of the dropdown to the next available value
        if self.dropdown["values"]:
            self.configuration_var.set(self.dropdown["values"][0])
        else:
            self.configuration_var.set('')

        conn.close()

    def add_new_configuration(self):
        self.new_window = tk.Toplevel(self.root)
        LanguageConfigurationWindow(self.new_window, self)
        
    def load_decks(self):
        print("YEAH!!")
        self.new_window = tk.Toplevel(self.root)
        DecksLandingWindow(self.new_window, self)
        
        # This function can be used to execute some operation based on the selected language configuration
        selected_language_configuration = self.language_configurations[self.configuration_var.get()]
        
        # Extract details and process them as needed
        # For example:
        known_deck_details = selected_language_configuration["learned_deck"]
        new_deck_details = selected_language_configuration["new_deck"]


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
        self.load_language_configurations_to_dropdown()

        # Set the selected value of the dropdown to the next available value
        if self.dropdown["values"]:
            self.configuration_var.set(self.dropdown["values"][0])
        else:
            self.configuration_var.set('')
        
##### This class implements the logic for adding a new language configuration to a user profile
class LanguageConfigurationWindow:
    def __init__(self, root, main_app):
        self.root = root
        self.main_app = main_app
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
                # Insert new language configuration
                c.execute("INSERT INTO languages (user_id, configuration_name, learned_deck, learned_deck_cards, learned_deck_fields, new_deck, new_deck_cards, new_deck_fields) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                          (self.main_app.selected_user_id, configuration_name, learned_deck, learned_deck_cards, learned_deck_fields, new_deck, new_deck_cards, new_deck_fields))

                conn.commit()
            except sqlite3.Error as e:
                print(f"Error saving configuration to database: {e}")
            finally:
                conn.close()

        # After saving the new configuration, refresh the dropdown in the main app
        self.main_app.load_language_configurations_to_dropdown()

        self.root.destroy()

class DecksLandingWindow:
    def __init__(self, root, main_app):
        self.root = root
        self.main_app = main_app
        self.root.title("Current Decks")
        self.user_config_frame.pack_forget()
        
    def load_decks(self):
        # Fetch user's configuration for 'learned' and 'new' decks
        learned_deck = self.main_app.learned_deck_entry.get()
        learned_deck_config = ','.join([entry.get() for entry in self.main_app.learned_card_entries]) + ',' + ','.join([entry.get() for entry in self.main_app.learned_field_entries])
        new_deck = self.main_app.new_deck_entry.get()
        new_deck_config = ','.join([entry.get() for entry in self.main_app.new_card_entries]) + ',' + ','.join([entry.get() for entry in self.main_app.new_field_entries])

        # Load data from Anki
        learned_data = self.load_vocab_from_deck(learned_deck, learned_deck_config)
        new_data = self.load_vocab_from_deck(new_deck, new_deck_config)

        # Create and display the data in a new window
        self.display_decks(learned_data, new_data)

 #
 # def load_vocab_from_deck(self, deck_name, card_types_and_fields_str):
        # Your existing logic to load vocabulary from Anki
        # ...

   # def display_decks(self, learned_data, new_data):
   #     # Create a new window
   #     new_window = tk.Toplevel(self.main_app.root)
   #     new_window.title("Deck Information")
#
   #     # Create scrollable tables for the loaded data
   #     self.create_scrollable_table(new_window, learned_data, "Learned Deck", 0)
   #     self.create_scrollable_table(new_window, new_data, "New Deck", 1)
#
   # def create_scrollable_table(self, window, data, title, column):
   #     # Your existing logic to create a scrollable table
        # ...
        
root = tk.Tk()
app = MainApp(root)
root.mainloop()
