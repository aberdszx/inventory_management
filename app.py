import sqlite3
from tabulate import tabulate


def db_commit(statement, parameters):
    with sqlite3.connect('ims.db') as conn:
        cursor = conn.cursor()
        cursor.execute(statement, parameters)
        conn.commit()


def db_transaction(statement, log, confirmation,
                   statement_parameters, log_parameters, confirmation_parameters):

    with sqlite3.connect('ims.db') as conn:
        cursor = conn.cursor()

        try:
            cursor.execute('BEGIN TRANSACTION;')

            cursor.execute(statement, statement_parameters)
            cursor.execute(log, log_parameters)
            cursor.execute(confirmation, confirmation_parameters)

            updated = cursor.fetchall()

            conn.commit()

            return updated

        except Exception as e:
            conn.rollback()
            print(f"Transaction failed: {e}")

def show_items(statement, parameters):
    with sqlite3.connect('ims.db') as conn:
        cursor = conn.cursor()
        cursor.execute(statement, parameters)
        items = cursor.fetchall()
        return items


def add_item():
    print("-----ADD AN ITEM-----")
    while True:
        item_name = input("Enter item name: ")
        if item_name.strip() == '':
            print("Item name cannot be empty")
        else:
            break
    while True:
        sku = input("Enter sku: ")
        if sku.strip() == '':
            print("Sku cannot be empty")
            continue

        check_statement = 'SELECT * FROM stocks WHERE sku = ?;'
        item = show_items(check_statement, (sku,))
        if item:
            print("SKU already exists")

        else:
            break
    while True:
        category = input("Enter category: ")
        if category.strip() == '':
            print("Category cannot be empty")
        else:
            break
    while True:
        warehouse = input("Enter warehouse: ")
        if warehouse.strip() == '':
            print("Warehouse cannot be empty")
        else:
            break

    while True:
        try:
            quantity = int(input("Enter quantity: "))
            if quantity < 0:
                print("Quantity cannot be negative!")
                continue
            break
        except ValueError:
            print("Invalid quantity")


    print(quantity)
    commit_statement = 'INSERT INTO stocks (item_name, sku, category, warehouse, quantity) VALUES (?, ?, ?, ?, ?);'
    commit_parameters = (item_name, sku, category, warehouse, quantity)
    show_statement = 'SELECT * FROM stocks WHERE item_name = ?'
    show_param = (item_name,)
    db_commit(commit_statement, commit_parameters)
    show_items(show_statement, show_param)


def view_inventory():
    print("-----IVENTORY-----")
    statement = 'SELECT * FROM stocks WHERE category != "INACTIVE" ;'
    with sqlite3.connect('ims.db') as conn:
        cursor = conn.cursor()
        cursor.execute(statement)
        items = cursor.fetchall()
    table = tabulate(items, headers=["ID", "Item Name", "SKU", "Category", "Warehouse", "Quantity"], tablefmt="pipe")
    print(table)


def search_inventory(search_key):
    search_key += "%"
    statement = 'SELECT * FROM stocks WHERE item_name LIKE ? OR sku LIKE ?;'
    items = show_items(statement, (search_key, search_key))
    if not items:
        return
    return items


def update_quantity():
    print("-----UPDATE QUANTITY-----")
    update_statement = 'UPDATE stocks SET quantity = ? WHERE id = ?;'
    show_statement = 'SELECT * FROM stocks WHERE id = ?;'
    log = 'INSERT INTO transactions (item_id, transaction_type, quantity, created_at) VALUES (?, ?, ?, datetime("now"));'

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
        table = tabulate(items, headers=["ID", "Item Name", "SKU", "Category", "Warehouse", "Quantity"], tablefmt="pipe")
        print(table)

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
    current_count = items[0][5]
    difference = new_quantity - current_count
    print(difference)
    if difference == 0:
        print("No change in quantity")
        return

    updated = db_transaction(update_statement,log, show_statement, (new_quantity, ID), (ID, "UPDATE", difference), (ID,))
    for item in updated:
        print("\n-ITEM NAME " + "                   NEW COUNT \n" + item[1] + "                   " + str(item[5]))     



def delete_item():
    print("-----DELETE AN ITEM-------")
    delete_statement = 'UPDATE stocks SET category = "INACTIVE" WHERE id = ?;'
    show_statement = 'SELECT * FROM stocks WHERE id = ?;'
    log = 'INSERT INTO transactions (item_id, transaction_type, quantity, created_at) VALUES (?, ?, ?, datetime("now"));'

    item_name = input("Enter item name or sku: ")
    items = search_inventory(item_name)
    if not items:
        print("No items found")
        return

    elif len(items) > 1:
        result_ids = []
        for item in items:
            result_ids.append(item[0])
        table = tabulate(items, headers=["ID", "Item Name", "SKU", "Category", "Warehouse", "Quantity"], tablefmt="pipe")
        print(table)

        while True:
            try:
                ID = int(input("Enter item id instead: "))
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
            db_transaction(log, show_statement, delete_statement, (ID, "DELETED", item[0][5]), (ID,), (ID,))
            print("Item " + item[0][1] + " has been deleted")
            return
        elif confirmation == "N":
            print("Exiting...")
            return
        else:
            print("Invalid input")


def restock_item():
    print("-----RESTOCK ITEM-----")
    search_key = input("Enter item name or sku: ")
    items = search_inventory(search_key)

    # NO ITEM MATCHED
    if not items:
        print("No items found")
        return
    # MORE THAN ONE ITEM MATCHED
    elif len(items) > 1:
        print("Multiple items found")
        result_ids = []
        for item in items:
            result_ids.append(item[0])
        table = tabulate(items, headers=["ID", "Item Name", "SKU", "Category", "Warehouse", "Quantity"], tablefmt="pipe")
        print(table)

        while True:
            try:
                ID = int(input("Enter item id instead: "))
                if ID not in result_ids:
                    print("ID not in the selection")
                    continue
                break
            except ValueError:
                print("Invalid ID")

    # ONE ITEM MATCHED
    else:
        print("Current item count of " + items[0][1] + " is " + str(items[0][5]))
        ID = items[0][0]


    while True:
        try:
            added_quantity = int(input("Enter quantity to add: "))
            if added_quantity < 0:
                print("Quantity cannot be negative!")
                continue
            break
        except ValueError:
            print("Invalid quantity")

    restock_statement = 'UPDATE stocks SET quantity = quantity + ? WHERE id = ?;'
    updated_quantity = 'SELECT * FROM stocks WHERE id = ?;'
    transaction_log = 'INSERT INTO transactions (item_id, transaction_type, quantity, created_at) VALUES (?, ?, ?, datetime("now"));'
    updated = db_transaction(restock_statement, transaction_log, updated_quantity, (added_quantity, ID), (ID, "RESTOCK", added_quantity), (ID,))
    print("Updated quantity of " + updated[0][1] + " is " + str(updated[0][5]))


def sell_item():
    print("-----SELL ITEM-----")
    search_key = input("Enter item name or sku: ")
    items = search_inventory(search_key)

    # NO ITEM MATCHED
    if not items:
        print("No items found")
        return
    # MORE THAN ONE ITEM MATCHED
    elif len(items) > 1:
        print("Multiple items found")
        result_ids = []
        table = tabulate(items, headers=["ID", "Item Name", "SKU", "Category", "Warehouse", "Quantity"], tablefmt="pipe")
        for item in items:
            result_ids.append(item[0])
        print(table)

        while True:
            try:
                ID = int(input("Enter item id instead: "))
                if ID not in result_ids:
                    print("ID not in the selection")
                    continue
                break
            except ValueError:
                print("Invalid ID")

    # ONE ITEM MATCHED
    else:
        print("Current item count of " + items[0][1] + " is " + str(items[0][5]))
        ID = items[0][0]

    show_statement = 'SELECT * FROM stocks WHERE id = ?'
    selected_item = show_items(show_statement, (ID,))
    current_item_quantity = selected_item[0][5]

    while True:
        try:
            sold_quantity = int(input("Enter quantity to sell: "))
            if sold_quantity < 0:
                print("Quantity cannot be negative!")
                continue
            elif current_item_quantity - sold_quantity < 0:
                print("Not enough items to sell")
                continue
            break
        except ValueError:
            print("Invalid quantity")

    sell_statement = 'UPDATE stocks SET quantity = quantity - ? WHERE id = ?;'
    updated_quantity = 'SELECT * FROM stocks WHERE id = ?;'
    transaction_log = 'INSERT INTO transactions (item_id, transaction_type, quantity, created_at) VALUES (?, ?, ?, datetime("now"));'
    updated = db_transaction(sell_statement, transaction_log, updated_quantity, (sold_quantity, ID), (ID, "SELL", sold_quantity), (ID,))
    print("Updated quantity of " + updated[0][1] + " is " + str(updated[0][5]))


def view_transactions():
    statement = 'SELECT t.id, s.item_name, t.transaction_type, t.quantity, t.created_at ' \
    'FROM stocks s ' \
    'INNER JOIN transactions t ON s.id = t.item_id ' \
    'ORDER BY t.id DESC;'
    with sqlite3.connect('ims.db') as conn:
        cursor = conn.cursor()
        cursor.execute(statement)
        transactions = cursor.fetchall()


    updated_transactions = []
    for transaction in transactions:
        quantity = transaction[3]
        quantity = int(quantity)
        print(quantity)
        print(type(quantity))
        if transaction[2] == "UPDATE":
            if quantity < 0:
                quantity = "+" + str(quantity)
                updated_transactions.append((transaction[0], transaction[1], transaction[2], quantity, transaction[4])) 
    print("-----------------------------------TRANSACTIONS--------------------------------")
    table = tabulate(transactions, headers=["ID", "Item Name", "Transaction Type", "Quantity", "Created At"], tablefmt="pipe")
    print(table)


def view_item_transactions():
    print("-----VIEW ITEM TRANSACTIONS-----")
    search_key = input("Enter item name or sku: ")
    items = search_inventory(search_key)
    # NO ITEM MATCHED
    if not items:
        print("No items found")
        return
    # MORE THAN ONE ITEM MATCHED
    elif len(items) > 1:
        print("Multiple items found")
        result_ids = []
        for item in items:
            result_ids.append(item[0])
        table = tabulate(items, headers=["ID", "Item Name", "SKU", "Category", "Warehouse", "Quantity"], tablefmt="pipe")
        print(table)

        while True:
            try:
                ID = int(input("Enter item id instead: "))
                if ID not in result_ids:
                    print("ID not in the selection")
                    continue
                break
            except ValueError:
                print("Invalid ID")

    # ONE ITEM MATCHED
    else:
        print("Current item count of " + items[0][1] + " is " + str(items[0][5]))
        ID = items[0][0]

    statement = 'SELECT t.id, s.item_name, t.transaction_type, t.quantity, t.created_at ' \
    'FROM stocks s ' \
    'INNER JOIN transactions t ON s.id = t.item_id ' \
    'WHERE s.id = ? ' \
    'ORDER BY t.id DESC;'
    with sqlite3.connect('ims.db') as conn:
        cursor = conn.cursor()
        cursor.execute(statement, (ID,))
        transactions = cursor.fetchall()

    if not transactions:
        print("No transactions found for this item")
        return
    else:
        print("-----------------------------------TRANSACTIONS--------------------------------")
        table = tabulate(transactions, headers=["ID", "Item Name", "Transaction Type", "Quantity", "Created At"], tablefmt="pipe")
        print(table)


    
def main():
    while True:
        print("-----Welcome to Stock Inventory System-----")
        print("1. Add item")
        print("2. Update quantity")
        print("3. Delete item")
        print("4. View inventory")
        print("5. Search an item")
        print("6. Restock item")
        print("7. Sell item")
        print("8. View transactions")
        print("9. View item transactions")
        print("10. Exit")

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
                restock_item()

            elif operation == 7:
                sell_item()

            elif operation == 8:
                view_transactions()

            elif operation == 9:
                view_item_transactions()

            elif operation == 10:
                print("Exiting...")
                break

            else:
                print("NOT IN THE SELECTION!")
        except ValueError:
            print("INVALID INPUT!")



# sell_item()
# restock_item()
view_transactions()
#view_inventory()
#update_quantity()