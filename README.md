# Event-Driven Serverless AI Image Analyzer

A scalable, serverless image ingestion, classification, and analysis pipeline built on Amazon Web Services (AWS S3, Lambda, Amazon Rekognition, DynamoDB, and SQS Dead-Letter Queue).

---

## Architecture Overview

```
[ S3 Upload ] ---> [ S3 ObjectCreated Event ] ---> [ AWS Lambda (Python 3.12) ]
                                                           |
                      +------------------------------------+-----------------------------------+
                      | (Valid Image: .jpg, .png, .jpeg)                                       | (Invalid Format / Error)
                      v                                                                        v
           [ Amazon Rekognition ]                                                  [ Amazon SQS DLQ ]
           (DetectLabels API)                                                      (ImageProcessingDLQ)
                      |
                      v
           [ Amazon DynamoDB ] ---> [ AWS CloudWatch Logs ]
           (ImageTags Table)
```

---

## Repository Structure

```
CAD/
├── lambda/
│   └── handler.py                      # AWS Lambda Python 3.12 entrypoint with DLQ routing
├── iam/
│   ├── lambda-execution-policy.json    # Least-privilege IAM policy (5 scoped statements)
│   └── s3-invoke-permission.json       # S3 trigger permission policy
├── infra/
│   └── template.yaml                   # AWS SAM Infrastructure-as-Code template
├── web/                                # Review 3: Interactive browser dashboard
│   ├── index.html                      # 3-tab UI: Pipeline demo, metrics, infrastructure
│   ├── style.css                       # Responsive dark-theme dashboard styling
│   └── app.js                          # Client-side simulator logic and metrics engine
├── scripts/
│   ├── local_test.py                   # Offline test harness with mocked AWS SDK calls
│   ├── demo.py                         # 10-step interactive CLI pipeline walk-through
│   ├── load_benchmark.py               # Review 3: Multi-threaded load benchmark at scale
│   ├── benchmark_results.json          # Empirical benchmark output across 4 scenarios
│   └── sample_event.json               # S3 notification test payload
├── files/                              # Architecture planning documentation
│   ├── plan.md
│   ├── prd.md
│   └── tech-stack.md
├── submissions/                        # Official presentation, reports & speaker notes
│   ├── CAD_Review_1_2.pptx             # Presentation slide deck (Reviews 1 & 2)
│   ├── CAD_Review_1_2_Report_v2.docx   # Formatted IEEE Word Document (Reviews 1 & 2)
│   ├── CAD_Review3_Consolidated_Report.docx # Formatted IEEE Word Document (Review 3)
│   ├── Speaker_Notes_Aniruddh_Review_1_2.docx # Simplified speaker notes (Aniruddh)
│   └── Speaker_Notes_Konark_Review_1_2.docx   # Simplified speaker notes (Konark)
├── samples/                            # Sample test images for demo
├── IEEE_Consolidated_Project_Report.md # Comprehensive IEEE markdown report
├── PROJECT_OVERVIEW_AND_SPEAKER_NOTES.md # Architecture overview & defense notes
├── run_web.py                          # Local HTTP server launcher for web dashboard
└── README.md
```

---

## Quick Start & Verification

### 1. Run Unit Simulation Test
Verifies end-to-end event parsing, Rekognition payload extraction, and DynamoDB item schema:
```bash
python scripts/local_test.py
```

### 2. Run Interactive CLI Demonstration
Walks through a 10-step step-by-step verification of S3 triggers, extension validation, DLQ error paths, and batch processing:
```bash
python scripts/demo.py
```

### 3. Launch the Web Simulation Dashboard
Starts a local server and opens the interactive visual simulator:
```bash
python run_web.py
```
Open your browser at `http://localhost:8080`.

### 4. Run Multi-Threaded Load Benchmark (Review 3)
Evaluates pipeline throughput and latency under burst concurrency (10 to 250 images, concurrency 5 to 100):
```bash
python scripts/load_benchmark.py
```

---

## AWS SAM Deployment

Deploy directly to your AWS account using the AWS SAM CLI:
```bash
sam build --template infra/template.yaml
sam deploy --guided
```

---

## Review Milestones Summary

- **Review 1**: Problem statement, literature survey, decoupled architecture diagram, hardware-software specifications, and scoped IAM policy design.
- **Review 2**: Lambda handler implementation, Rekognition integration, DynamoDB schema design, and local test verification.
- **Review 3**: Amazon SQS Dead-Letter Queue (DLQ) error handling, interactive web simulation dashboard (`web/index.html`), and empirical load benchmarking at scale (`scripts/load_benchmark.py`).
