import requests
from pydantic import BaseModel
from threading import Thread, Event
import time
import random

class Location(BaseModel):
    name: str
    locationName: str
    currentInventory: float
    maxInventory: float

# Function to decrease inventory for a restaurant
def decrease_inventory_thread(restaurant_data, stop_event):
    while not stop_event.is_set():
        try:
            # Decrease inventory by a random value between 1 and 10
            decrease_amount = random.randint(1, 10)
            response = requests.put(f"http://127.0.0.1:8080/restaurant/inventory/{restaurant_data['name']}", json={"inventory": decrease_amount})
            response.raise_for_status()  # Raise an error for unsuccessful response (4xx or 5xx)
            print(f"Inventory decreased for {restaurant_data['name']} by {decrease_amount}.")
        except requests.exceptions.HTTPError as err:
            print(f"Error decreasing inventory for {restaurant_data['name']}: {err.response.text}")
        time.sleep(random.uniform(5, 10))  # Sleep for a random time between 5 and 10 seconds

# API endpoint
restaurant_api_url = "http://127.0.0.1:8080/restaurant/"
warehouse_api_url = "http://127.0.0.1:8080/warehouse/"

# List of 10 restaurant objects
restaurants = [
    {"name": "Restaurant1", "locationName": "Location1", "currentInventory": 500.0, "maxInventory": 1500.0},
    {"name": "Restaurant2", "locationName": "Location2", "currentInventory": 300.0, "maxInventory": 1200.0},
    {"name": "Restaurant3", "locationName": "Location3", "currentInventory": 800.0, "maxInventory": 2000.0},
    {"name": "Restaurant4", "locationName": "Location4", "currentInventory": 600.0, "maxInventory": 1800.0},
    {"name": "Restaurant5", "locationName": "Location5", "currentInventory": 400.0, "maxInventory": 1300.0},
    {"name": "Restaurant6", "locationName": "Location6", "currentInventory": 700.0, "maxInventory": 1600.0},
    {"name": "Restaurant7", "locationName": "Location7", "currentInventory": 900.0, "maxInventory": 1700.0},
    {"name": "Restaurant8", "locationName": "Location8", "currentInventory": 200.0, "maxInventory": 1100.0},
    {"name": "Restaurant9", "locationName": "Location9", "currentInventory": 1200.0, "maxInventory": 2200.0},
    {"name": "Restaurant10", "locationName": "Location10", "currentInventory": 1100.0, "maxInventory": 2100.0},
]


# List of 2 warehouse objects
warehouses = [
    {"name": "Warehouse1", "locationName": "LocationW1", "currentInventory": 1500.0, "maxInventory": 12000.0},
    {"name": "Warehouse2", "locationName": "LocationW2", "currentInventory": 2000.0, "maxInventory": 15000.0},
]

# Make API calls for each restaurant
for restaurant_data in restaurants:
    try:
        response = requests.post(restaurant_api_url, json=Location(**restaurant_data).dict())
        response.raise_for_status()  # Raise an error for unsuccessful response (4xx or 5xx)
        print(f"Restaurant {restaurant_data['name']} added successfully.")
    except requests.exceptions.HTTPError as err:
        print(f"Error adding restaurant {restaurant_data['name']}: {err.response.text}")
# Make API calls for each warehouse
for warehouse_data in warehouses:
    try:
        response = requests.post(warehouse_api_url, json=Location(**warehouse_data).dict())
        response.raise_for_status()  # Raise an error for unsuccessful response (4xx or 5xx)
        print(f"Warehouse {warehouse_data['name']} added successfully.")
    except requests.exceptions.HTTPError as err:
        print(f"Error adding warehouse {warehouse_data['name']}: {err.response.text}")


user_input = input("Do you want to proceed? Enter 'S' to continue: ")

if user_input.upper() == 'S':
    # Create threads for each restaurant
    stop_event = Event()
    threads = []

    for restaurant_data in restaurants:
        thread = Thread(target=decrease_inventory_thread, args=(restaurant_data, stop_event))
        threads.append(thread)
        thread.start()

    # Prompt user to stop
    user_input = input("Type 'stop' to stop the inventory decrease threads: ")

    # Set the stop event and wait for threads to finish
    stop_event.set()
    for thread in threads:
        thread.join()

    print("Inventory decrease threads stopped.")
else:
    print("Operation aborted by the user.")
