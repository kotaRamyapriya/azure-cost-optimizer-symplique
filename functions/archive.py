from datetime import datetime, timedelta
import json
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient
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

def archive_old_records():
    threshold_date = (datetime.utcnow() - timedelta(days=90)).isoformat()
    query = f"SELECT * FROM c WHERE c.date < '{threshold_date}'"
    for item in container.query_items(query=query, enable_cross_partition_query=True):
        record_id = item['id']
        blob_path = f"billing/{item['date'][:7]}/{record_id}.json"
        blob_client.upload_blob(blob_path, json.dumps(item), overwrite=True)
        container.delete_item(item, partition_key=item['partitionKey'])
