from typing import Optional, List

class ExampleService:
    """
    Example service class for business logic
    Services contain the business logic and orchestrate between controllers and repositories
    """
    
    def __init__(self):
        # Initialize with repository dependencies if needed
        pass
    
    async def get_data(self, id: int) -> dict:
        """
        Example method to retrieve data
        """
        # Business logic here
        return {"id": id, "data": "example"}
    
    async def process_data(self, data: dict) -> dict:
        """
        Example method to process data
        """
        # Business logic here
        processed = {**data, "processed": True}
        return processed
