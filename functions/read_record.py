import json
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient
import os

COSMOS_CONN = os.environ["COSMOS_CONN"]
STORAGE_CONN = os.environ["STORAGE_CONN"]
DATABASE_NAME = "billing-db"
CONTAINER_NAME = "billing"
BLOB_CONTAINER = "archived-billing"

cosmos_client = CosmosClient.from_connection_string(COSMOS_CONN)
database = cosmos_client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)
blob_client = BlobServiceClient.from_connection_string(STORAGE_CONN).get_container_client(BLOB_CONTAINER)

def get_billing_record(record_id):
    try:
        item = container.read_item(item=record_id, partition_key=record_id)
        return item
    except:
        year_month = "2023-01"  # Replace with real logic
        blob_path = f"billing/{year_month}/{record_id}.json"
        blob_data = blob_client.download_blob(blob_path).readall()
        return json.loads(blob_data)
