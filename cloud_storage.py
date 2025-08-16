import boto3

def upload_to_s3(file_path, bucket_name, object_name=None):
    s3_client = boto3.client('s3')
    if object_name is None:
        object_name = file_path
    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
        print(f"Uploaded {file_path} to S3 bucket {bucket_name}")
    except Exception as e:
        print(f"Upload failed: {e}")