import sqlite3

DATABASE = 'database.db'

def seed_db():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('admin', 'admin', 'admin'))
        db.commit()
        print("Admin user seeded successfully.")
    else:
        print("Admin user already exists.")
    db.close()

if __name__ == '__main__':
    seed_db()