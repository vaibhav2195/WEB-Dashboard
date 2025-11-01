import sqlite3

DATABASE = 'database.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    with open('schema.sql', 'r') as f:
        db.executescript(f.read())
    db.commit()
    cursor = db.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        db.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin', 'admin')")
        db.commit()