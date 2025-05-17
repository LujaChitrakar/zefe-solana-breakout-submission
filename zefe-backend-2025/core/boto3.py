import boto3
import os
from io import BytesIO
import mimetypes
import magic
from dotenv import load_dotenv

load_dotenv()
region_name = os.environ.get("AWS_S3_REGION")
S3_CLIENT = boto3.client(
    "s3",
    region_name=region_name,
    aws_access_key_id=os.environ.get("AWS_S3_ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("AWS_S3_SECRET_KEY"),
)

bucket_name = os.environ.get("AWS_S3_BUCKET_NAME")


def get_metadata_for_file(file):
    # by getting the extension of the file try to get the content type
    content_type = mimetypes.guess_type(file)[0]
    return content_type


def upload_file_to_s3(file, key):
    with open(file, "rb") as f:
        S3_CLIENT.upload_fileobj(
            f,
            bucket_name,
            key,
            ExtraArgs={
                "ContentType": get_metadata_for_file(file),
                "ACL": "public-read",
            },
        )


def upload_temporary_file_to_s3(temporary_file, key):
    try:
        # Read the content of the file to determine the MIME type
        file_content = temporary_file.read()  # Read the file content
        temporary_file.seek(0)  # Reset the file pointer to the beginning of the file

        # Determine the MIME type using python-magic
        mime = magic.Magic(mime=True)
        content_type = mime.from_buffer(file_content)

        # Upload the file to S3 with the determined content type
        S3_CLIENT.upload_fileobj(
            temporary_file,
            bucket_name,
            key,
            ExtraArgs={
                "ContentType": content_type,
                "ACL": "public-read",
            },
        )
    except Exception as e:
        print("Exception is here", e)


def delete_file_from_s3(key):
    S3_CLIENT.delete_object(Bucket=bucket_name, Key=key)


def get_file_from_s3(key):
    return S3_CLIENT.get_object(Bucket=bucket_name, Key=key)["Body"]


def get_presigned_url(key):
    if not key:
        return None
    # url = S3_CLIENT.generate_presigned_url(
    #     "get_object", Params={"Bucket": bucket_name, "Key": key}, ExpiresIn=1800
    # )
    url = f"https://{bucket_name}.s3.amazonaws.com/{key}"
    return url
