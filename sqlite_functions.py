import sqlite3
import pandas as pd
from datetime import datetime

def append_to_database(db_name, dat):
    
    # Create the tables if they don't yet exist
    create_tables(db_name)

    # Append metadata to the database and return the run_id
    run_id = append_run_entry(db_name, datetime.now().isoformat())

    # Append the enhanced gpt outputs to the database
    append_sentences(dat, run_id, db_name)

# Function to create the tables if they don't already exist
def create_tables(db_name):
    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS runs
                     (run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      timestamp TEXT NOT NULL);''')
                      
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
                      FOREIGN KEY(run_id) REFERENCES runs(run_id));''')
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
            
# Append a few things to a 'metadata' table
def append_run_entry(db_file, timestamp):
    try:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute('''INSERT INTO runs(timestamp)
                     VALUES(?);''', (timestamp,))
        run_id = c.lastrowid
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.commit()
            conn.close()
    return run_id

# Append the enhanced GPT response
def append_sentences(gpt_response, run_id, db_name: str = 'database.db'):
    gpt_response['run_id'] = run_id
    with sqlite3.connect(db_name) as conn:
        gpt_response.to_sql('gpt_responses', conn, if_exists='append', index=True, index_label='sentence_order')

# Basic querying function for debugging
def query_db(db_name, query):
    with sqlite3.connect(db_name) as conn:
        df = pd.read_sql_query(query, conn)
    return df

