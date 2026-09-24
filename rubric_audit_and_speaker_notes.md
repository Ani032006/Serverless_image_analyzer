# Rubric Compliance Audit & Speaker Notes

**Project**: Event-Driven Serverless AI Image Tagging Pipeline  
**Review**: 1 & 2 Combined (20 Marks)

---

## Rubric Compliance Audit

### Review 1 (10 marks)

| Rubric Column | Criteria | Max Marks | Status | Where It's Covered |
|---|---|---|---|---|
| **Z** | Title, Abstract, Introduction | 3 | ✅ Covered | Report Sections: Title page, Abstract, Section 1 (Intro) |
| **AA** | Literature Survey, Analysis, References | 3 | ✅ Covered | Report Section 2 (Related Works) + 10 IEEE references |
| **AB** | Architecture Diagram, Hardware-Software | 4 | ✅ Covered | Report Sections 3 & 4 (two diagrams, SAM template, service specs) |

### Review 2 (10 marks)

| Rubric Column | Criteria | Max Marks | Status | Where It's Covered |
|---|---|---|---|---|
| **AC** | Implementation | 4 | ✅ Covered | handler.py (132 lines), local_test.py, web simulator, live demo |
| **AD** | Algorithm / Formula / Methodology / AWS Components | 4 | ✅ Covered | Report Section 5 (3 equations + pseudocode), Section 3 (methodology) |
| **AE** | Result and Analysis | 2 | ✅ Covered | Report Section 7 (benchmark table, cost analysis, DynamoDB output) |

> [!TIP]
> All 6 rubric categories are covered. The sections below give you exactly what to say for each one during the review.

---

## Speaker Notes: Rubric Section by Section

---

### SECTION Z: Title, Abstract, Introduction (3 marks)

**What to say when the reviewer asks about your project title:**

> Our project is called "Event-Driven Serverless AI Image Tagging and Analysis Pipeline using AWS S3, Lambda, Rekognition, and DynamoDB." We chose this title because it spells out exactly what the system does and which AWS services are involved with zero ambiguity.

**What to say about the Abstract:**

> The abstract covers the core idea in one paragraph: we built a pipeline where uploading an image to S3 triggers a Lambda function. That function calls Rekognition to identify objects in the image, then stores the labels in DynamoDB. The system costs nothing when idle, about one-tenth of a cent per image when active, and processes each image in under a second. We also mention upfront that our test set was small and hand-picked, so the accuracy numbers shouldn't be taken as gospel for harder inputs.

**What to say about the Introduction:**

> Section 1 of the report covers three things. First, why this problem matters: any app with user-uploaded images needs automated tagging, and running a VM with a PyTorch model means paying 24/7 even when nobody's uploading. Second, the specific problem statement: build a pipeline that triggers on S3 upload, calls Rekognition, writes to DynamoDB, and uses scoped IAM policies. Third, how we split work: Aniruddh handled infrastructure and IAM, Konark handled Rekognition integration and testing.

---

### SECTION AA: Literature Survey, Analysis, References (3 marks)

**What to say:**

> Section 2 of the report compares three deployment approaches for image processing: running your own model on a VM, deploying a custom model inside a Lambda container, and using a managed API like Rekognition in an event-driven pipeline. We included a comparison table (Table 1) that looks at idle cost, scaling speed, cold start latency, security surface, and maintenance burden across all three.
>
> Our references include the Berkeley serverless paper by Jonas et al., which argues that event-driven architectures cut costs for bursty workloads. We also cite Wang et al.'s USENIX paper on serverless cold starts, the AWS Rekognition developer guide, and the AWS least-privilege security whitepaper. In total we have 10 references: a mix of academic papers, books, and AWS documentation.

**If asked "why not train your own model?":**

> We address this in the related works. Running PyTorch inside Lambda adds 3 to 10 seconds of cold start because you have to load the model weights. Rekognition's model is already loaded on Amazon's side; our Lambda just makes an HTTP API call, so cold start stays around 250ms. The trade-off is that we can't customize the model, but for general object detection, Rekognition's pre-trained model works well enough.

---

### SECTION AB: Architecture Diagram, Hardware-Software (4 marks)

**What to say about the architecture:**

> We have two architecture diagrams in the report. Figure 1 shows the high-level system architecture: four layers connected together: the Storage Layer (S3), Compute Layer (Lambda), AI Layer (Rekognition), and Database Layer (DynamoDB). Figure 2 shows the sequential data flow: from user upload to the final CloudWatch log entry.
>
> The pipeline works in 5 steps:
> 1. A user uploads an image to the `incoming/` prefix of our S3 bucket.
> 2. S3 fires an `ObjectCreated:Put` event notification and invokes our Lambda function.
> 3. Lambda validates the file extension: only `.jpg`, `.jpeg`, `.png` are accepted. PDFs and other files get skipped with a warning.
> 4. Lambda calls Rekognition `DetectLabels` by passing an S3 pointer, not the image bytes. Rekognition reads directly from S3.
> 5. Lambda formats the detected labels and writes them to the DynamoDB `ImageTags` table using `PutItem`.

**What to say about hardware-software specs:**

> On the software side: Python 3.12 runtime, boto3 AWS SDK (pre-installed in Lambda), 256 MB memory allocation, 30-second timeout. The SAM template (`template.yaml`) defines all infrastructure as code: S3 bucket with event notification config, DynamoDB table with on-demand billing and server-side encryption, Lambda function with environment variables, and the S3-to-Lambda invocation permission.
>
> There's no hardware we manage: that's the point of serverless. AWS handles the compute instances, storage drives, and networking. We interact only through API calls and configuration.

**If asked about the SAM template:**

> The `template.yaml` file uses AWS SAM (Serverless Application Model). It creates four resources: the S3 bucket with event notification configured to fire on `s3:ObjectCreated:*` within the `incoming/` prefix; the DynamoDB table with `ImageKey` as the partition key; the Lambda function pointing to our `handler.py` with environment variables for table name, min confidence, and max labels; and a Lambda permission that allows only our specific S3 bucket to invoke the function. You deploy the entire stack with a single `sam deploy` command.

---

### SECTION AC: Implementation (4 marks)

**What to say:**

> The implementation is in `handler.py` (132 lines of Python). Let me walk through the key decisions.
>
> **Client initialization outside the handler**: Lines 14-16 create the boto3 clients for S3, Rekognition, and DynamoDB at the module level, not inside the handler function. This matters because Lambda reuses containers across invocations. If I initialize clients inside the handler, every invocation creates new TCP connections (an extra 100 to 200ms wasted). By keeping them at the module level, warm invocations reuse the existing connections.
>
> **Configuration via environment variables**: The DynamoDB table name, minimum confidence threshold, and max label count are all read from environment variables with fallback defaults. This means we can change the confidence threshold from 70% to 80% without redeploying code: just update the Lambda configuration.
>
> **Extension validation**: Before calling Rekognition, we check the file extension. If someone uploads a PDF or CSV, we skip it with a log warning instead of crashing. This is defensive coding: S3 can store any file type, and our Lambda shouldn't break because of an unexpected file.
>
> **The Rekognition call**: We pass `Image={'S3Object': {'Bucket': ..., 'Name': ...}}` (an S3 pointer, not image bytes). Rekognition reads the image directly from S3. This avoids downloading the image into Lambda memory and re-uploading it to Rekognition. It's faster and uses less memory.
>
> **DynamoDB write format**: DynamoDB's low-level API requires type annotations: `'S'` for strings, `'N'` for numbers, `'L'` for lists, `'M'` for maps. Our formatted label structure stores each label as a map with Name, Confidence, and a list of parent categories.
>
> **Error handling**: We catch `ClientError` (AWS-specific errors like throttling or permission denied) separately from general exceptions. The status code logic uses 200 for full success, 500 for full failure, and 207 (Multi-Status) for partial success in batch processing.

**If asked about testing:**

> We have a local test script (`local_test.py`) that mocks the AWS clients using Python's `unittest.mock`. It feeds a fake S3 event to the handler, verifies Rekognition was called with the correct bucket and key, and checks that DynamoDB received the right item structure. We also have an interactive demo script (`demo.py`) that walks through 10 steps of the pipeline: extension validation, Rekognition output, DynamoDB write, error handling, and batch processing. And we built a web-based visual simulator that lets you click through the pipeline in a browser.

**If asked about the web simulator:**

> The web interface is a local HTML/CSS/JS application that visually simulates the entire pipeline. You select a sample image or upload your own, adjust the confidence threshold and max labels with sliders, then click "Run Pipeline Trigger." It shows each AWS service lighting up in sequence as the pipeline processes the image, displays the detected labels with confidence bars, shows the exact DynamoDB JSON record that would be stored, and includes a real-time console log of every step. It also has an IAM policy viewer tab. This isn't deployed to AWS; it runs locally on localhost:8000 using Python's built-in HTTP server.

---

### SECTION AD: Algorithm / Formula / Methodology / AWS Components (4 marks)

**What to say about the algorithms and formulas:**

> Section 5 of the report has three equations and a pseudocode algorithm.
>
> **Equation 1: Confidence Score Thresholding**:  
> `L_output = { l | l ∈ L_candidate, C(l) ≥ τ, Rank(C(l)) ≤ N }`  
> This says: from all candidate labels Rekognition returns, keep only those with confidence at or above the threshold τ (which we set to 70%), and take at most N of them (which we set to 10). Without this filter, Rekognition might return 50+ speculative labels: things like labeling a mountain as "Volcano" at 30% confidence. The threshold keeps the output relevant.
>
> **Equation 2: Latency Composition**:  
> `T_total = T_event_notify + T_lambda_init + T_rekognition + T_dynamodb_write`  
> This breaks down where time goes. S3 event notification takes 50 to 150ms. Lambda initialization is about 250ms on cold start, under 10ms on warm start. Rekognition inference takes 400 to 600ms (this is the bottleneck because it's running a deep learning model). DynamoDB write is 15 to 35ms. Total average: about 842ms.
>
> **Equation 3: Cost Per Image**:  
> `Cost_image = Cost_S3_PUT + (M_Lambda × T_exec × P_GB-sec) + P_Rekognition + P_DynamoDB_WCU`  
> Lambda costs $0.0000166667 per GB-second. With 256 MB memory and ~500ms execution, that's essentially free. Rekognition charges $0.001 per image after the free tier (5,000 images/month). DynamoDB's on-demand write cost is negligible. For 1,000 images, the total comes to about $1.00: almost entirely Rekognition charges.
>
> **Algorithm 1 (Pseudocode)**: The pseudocode in the report formalizes the handler logic: check for empty records, loop through each record, validate extension, call Rekognition with S3 pointer, format labels, write to DynamoDB. This matches the actual Python implementation line by line.

**What to say about AWS Components:**

> We use four core AWS services:
> - **Amazon S3**: Object storage with event notifications. Our bucket has a prefix filter on `incoming/` so only uploads to that path trigger the Lambda. This prevents infinite loops if we ever write output back to the same bucket.
> - **AWS Lambda**: Serverless compute running Python 3.12. 256 MB memory, 30-second timeout. Scales horizontally: 100 simultaneous uploads means 100 parallel Lambda instances.
> - **Amazon Rekognition**: Managed computer vision service. We use the `DetectLabels` API. The model is a pre-trained convolutional neural network hosted on Amazon's infrastructure: we don't train or manage it.
> - **Amazon DynamoDB**: NoSQL key-value database. Our table uses `ImageKey` as the partition key with on-demand billing. NoSQL is the right choice because each image produces a variable number of labels: a relational database would need either a separate labels table or a JSON column.
>
> We also use **AWS CloudWatch** for logging and **AWS SAM** for infrastructure-as-code deployment.

---

### SECTION AE: Result and Analysis (2 marks)

**What to say:**

> Section 7 of the report presents our benchmark results. We tested with four images from different categories: landscape, urban street, office desk, and portrait. All four were successfully processed. The key metrics:
>
> - **Average end-to-end latency**: 842 milliseconds (well under one second).
> - **Top label confidence**: Range of 97.10% to 99.45% across all test images.
> - **Lambda execution time**: 388ms to 485ms, with the larger PNG file (2.3 MB) predictably taking longer than smaller JPEGs.
> - **DynamoDB write success rate**: 100% (HTTP 200 on all writes).
> - **Cost per image**: $0.001 when active, $0.00 when idle.
>
> I want to be honest about the limitations. Our test set was four images, all clean and well-lit. That's not enough to make claims about real-world accuracy. Rekognition would likely return lower confidence scores on blurry, dark, or heavily occluded images. We also haven't stress-tested at high concurrency to check for Rekognition throttling or DynamoDB scaling delays. And cold-start latency (about 250ms) is included in the total but not broken out separately in the Lambda execution time column: those numbers are from warm invocations.

**What to say about cost analysis:**

> For a demo-scale project, nearly everything falls within the AWS Free Tier. Lambda gives 1 million free requests per month: we used a handful. Rekognition gives 5,000 free images per month for the first year. DynamoDB's free tier includes 25 GB storage and 25 write capacity units. The only real cost at scale is Rekognition at $0.001 per image after the free tier. For 1,000 images, total cost is roughly $1.00.

---

## Quick Reference: Numbers to Memorize

| Metric | Value |
|---|---|
| Average latency | approx 842 ms |
| Lambda memory | 256 MB |
| Lambda timeout | 30 sec |
| Lambda cold start | approx 250 ms |
| Rekognition inference | 400 to 600 ms |
| DynamoDB write | 15 to 35 ms |
| Cost per image | $0.001 |
| Idle cost | $0.00 |
| Min confidence threshold | 70% |
| Max labels | 10 |
| Test images | 4 categories |
| IAM policy statements | 4 |
| References cited | 10 |

---

## Likely Tough Questions & Answers

**"Why is Rekognition Resource set to `*`?"**
> That's an AWS API constraint, not a mistake. The `DetectLabels` action doesn't support resource-level ARNs: you can't scope it to a specific image or bucket. Every other statement in our policy IS scoped to a specific ARN, which shows this is intentional. It's documented in the AWS IAM User Guide for Rekognition.

**"Why initialize boto3 clients outside the handler?"**
> Lambda container reuse. On warm starts, the module-level code isn't re-executed: the existing clients and their TCP connections are reused. This saves about 100 to 200ms per invocation. If I put them inside the handler, every invocation would create new connections from scratch.

**"What if someone uploads a non-image file?"**
> The handler checks the file extension before calling Rekognition. If it's not `.jpg`, `.jpeg`, or `.png`, the file is skipped with a warning log: no crash, no error, no wasted Rekognition API call. I can demo this live with the PDF test case.

**"What does HTTP 207 mean in your code?"**
> Multi-Status. S3 can send a batch of multiple records in one event. If we process 5 images and 3 succeed but 2 fail, returning 200 would be dishonest (not everything worked), and 500 would be wrong too (some things did work). 207 communicates partial success: the response body includes both the success count and the error list.

**"Why DynamoDB and not a relational database?"**
> Each image produces a different number of labels: one image might get 3 labels, another might get 10. In a relational database, you'd need a separate labels table with a join (overhead), or dump JSON into a text column (lose query ability). DynamoDB stores lists of maps natively: the label structure maps directly to the data model without schema gymnastics.

**"How does your system handle scaling?"**
> Lambda scales horizontally. Each S3 upload triggers a separate Lambda instance. AWS supports 1,000 concurrent executions by default. DynamoDB on-demand mode auto-scales write capacity. Rekognition is a managed API: Amazon handles the scaling behind the scenes. The only bottleneck would be Rekognition's per-account throttle limit, which we haven't tested yet.

**"What's Infrastructure as Code and why does it matter?"**
> Our `template.yaml` defines every AWS resource (the S3 bucket, DynamoDB table, Lambda function, and permissions) in a single YAML file. Instead of clicking through the AWS Console (which is error-prone and impossible to reproduce), we run `sam deploy` and the entire stack is created automatically. If we delete everything and deploy again, we get the exact same setup. It's version-controlled in Git, so we can track infrastructure changes like code changes.
