# Tech Stack — Event-Driven Serverless AI Image Analyzer

## 1. Chosen Cloud: AWS

Picked over GCP/Azure because it lines up with the AWS for Cloud
Computing coursework already underway — the IAM, S3, and Lambda concepts
transfer directly. GCP/Azure equivalents are listed per component below
in case the course later asks for a specific provider.

| Layer | AWS (chosen) | GCP equivalent | Azure equivalent |
|---|---|---|---|
| Storage | S3 | Cloud Storage | Blob Storage |
| Compute | Lambda | Cloud Functions | Azure Functions |
| AI | Rekognition | Vision API | Computer Vision |
| Database | DynamoDB | Firestore | Cosmos DB |

## 2. Component Details

### 2.1 Storage — Amazon S3
- One bucket, e.g. `image-analyzer-<yourname>-dev`.
- Uploads go under an `incoming/` prefix; keep any derived/processed
  output (if added later) in a different prefix or bucket to avoid
  trigger recursion.
- **Event notification**: `s3:ObjectCreated:*` on the `incoming/` prefix,
  filtered to `.jpg`/`.jpeg`/`.png`, targeting the Lambda function.

### 2.2 Compute — AWS Lambda
- Runtime: Python 3.12 (boto3 is bundled with the Lambda Python runtime,
  no extra layer needed for basic S3/Rekognition/DynamoDB calls).
- Trigger: S3 event notification (Phase 1); can add EventBridge later if
  you want retry/DLQ handling beyond Lambda's built-in retry.
- Timeout: set to ~30s (default 3s is too short once you add the
  Rekognition round-trip).
- Memory: 256–512 MB is plenty for this workload; higher memory also
  proportionally increases CPU, which can shorten cold starts slightly.
- Environment variables: DynamoDB table name, Rekognition min confidence
  threshold — keep these out of hardcoded strings.

### 2.3 AI Integration — Amazon Rekognition
- API: `DetectLabels` (image object detection/classification — exactly
  the "Car / Tree / Person" style tagging described in the brief).
- Input: either pass the S3 object reference directly to Rekognition
  (`S3Object: {Bucket, Name}` — Rekognition reads it itself, so the
  Lambda doesn't need to download the whole image) or download bytes
  and pass inline. **Prefer the S3-object-reference form** — it avoids
  the Lambda needing large memory/network for image bytes and is the
  standard pattern.
- Recommended params: `MaxLabels=10`, `MinConfidence=70` (tune based on
  test results — this is a good "Results and Discussion" data point).

### 2.4 Database — Amazon DynamoDB
- Table name: e.g. `ImageTags`.
- Partition key: `ImageKey` (String) — the S3 object key, so it's a
  stable, natural identifier with no extra UUID generation needed.
- Suggested attributes:
  - `ImageKey` (PK)
  - `Labels` (List of Maps: `{Name, Confidence}`)
  - `ProcessedAt` (String, ISO-8601 timestamp)
  - `SourceBucket` (String)
- Billing mode: On-Demand (pay-per-request) — no capacity planning
  needed for a demo-scale project, and it's Free-Tier friendly.

## 3. IAM — the part that actually gets graded carefully

Two separate trust relationships, each scoped as tightly as possible.

### 3.1 S3 → Lambda invoke permission
A **resource-based policy on the Lambda function** (not a role) granting
S3 permission to invoke it, scoped to the specific bucket ARN as the
source:

```json
{
  "Action": "lambda:InvokeFunction",
  "Principal": "s3.amazonaws.com",
  "SourceArn": "arn:aws:s3:::image-analyzer-<yourname>-dev",
  "SourceAccount": "<your-account-id>"
}
```

### 3.2 Lambda execution role (the function's own permissions)
A custom policy — **not** `AmazonS3FullAccess`, `AmazonRekognitionFullAccess`,
or `AmazonDynamoDBFullAccess` — scoped like this:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadUploadedImage",
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::image-analyzer-<yourname>-dev/incoming/*"
    },
    {
      "Sid": "DetectLabels",
      "Effect": "Allow",
      "Action": "rekognition:DetectLabels",
      "Resource": "*"
    },
    {
      "Sid": "WriteTags",
      "Effect": "Allow",
      "Action": "dynamodb:PutItem",
      "Resource": "arn:aws:dynamodb:<region>:<account-id>:table/ImageTags"
    },
    {
      "Sid": "Logging",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:<region>:<account-id>:*"
    }
  ]
}
```

Notes for the report/demo:
- `rekognition:DetectLabels` doesn't support resource-level scoping
  (Rekognition actions are typically `Resource: "*"`) — call this out
  explicitly rather than leaving it unexplained, since a reviewer may
  ask why it isn't scoped like the S3/DynamoDB statements.
- Every other statement **is** scoped to a specific ARN — this contrast
  is worth stating directly in the IAM section of the report as evidence
  of intentional least-privilege design, not an oversight.

## 4. Supporting Tools

| Purpose | Tool |
|---|---|
| Architecture diagram | draw.io (diagrams.net) or Lucidchart — export as PNG/SVG for the report |
| Local testing | AWS CLI + `aws lambda invoke` with sample S3 event payloads |
| IaC (optional, adds polish) | AWS SAM or a minimal CloudFormation template — lets you show reproducible infra in the report instead of "clicked around in the console" |
| Logs/debugging | CloudWatch Logs Insights |
| Version control | Git + GitHub (private repo) |

## 5. Suggested Repo Layout

```
image-analyzer/
├── lambda/
│   └── handler.py
├── infra/              # optional: SAM/CloudFormation template
│   └── template.yaml
├── iam/
│   ├── lambda-execution-policy.json
│   └── s3-invoke-permission.json
├── test-images/
├── docs/
│   ├── plan.md
│   ├── prd.md
│   └── tech-stack.md
└── README.md
```
