"""
Test script to demonstrate the custom task_id system
This script shows how to initialize the counter_master collection
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def initialize_counter():
    """Initialize the counter_master collection with TASK counter"""
    # Update this connection string with your MongoDB URI
    mongodb_uri = "your_mongodb_connection_string_here"
    
    client = AsyncIOMotorClient(
        mongodb_uri,
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=5000
    )
    
    db = client["sqlautomation"]
    counter_collection = db["counter_master"]
    
    # Check if TASK counter exists
    existing = await counter_collection.find_one({"counter_type": "TASK"})
    
    if existing:
        print(f"✅ TASK counter already exists with value: {existing['counter_value']}")
    else:
        # Initialize counter
        await counter_collection.insert_one({
            "counter_type": "TASK",
            "counter_value": 0
        })
        print("✅ TASK counter initialized with value: 0")
    
    client.close()

if __name__ == "__main__":
    print("Initializing counter_master collection...")
    asyncio.run(initialize_counter())
