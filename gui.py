import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
import json
import os

CONFIGURATIONS_FILE = "configurations.json"

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Main App")
  

        # Create the user config frame and pack it immediately
        self.create_user_config_frame()
        self.user_config_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Load the user configuration
        self.load_user_configuration()

        # Create the language config frame but don't pack it yet
        self.create_language_config_frame()

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
        
    def load_all_saved_users(self):
        if os.path.exists(CONFIGURATIONS_FILE):
            with open(CONFIGURATIONS_FILE, 'r') as f:
                all_configurations = json.load(f)
                user_profiles = list(all_configurations.get('user_configuration', {}).keys())
                self.saved_users_dropdown["values"] = user_profiles

    def proceed_with_selected_user(self):
        selected_user = self.saved_users_var.get()
        if selected_user:
            # Set the user configuration and proceed to the language config screen
            self.set_user_configuration(selected_user)
            self.user_config_frame.pack_forget()
            self.language_config_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    def add_new_user(self):
        new_user = simpledialog.askstring("Input", "Enter new user profile name:")
        if new_user:
            # Update the configurations file immediately
            self.set_user_configuration(new_user)
            # Refresh the dropdown with the updated users list
            self.load_all_saved_users()

    def set_user_configuration(self, user_name):
        if os.path.exists(CONFIGURATIONS_FILE):
            with open(CONFIGURATIONS_FILE, 'r') as f:
                all_configurations = json.load(f)
        else:
            all_configurations = {}

        # Update the user configuration
        user_config = all_configurations.get('user_configuration', {})
        user_config[user_name] = {' ': user_name}
        all_configurations['user_configuration'] = user_config

        with open(CONFIGURATIONS_FILE, 'w') as f:
            json.dump(all_configurations, f)
        
    def create_language_config_frame(self):
        self.language_config_frame = tk.Frame(self.root)
        
        # Configure the language_config_frame's rows and columns
        for i in range(5):  # Assuming 5 rows
            self.language_config_frame.rowconfigure(i, weight=1)
        self.language_config_frame.columnconfigure(0, weight=1)
        self.language_config_frame.columnconfigure(1, weight=1)

        tk.Label(self.language_config_frame, text="Language Configuration", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)

        self.configuration_var = tk.StringVar(self.root)
        self.dropdown = ttk.Combobox(self.language_config_frame, textvariable=self.configuration_var)
        self.load_language_configurations_to_dropdown()
        self.dropdown.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")

        tk.Button(self.language_config_frame, text="Add New Configuration", command=self.add_new_configuration).grid(row=2, column=0, pady=10)
        tk.Button(self.language_config_frame, text="Delete Configuration", command=self.delete_configuration).grid(row=2, column=1, pady=10)
        tk.Button(self.language_config_frame, text="Execute", command=self.execute_load_vocab).grid(row=3, columnspan=2, pady=10)
        
        # Back button to return to the user config screen
        tk.Button(self.language_config_frame, text="Back", command=self.back_to_user_config).grid(row=4, columnspan=2, pady=10)

    def back_to_user_config(self):
        self.language_config_frame.pack_forget()
        self.user_config_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    def load_user_configuration(self):
        if os.path.exists(CONFIGURATIONS_FILE):
            with open(CONFIGURATIONS_FILE, 'r') as f:
                all_configurations = json.load(f)
                user_configuration = all_configurations.get('user_configuration', {})
                anki_profile_name = user_configuration.get('anki_profile_name', "")
                self.saved_users_var.set(anki_profile_name)

    def save_user_configuration(self):
        if os.path.exists(CONFIGURATIONS_FILE):
            with open(CONFIGURATIONS_FILE, 'r') as f:
                all_configurations = json.load(f)
        else:
            all_configurations = {}
        
        # Use the saved_users_var value instead of the anki_profile_entry
        all_configurations['user_configuration'] = {
            'anki_profile_name': self.saved_users_var.get()
        }

        with open(CONFIGURATIONS_FILE, 'w') as f:
            json.dump(all_configurations, f)
            
        self.user_config_frame.pack_forget()  # Hide user configuration frame   
        self.user_config_frame.pack_forget()
        self.language_config_frame.pack(pady=10, fill=tk.BOTH, expand=True)


    def load_language_configurations_to_dropdown(self):
        if os.path.exists(CONFIGURATIONS_FILE):
            with open(CONFIGURATIONS_FILE, 'r') as f:
                all_configurations = json.load(f)
                self.language_configurations = all_configurations.get("language_configurations", {})
            self.dropdown["values"] = list(self.language_configurations.keys())
        else:
            self.language_configurations = {}

    def add_new_configuration(self):
        self.new_window = tk.Toplevel(self.root)
        VocabApp(self.new_window, self)
        
    def load_language_configuration_screen(self):
        language_config_frame = tk.Frame(self.root)
        language_config_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        tk.Label(language_config_frame, text="Language Configuration", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)

        self.configuration_var = tk.StringVar(self.root)
        self.dropdown = ttk.Combobox(language_config_frame, textvariable=self.configuration_var)
        self.load_language_configurations_to_dropdown()
        self.dropdown.grid(row=1, column=0, columnspan=2, pady=10)

        tk.Button(language_config_frame, text="Add New Configuration", command=self.add_new_configuration).grid(row=2, column=0, pady=10)
        tk.Button(language_config_frame, text="Delete Configuration", command=self.delete_configuration).grid(row=2, column=1, pady=10)
        tk.Button(language_config_frame, text="Execute", command=self.execute_load_vocab).grid(row=3, columnspan=2, pady=10)

    def execute_load_vocab(self):
        # This function can be used to execute some operation based on the selected language configuration
        selected_language_configuration = self.language_configurations[self.configuration_var.get()]
        
        # Extract details and process them as needed
        # For example:
        known_deck_details = selected_language_configuration["learned_deck"]
        new_deck_details = selected_language_configuration["new_deck"]

        # You can continue with the rest of the operations you had in the original function
        
    def edit_configuration(self):
        # Get the selected language configuration
        selected_language_configuration = self.language_configurations[self.configuration_var.get()]
        if selected_language_configuration:
            # Open the VocabApp window with prefilled values
            edit_window = tk.Toplevel(self.root)
            edit_app = VocabApp(edit_window, self, selected_language_configuration)

    def delete_configuration(self):
        # Confirm the deletion
        answer = tk.messagebox.askyesno("Delete Configuration", "Are you sure you want to delete this language configuration?")
        if answer:
            del self.language_configurations[self.configuration_var.get()]
            
            # Update the configurations file
            if os.path.exists(CONFIGURATIONS_FILE):
                with open(CONFIGURATIONS_FILE, 'r') as f:
                    all_configurations = json.load(f)
                all_configurations["language_configurations"] = self.language_configurations
                
                with open(CONFIGURATIONS_FILE, 'w') as f:
                    json.dump(all_configurations, f)
            
            self.load_language_configurations_to_dropdown()
            
class VocabApp:
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
        tk.Button(root, text="Save Configuration", command=self.save_configuration).grid(row=1, columnspan=2, pady=20)

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

    def save_configuration(self):
        configuration_name = simpledialog.askstring("Input", "Enter name for this configuration:")
        if configuration_name:
            learned_card_types_and_fields = {card.get(): field.get().split(", ") for card, field in zip(self.learned_card_entries, self.learned_field_entries)}
            new_card_types_and_fields = {card.get(): field.get().split(", ") for card, field in zip(self.new_card_entries, self.new_field_entries)}

            self.main_app.configurations[configuration_name] = {
                "learned_deck": {
                    "deck_name": self.learned_deck_entry.get(),
                    "card_types_and_fields": learned_card_types_and_fields
                },
                "new_deck": {
                    "deck_name": self.new_deck_entry.get(),
                    "card_types_and_fields": new_card_types_and_fields
                }
            }

            with open(CONFIGURATIONS_FILE, 'w') as f:
                json.dump(self.main_app.configurations, f)
            self.main_app.load_configurations_to_dropdown()
            self.root.destroy()


root = tk.Tk()
app = MainApp(root)
root.mainloop()
