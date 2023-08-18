import sqlite3
import pandas as pd
from datetime import datetime

### The database is created right away, in gui.py
# Function to call the other functions below
def save_to_database(db_name, dat, gpt_model, audio_provider):

    # Append metadata to the database and return the run_id
    run_id = append_run_entry(db_name, datetime.now().isoformat(), gpt_model, audio_provider)

    # Append the enhanced gpt outputs to the database
    append_sentences(dat, run_id, db_name)
            
# Append a few things to a 'metadata' table
def append_run_entry(db_file, timestamp, gpt_model, audio_provider):
    try:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute('''INSERT INTO runs(timestamp, gpt_model, audio_provider)
                     VALUES(?, ?, ?);''', (timestamp, gpt_model, audio_provider))
        conn.commit()
        run_id = c.lastrowid
    except sqlite3.Error as e:
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

