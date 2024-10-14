# database.py
import sqlite3

def initialize_database():
    conn = sqlite3.connect('assistant.db')
    cursor = conn.cursor()

    # Create a table for frequently asked questions (FAQs)
    cursor.execute('''CREATE TABLE IF NOT EXISTS faq (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      question TEXT,
                      answer TEXT)''')

    # Create a table for user preferences
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_preferences (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      key TEXT UNIQUE,
                      value TEXT)''')

    # Create a table to log interactions
    cursor.execute('''CREATE TABLE IF NOT EXISTS interactions (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      command TEXT,
                      response TEXT,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    conn.commit()
    conn.close()

def add_faq(question, answer):
    conn = sqlite3.connect('assistant.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO faq (question, answer) VALUES (?, ?)", (question, answer))
    conn.commit()
    conn.close()

def get_faq(question):
    conn = sqlite3.connect('assistant.db')
    cursor = conn.cursor()
    cursor.execute("SELECT answer FROM faq WHERE question LIKE ?", ('%' + question + '%',))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

def log_interaction(command, response):
    conn = sqlite3.connect('assistant.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO interactions (command, response) VALUES (?, ?)", (command, response))
    conn.commit()
    conn.close()

def set_user_preference(key, value):
    conn = sqlite3.connect('assistant.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO user_preferences (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_user_preference(key):
    conn = sqlite3.connect('assistant.db')
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM user_preferences WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None
