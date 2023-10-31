import boto3

from app.server.config import config

sms_client = boto3.client('sns', region_name=config.AWS_REGION, aws_access_key_id=config.AWS_ACCESS_ID, aws_secret_access_key=config.AWS_SECRET_KEY)
email_client = boto3.client('ses', region_name=config.AWS_REGION, aws_access_key_id=config.AWS_ACCESS_ID, aws_secret_access_key=config.AWS_SECRET_KEY)
storage_client = boto3.client('s3', region_name=config.AWS_REGION, aws_access_key_id=config.AWS_ACCESS_ID, aws_secret_access_key=config.AWS_SECRET_KEY)
