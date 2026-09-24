import os
import json
import logging
import urllib.parse
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

# Configure structured logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS SDK clients outside handler for connection reuse across cold starts
s3_client = boto3.client('s3')
rekognition_client = boto3.client('rekognition')
dynamodb_client = boto3.client('dynamodb')

# Configuration from environment variables with fallback defaults
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'ImageTags')
MIN_CONFIDENCE = float(os.environ.get('MIN_CONFIDENCE', '70.0'))
MAX_LABELS = int(os.environ.get('MAX_LABELS', '10'))
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

def lambda_handler(event, context):
    """
    AWS Lambda entry point for S3 ObjectCreated event notifications.
    Processes uploaded images using Amazon Rekognition DetectLabels API
    and persists structured metadata into Amazon DynamoDB.
    """
    logger.info("Received event: %s", json.dumps(event))

    if 'Records' not in event or not event['Records']:
        logger.warning("Event contains no Records statement. Exiting.")
        return {'statusCode': 400, 'body': 'No records found'}

    processed_count = 0
    errors = []

    for record in event['Records']:
        event_name = record.get('eventName', '')
        if not event_name.startswith('ObjectCreated:'):
            logger.info("Ignoring non-creation event: %s", event_name)
            continue

        try:
            bucket_name = record['s3']['bucket']['name']
            object_key = urllib.parse.unquote_plus(record['s3']['object']['key'], encoding='utf-8')
            file_size = record['s3']['object'].get('size', 0)

            logger.info("Processing object key: '%s' from bucket: '%s' (Size: %d bytes)",
                        object_key, bucket_name, file_size)

            # Validate file extension
            _, ext = os.path.splitext(object_key.lower())
            if ext not in ALLOWED_EXTENSIONS:
                logger.warning("Unsupported file extension '%s' for key '%s'. Skipping.", ext, object_key)
                continue

            # Step 1: Call Amazon Rekognition DetectLabels using direct S3 reference
            rekognition_response = call_rekognition(bucket_name, object_key)
            labels = rekognition_response.get('Labels', [])
            orientation = rekognition_response.get('OrientationCorrection', 'ROTATE_0')

            logger.info("Rekognition detected %d labels for '%s'", len(labels), object_key)

            # Step 2: Format labels for DynamoDB
            formatted_labels = []
            for label in labels:
                formatted_labels.append({
                    'M': {
                        'Name': {'S': label['Name']},
                        'Confidence': {'N': f"{label['Confidence']:.2f}"},
                        'Parents': {
                            'L': [{'S': parent['Name']} for parent in label.get('Parents', [])]
                        }
                    }
                })

            # Step 3: Write metadata item to DynamoDB
            processed_at = datetime.utcnow().isoformat() + 'Z'
            db_item = {
                'ImageKey': {'S': object_key},
                'SourceBucket': {'S': bucket_name},
                'FileSize': {'N': str(file_size)},
                'ProcessedAt': {'S': processed_at},
                'LabelCount': {'N': str(len(labels))},
                'Orientation': {'S': orientation},
                'Labels': {'L': formatted_labels}
            }

            dynamodb_client.put_item(
                TableName=DYNAMODB_TABLE_NAME,
                Item=db_item
            )

            logger.info("Successfully wrote tags for '%s' to DynamoDB table '%s'",
                        object_key, DYNAMODB_TABLE_NAME)
            processed_count += 1

        except ClientError as ce:
            error_msg = f"AWS ClientError processing record: {ce.response['Error']['Message']}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error processing record: {str(e)}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)

    status_code = 200 if not errors else (207 if processed_count > 0 else 500)
    return {
        'statusCode': status_code,
        'body': json.dumps({
            'message': f"Processed {processed_count} images successfully",
            'errors': errors
        })
    }

def call_rekognition(bucket_name, object_key):
    """
    Invokes Amazon Rekognition DetectLabels API using S3 object reference.
    """
    return rekognition_client.detect_labels(
        Image={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': object_key
            }
        },
        MaxLabels=MAX_LABELS,
        MinConfidence=MIN_CONFIDENCE
    )
