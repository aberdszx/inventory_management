import sqlite3


def db_commit(statement, parameters):
    with sqlite3.connect('ims.db') as conn:
        cursor = conn.cursor()
        cursor.execute(statement, parameters)
        conn.commit()


def show_items(statement, parameters):
    with sqlite3.connect('ims.db') as conn:
        cursor = conn.cursor()
        cursor.execute(statement, parameters)
        items = cursor.fetchall()
        return items



def add_item():
    item_name = input("Enter item name: ")
    sku = input("Enter sku: ")
    category = input("Enter category: ")
    warehouse = input("Enter warehouse: ")
    while True:
        try:
            quantity = int(input("Enter new quantity: "))
            if quantity < 0:
                print("Quantity cannot be negative!")
                continue
            return quantity
        except ValueError:
            print("Invalid quantity")


    commit_statement = 'INSERT INTO stocks (item_name, sku, category, warehouse, quantity) VALUES (?, ?, ?, ?, ?);'
    commit_parameters = (item_name, sku, category, warehouse, quantity)
    show_statement = 'SELECT * FROM stocks WHERE item_name = ?'
    show_param = (item_name,)
    db_commit(commit_statement, commit_parameters)
    show_items(show_statement, show_param)


def view_inventory():
    statement = 'SELECT * FROM stocks;'
    with sqlite3.connect('ims.db') as conn:
        cursor = conn.cursor()
        cursor.execute(statement)
        items = cursor.fetchall()
    for item in items:
        print(item)


def search_inventory(search_key):
    search_key += "%"
    statement = 'SELECT * FROM stocks WHERE item_name LIKE ? OR sku LIKE ?;'
    items = show_items(statement, (search_key, search_key))
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
    db_commit(update_statement, (new_quantity, ID))
    # SHOWING THE UPDATED QUANTITY
    updated = show_items(show_statement, (ID,))
    for item in updated:
        print("\n-ITEM NAME " + "                   NEW COUNT \n" + item[1] + "                   " + str(item[5]))


def delete_item():
    delete_statement = 'DELETE FROM stocks WHERE id = ?;'
    show_statement = 'SELECT * FROM stocks WHERE id = ?;'

    item_name = input("Enter item name or sku: ")
    items = search_inventory(item_name)
    if not items:
        print("No items found")
        return

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

    else:
        ID = items[0][0]
    item = show_items(show_statement, (ID,))

    while True:
        confirmation = input("Are you sure you want to delete " + item[0][1] + "? (y/n): ")
        confirmation = confirmation.upper()
        if confirmation == "Y":
            db_commit(delete_statement, (ID, ))
            print("Item " + item[0][1] + " has been deleted")
            return
        elif confirmation == "N":
            print("Exiting...")
            return
        else:
            print("Invalid input")


def main():
    while True:
        print("-----Welcome to Stock Inventory System-----")
        print("1. Add item")
        print("2. Update quantity")
        print("3. Delete item")
        print("4. View inventory")
        print("5. Search an item")
        print("6. Exit")

        try:
            operation = int(input("Enter your choice: "))
            if operation == 1:
                add_item()

            elif operation == 2:
                update_quantity()

            elif operation == 3:
                delete_item()

            elif operation == 4:
                view_inventory()

            elif operation == 5:
                item = search_inventory(input("Enter item name or sku: "))
                if not item:
                    print("No items found")
                else:
                    for item in item:
                        print(item)


            elif operation == 6:
                print("Exiting...")
                break

            else:
                print("NOT IN THE SELECTION!")
        except ValueError:
            print("INVALID INPUT!")

view_inventory()
add_item()