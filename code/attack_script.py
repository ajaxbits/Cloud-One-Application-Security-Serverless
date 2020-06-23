import boto3
import os
import sys
from pathlib import Path
from typing import Tuple

try:
    ACCESS_KEY = os.environ["AWS_ACCESS_KEY"]
    SECRET_KEY = os.environ["AWS_SECRET_KEY"]
    SESSION_TOKEN = os.environ["AWS_SESSION_TOKEN"]

except KeyError as e:
    sys.exit(f"Error: Missing environment variable - {e}")

BASE_DEST_DIR = os.environ.get("BASE_DEST_DIR", "/tmp")


def get_s3_sessions(
    access_key: str = ACCESS_KEY,
    secret_key: str = SECRET_KEY,
    session_token: str = SESSION_TOKEN,
) -> Tuple[boto3.client, boto3.resource]:
    client = boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        aws_session_token=session_token,
    )

    resource = boto3.resource(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        aws_session_token=session_token,
    )

    return client, resource


def download_objects(s3_resource: boto3.resource, bucket_name: str) -> int:
    bucket = s3_resource.Bucket(bucket_name)
    download_count = 0

    for s3_object in bucket.objects.all():
        key_path, filename = os.path.split(s3_object.key)
        object_path = os.sep.join([BASE_DEST_DIR, s3_object.bucket_name, key_path])

        Path(object_path).mkdir(parents=True, exist_ok=True)

        if not filename:
            continue

        object_file_path = os.sep.join([object_path, filename])

        print(f"Downloading: {object_file_path}")
        bucket.download_file(s3_object.key, object_file_path)
        download_count += 1

    return download_count


def download_all_buckets(s3_resource: boto3.resource, s3_buckets: dict) -> int:
    total_count = 0

    for entry in s3_buckets["Buckets"]:
        bucket_name = entry["Name"]
        print(f"Found bucket: {bucket_name}")
        objects_downloaded = download_objects(s3_resource, bucket_name)
        total_count += objects_downloaded
        print("")

    return total_count


def main() -> None:
    s3_client, s3_resource = get_s3_sessions()

    if len(sys.argv) != 2:
        sys.exit("Error: Please specify a bucket name")

    if sys.argv[1].lower() == "all":
        get_buckets = s3_client.list_buckets()
        total_count = download_all_buckets(s3_resource, get_buckets)

    else:
        bucket_name = sys.argv[1]
        print(f"Checking if {bucket_name} exists...")
        total_count = download_objects(s3_resource, bucket_name)
        print("")

    print("=" * 100)
    print(f"Successfully downloaded {total_count} files")


if __name__ == "__main__":
    main()
