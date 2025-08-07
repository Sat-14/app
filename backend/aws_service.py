import boto3
from config import Config
import uuid
from datetime import datetime

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
    region_name=Config.AWS_REGION
)

def upload_receipt_to_s3(file, user_id):
    """Upload receipt image to AWS S3"""
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_extension = file.filename.split('.')[-1]
        filename = f"receipts/{user_id}/{timestamp}_{uuid.uuid4()}.{file_extension}"
        
        # Upload to S3
        s3_client.upload_fileobj(
            file,
            Config.AWS_S3_BUCKET,
            filename,
            ExtraArgs={
                'ContentType': file.content_type,
                'ACL': 'private'
            }
        )
        
        # Generate presigned URL (valid for 1 hour)
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': Config.AWS_S3_BUCKET,
                'Key': filename
            },
            ExpiresIn=3600
        )
        
        return {
            "success": True,
            "filename": filename,
            "url": url
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def delete_receipt_from_s3(filename):
    """Delete receipt from S3"""
    try:
        s3_client.delete_object(
            Bucket=Config.AWS_S3_BUCKET,
            Key=filename
        )
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_receipt_url(filename):
    """Get presigned URL for receipt"""
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': Config.AWS_S3_BUCKET,
                'Key': filename
            },
            ExpiresIn=3600
        )
        return {"success": True, "url": url}
    except Exception as e:
        return {"success": False, "error": str(e)}