from init_env import AZ_BLOB_CONNECTION_STRING, AZ_BLOB_CONTAINER_NAME
from azure.storage.blob import BlobServiceClient, ContentSettings
from datetime import datetime

def generate_random_png_file_name():
    return f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}.png"

def upload_file_bytes(file_name, file_bytes, content_type="image/png"):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(
            AZ_BLOB_CONNECTION_STRING
        )
        container_client = blob_service_client.get_container_client(
            AZ_BLOB_CONTAINER_NAME
        )
        if not file_name:
            file_name = generate_random_png_file_name() if content_type == "image/png" else f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}.dat"

        blob_client = container_client.get_blob_client(file_name)

        # Explicitly delete if exists
        if blob_client.exists():
            blob_client.delete_blob()

        content_settings = ContentSettings(
            content_type=content_type,
            content_disposition="inline",
        )

        blob_client.upload_blob(
            file_bytes,
            overwrite=True,
            blob_type="BlockBlob",
            content_settings=content_settings,
            timeout=120,
        )

        print(f"File {file_name} uploaded successfully.")
        return blob_client.url

    except Exception as ex:
        print(f"Error during file upload: {ex}")
        raise