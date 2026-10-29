# IEEE Consolidated Project Document
## Event-Driven Serverless AI Image Tagging and Analysis Pipeline using AWS S3, Lambda, Rekognition, and DynamoDB

**Course Code / Title**: E1 & E2: Cloud Architecture and Solution  
**Review Stage**: Reviews 1, 2, and 3 Combined (30 Marks Evaluation)  
**Review 1 & 2 Window**: September 21, 2026 to September 24, 2026 (20 Marks)  
**Review 3 Window**: October 12, 2026 to October 17, 2026 (10 Marks)  
**Document Status**: Consolidated Project Document (Version 2.0: All Reviews Completed)  

**Team Members (Team Size: 2)**:
1. **Aniruddh V K (24BAI1490) (Team Lead & Cloud Architect)**: Infrastructure Provisioning, S3 Storage Configuration, Serverless FaaS Orchestration, Scoped IAM Policy Design, SQS DLQ Integration, and Web Frontend Development (Review 3).
2. **Konark Verma (24BAI1533) (AI Integration & Data Engineer)**: Amazon Rekognition Service Integration, NoSQL Data Schema Design (DynamoDB), Test Simulation, Latency Benchmarking, and Load Testing at Scale (Review 3).

---

### Abstract
Any application that stores user-uploaded images — product catalogues, surveillance feeds, media archives — eventually needs a way to tag and sort them. Running a server around the clock just to wait for uploads is wasteful. This project builds an event-driven serverless pipeline on AWS that handles the tagging automatically: upload an image to S3, a Lambda function picks it up, calls Rekognition `DetectLabels`, and writes the results to a DynamoDB table called `ImageTags`. Nothing runs when nothing is being uploaded.

In Review 3 we added an SQS Dead-Letter Queue so invalid files and processing failures don't get silently dropped, a browser-based dashboard (`web/index.html`) that visualizes the pipeline end-to-end, and a multi-threaded load benchmark (`scripts/load_benchmark.py`) that pushes up to 250 concurrent invocations to see where things break.

IAM policies are scoped to specific ARNs and actions throughout. Under load testing, p95 latency stayed below 905 ms. Rekognition inference (380–620 ms) accounts for the bulk of that. When idle, cost is zero.

**Keywords**: Serverless Computing, Event-Driven Architecture, Artificial Intelligence, Image Classification, AWS Lambda, Amazon Rekognition, Least-Privilege IAM, NoSQL, Amazon DynamoDB, SQS Dead-Letter Queue, Load Benchmarking.

---

### 1. Introduction

#### 1.1 Background and Motivation
If you run an e-commerce site or a photo archive, at some point you need to tag the images so people can search them. The usual approach is to keep a VM or Kubernetes pod running with a vision model loaded. That works, but it has problems. The VM bills by the hour whether anyone is uploading or not. Somebody has to patch the OS, update the container runtime, and tune the load balancer. And if traffic spikes, spinning up more VMs takes 2–5 minutes — too slow.

Serverless flips this around. Lambda doesn't run until an event fires. AWS spins up a container, runs your function, and tears it down. You pay per millisecond of actual execution. No uploads, no cost.

#### 1.2 Problem Statement
The goal of this project is to construct an automated image tagging pipeline that:
- Triggers immediately upon image upload to Amazon S3 without polling loops or manual intervention.
- Calls Amazon Rekognition `DetectLabels` to extract object names and confidence scores.
- Persists structured metadata (label arrays, confidence values, parent categories, timestamps) into DynamoDB.
- Enforces scoped IAM execution policies giving each AWS service minimal required operational rights.
- Routes invalid file formats and processing failures to an SQS Dead-Letter Queue (DLQ) for error recovery (Review 3).

#### 1.3 Team Division of Responsibilities
Responsibilities across the two-member project team are split as follows:
- **Aniruddh V K (24BAI1490)**: Responsible for AWS SAM Infrastructure-as-Code (`infra/template.yaml`), S3 bucket event notifications, AWS Lambda execution configuration, IAM policy scoping, SQS DLQ resource provisioning, and web frontend development (Review 3).
- **Konark Verma (24BAI1533)**: Responsible for Amazon Rekognition `boto3` API integration, DynamoDB schema design, local test harness implementation (`scripts/local_test.py`), interactive demo generation (`scripts/demo.py`), latency benchmarking, and load testing at scale (`scripts/load_benchmark.py`) (Review 3).

---

### 2. Related Works

The main design question for image processing on the cloud is: do you run your own model, or call a managed API? Each approach has different cost, latency, and maintenance trade-offs.

| Reference / Dimension | Traditional VM / Container Architecture | Custom Model on FaaS (e.g., PyTorch on Lambda) | Managed Event-Driven AI Pipeline (Proposed) |
|---|---|---|---|
| **Compute Idle Cost** | Continuous (24/7 billing) | Zero idle cost | Zero idle cost |
| **Scaling Dynamics** | Scale-out delay (2 to 5 min) | Rapid FaaS scale (1 to 2 sec) | Sub-second event-driven scale |
| **Cold Start Latency** | None (always running) | High (3 to 10 sec due to ML model weights) | Low (200 to 400 ms) |
| **Security Surface** | Large (OS + Container vulnerabilities) | Medium (runtime dependencies) | Minimal (managed AWS IAM per-action) |
| **Maintenance Burden** | High (patching, scaling rules) | Medium (model retraining/updating) | Zero infrastructure management |
| **Error Recovery** | Manual log inspection | Custom retry logic required | SQS DLQ automatic routing (Review 3) |

**Table 1**: Comparative matrix of image processing deployment models.

Roberts and Chapin [1] and the Berkeley serverless paper by Jonas et al. [2] both argue that FaaS cuts cost for bursty workloads. The catch with running PyTorch or TensorFlow inside Lambda is cold start — importing model weights adds 3–10 seconds of startup delay [3]. Rekognition [4] sidesteps this because the model is already loaded on Amazon's side; our Lambda just makes an HTTP call. On security, AWS's own documentation [5] is clear that scoped IAM policies should be the default, not something you add later — over-permissioned roles are one of the most common cloud misconfigurations. Leitner et al. [6] cover SQS Dead-Letter Queues as the standard pattern for handling async failures in serverless pipelines.

---

### 3. Proposed Methodology

#### 3.1 Architectural Principles
Five rules guided the design:
1. **Event-driven execution**: Nothing runs until S3 fires an `s3:ObjectCreated:*` notification. No polling.
2. **Stateless compute**: Each Lambda invocation is independent — no shared memory, no session.
3. **Managed AI inference**: We call Rekognition's `DetectLabels` instead of loading our own model. This means we can't fine-tune the model for specific domains, but we also don't have to maintain it.
4. **Least-privilege security**: Every IAM statement names specific actions and ARNs. The one wildcard (`Resource: "*"` for Rekognition) is because the `DetectLabels` API doesn't support resource-level ARNs — it's an AWS limitation, not a shortcut on our part.
5. **Explicit error routing**: Invalid files and processing errors go to an SQS Dead-Letter Queue. Before Review 3, a failed image was just a log line. Now it's a recoverable message (Review 3).

#### 3.2 System Architecture Overview
The pipeline consists of five architectural layers in Review 3:
- **Storage Layer**: Amazon S3 bucket (`image-analyzer-dev-bucket`) configured with an `incoming/` prefix filter.
- **Compute Layer**: AWS Lambda function (`ImageAnalyzerFunction`) executing on Python 3.12.
- **AI Analytics Layer**: Amazon Rekognition vision engine (`DetectLabels` API).
- **Database Layer**: Amazon DynamoDB NoSQL table (`ImageTags`) operating in On-Demand capacity mode.
- **Error Recovery Layer**: Amazon SQS Dead-Letter Queue (`ImageProcessingDLQ`) for failed or invalid invocations (Review 3 Addition).

```
+------------------+      S3 ObjectCreated      +------------------------+
|  Amazon S3       | -------------------------> |  AWS Lambda            |
|  (incoming/*)    |                            |  handler.py (Py 3.12)  |
+------------------+                            +------------------------+
                                                    |              |
                            (Valid Image)           |              | (Invalid / Error)
                                                    v              v
                                        +-----------+    +---------+----------+
                                        | Amazon    |    | Amazon SQS DLQ     |
                                        | Rekog.    |    | ImageProcessingDLQ |
                                        +-----------+    +--------------------+
                                              |
                                    (Labels Returned)
                                              v
                                        +-----------+    +-------------------+
                                        | DynamoDB  |    | CloudWatch Logs   |
                                        | ImageTags |    | (Structured JSON) |
                                        +-----------+    +-------------------+
```
**Fig. 1**: Architecture Diagram of the Event-Driven Serverless AI Image Analyzer (Review 3 with DLQ).

---

### 4. Architecture Diagram and Workflow

#### 4.1 Detailed Sequential Workflow (Review 3 Updated)
Execution follows six sequential stages:

1. **Upload Phase**: An image file (`.jpg`, `.jpeg`, or `.png`) is written to `s3://image-analyzer-dev-bucket/incoming/`.
2. **Notification Phase**: Amazon S3 generates an `s3:ObjectCreated:Put` event notification payload and invokes the registered AWS Lambda ARN.
3. **Extraction & Validation Phase**: The Lambda handler decodes the S3 key and checks the file extension. If the format is invalid (e.g., `.pdf` or `.csv`), the handler calls `send_to_dlq()`, logs a warning, and skips Rekognition inference (Review 3).
4. **AI Inference Phase**: Lambda passes the S3 bucket and object key reference directly to `rekognition.detect_labels()`. Binary image data remains inside S3 and is not pulled into Lambda memory.
5. **Persistence Phase**: Rekognition returns detected labels, confidence percentages, and parent categories. Lambda formats these into DynamoDB attribute types and issues a `PutItem` request to `ImageTags`.
6. **Error Recovery Phase**: If a `ClientError` or unexpected exception occurs during processing, `send_to_dlq()` packages the event with error classification tags into SQS for a 14-day retention window (Review 3).

```
[ User / App ] ==> Upload Image ==> [ S3 Bucket: incoming/ ]
                                              |
                                    (s3:ObjectCreated)
                                              v
                                    [ AWS Lambda Handler ]
                                              |
                       +----------------------+---------------------+
                       | Extension valid?                           |
                       | YES                                        | NO
                       v                                            v
             [ Rekognition API ]                        [ SQS DLQ: ImageProcessingDLQ ]
                       |                                  (UNSUPPORTED_FORMAT event)
             (Labels Returned)
                       v
             [ DynamoDB: ImageTags ] ==> [ CloudWatch Logs ]
```
**Fig. 2**: Updated Sequential Data Flow with DLQ Error Branch (Review 3).

---

### 5. Algorithm and Mathematical Formulations

#### 5.1 Confidence Score Thresholding Formula
Amazon Rekognition assigns a confidence score $C(l) \in [0.0, 100.0]$ for each detected visual concept $l \in L_{\text{candidate}}$. The persisted output label set $L_{\text{output}}$ is defined as:

$$\text{Eq. 1: } \quad L_{\text{output}} = \Big\{ l \;\Big|\; l \in L_{\text{candidate}}, \, C(l) \ge \tau, \, \text{Rank}(C(l)) \le N \Big\}$$

Where:
- $\tau = 70.0\%$ specifies the minimum confidence cutoff threshold.
- $N = 10$ specifies the maximum label count returned per image.

#### 5.2 Latency Composition Model
Total end-to-end processing latency $T_{\text{total}}$ is expressed as:

$$\text{Eq. 2: } \quad T_{\text{total}} = T_{\text{s3\_notify}} + T_{\text{lambda\_init}} + T_{\text{rekognition}} + T_{\text{dynamodb\_write}}$$

Measured latency ranges per component:
- $T_{\text{s3\_notify}}$: S3 notification delivery delay (50 to 150 ms).
- $T_{\text{lambda\_init}}$: FaaS execution environment setup (Cold start: 200 to 350 ms; Warm start: 5 to 25 ms).
- $T_{\text{rekognition}}$: Amazon Rekognition `DetectLabels` API response latency (380 to 620 ms).
- $T_{\text{dynamodb\_write}}$: DynamoDB `PutItem` API persistence latency (12 to 38 ms).

#### 5.3 Cost Formulation Model
Cost per image inference $\text{Cost}_{\text{image}}$ is calculated via:

$$\text{Eq. 3: } \quad \text{Cost}_{\text{image}} = \text{Cost}_{\text{S3\_PUT}} + \left( M_{\text{Lambda}} \times T_{\text{exec}} \times P_{\text{GB-sec}} \right) + P_{\text{Rekognition}} + P_{\text{DynamoDB\_WCU}} + P_{\text{SQS\_msg}}$$

Baseline parameters:
- $M_{\text{Lambda}} = 0.25 \text{ GB}$ (256 MB RAM allocation).
- $P_{\text{GB-sec}} = \$0.0000166667 \text{ per GB-second}$.
- $P_{\text{Rekognition}} = \$0.001 \text{ per image}$.
- $P_{\text{DynamoDB\_WCU}} = \$0.00000125 \text{ per write unit}$.
- $P_{\text{SQS\_msg}} = \$0.0000004 \text{ per DLQ message sent}$.

#### 5.4 DLQ Routing Decision Formula (Review 3)
The error routing decision function $D(f)$ for an incoming file $f$ is defined as:

$$\text{Eq. 4: } \quad D(f) = \begin{cases} \text{PROCESS}, & \text{if } \text{ext}(f) \in \{\text{.jpg, .jpeg, .png}\} \land \text{no ClientError} \\ \text{DLQ\_ROUTE}, & \text{otherwise} \end{cases}$$

The DLQ message payload contains the schema:
$$\text{Payload} = \{\text{errorCode}, \text{errorMessage}, \text{sourceBucket}, \text{objectKey}, \text{fileSize}, \text{failedAt}\}$$

#### 5.5 Processing Algorithm Pseudocode (Review 3 Updated)

```
================================================================================
Algorithm 1 (v2): S3 Event-Driven Rekognition Tagging with DLQ Error Routing
================================================================================
Input  : Event Payload E from S3, Context C
Output : Status Code S, Execution Logs L

1: Procedure LambdaHandler(E, C)
2:   If E.Records is Empty Then
3:     Return Status(400, "No Records Found")
4:   End If
5:   
6:   For Each record In E.Records Do
7:     bucket  <-- record.s3.bucket.name
8:     rawKey  <-- record.s3.object.key
9:     key     <-- URLDecode(rawKey)
10:    ext     <-- GetExtension(key)
11:    
12:    If ext Not In {".jpg", ".jpeg", ".png"} Then
13:      SendToDLQ(bucket, key, "UNSUPPORTED_FORMAT")   // Review 3 addition
14:      Continue Loop
15:    End If
16:    
17:    Try:
18:      rekogResp <-- Rekognition.DetectLabels(
19:                      Image={ S3Object: { Bucket: bucket, Name: key } },
20:                      MaxLabels: 10,
21:                      MinConfidence: 70.0
22:                    )
23:      formattedLabels <-- FormatLabels(rekogResp.Labels)
24:      dbItem <-- BuildDBItem(key, bucket, record.size, formattedLabels)
25:      DynamoDB.PutItem(Table: "ImageTags", Item: dbItem)
26:      processed_count += 1
27:    Except ClientError as ce:
28:      SendToDLQ(bucket, key, "AWS_CLIENT_ERROR")      // Review 3 addition
29:    Except Exception as e:
30:      SendToDLQ(bucket, key, "UNEXPECTED_ERROR")      // Review 3 addition
31:  End For
32:  
33:  Return Status(200 | 207 | 500)
34: End Procedure
================================================================================
Procedure SendToDLQ(bucket, key, errorCode):
  payload = {errorCode, sourceBucket: bucket, objectKey: key, failedAt: ISO8601Timestamp()}
  SQS.SendMessage(QueueUrl: DLQ_QUEUE_URL, MessageBody: JSON(payload))
================================================================================
```

---

### 6. Security Analysis and Least-Privilege IAM Policy

IAM policy design restricts execution credentials to explicit API calls and target ARNs. Review 3 introduces a fifth policy statement allowing `sqs:SendMessage` restricted exclusively to the `ImageProcessingDLQ` queue ARN.

#### 6.1 IAM Execution Policy Scoping (Review 3 Updated)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadS3UploadedImage",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::image-analyzer-dev-bucket/incoming/*"
    },
    {
      "Sid": "InvokeRekognitionDetectLabels",
      "Effect": "Allow",
      "Action": [
        "rekognition:DetectLabels"
      ],
      "Resource": "*"
    },
    {
      "Sid": "WriteDynamoDBImageTags",
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/ImageTags"
    },
    {
      "Sid": "SendSQSDLQMessage",
      "Effect": "Allow",
      "Action": [
        "sqs:SendMessage"
      ],
      "Resource": "arn:aws:sqs:us-east-1:123456789012:ImageProcessingDLQ"
    },
    {
      "Sid": "CloudWatchLoggingPermissions",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/ImageAnalyzerFunction:*"
    }
  ]
}
```

| Statement ID | Action Allowed | Target Resource Scoping | Justification & Least-Privilege Principle |
|---|---|---|---|
| `ReadS3UploadedImage` | `s3:GetObject` | `arn:aws:s3:::.../incoming/*` | Restricts read permissions strictly to the `incoming/` object key prefix. |
| `InvokeRekognitionDetectLabels` | `rekognition:DetectLabels` | `*` | Amazon Rekognition `DetectLabels` action does not support resource-level ARNs (documented AWS API limitation). |
| `WriteDynamoDBImageTags` | `dynamodb:PutItem` | `arn:aws:dynamodb:...:table/ImageTags` | Restricts write capability to the `ImageTags` table ARN. |
| `SendSQSDLQMessage (Review 3)` | `sqs:SendMessage` | `arn:aws:sqs:...:ImageProcessingDLQ` | Restricts queue write access exclusively to the designated DLQ ARN. |
| `CloudWatchLoggingPermissions` | `logs:CreateLogGroup`, `PutLogEvents` | `arn:aws:logs:...:log-group:/aws/lambda/...` | Limits log creation rights to the function's own CloudWatch log group. |

**Table 2**: IAM Policy Permission Scoping and Security Matrix (5 statements after Review 3).

---

### 7. Implementation, Results, and Discussion

#### 7.1 Local Test Simulation Results (Reviews 1 & 2)
System execution was validated locally using `scripts/local_test.py` with `unittest.mock` patching `boto3` clients.

```json
{
  "ImageKey": {
    "S": "incoming/sample_landscape.jpg"
  },
  "SourceBucket": {
    "S": "image-analyzer-dev-bucket"
  },
  "FileSize": {
    "N": "1048576"
  },
  "ProcessedAt": {
    "S": "2026-09-03T16:13:02.006579Z"
  },
  "LabelCount": {
    "N": "3"
  },
  "Orientation": {
    "S": "ROTATE_0"
  },
  "Labels": {
    "L": [
      {
        "M": {
          "Name": { "S": "Mountain" },
          "Confidence": { "N": "99.45" },
          "Parents": { "L": [{ "S": "Outdoors" }, { "S": "Nature" }] }
        }
      },
      {
        "M": {
          "Name": { "S": "Tree" },
          "Confidence": { "N": "96.12" },
          "Parents": { "L": [{ "S": "Plant" }] }
        }
      },
      {
        "M": {
          "Name": { "S": "Sky" },
          "Confidence": { "N": "94.80" },
          "Parents": { "L": [] }
        }
      }
    ]
  }
}
```
*Listing 1: Formatted DynamoDB item generated during local execution test.*

#### 7.2 4-Image Baseline Benchmark Results (Reviews 1 & 2)
We tested with four images from different categories. All were clean, well-lit photos — the kind where Rekognition performs best.

| Test Case Image | Format / File Size | Detected Labels ($\ge 70\%$ Conf) | Top Label Confidence | Lambda Exec Time ($T_{\text{exec}}$) | Total Latency ($T_{\text{total}}$) | DynamoDB Write Status |
|---|---|---|---|---|---|---|
| `landscape_01.jpg` | JPG / $1.05 \text{ MB}$ | Mountain, Tree, Sky, Nature | $99.45\%$ | $412 \text{ ms}$ | $580 \text{ ms}$ | Success (HTTP 200) |
| `urban_street.png` | PNG / $2.30 \text{ MB}$ | Car, Vehicle, Building, Road | $98.80\%$ | $485 \text{ ms}$ | $690 \text{ ms}$ | Success (HTTP 200) |
| `office_desk.jpeg` | JPEG / $850 \text{ KB}$ | Laptop, Computer, Desk, Office | $97.10\%$ | $388 \text{ ms}$ | $520 \text{ ms}$ | Success (HTTP 200) |
| `portrait_user.jpg` | JPG / $1.80 \text{ MB}$ | Person, Human, Face, Smile | $99.12\%$ | $440 \text{ ms}$ | $610 \text{ ms}$ | Success (HTTP 200) |

**Table 3**: Baseline latency and accuracy benchmark results (4 images).

One thing worth noting: the PNG file (2.30 MB) took noticeably longer than the smaller JPEGs, which makes sense — more bytes for Rekognition to decode. We initially set the confidence threshold at 80%, but that caused Rekognition to drop valid parent-category labels like "Nature" and "Plant" that fell in the 70–79% range. After a few rounds of testing we settled on 70% as the cutoff.

#### 7.3 Review 3: Dead-Letter Queue (DLQ) Integration
Before Review 3, if someone uploaded a `.pdf` or if Rekognition threw an error, the handler logged a warning and moved on. The file was effectively lost — nobody got notified, and there was no way to retry. The SQS Dead-Letter Queue (`ImageProcessingDLQ`) fixes this. Failed events now land in a queue with a 14-day retention window, tagged with an error code so you can tell what went wrong.

| Event Type | Trigger Condition | DLQ Error Code | DynamoDB Write |
|---|---|---|---|
| Invalid Format | Extension not in {`.jpg`, `.jpeg`, `.png`} | `UNSUPPORTED_FORMAT` | No |
| Rekognition Error | AWS ClientError from `detect_labels()` | `AWS_CLIENT_ERROR` | No |
| Unexpected Error | Python runtime error | `UNEXPECTED_ERROR` | No |
| Valid Image | Extension valid, inference successful | N/A (not sent) | Yes |

**Table 4**: DLQ Routing Decision Matrix: Review 3.

One design choice we went back and forth on: whether to DLQ unsupported file formats or just silently skip them. We decided to DLQ them because in a production system, a spike of `.pdf` uploads hitting the bucket probably means something is misconfigured upstream, and someone should know about it.

#### 7.4 Review 3: Interactive Web Simulation Dashboard
A browser-based client dashboard (`web/index.html`) was developed using vanilla HTML, CSS, and JavaScript. It provides:
1. **Pipeline Demo Tab**: Visual 5-step animated diagram lighting up active AWS services in real time, threshold/label sliders, DLQ simulation toggle, detected label display with confidence bars, real-time console log, DynamoDB JSON viewer, and SQS DLQ event viewer.
2. **Metrics Dashboard Tab**: Four aggregate metric cards (average latency, top confidence, cost per image, idle cost), two bar charts for latency and confidence distributions, and an itemized cost projection table.
3. **Infrastructure Tab**: High-level AWS architecture diagram, embedded AWS SAM `template.yaml`, and a service configuration matrix.

#### 7.5 Review 3: Load Benchmark at Scale
We wrote a multi-threaded benchmark script (`scripts/load_benchmark.py`) and ran it across four scenarios to see how the pipeline holds up under pressure.

| Scenario | Batch Size | Concurrency | Avg Latency | p95 Latency | DLQ Routed | Success Rate |
|---|---|---|---|---|---|---|
| A: Low-Volume | 10 | 5 | 669.3 ms | 859 ms | 1 | 90.0% |
| B: Medium-Volume | 50 | 20 | 515.9 ms | 865 ms | 15 | 70.0% |
| C: High-Volume | 100 | 50 | 557.7 ms | 889 ms | 25 | 75.0% |
| D: Burst Load | 250 | 100 | 590.0 ms | 903 ms | 50 | 80.0% |

**Table 5**: Load Benchmark Results across 4 concurrency scenarios (`scripts/load_benchmark.py`).

A few things stood out. p95 latency stayed under 905 ms even at 250 concurrent requests, which was better than we expected — we thought Rekognition might start throttling around 100. Rekognition inference (500–540 ms on average) is the clear bottleneck, eating over 85% of total execution time. Lambda's own warm runtime stays under 25 ms, so there's not much to optimize on the compute side. The DLQ dispatch adds about 5 ms per message and doesn't block the main processing loop.

One number that surprised us: Scenario A (10 images, 5 threads) had the highest average latency at 669 ms. This is likely because the first few invocations hit cold starts, and with only 10 total invocations, those cold starts drag the average up more than in larger batches where warm invocations dominate.

#### 7.6 Cost Analysis
Under low volume or evaluation workloads, system costs fall entirely within the AWS Free Tier:
- **AWS Lambda**: 1 million free requests per month.
- **Amazon Rekognition**: 5,000 free image inferences per month during the first 12 months.
- **Amazon DynamoDB**: 25 GB storage and 25 write capacity units free.
- **Amazon SQS**: 1 million free requests per month.
- **Paid Tier Estimate**: Beyond free allowances, processing 1,000 images costs approximately $1.01 (derived almost exclusively from Rekognition API fees at $0.001 per call).

---

### 8. Conclusion

The pipeline does what we set out to build: upload an image, get tags in DynamoDB, pay nothing when idle. The DLQ addition in Review 3 was probably the most important change — before that, failed images just disappeared into a log line. Now they're recoverable.

The load benchmark confirmed that Rekognition is the bottleneck, not Lambda. If latency requirements ever dropped below 400 ms, we'd need to look at a different inference approach entirely — possibly a lightweight custom model on Lambda with a smaller weight footprint, though that brings back cold-start problems.

We should be honest about what we didn't test. All our benchmark images were clean JPEGs and PNGs under 3 MB. We haven't tried heavily compressed JPEG artifacts (quality below 20), motion-blurred surveillance frames, night-vision IR images, or images with dozens of small overlapping objects. Rekognition's confidence scores would almost certainly drop on those inputs, and some objects might not get detected at all. We also can't fine-tune Rekognition — if you needed to distinguish 50 breeds of dogs, the generic labels ("Dog", "Canine", "Animal") wouldn't be enough, and you'd need a custom SageMaker endpoint instead.

---

### 9. Future Work

Remaining production enhancements beyond the scope of Review 3:
1. **Automated DLQ Replay**: Implementing a secondary Lambda function triggered by DLQ depth alarms to reprocess messages after upstream issues resolve.
2. **Multi-Region Redundancy**: Deploying cross-region S3 replication and global DynamoDB tables for disaster recovery.
3. **Custom Model Endpoint Integration**: Allowing seamless toggling between Rekognition and custom Amazon SageMaker serverless inference endpoints for domain-specific taxonomy.

---

### 10. References

1. M. Roberts and J. Chapin, *What is Serverless Architecture?*, O'Reilly Media, Inc., 2017.
2. E. Jonas, J. Schleier-Smith, V. Sreekanti, C. Tsai, A. Khandelwal, Q. Pu, V. Shankar, J. Carreira, K. Krauth, Y. Yadwadkar, J. Gonzalez, R. A. Popa, I. Stoica, and D. A. Patterson, "Cloud Programming Simplified: A Berkeley View on Serverless Computing," *arXiv preprint arXiv:1902.03383*, 2019.
3. L. Wang, M. Li, Y. Zhang, T. Ristenpart, and M. Swift, "Peeking Behind the Curtains of Serverless Platforms," in *Proceedings of the 2018 USENIX Annual Technical Conference (ATC)*, 2018, pp. 133-146.
4. Amazon Web Services, *Amazon Rekognition Developer Guide: Detecting Labels in an Image*, AWS Documentation, 2026. [Online]. Available: https://docs.aws.amazon.com/rekognition/
5. Amazon Web Services, *AWS Security Best Practices: Applying the Principle of Least Privilege*, AWS Infrastructure Security Whitepaper, 2026.
6. P. Leitner, E. Wittern, J. Spillner, and W. Hummer, "A Mixed-Method Empirical Study of Function-as-a-Service Software Development in Industrial Practice," *Journal of Systems and Software*, vol. 149, pp. 340-359, 2019.
7. A. S. Tanenbaum and M. Van Steen, *Distributed Systems: Principles and Paradigms*, 3rd ed., CreateSpace Independent Publishing, 2017.
8. M. Fowler, *Patterns of Enterprise Application Architecture*, Addison-Wesley Professional, 2002.
9. IEEE Computer Society, *IEEE Guidelines for Authoring Conference and Periodical Papers*, IEEE Publishing, 2025.
10. Amazon Web Services, *AWS Lambda Developer Guide: Operating Lambda Functions with Python*, 2026.
11. Amazon Web Services, *Amazon SQS Developer Guide: Using Dead-Letter Queues in Amazon SQS*, 2026.
