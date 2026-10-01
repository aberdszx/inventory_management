import sqlite3


def add_item():
    item_name = input("Enter item name: ")
    sku = input("Enter sku: ")
    category = input("Enter category: ")
    warehouse = input("Enter warehouse: ")
    quantity = input("Enter quantity: ")
    with sqlite3.connect('ims.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO stocks (item_name, sku, category, warehouse, quantity) VALUES (?, ?, ?, ?, ?);',(item_name, sku, category, warehouse, quantity))
        conn.commit()
        cursor.execute('SELECT * FROM stocks WHERE item_name = ?', (item_name,))
        print(cursor.fetchall())


def view_inventory():
    with sqlite3.connect('ims.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM stocks;')
        items = cursor.fetchall()
        for item in items:
            print(item)


def search_inventory(search_key):
    search_key += "%"
    statement = 'SELECT * FROM stocks WHERE item_name LIKE ? OR sku LIKE ?;'
    with sqlite3.connect('ims.db') as conn:
        cursor = conn.cursor()
        cursor.execute(statement, (search_key,search_key))
        items = cursor.fetchall()
        if not items:
            return
        return items



def update_quantity():
    statement = 'UPDATE stocks SET quantity = ? WHERE item_name = ? OR sku = ?;'
    print("Update quantity")
    item_name = input("Enter item name: ")
    if not search_inventory(item_name):
        print("No items found")
        return
    new_quantity = input("Enter new quantity: ")
    with sqlite3.connect('ims.db') as conn:
        cursor = conn.cursor()
        cursor.execute(statement, (new_quantity,item_name,item_name) )
        conn.commit()
    with sqlite3.connect('ims.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM stocks WHERE item_name = ? OR sku = ?;', (item_name, item_name, ) )
        updated = cursor.fetchall()
        for item in updated:
            print("item_name " + "    new quantity \n" + item[1] + "        " + str(item[5]))

