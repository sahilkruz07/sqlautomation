from typing import Optional, List

class ExampleRepository:
    """
    Example repository class for data access
    Repositories handle all database operations and queries
    """
    
    def __init__(self):
        # Initialize with database connection/session if needed
        pass
    
    async def get_by_id(self, id: int) -> Optional[dict]:
        """
        Example method to fetch data by ID from database
        """
        # Database query logic here
        return {"id": id, "name": "example"}
    
    async def create(self, data: dict) -> dict:
        """
        Example method to create a new record in database
        """
        # Database insert logic here
        return {**data, "id": 1}
    
    async def update(self, id: int, data: dict) -> Optional[dict]:
        """
        Example method to update a record in database
        """
        # Database update logic here
        return {**data, "id": id}
    
    async def delete(self, id: int) -> bool:
        """
        Example method to delete a record from database
        """
        # Database delete logic here
        return True
