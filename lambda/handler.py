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

# Initialize AWS SDK clients outside handler for connection reuse across warm starts
s3_client = boto3.client('s3')
rekognition_client = boto3.client('rekognition')
dynamodb_client = boto3.client('dynamodb')
sqs_client = boto3.client('sqs')

# Configuration from environment variables with fallback defaults
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'ImageTags')
MIN_CONFIDENCE = float(os.environ.get('MIN_CONFIDENCE', '70.0'))
MAX_LABELS = int(os.environ.get('MAX_LABELS', '10'))
DLQ_QUEUE_URL = os.environ.get('DLQ_QUEUE_URL', '')
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}


def lambda_handler(event, context):
    """
    AWS Lambda entry point for S3 ObjectCreated event notifications.

    Review 3 Update: Integrates SQS Dead-Letter Queue (DLQ) for explicit
    error routing. Unsupported file types and processing failures are
    forwarded to ImageProcessingDLQ for inspection and retry.

    Args:
        event  : S3 event payload containing one or more Records.
        context: Lambda execution context (function name, request ID, etc.)

    Returns:
        dict: HTTP status code and summary body.
              200 = all records processed successfully.
              207 = partial success (some records failed).
              400 = no valid records found.
              500 = complete processing failure.
    """
    logger.info("Received event: %s", json.dumps(event))

    if 'Records' not in event or not event['Records']:
        logger.warning("Event contains no Records. Exiting early.")
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
            object_key  = urllib.parse.unquote_plus(
                record['s3']['object']['key'], encoding='utf-8'
            )
            file_size = record['s3']['object'].get('size', 0)

            logger.info(
                "Processing object: '%s' from bucket: '%s' (size: %d bytes)",
                object_key, bucket_name, file_size
            )

            # ── Extension Validation ────────────────────────────────────
            _, ext = os.path.splitext(object_key.lower())
            if ext not in ALLOWED_EXTENSIONS:
                warning_msg = (
                    f"Unsupported file extension '{ext}' for key '{object_key}'. "
                    "Routing to DLQ."
                )
                logger.warning(warning_msg)
                send_to_dlq(bucket_name, object_key, file_size, "UNSUPPORTED_FORMAT",
                            f"File extension '{ext}' is not in allowed set {ALLOWED_EXTENSIONS}")
                errors.append(warning_msg)
                continue

            # ── Step 1: Amazon Rekognition DetectLabels ─────────────────
            rekognition_response = call_rekognition(bucket_name, object_key)
            labels = rekognition_response.get('Labels', [])
            orientation = rekognition_response.get('OrientationCorrection', 'ROTATE_0')

            logger.info(
                "Rekognition detected %d label(s) for '%s'",
                len(labels), object_key
            )

            # ── Step 2: Format Labels for DynamoDB ──────────────────────
            formatted_labels = []
            for label in labels:
                formatted_labels.append({
                    'M': {
                        'Name':       {'S': label['Name']},
                        'Confidence': {'N': f"{label['Confidence']:.2f}"},
                        'Parents': {
                            'L': [{'S': p['Name']} for p in label.get('Parents', [])]
                        }
                    }
                })

            # ── Step 3: Persist Metadata to DynamoDB ────────────────────
            processed_at = datetime.utcnow().isoformat() + 'Z'
            db_item = {
                'ImageKey':     {'S': object_key},
                'SourceBucket': {'S': bucket_name},
                'FileSize':     {'N': str(file_size)},
                'ProcessedAt':  {'S': processed_at},
                'LabelCount':   {'N': str(len(labels))},
                'Orientation':  {'S': orientation},
                'Labels':       {'L': formatted_labels}
            }

            dynamodb_client.put_item(
                TableName=DYNAMODB_TABLE_NAME,
                Item=db_item
            )

            logger.info(
                "Successfully wrote tags for '%s' to DynamoDB table '%s'",
                object_key, DYNAMODB_TABLE_NAME
            )
            processed_count += 1

        except ClientError as ce:
            error_msg = (
                f"AWS ClientError processing '{object_key}': "
                f"{ce.response['Error']['Message']}"
            )
            logger.error(error_msg, exc_info=True)
            send_to_dlq(
                record.get('s3', {}).get('bucket', {}).get('name', 'unknown'),
                record.get('s3', {}).get('object', {}).get('key', 'unknown'),
                0,
                "AWS_CLIENT_ERROR",
                ce.response['Error']['Message']
            )
            errors.append(error_msg)

        except Exception as e:
            error_msg = f"Unexpected error processing record: {str(e)}"
            logger.error(error_msg, exc_info=True)
            send_to_dlq(
                record.get('s3', {}).get('bucket', {}).get('name', 'unknown'),
                record.get('s3', {}).get('object', {}).get('key', 'unknown'),
                0,
                "UNEXPECTED_ERROR",
                str(e)
            )
            errors.append(error_msg)

    # ── Response Status ─────────────────────────────────────────────────
    if not errors:
        status_code = 200
    elif processed_count > 0:
        status_code = 207   # Multi-Status: partial success
    else:
        status_code = 500

    return {
        'statusCode': status_code,
        'body': json.dumps({
            'message': f"Processed {processed_count} image(s) successfully",
            'errors':  errors,
            'dlq_messages_sent': len(errors)
        })
    }


def call_rekognition(bucket_name, object_key):
    """
    Invokes Amazon Rekognition DetectLabels using a direct S3 object reference.
    Binary image bytes are NOT pulled into Lambda memory — Rekognition reads
    directly from S3, reducing memory usage and avoiding re-upload overhead.
    """
    return rekognition_client.detect_labels(
        Image={
            'S3Object': {
                'Bucket': bucket_name,
                'Name':   object_key
            }
        },
        MaxLabels=MAX_LABELS,
        MinConfidence=MIN_CONFIDENCE
    )


def send_to_dlq(bucket_name, object_key, file_size, error_code, error_message):
    """
    Sends a structured failure event to the SQS Dead-Letter Queue.

    Review 3 Feature: Explicit DLQ routing provides observability into
    failed or unsupported uploads without losing event data. Each DLQ
    message includes the original S3 reference and error classification
    to support automated retry or manual inspection workflows.

    Args:
        bucket_name   : Source S3 bucket name.
        object_key    : S3 object key that failed processing.
        file_size     : File size in bytes (0 if unknown).
        error_code    : Machine-readable error classification code.
        error_message : Human-readable error description.
    """
    if not DLQ_QUEUE_URL:
        logger.warning("DLQ_QUEUE_URL not set. Skipping DLQ routing for '%s'.", object_key)
        return

    dlq_payload = {
        'errorCode':    error_code,
        'errorMessage': error_message,
        'sourceBucket': bucket_name,
        'objectKey':    object_key,
        'fileSize':     file_size,
        'failedAt':     datetime.utcnow().isoformat() + 'Z'
    }

    try:
        sqs_client.send_message(
            QueueUrl=DLQ_QUEUE_URL,
            MessageBody=json.dumps(dlq_payload)
        )
        logger.info(
            "DLQ message sent for key '%s' with error code '%s'",
            object_key, error_code
        )
    except ClientError as ce:
        logger.error(
            "Failed to send DLQ message: %s",
            ce.response['Error']['Message']
        )
