import sys
import os
import json
from unittest.mock import MagicMock

# Mock boto3 and botocore before importing handler if boto3 is not installed in local environment
try:
    import boto3
    import botocore.exceptions
except ImportError:
    mock_boto3 = MagicMock()
    mock_botocore = MagicMock()
    mock_botocore.exceptions.ClientError = Exception
    sys.modules['boto3'] = mock_boto3
    sys.modules['botocore'] = mock_botocore
    sys.modules['botocore.exceptions'] = mock_botocore.exceptions

# Add lambda directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../lambda')))

import handler

def run_mock_test():
    print("=== Running Local Offline Simulation Test ===")

    # Load sample event
    event_path = os.path.join(os.path.dirname(__file__), 'sample_event.json')
    with open(event_path, 'r', encoding='utf-8') as f:
        sample_event = json.load(f)

    # Mock Rekognition client call
    mock_rekognition_response = {
        'Labels': [
            {
                'Name': 'Mountain',
                'Confidence': 99.45,
                'Parents': [{'Name': 'Outdoors'}, {'Name': 'Nature'}]
            },
            {
                'Name': 'Tree',
                'Confidence': 96.12,
                'Parents': [{'Name': 'Plant'}]
            },
            {
                'Name': 'Sky',
                'Confidence': 94.80,
                'Parents': []
            }
        ],
        'OrientationCorrection': 'ROTATE_0'
    }

    # Patch clients in handler
    handler.rekognition_client = MagicMock()
    handler.rekognition_client.detect_labels.return_value = mock_rekognition_response

    handler.dynamodb_client = MagicMock()
    handler.dynamodb_client.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}

    # Invoke Lambda handler
    result = handler.lambda_handler(sample_event, None)

    print("Lambda Execution Result Status Code:", result['statusCode'])
    print("Lambda Response Body:", result['body'])

    # Verify calls
    handler.rekognition_client.detect_labels.assert_called_once_with(
        Image={
            'S3Object': {
                'Bucket': 'image-analyzer-dev-bucket',
                'Name': 'incoming/sample_landscape.jpg'
            }
        },
        MaxLabels=10,
        MinConfidence=70.0
    )

    handler.dynamodb_client.put_item.assert_called_once()
    called_item = handler.dynamodb_client.put_item.call_args[1]['Item']
    print("\nValidated DynamoDB PutItem Payload:")
    print(json.dumps(called_item, indent=2))
    print("\n[SUCCESS] Simulation Test Passed Successfully!")

if __name__ == '__main__':
    run_mock_test()
