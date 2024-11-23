import os
import logging
import azure.functions as func
from azure.cosmos import CosmosClient, PartitionKey, exceptions

COSMOS_DB_CONNECTION_STRING = os.getenv("CosmosDBConnectionString")
DATABASE_NAME = "VisitorDatabase"
TABLE_NAME = "VisitorTable"

# Initialize CosmosDB client
client = CosmosClient.from_connection_string(COSMOS_DB_CONNECTION_STRING)
database = client.create_database_if_not_exists(id=DATABASE_NAME)
container = database.create_container_if_not_exists(
    id=TABLE_NAME,
    partition_key=PartitionKey(path="/id"),
)

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Retrieve or initialize the visitor counter
        item_id = "counter"
        try:
            item = container.read_item(item_id, partition_key=item_id)
            item["count"] += 1
        except exceptions.CosmosResourceNotFoundError:
            item = {"id": item_id, "count": 1}

        container.upsert_item(item)
        return func.HttpResponse(f"Visitor count: {item['count']}")
    except Exception as e:
        logging.error(f"Error: {e}")
        return func.HttpResponse("An error occurred.", status_code=500)
