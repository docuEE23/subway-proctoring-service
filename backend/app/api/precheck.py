from google.cloud import storage
import os
from dotenv import load_dotenv

load_dotenv()

# Instantiates a client
storage_client = storage.Client(project=os.getenv("GCP_PROJECT_NAME"))

# The name for the bucket
bucket_name = os.getenv("GCP_BUCKET_NAME")

# get the bucket
bucket = storage_client.get_bucket(bucket_or_name=bucket_name)

print(f"Bucket {bucket.name} created.")