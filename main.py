import sqlite3
import sys

database = "ims.db"
create_table = '''
            CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            sku TEXT NOT NULL,
            category TEXT,
            warehouse TEXT,
            quantity INTEGER NOT NULL);
'''


def insert():
    # Name = input("Enter item name: ")
    # Count = input("Enter item count: ")
    try:
        with sqlite3.connect(database) as conn:
            cursor = conn.cursor()
            cursor.execute(create_table)
            conn.commit()

    except sqlite3.OperationalError as e:
        print(e)



def query(item_name):
    #search = input('Enter search term: ')
    item_name += "%"
    try:
        with sqlite3.connect(database) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM test WHERE item LIKE (?);", (item_name, ))
            items = cursor.fetchall()
            found_item = items[0][1]
            return found_item
    except IndexError:
        print("INVALID ITEM NAME")
        sys.exit(0)

def update_count():
    item_name = input("Enter item name: ")
    if query(item_name) is not None:
        new_count = input("Enter new value: ")

        with sqlite3.connect(database) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE test SET count = ? WHERE item = ?", (new_count, item_name))
            conn.commit()
            cursor.execute("SELECT * FROM test WHERE item = (?);", (item_name, ))
            print(cursor.fetchall())

