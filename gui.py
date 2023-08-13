import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
import json
import os
from anki_connect_functions import * 

CONFIGURATIONS_FILE = "configurations.json"

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Main App")

        # Dropdown for configurations
        tk.Label(root, text="Select Configuration").pack(pady=10)
        self.configuration_var = tk.StringVar(root)
        self.dropdown = ttk.Combobox(root, textvariable=self.configuration_var)
        self.load_configurations_to_dropdown()
        self.dropdown.pack(pady=10)

        # Configurations buttons
        tk.Button(root, text="Add New Configuration", command=self.add_new_configuration).pack(pady=10)
        tk.Button(root, text="Delete Configuration", command=self.delete_configuration).pack(pady=5)

        # Execute Button
        tk.Button(root, text="Execute", command=self.execute_load_vocab).pack(pady=10)

        # Text areas for displaying the vocab lists
        self.known_vocab_text = tk.Text(root, width=50, height=15)
        self.known_vocab_text.pack(padx=10, pady=10, side=tk.LEFT)

        self.new_vocab_text = tk.Text(root, width=50, height=15)
        self.new_vocab_text.pack(padx=10, pady=10, side=tk.RIGHT)

    ### CONFIGURATIONS FUNCTIONS
    def load_configurations_to_dropdown(self):
        if os.path.exists(CONFIGURATIONS_FILE):
            with open(CONFIGURATIONS_FILE, 'r') as f:
                self.configurations = json.load(f)
            self.dropdown["values"] = list(self.configurations.keys())
        else:
            self.configurations = {}

    def add_new_configuration(self):
        self.new_window = tk.Toplevel(self.root)
        VocabApp(self.new_window, self)
        
    ### ANKI LOADING FUNCTIONS
    def execute_load_vocab(self):
        # Extract the selected configuration details
        selected_configuration = self.configurations[self.configuration_var.get()]
        known_deck_details = selected_configuration["learned_deck"]
        new_deck_details = selected_configuration["new_deck"]

        known_vocab_deck = known_deck_details["deck_name"]
        known_card_types_and_fields = known_deck_details["card_types_and_fields"]

        new_vocab_deck = new_deck_details["deck_name"]
        new_card_types_and_fields = new_deck_details["card_types_and_fields"]

        print(known_card_types_and_fields)
        # Call the load_vocab_from_deck function
        known_vocab = load_vocab_from_deck(known_vocab_deck, known_card_types_and_fields)
        new_vocab = load_vocab_from_deck(new_vocab_deck, new_card_types_and_fields)
        
        # Make sure there's no overlap between the known and new vocab lists by mistake
        new_vocab = new_vocab[~new_vocab.isin(known_vocab)]

        # Display the number of words and vocab lists in the text areas
        self.known_vocab_text.delete(1.0, tk.END)  # Clear previous content
        self.known_vocab_text.insert(tk.END, f"Number of Words in Learned Vocab: {len(known_vocab)}\n\n")
        self.known_vocab_text.insert(tk.END, "\n".join(known_vocab))

        self.new_vocab_text.delete(1.0, tk.END)  # Clear previous content
        self.new_vocab_text.insert(tk.END, f"Number of Words in New Vocab: {len(new_vocab)}\n\n")
        self.new_vocab_text.insert(tk.END, "\n".join(new_vocab))

    def edit_configuration(self):
        # Get the selected configuration
        selected_configuration = self.configurations[self.configuration_var.get()]
        if selected_configuration:
            # Open the VocabApp window with prefilled values
            edit_window = tk.Toplevel(self.root)
            edit_app = VocabApp(edit_window, self, selected_configuration)

    def delete_configuration(self):
        # Confirm the deletion
        answer = tk.messagebox.askyesno("Delete Configuration", "Are you sure you want to delete this configuration?")
        if answer:
            del self.configurations[self.configuration_var.get()]
            with open(CONFIGURATIONS_FILE, 'w') as f:
                json.dump(self.configurations, f)
            self.load_configurations_to_dropdown()
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
            learned_card_types_and_fields = {card.get(): field.get().split(",") for card, field in zip(self.learned_card_entries, self.learned_field_entries)}
            new_card_types_and_fields = {card.get(): field.get().split(",") for card, field in zip(self.new_card_entries, self.new_field_entries)}

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
