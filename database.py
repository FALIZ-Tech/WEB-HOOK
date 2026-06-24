import sqlite3
from config import DB_PATH, SUPPORTED_LANGUAGES

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT UNIQUE NOT NULL,
            user_language_preference TEXT CHECK(user_language_preference IN ('en','es','fr','pt') OR user_language_preference IS NULL),
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            incoming_message TEXT NOT NULL,
            bot_response TEXT,
            detected_language TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS language_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT NOT NULL,
            detected_lang TEXT,
            confidence REAL,
            was_supported BOOLEAN,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("[DB] Database schema initialized / verified.")

def get_user_by_phone(phone: str):
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE phone_number = ?", (phone,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def create_user(phone: str, lang_pref: str = None):
    conn = get_db_connection()
    conn.execute(
        "INSERT OR IGNORE INTO users (phone_number, user_language_preference) VALUES (?, ?)",
        (phone, lang_pref)
    )
    conn.commit()
    row = conn.execute(
        "SELECT id FROM users WHERE phone_number = ?", (phone,)
    ).fetchone()
    conn.close()
    return row['id'] if row else None

def update_user_lang(user_id: int, lang: str):
    conn = get_db_connection()
    conn.execute(
        "UPDATE users SET user_language_preference = ?, last_seen = CURRENT_TIMESTAMP WHERE id = ?",
        (lang, user_id)
    )
    conn.commit()
    conn.close()

def add_conversation(user_id: int, incoming: str, response: str, detected_lang: str):
    conn = get_db_connection()
    conn.execute(
        """INSERT INTO conversations 
           (user_id, incoming_message, bot_response, detected_language)
           VALUES (?, ?, ?, ?)""",
        (user_id, incoming, response, detected_lang)
    )
    conn.commit()
    conn.close()

def get_history(user_id: int, limit: int = 8):
    conn = get_db_connection()
    rows = conn.execute(
        """SELECT incoming_message, bot_response, detected_language 
           FROM conversations 
           WHERE user_id = ? 
           ORDER BY timestamp DESC 
           LIMIT ?""",
        (user_id, limit)
    ).fetchall()
    conn.close()

    history = []
    for row in reversed(rows):
        history.append({
            "user_msg": row["incoming_message"],
            "bot_resp": row["bot_response"],
            "detected_language": row["detected_language"]
        })
    return history

def log_language_detection(phone: str, detected: str, conf: float, was_supported: bool):
    conn = get_db_connection()
    conn.execute(
        """INSERT INTO language_logs 
           (phone_number, detected_lang, confidence, was_supported)
           VALUES (?, ?, ?, ?)""",
        (phone, detected, conf, was_supported)
    )
    conn.commit()
    conn.close()
