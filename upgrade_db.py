import sqlite3

def upgrade_db():
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN session_token VARCHAR(256)")
        print("Added session_token column.")
    except sqlite3.OperationalError as e:
        print(f"session_token column might already exist: {e}")
        
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN last_active DATETIME")
        print("Added last_active column.")
    except sqlite3.OperationalError as e:
        print(f"last_active column might already exist: {e}")
        
    conn.commit()
    conn.close()
    print("Database upgrade finished.")

if __name__ == "__main__":
    upgrade_db()
