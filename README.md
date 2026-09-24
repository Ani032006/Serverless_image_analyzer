# Event-Driven Serverless AI Image Analyzer

A scalable, serverless image ingestion and classification pipeline built on AWS (S3, Lambda, Amazon Rekognition, and DynamoDB).

## Repository Structure

```
CAD/
├── lambda/
│   └── handler.py                      # AWS Lambda Python 3.12 entrypoint
├── iam/
│   ├── lambda-execution-policy.json    # Least-privilege IAM policy
│   └── s3-invoke-permission.json       # S3 trigger permission policy
├── infra/
│   └── template.yaml                   # AWS SAM / CloudFormation template
├── scripts/
│   ├── local_test.py                   # Offline test harness with AWS mocks
│   └── sample_event.json               # S3 notification test payload
├── files/                              # Project planning documents
│   ├── plan.md
│   ├── prd.md
│   └── tech-stack.md
├── IEEE_Consolidated_Project_Report.md # Main project report (Review 1 & 2 + Review 3)
└── README.md
```

## Quick Start (Local Verification)

Run the local offline test simulation:
```bash
python scripts/local_test.py
```

## AWS SAM Deployment

Deploy directly to your AWS account using AWS SAM CLI:
```bash
sam build --template infra/template.yaml
sam deploy --guided
```
