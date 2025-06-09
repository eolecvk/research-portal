# src/download_data.py

import boto3
from botocore.config import Config
import os
from pathlib import Path
from src.config import (
    SUPABASE_S3_ENDPOINT_URL,
    SUPABASE_S3_REGION_NAME,
    SUPABASE_S3_ACCESS_ID,
    SUPABASE_S3_ACCESS_KEY,
    SUPABASE_S3_BUCKET_NAME,
)

def download_if_needed():
    target_dir = Path("../data/reports/JSON")
    if target_dir.exists():
        print(f"{target_dir} already exists. Skipping download.")
        return

    DOWNLOAD_DIR = Path("downloads")
    DOWNLOAD_DIR.mkdir(exist_ok=True)

    s3 = boto3.client(
        "s3",
        endpoint_url=SUPABASE_S3_ENDPOINT_URL,
        aws_access_key_id=SUPABASE_S3_ACCESS_ID,
        aws_secret_access_key=SUPABASE_S3_ACCESS_KEY,
        region_name=SUPABASE_S3_REGION_NAME,
        config=Config(signature_version="s3v4")
    )

    try:
        response = s3.list_objects_v2(Bucket=SUPABASE_S3_BUCKET_NAME)
        objects = response.get("Contents", [])
    except Exception as e:
        print(f"Failed to list objects: {e}")
        return

    if not objects:
        print("No objects found in the bucket.")
        return

    print(f"Found {len(objects)} objects. Downloading...")
    for obj in objects:
        key = obj["Key"]
        local_path = DOWNLOAD_DIR / os.path.basename(key)

        print(f"Downloading {key} -> {local_path}")
        try:
            s3.download_file(SUPABASE_S3_BUCKET_NAME, key, str(local_path))
        except Exception as e:
            print(f"Failed to download {key}: {e}")

    print("All files downloaded to 'downloads/'")
