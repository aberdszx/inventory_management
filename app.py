import sqlite3
import time


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


# UPDATING QUANTITY. WHEN MORE THAN 1 RESULT RETURNED IT WILL ASK THE USER TO ENTER THE ITEM ID INSTEAD

def update_quantity():
    update_statement = 'UPDATE stocks SET quantity = ? WHERE id = ?;'
    show_statement = 'SELECT * FROM stocks WHERE id = ?;'

    search_key = input("Enter item name or sku: ")
    items = search_inventory(search_key)

    # NO ITEM MATCHED
    if not items:
        print("No items found")
        return
    # MORE THAN ONE ITEM MATCHED
    elif len(items) > 1:
        result_ids = []
        for item in items:
            result_ids.append(item[0])
            print(item)

        while True:
            try:
                id = int(input("Enter item id instead: "))
                ID = id
                break
            except ValueError:
                print("Invalid ID")

        while True:
            if ID not in result_ids:
                print("ID not in the selection")
                ID = int(input("Enter item id instead: "))
            else:
                break


    # ONE ITEM MATCHED
    else:
        ID = items[0][0]

    while True:
        try:
            new_quantity = int(input("Enter new quantity: "))
            if new_quantity < 0:
                print("Quantity cannot be negative!")
                continue
            break
        except ValueError:
            print("Invalid quantity")
    # UPDATING THE QUANTITY
    with sqlite3.connect('ims.db') as conn:
        cursor = conn.cursor()
        cursor.execute(update_statement, (new_quantity, ID))
        conn.commit()

    # SHOWING THE UPDATED QUANTITY
    with sqlite3.connect('ims.db') as conn:
        cursor = conn.cursor()
        cursor.execute(show_statement, (ID, ))
        updated = cursor.fetchall()
        for item in updated:
            print("item_name " + "    new quantity \n" + item[1] + "        " + str(item[5]))


