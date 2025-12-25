from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os

class MongoDB:
    """MongoDB database connection manager"""
    
    client: Optional[AsyncIOMotorClient] = None
    database = None
    
    @classmethod
    async def connect_to_database(cls, mongodb_uri: str, db_name: str = "sqlautomation"):
        """
        Connect to MongoDB database
        
        Args:
            mongodb_uri: MongoDB connection URI
            db_name: Database name (default: sqlautomation)
        """
        try:
            # Configure TLS/SSL settings for MongoDB Atlas
            # Note: tlsAllowInvalidCertificates=True is for development only
            # For production, fix SSL certificates properly
            cls.client = AsyncIOMotorClient(
                mongodb_uri,
                tlsAllowInvalidCertificates=True,  # Development workaround for macOS SSL issues
                serverSelectionTimeoutMS=5000
            )
            cls.database = cls.client[db_name]
            # Test the connection
            await cls.client.admin.command('ping')
            print(f"✅ Connected to MongoDB database: {db_name}")
        except Exception as e:
            print(f"❌ Error connecting to MongoDB: {e}")
            raise
    
    @classmethod
    async def close_database_connection(cls):
        """Close MongoDB database connection"""
        if cls.client:
            cls.client.close()
            print("✅ MongoDB connection closed")
    
    @classmethod
    def get_database(cls):
        """Get database instance"""
        if cls.database is None:
            raise Exception("Database not connected. Call connect_to_database first.")
        return cls.database
    
    @classmethod
    def get_collection(cls, collection_name: str):
        """
        Get a collection from the database
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection instance
        """
        db = cls.get_database()
        return db[collection_name]


# Collection names
class Collections:
    """MongoDB collection names"""
    TASK_MASTER = "task_master"
    COUNTER_MASTER = "counter_master"
    ENV_CONFIG = "env_config"


# Helper function to get task_master collection
def get_task_master_collection():
    """Get task_master collection"""
    return MongoDB.get_collection(Collections.TASK_MASTER)


# Helper function to get counter_master collection
def get_counter_master_collection():
    """Get counter_master collection"""
    return MongoDB.get_collection(Collections.COUNTER_MASTER)


# Helper function to get env_config collection
def get_env_config_collection():
    """Get env_config collection"""
    return MongoDB.get_collection(Collections.ENV_CONFIG)
