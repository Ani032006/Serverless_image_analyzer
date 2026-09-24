# PRD — Event-Driven Serverless AI Image Analyzer

## 1. Problem Statement

Manually tagging or categorizing images (for a photo archive, inventory
system, moderation queue, etc.) doesn't scale and doesn't need a
always-on server. The goal is a pipeline that reacts only when an image
actually arrives, classifies it using a managed AI service, and persists
structured results — with no server left running between events.

## 2. Goals

- Demonstrate event-driven architecture: nothing runs until an object
  lands in storage.
- Demonstrate secure service-to-service integration via scoped IAM,
  not shared credentials or admin roles.
- Demonstrate use of a managed AI API instead of a custom-trained model.
- Demonstrate schema design for a NoSQL store driven by semi-structured
  AI output (variable-length label lists, confidence scores).

## 3. Non-Goals

- Not building a user-facing upload UI (a direct-to-S3 upload, CLI, or
  the AWS Console is sufficient for the demo).
- Not training or fine-tuning a custom vision model.
- Not handling video, only static images (jpg/png).
- Not building multi-region or high-availability infrastructure — this
  is a portfolio/academic project, not a production system.

## 4. User Stories

- As the project owner, I can drop an image into a storage bucket and,
  within seconds, see structured tags for that image appear in the
  database — with no manual step in between.
- As a reviewer (professor), I can see exactly which IAM permissions
  each component holds and understand why each one is necessary.
- As a reviewer, I can trace one image through the whole pipeline (S3
  object → CloudWatch log → Rekognition response → DynamoDB item) to
  verify the system actually works, not just the diagram.

## 5. Functional Requirements

| ID | Requirement |
|---|---|
| FR1 | Uploading an image object to the designated S3 bucket/prefix triggers the Lambda function automatically via an S3 event notification. |
| FR2 | The Lambda function retrieves the uploaded image and calls Amazon Rekognition `DetectLabels` to obtain a list of labels with confidence scores. |
| FR3 | The function writes the image identifier, detected labels, confidence scores, and a timestamp to a DynamoDB table. |
| FR4 | The system supports at minimum `.jpg`/`.jpeg` and `.png` images. |
| FR5 | Failures (unsupported file type, Rekognition error, write failure) are logged to CloudWatch rather than failing silently. |
| FR6 | A simple read path (CLI script, notebook, or minimal page) can query DynamoDB by image ID and display its tags, for demo purposes. |

## 6. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR1 | **Least privilege**: every IAM role/policy grants only the specific actions and resource ARNs required — no `*` on actions or resources, no managed "FullAccess" policies. |
| NFR2 | **Cost**: pay-per-use only; no always-on compute. Should stay within AWS Free Tier for a demo-scale number of images. |
| NFR3 | **Latency**: end-to-end (upload → DynamoDB item visible) should complete in well under a minute for a single image, ideally single-digit seconds. |
| NFR4 | **Observability**: every invocation is traceable through CloudWatch Logs. |
| NFR5 | **Region consistency**: all resources deployed in a single AWS region to avoid cross-region call failures/costs. |

## 7. Architecture Summary (detail lives in the tech stack doc)

`S3 (upload event)` → `Lambda (orchestrator)` → `Rekognition (DetectLabels)` → `Lambda (writes result)` → `DynamoDB (tags table)`

## 8. Success Criteria

- End-to-end pipeline works reliably on a batch of at least 10–15 varied
  test images.
- IAM policies for both S3→Lambda and Lambda's execution role are fully
  scoped and can be explained line-by-line in the demo.
- Architecture diagram and workflow section in the consolidated document
  match what's actually deployed (no drift between the diagram and the
  real infrastructure).
- Review 1 & 2 checklist (see plan.md) complete by 24-09-2026; full
  pipeline + document complete by 17-10-2026.

## 9. Open Questions / Decisions to Make Early

- Single S3 bucket with an `incoming/` prefix, or two buckets
  (upload vs. processed)? (Recommendation: single bucket, one prefix —
  simpler IAM and event filtering.)
- DynamoDB partition key: derive from S3 object key, or generate a UUID
  per image? (Recommendation: use the S3 object key as the partition
  key — avoids a second lookup table.)
- Do results need versioning (re-processing the same image twice)? If
  not in scope, note this explicitly as Future Work in the report.
