import sqlite3
from datetime import datetime

DATABASE_NAME = "honeypot.db"


def initialize_database():

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            ip_address TEXT,
            username TEXT,
            password TEXT
    )
""")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            source_ip TEXT,
            start_time TEXT,
            end_time TEXT,
            status TEXT
    )
""")

    connection.commit()

    connection.close()

    print("[+] Database initialized.")


def log_login_attempt(ip_address, username, password):

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO login_attempts (
            timestamp,
            ip_address,
            username,
            password
        )
        VALUES (?, ?, ?, ?)
    """, (timestamp, ip_address, username, password))

    connection.commit()

    connection.close()

    print(f"[+] Login attempt stored for {ip_address}")
    

def create_session(
    session_id,
    source_ip,
    start_time
):

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO sessions (
            session_id,
            source_ip,
            start_time,
            status
        )
        VALUES (?, ?, ?, ?)
    """, (
        session_id,
        source_ip,
        start_time,
        "ACTIVE"
    ))

    connection.commit()

    connection.close()
    
def close_session(
    session_id,
    end_time
):

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE sessions
        SET
            end_time = ?,
            status = ?
        WHERE session_id = ?
    """, (
        end_time,
        "CLOSED",
        session_id
    ))

    connection.commit()

    connection.close()