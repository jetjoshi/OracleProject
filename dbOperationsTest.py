import unittest
import os

from TransactionHandler import TransactionHandler
from dbOperations import (
    create_location_table,
    insert_location_data,
    search_restaurants,
    get_restaurant_info,
    create_restaurant,
    create_warehouse,
    decrease_inventory,
    get_all_warehouses,
    increase_warehouse_inventory,
    transfer_inventory,
    drop_all_tuples
)

class TestLocationsFunctions(unittest.TestCase):
    handler = None

    def setUp(self):
        # Set up a temporary database file for testing
        
        create_location_table()

        # Create a TransactionHandler object for testing
        self.handler = TransactionHandler()

    def tearDown(self):
        # Stop the TransactionHandler after each test
        self.handler.stop()
        self.handler = None
        drop_all_tuples()

    def test_search_restaurants(self):
        # Test searching for restaurants
        insert_location_data('Restaurant1', 'Location A', 50.0, 100.0, 0, self.handler)
        insert_location_data('Restaurant2', 'Location B', 30.0, 80.0, 0, self.handler)

        result = search_restaurants('Restaurant', self.handler)
        self.assertEqual(len(result), 2)

        result_empty_query = search_restaurants('', self.handler)
        self.assertEqual(len(result_empty_query), 2)

    def test_get_restaurant_info(self):
        # Test getting restaurant information
        insert_location_data('Restaurant1', 'Location A', 50.0, 100.0, 0, self.handler)
        result = get_restaurant_info('Restaurant1', self.handler)
        self.assertEqual(result[0], ('Restaurant1', 'Location A', 50.0, 100.0))

    def test_create_restaurant(self):
        # Test creating a restaurant
        with self.assertRaises(Exception):
            create_restaurant('NewRestaurant', 'Location C', 70.0, 50.0, self.handler)

        result = get_restaurant_info('NewRestaurant', self.handler)
        self.assertEqual(len(result), 0, "List should be empty")
    def test_create_warehouse(self):
        # Test creating a warehouse
        create_warehouse('NewWarehouse', 'Location D', 150.0, 200.0, self.handler)

        warehouses = get_all_warehouses(self.handler)
        self.assertEqual(len(warehouses), 1)  # Ensure the warehouse is created

    def test_decrease_inventory(self):
        # Test decreasing inventory in a restaurant
        insert_location_data('Restaurant1', 'Location A', 50.0, 100.0, 0, self.handler)

        decrease_inventory('Restaurant1', 20.0, self.handler)

        result = get_restaurant_info('Restaurant1', self.handler)
        self.assertEqual(result[0], ('Restaurant1', 'Location A', 30.0, 100.0))

        # Test decreasing inventory with not enough quantity
        with self.assertRaises(Exception):
            decrease_inventory('Restaurant1', 40.0, self.handler)

    def test_increase_warehouse_inventory(self):
        # Test increasing inventory in a warehouse
        create_warehouse('Warehouse1', 'Location E', 50.0, 150.0, self.handler)

        increase_warehouse_inventory('Warehouse1', 30.0, self.handler)

        warehouses = get_all_warehouses(self.handler)
        self.assertEqual(warehouses[0], ('Warehouse1', 'Location E', 80.0, 150.0))

        # Test increasing inventory exceeding max_inventory
        with self.assertRaises(Exception):
            increase_warehouse_inventory('Warehouse1', 100.0, self.handler)

    def test_transfer_inventory(self):
        # Test transferring inventory from warehouse to restaurant
        create_warehouse('Warehouse1', 'Location F', 100.0, 200.0, self.handler)
        create_restaurant('Restaurant1', 'Location F', 50.0, 100.0, self.handler)

        transfer_inventory('Warehouse1', 'Restaurant1', 30.0, self.handler)

        result_warehouse = get_all_warehouses(self.handler)
        result_restaurant = get_restaurant_info('Restaurant1', self.handler)

        self.assertEqual(result_restaurant[0], ('Restaurant1', 'Location F', 80.0, 100.0))
        self.assertEqual(result_warehouse[0], ('Warehouse1', 'Location F', 70.0, 200.0))

        # Test transferring more inventory than available in the warehouse
        with self.assertRaises(Exception):
            transfer_inventory('Warehouse1', 'Restaurant1', 100.0, self.handler)

if __name__ == '__main__':
    unittest.main()
