import sqlite3

from TransactionHandler import TransactionHandler 

def create_location_table():
    conn = sqlite3.connect('locations.db')
    cursor = conn.cursor()

    create_table_query = '''
    CREATE TABLE IF NOT EXISTS location (
        name TEXT PRIMARY KEY,
        location_name TEXT,
        inventory_amount REAL,
        max_inventory REAL,
        is_warehouse INTEGER
    );
    '''

    cursor.execute(create_table_query)
    conn.commit()
    conn.close()

def insert_location_data(name, location_name, inventory_amount, max_inventory, is_warehouse, handler: TransactionHandler):
    query = '''
    INSERT INTO location (name, location_name, inventory_amount, max_inventory, is_warehouse)
    VALUES (?, ?, ?, ?, ?);
    '''
    params = (name, location_name, inventory_amount, max_inventory, is_warehouse)
    handler.add_transaction(query, params)

def search_restaurants(query, handler: TransactionHandler):
    result = ''
    if query:
        search_query = '''
        SELECT * FROM location
        WHERE is_warehouse = 0 AND (name LIKE ? OR location_name LIKE ?);
        '''
        params = (f'%{query}%', f'%{query}%')
        result = handler.add_transaction(search_query, params, True)
    else:
        # If query is empty, return all restaurants
        result = handler.add_transaction('SELECT * FROM location WHERE is_warehouse = 0;', None, True)

    return result

def get_restaurant_info(restaurant_name, handler: TransactionHandler):

    get_info_query = '''
    SELECT name, location_name, inventory_amount, max_inventory FROM location
    WHERE is_warehouse = 0 AND name = ?;
    '''
    restaurant_info=  handler.add_transaction(get_info_query, (restaurant_name,), True)
    print(restaurant_info)
    
    return restaurant_info

def create_restaurant(restaurant_name, location_name, starting_inventory, max_inventory, handler: TransactionHandler):
    if starting_inventory > max_inventory:
        raise Exception("Starting inventory cannot be greater than max inventory.")
    insert_location_data(restaurant_name, location_name, starting_inventory, max_inventory, 0, handler)

def create_warehouse(warehouse_name, location_name, starting_inventory, max_inventory, handler: TransactionHandler):
    if starting_inventory > max_inventory:
        raise Exception("Starting inventory cannot be greater than max inventory.")
    insert_location_data(warehouse_name, location_name, starting_inventory, max_inventory, 1, handler)

def decrease_inventory(restaurant_name, amount, handler: TransactionHandler):
    
    check_inventory_query = '''
    SELECT inventory_amount FROM location
    WHERE is_warehouse = 0 AND name = ?;
    '''
    current_inventory = handler.add_transaction(check_inventory_query, (restaurant_name,), True)

    if current_inventory and current_inventory[0][0] >= amount:
        # Decrease inventory if enough quantity is available
        decrease_inventory_query = '''
        UPDATE location SET inventory_amount = inventory_amount - ?
        WHERE is_warehouse = 0 AND name = ?;
        '''
        handler.add_transaction(decrease_inventory_query, (amount, restaurant_name))
    else:
        raise Exception("Not enough inventory in the restaurant or restuarant doesn't exist.")

def get_all_warehouses(handler: TransactionHandler):
    get_warehouses_query = '''
    SELECT name, location_name, inventory_amount, max_inventory FROM location
    WHERE is_warehouse = 1;
    '''
    warehouses = handler.add_transaction(get_warehouses_query, is_select=True)
    return warehouses

def increase_warehouse_inventory(warehouse_name, amount, handler: TransactionHandler):
    # Check if increasing inventory exceeds max_inventory
    check_max_inventory_query = '''
    SELECT max_inventory, inventory_amount FROM location
    WHERE is_warehouse = 1 AND name = ?;
    '''
    result = handler.add_transaction(check_max_inventory_query, (warehouse_name,), True)
    
    if result:
        max_inventory, current_inventory = result[0]

        if current_inventory + amount <= max_inventory:
            # Increase inventory if within the limit
            increase_inventory_query = '''
            UPDATE location SET inventory_amount = inventory_amount + ?
            WHERE is_warehouse = 1 AND name = ?;
            '''
            handler.add_transaction(increase_inventory_query, (amount, warehouse_name))
        else:
            raise Exception("Increasing inventory exceeds the maximum limit.")
    else:
        raise Exception("Warehouse does not exist.")


def transfer_inventory(warehouse_name, restaurant_name, amount, handler: TransactionHandler):

    # Check if the warehouse has enough inventory
    check_warehouse_inventory_query = '''
    SELECT inventory_amount FROM location
    WHERE is_warehouse = 1 AND name = ?;
    '''
    warehouse_inventory = handler.add_transaction(check_warehouse_inventory_query, (warehouse_name,), True)[0]
    check_restaurant_exists = '''
    SELECT name FROM location 
    WHERE is_warehouse = 0 AND name = ?
    '''

    restaurant = handler.add_transaction(check_restaurant_exists, (restaurant_name,), True)

    if warehouse_inventory and restaurant and warehouse_inventory[0] >= amount:
        # Transfer inventory from warehouse to restaurant
        transfer_query_1 = '''
        UPDATE location SET inventory_amount = inventory_amount - ?
        WHERE is_warehouse = 1 AND name = ?;
        '''
        transfer_query_2 = '''
        UPDATE location SET inventory_amount = inventory_amount + ?
        WHERE is_warehouse = 0 AND name = ?;
        '''
        handler.add_transaction(transfer_query_1, (amount, warehouse_name))
        handler.add_transaction(transfer_query_2, (amount, restaurant_name))
    else:
        raise Exception("Warehouse does not exist or restaurant does not exist or warehouse inventory not enough")

def drop_all_tuples():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('locations.db')  # Adjust the database name if needed
        cursor = conn.cursor()

        # Execute the DELETE statement to remove all rows from the location table
        delete_query = 'DELETE FROM location;'
        cursor.execute(delete_query)

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        print("All tuples in the location table have been dropped.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

drop_all_tuples()
