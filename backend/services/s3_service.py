"""
AWS S3 service for handling image uploads
"""

import boto3
from botocore.exceptions import ClientError
import logging
import uuid
from pathlib import Path
from typing import Optional
from schemas.user import settings

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self):
        """Initialize S3 client with credentials from settings"""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.AWS_S3_BUCKET

    def upload_file(
        self,
        file_data: bytes,
        filename: str,
        content_type: str = "image/jpeg",
        folder: str = "images"
    ) -> Optional[str]:
        """
        Upload a file to S3

        Args:
            file_data: The file content as bytes
            filename: Original filename
            content_type: MIME type of the file
            folder: Folder/prefix in S3 bucket (default: "images")

        Returns:
            S3 URL of uploaded file, or None if upload failed
        """
        try:
            # Generate unique filename to prevent collisions
            file_extension = Path(filename).suffix
            clean_filename = Path(filename).stem
            unique_filename = f"{folder}/{clean_filename}_{uuid.uuid4().hex[:8]}{file_extension}"

            # Upload to S3 (private bucket - no public ACL)
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=unique_filename,
                Body=file_data,
                ContentType=content_type
            )

            # Return the S3 URL
            s3_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_filename}"
            logger.info(f"Successfully uploaded {filename} to {s3_url}")
            return s3_url

        except ClientError as e:
            logger.error(f"Failed to upload {filename} to S3: {str(e)}")
            return None

    def delete_file(self, file_url: str) -> bool:
        """
        Delete a file from S3

        Args:
            file_url: Full S3 URL of the file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract the key (filename) from the URL
            # URL format: https://bucket.s3.region.amazonaws.com/folder/filename.jpg
            key = file_url.split(f"{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/")[1]

            # Delete from S3
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )

            logger.info(f"Successfully deleted {key} from S3")
            return True

        except (ClientError, IndexError) as e:
            logger.error(f"Failed to delete file from S3: {str(e)}")
            return False

    def generate_presigned_url(self, file_url: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for temporary access to a private S3 object

        Args:
            file_url: Full S3 URL of the file
            expiration: URL expiration time in seconds (default: 1 hour)

        Returns:
            Presigned URL, or None if generation failed
        """
        try:
            # Extract the key from the URL
            key = file_url.split(f"{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/")[1]

            # Generate presigned URL
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expiration
            )

            return presigned_url

        except (ClientError, IndexError) as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            return None


# Global S3 service instance
s3_service = S3Service()
