from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from TransactionHandler import TransactionHandler
from sqlite3 import IntegrityError
from fastapi.responses import JSONResponse
import json

from typing import List
from dbOperations import (
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
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
handler = TransactionHandler()  # Create a TransactionHandler instance
origins = ["http://localhost:8000"]  # Add the origins that you want to allow
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Model for request payload
class RestaurantSearchRequest(BaseModel):
    query: str

class Inventory(BaseModel):
    inventory: float
# Model for location response and request
class Location(BaseModel):
    name: str
    locationName: str
    currentInventory: float
    maxInventory: float

@app.post("/restaurant/search", response_model=List[Location], status_code=200)
async def search_restaurants_api(request: RestaurantSearchRequest):
    
    try:
        # Assuming you have a TransactionHandler instance
        handler = TransactionHandler()
        result = search_restaurants(request.query, handler)
        final = []
        for r in result:
            currObj = Location(
                name=r[0],
                locationName=r[1],
                currentInventory=r[2],
                maxInventory=r[3]
            )
            final.append(currObj)
        return final
    except Exception as e:
        # Handle exceptions and return appropriate HTTP status codes
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/restaurant/inventory/{restaurant_name}", response_model=Location)
def get_restaurant_inventory(restaurant_name: str):

    # Get restaurant information
    restaurant_info = get_restaurant_info(restaurant_name, handler)

    if not restaurant_info:
        raise HTTPException(status_code=404, detail="Restaurant doesn't exist")
    # Map the response to RestaurantResponse
    response_model = Location(
        name=restaurant_info[0][0],
        locationName=restaurant_info[0][1],
        currentInventory=restaurant_info[0][2],
        maxInventory=restaurant_info[0][3]
    )
    
    return JSONResponse(content=response_model)

@app.post("/restaurant/")
def create_restaurant_api(restaurant_request: Location):
   
    if not restaurant_request or not restaurant_request.name or not restaurant_request.locationName or not restaurant_request.currentInventory or not restaurant_request.maxInventory:
        raise HTTPException(status_code=422, detail="Incorrect Payload format")
    try:
        # Create the restaurant
        create_restaurant(
            restaurant_request.name,
            restaurant_request.locationName,
            restaurant_request.currentInventory,
            restaurant_request.maxInventory,
            handler
        )

    except Exception as e:
        print(str(e))
        if "UNIQUE" in str(e):
            raise HTTPException(status_code=402, detail="Restaurant already exists")
        else:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

        
@app.post("/warehouse/")
async def create_warehouse_api(request: Location):

   
    if not request or not request.name or not request.locationName or not request.currentInventory or not request.maxInventory:
        raise HTTPException(status_code=422, detail="Incorrect Payload format")
    try:
        # Create the restaurant
        create_warehouse(
            request.name,
            request.locationName,
            request.currentInventory,
            request.maxInventory,
            handler
        )

    except Exception as e:
        if isinstance(e, IntegrityError):
            raise HTTPException(status_code=402, detail="Warehouse already exists")
        else:
            raise HTTPException(status_code=500, detail=f"{str(e)}")



@app.put("/restaurant/inventory/{restaurant_name}")
async def decrease_inventory_api(restaurant_name: str, request: Inventory):
    if not request or not request.inventory:
        raise HTTPException(status_code=422, detail="Incorrect Payload format")
    try:
        decrease_inventory(restaurant_name, request.inventory, handler)
        return {"message": "Inventory decreased successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/warehouse", response_model=List[Location])
async def get_all_warehouses_api():
    try:
        result = get_all_warehouses(handler)
        final = []
        for r in result:
            currObj = Location(
                name=r[0],
                locationName=r[1],
                currentInventory=r[2],
                maxInventory=r[3]
            )
            final.append(currObj)
        return JSONResponse(content=final)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/warehouse/inventory/{warehouse_name}")
async def increase_warehouse_inventory_api(warehouse_name: str, request: Inventory):
    if not request or not request.inventory:
        raise HTTPException(status_code=422, detail="Invalid Request Format")
    try:
        increase_warehouse_inventory(warehouse_name, request.inventory, handler)
        return {"message": "Warehouse inventory increased successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transfer/{warehouse_name}/{restaurant_name}")
async def transfer_inventory_api(warehouse_name: str, restaurant_name: str, request: Inventory):
    if not request or not request.inventory:
        raise HTTPException(status_code=422, detail="Invalid Request Format")
    try:
        transfer_inventory(warehouse_name, restaurant_name, request.inventory, handler)
        return {"message": "Inventory transferred successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/drop_all_tuples")
async def drop_all_tuples():
    drop_all_tuples()
    return {"message": "All tuples dropped successfully"}


if __name__ == "__main__":
    import uvicorn

    # Specify the custom port here (e.g., 8000)
    custom_port = 8080

    uvicorn.run(app, host="127.0.0.1", port=custom_port)