import sqlite3
import os

DB_PATH = "data/users.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            discord_id TEXT PRIMARY KEY,
            access_token TEXT,
            refresh_token TEXT,
            token_uri TEXT,
            client_id TEXT,
            client_secret TEXT,
            scopes TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_user(discord_id, creds_dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        discord_id,
        creds_dict["token"],
        creds_dict["refresh_token"],
        creds_dict["token_uri"],
        creds_dict["client_id"],
        creds_dict["client_secret"],
        " ".join(creds_dict["scopes"])
    ))

    conn.commit()
    conn.close()


def get_user(discord_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE discord_id=?", (discord_id,))
    row = c.fetchone()
    conn.close()
    return row