
# Create SQLite database for MOC
import sqlite3

# Create a connection to the database
def create_connection():
    conn = sqlite3.connect('../moc.db')
    return conn

# Create a table in the database
"""
aclist table have 3 columns
1. ID: primary key
2. REG: name of the aircraft
3. TYPE: type of the aircraft
"""
def create_table(conn):
    c = conn.cursor()
    c.execute('''CREATE TABLE aclist
                 (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                 REG TEXT NOT NULL,
                 TYPE TEXT NOT NULL)''')
    conn.commit()

def main():
    conn = create_connection()
    create_table(conn)
    conn.close()
if __name__ == '__main__':
    main()

