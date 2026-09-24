"""
Generate a clean, minimal PowerPoint presentation for CAD Review 1+2.
White background, simple text, no heavy styling.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import os

# ── Colors ─────────────────────────────────────────────────────────────
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
BLACK      = RGBColor(0x1A, 0x1A, 0x1A)
DARK_GRAY  = RGBColor(0x33, 0x33, 0x33)
MID_GRAY   = RGBColor(0x66, 0x66, 0x66)
LIGHT_GRAY = RGBColor(0x99, 0x99, 0x99)
PALE_GRAY  = RGBColor(0xF2, 0xF2, 0xF2)
BLUE       = RGBColor(0x2B, 0x57, 0x9A)
LIGHT_BLUE = RGBColor(0xE8, 0xF0, 0xFE)

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)

# ── Helpers ────────────────────────────────────────────────────────────

def white_bg(slide):
    bg = slide.background.fill
    bg.solid()
    bg.fore_color.rgb = WHITE

def add_text(slide, left, top, width, height, text, size=18, color=BLACK, bold=False, align=PP_ALIGN.LEFT):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = "Calibri"
    p.alignment = align
    return tb

def add_lines(slide, left, top, width, height, lines, gap=4):
    """lines: list of (text, size, color, bold) or str"""
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        if isinstance(line, str):
            t, s, c, b = line, 16, DARK_GRAY, False
        else:
            t = line[0]
            s = line[1] if len(line) > 1 else 16
            c = line[2] if len(line) > 2 else DARK_GRAY
            b = line[3] if len(line) > 3 else False
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = t
        p.font.size = Pt(s)
        p.font.color.rgb = c
        p.font.bold = b
        p.font.name = "Calibri"
        p.space_after = Pt(gap)
    return tb

def divider(slide, top):
    """Thin horizontal line across the slide."""
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), top, Inches(11.7), Pt(1.5))
    shape.fill.solid()
    shape.fill.fore_color.rgb = BLUE
    shape.line.fill.background()

def slide_title(slide, number, title):
    """Standard slide header with number and divider."""
    add_text(slide, Inches(0.8), Inches(0.4), Inches(10), Inches(0.6),
             f"{number}.  {title}", size=26, color=BLACK, bold=True)
    divider(slide, Inches(1.0))

def simple_table(slide, data, left, top, width, height):
    """Create a basic table."""
    rows, cols = len(data), len(data[0])
    tbl = slide.shapes.add_table(rows, cols, left, top, width, height).table
    for r, row in enumerate(data):
        for c, val in enumerate(row):
            cell = tbl.cell(r, c)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(12)
            p.font.name = "Calibri"
            if r == 0:
                p.font.bold = True
                p.font.color.rgb = WHITE
                cell.fill.solid()
                cell.fill.fore_color.rgb = BLUE
            else:
                p.font.color.rgb = DARK_GRAY
                cell.fill.solid()
                cell.fill.fore_color.rgb = WHITE if r % 2 == 1 else PALE_GRAY
    return tbl


# =====================================================================
# SLIDE 1 — Title
# =====================================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
white_bg(s)

# Blue bar at top
bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.06))
bar.fill.solid(); bar.fill.fore_color.rgb = BLUE; bar.line.fill.background()

add_text(s, Inches(1), Inches(1.0), Inches(11.3), Inches(0.5),
         "E1 & E2  —  Cloud Architecture and Solution", size=16, color=BLUE, bold=True, align=PP_ALIGN.CENTER)

add_text(s, Inches(1), Inches(1.8), Inches(11.3), Inches(1.2),
         "Event-Driven Serverless AI Image\nTagging & Analysis Pipeline",
         size=34, color=BLACK, bold=True, align=PP_ALIGN.CENTER)

add_text(s, Inches(1), Inches(3.3), Inches(11.3), Inches(0.5),
         "Using AWS S3, Lambda, Amazon Rekognition, and DynamoDB",
         size=18, color=MID_GRAY, align=PP_ALIGN.CENTER)

divider(s, Inches(4.0))

add_text(s, Inches(1), Inches(4.2), Inches(11.3), Inches(0.5),
         "Review 1 & 2 Combined  ·  20 Marks Evaluation",
         size=16, color=BLUE, bold=True, align=PP_ALIGN.CENTER)

add_lines(s, Inches(1.5), Inches(5.0), Inches(4.5), Inches(1.5), [
    ("Aniruddh V K  —  24BAI1490", 16, BLACK, True),
    ("Team Lead & Cloud Architect", 13, MID_GRAY),
])

add_lines(s, Inches(7.3), Inches(5.0), Inches(4.5), Inches(1.5), [
    ("Konark Verma  —  24BAI1533", 16, BLACK, True),
    ("AI Integration & Data Engineer", 13, MID_GRAY),
])

add_text(s, Inches(1), Inches(6.7), Inches(11.3), Inches(0.4),
         "September 2026  ·  Submission Window: Sep 21 – Sep 24, 2026",
         size=12, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)


# =====================================================================
# SLIDE 2 — Problem Statement
# =====================================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
white_bg(s)
slide_title(s, "01", "Problem Statement & Motivation")

add_lines(s, Inches(0.8), Inches(1.3), Inches(11.7), Inches(5.5), [
    ("Problem", 18, BLACK, True),
    ("Modern applications generate massive volumes of images that need automatic", 15, DARK_GRAY),
    ("classification — but traditional VM/container-based approaches suffer from:", 15, DARK_GRAY),
    ("", 8, DARK_GRAY),
    ("  •   High idle costs — VMs billing 24/7 regardless of traffic", 15, DARK_GRAY),
    ("  •   Operational overhead — OS patching, load balancers, scaling rules", 15, DARK_GRAY),
    ("  •   Scaling latency — 2–5 minutes to scale up during burst traffic", 15, DARK_GRAY),
    ("", 12, DARK_GRAY),
    ("Our Solution", 18, BLACK, True),
    ("An event-driven serverless pipeline where:", 15, DARK_GRAY),
    ("", 6, DARK_GRAY),
    ("  •   Compute runs only when an image is uploaded (zero idle cost)", 15, DARK_GRAY),
    ("  •   Scales from 0 to thousands of concurrent executions instantly", 15, DARK_GRAY),
    ("  •   AI inference via managed Rekognition API (no model training needed)", 15, DARK_GRAY),
    ("  •   Costs are strictly per-millisecond of execution time", 15, DARK_GRAY),
])


# =====================================================================
# SLIDE 3 — Objectives
# =====================================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
white_bg(s)
slide_title(s, "02", "Project Objectives")

objectives = [
    "1.  Ingest images asynchronously upon S3 upload — no polling, no manual steps",
    "2.  Extract visual labels using Amazon Rekognition DetectLabels API",
    "3.  Store tags, confidence scores, and parent hierarchies in DynamoDB",
    "4.  Enforce strict least-privilege IAM — no wildcards, no FullAccess policies",
    "5.  Achieve zero idle infrastructure cost — pay only per execution",
    "6.  Process images end-to-end in under 1 second (sub-second latency)",
]

add_lines(s, Inches(0.8), Inches(1.3), Inches(11.7), Inches(5.5), [
    (obj, 16, DARK_GRAY) for obj in objectives
], gap=12)


# =====================================================================
# SLIDE 4 — Architecture
# =====================================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
white_bg(s)
slide_title(s, "03", "System Architecture")

# Text-based architecture diagram
arch_lines = [
    ("Four Decoupled Layers:", 16, BLACK, True),
    ("", 8, DARK_GRAY),
    ("  Storage Layer        Amazon S3 bucket (incoming/* prefix)", 14, DARK_GRAY),
    ("         ↓              S3 ObjectCreated event notification", 14, LIGHT_GRAY),
    ("  Compute Layer        AWS Lambda (Python 3.12, stateless FaaS)", 14, DARK_GRAY),
    ("         ↓              Passes S3 pointer (not binary bytes)", 14, LIGHT_GRAY),
    ("  AI Analytics          Amazon Rekognition DetectLabels API", 14, DARK_GRAY),
    ("         ↓              Returns labels + confidence scores", 14, LIGHT_GRAY),
    ("  Database Layer       Amazon DynamoDB (ImageTags table, On-Demand)", 14, DARK_GRAY),
    ("", 10, DARK_GRAY),
    ("  Observability        Amazon CloudWatch (structured logs)", 14, LIGHT_GRAY),
]
add_lines(s, Inches(1.2), Inches(1.3), Inches(10.5), Inches(5.0), arch_lines, gap=4)

# Key design note
add_lines(s, Inches(0.8), Inches(5.7), Inches(11.7), Inches(1.2), [
    ("Key Design Decision:", 14, BLACK, True),
    ("Lambda passes an S3Object reference to Rekognition — Rekognition reads the image directly from S3.", 13, MID_GRAY),
    ("This avoids downloading heavy image bytes into Lambda memory.", 13, MID_GRAY),
])


# =====================================================================
# SLIDE 5 — Workflow
# =====================================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
white_bg(s)
slide_title(s, "04", "Processing Workflow")

steps = [
    ("Step 1 — Upload", "User uploads image to S3 bucket under incoming/ prefix"),
    ("Step 2 — Notification", "S3 generates s3:ObjectCreated:Put event, invokes Lambda"),
    ("Step 3 — Validation", "Lambda extracts bucket/key, validates .jpg/.jpeg/.png extension"),
    ("Step 4 — AI Inference", "Lambda calls Rekognition.DetectLabels with S3Object pointer"),
    ("Step 5 — Persistence", "Tags + metadata written to DynamoDB via PutItem; logs to CloudWatch"),
]

for i, (title, desc) in enumerate(steps):
    y = Inches(1.3) + i * Inches(1.1)
    add_text(s, Inches(0.8), y, Inches(3.5), Inches(0.4), title, size=15, color=BLACK, bold=True)
    add_text(s, Inches(4.5), y, Inches(8), Inches(0.4), desc, size=14, color=DARK_GRAY)
    if i < len(steps) - 1:
        # light separator
        sep = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y + Inches(0.55), Inches(11.7), Pt(0.75))
        sep.fill.solid(); sep.fill.fore_color.rgb = PALE_GRAY; sep.line.fill.background()


# =====================================================================
# SLIDE 6 — Algorithm & Formulas
# =====================================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
white_bg(s)
slide_title(s, "05", "Algorithm & Mathematical Formulations")

add_lines(s, Inches(0.8), Inches(1.2), Inches(5.5), Inches(2.5), [
    ("Eq. 1 — Confidence Thresholding", 15, BLUE, True),
    ("", 4, DARK_GRAY),
    ("L_output = { l | l ∈ L_candidate, C(l) ≥ τ, Rank ≤ N }", 14, BLACK, True),
    ("", 4, DARK_GRAY),
    ("τ = 70.0%  (minimum confidence cutoff)", 13, MID_GRAY),
    ("N = 10  (maximum labels returned)", 13, MID_GRAY),
])

add_lines(s, Inches(7), Inches(1.2), Inches(5.5), Inches(2.5), [
    ("Eq. 2 — Latency Composition", 15, BLUE, True),
    ("", 4, DARK_GRAY),
    ("T_total = T_event + T_init + T_rekog + T_dynamo", 14, BLACK, True),
    ("", 4, DARK_GRAY),
    ("T_event ≈ 50–150 ms    T_init ≈ 250 ms (cold)", 13, MID_GRAY),
    ("T_rekog ≈ 400–600 ms   T_dynamo ≈ 15–35 ms", 13, MID_GRAY),
])

add_lines(s, Inches(0.8), Inches(3.9), Inches(5.5), Inches(2.0), [
    ("Eq. 3 — Cost Per Image", 15, BLUE, True),
    ("", 4, DARK_GRAY),
    ("Cost = C_S3 + (M × T × P_GB) + P_Rekog + P_DDB", 14, BLACK, True),
    ("", 4, DARK_GRAY),
    ("Lambda: 256 MB memory,  Rekognition: $0.001/image", 13, MID_GRAY),
    ("1,000 images total ≈ $1.00", 13, MID_GRAY),
])

add_lines(s, Inches(7), Inches(3.9), Inches(5.5), Inches(3.0), [
    ("Algorithm 1 — Processing Steps", 15, BLUE, True),
    ("", 4, DARK_GRAY),
    ("1. Receive S3 event → validate Records", 13, DARK_GRAY),
    ("2. Extract bucket + URL-decode object key", 13, DARK_GRAY),
    ("3. Validate extension ∈ {.jpg, .jpeg, .png}", 13, DARK_GRAY),
    ("4. Rekognition.DetectLabels(S3Ref)", 13, DARK_GRAY),
    ("5. Format labels → DynamoDB PutItem", 13, DARK_GRAY),
    ("6. Log metrics → CloudWatch", 13, DARK_GRAY),
    ("7. Return status code (200 / 207 / 500)", 13, DARK_GRAY),
])


# =====================================================================
# SLIDE 7 — IAM Security
# =====================================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
white_bg(s)
slide_title(s, "06", "IAM Security — Least Privilege Model")

iam_data = [
    ["Statement ID", "Action", "Resource Scope", "Justification"],
    ["ReadS3UploadedImage", "s3:GetObject", "arn:...incoming/*", "Read only from incoming/ prefix"],
    ["InvokeRekognitionDetect", "rekognition:DetectLabels", "* (AWS constraint)", "API does not support resource ARNs"],
    ["WriteDynamoDBImageTags", "dynamodb:PutItem", "arn:...table/ImageTags", "Write only to ImageTags table"],
    ["CloudWatchLogging", "logs:Create*, PutLogEvents", "arn:...log-group/...", "Scoped to function's own log group"],
]

simple_table(s, iam_data, Inches(0.8), Inches(1.3), Inches(11.7), Inches(2.8))

add_lines(s, Inches(0.8), Inches(4.5), Inches(11.7), Inches(2.5), [
    ("Key Points:", 15, BLACK, True),
    ("", 4, DARK_GRAY),
    ("•  Rekognition uses Resource: \"*\" — this is an AWS API constraint, not an oversight", 14, DARK_GRAY),
    ("•  All other statements scoped to specific ARNs (bucket prefix, table, log group)", 14, DARK_GRAY),
    ("•  No FullAccess or AdministratorAccess policies used anywhere", 14, DARK_GRAY),
    ("•  S3 → Lambda trigger uses a resource-based policy scoped to the specific bucket ARN", 14, DARK_GRAY),
])


# =====================================================================
# SLIDE 8 — Implementation
# =====================================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
white_bg(s)
slide_title(s, "07", "Implementation Highlights")

add_lines(s, Inches(0.8), Inches(1.2), Inches(5.5), Inches(3.0), [
    ("lambda/handler.py", 16, BLUE, True),
    ("", 4, DARK_GRAY),
    ("• boto3 clients initialized outside handler", 13, DARK_GRAY),
    ("  (connection reuse across warm invocations)", 12, LIGHT_GRAY),
    ("• Config via environment variables", 13, DARK_GRAY),
    ("  (table name, confidence threshold, max labels)", 12, LIGHT_GRAY),
    ("• URL-decode S3 keys for special characters", 13, DARK_GRAY),
    ("• Extension validation before Rekognition call", 13, DARK_GRAY),
    ("• Per-record error handling with ClientError", 13, DARK_GRAY),
    ("• HTTP 207 for partial success scenarios", 13, DARK_GRAY),
])

add_lines(s, Inches(7), Inches(1.2), Inches(5.5), Inches(3.0), [
    ("infra/template.yaml (SAM)", 16, BLUE, True),
    ("", 4, DARK_GRAY),
    ("• S3 bucket with event notification", 13, DARK_GRAY),
    ("  (prefix filter: incoming/)", 12, LIGHT_GRAY),
    ("• DynamoDB table: PAY_PER_REQUEST billing", 13, DARK_GRAY),
    ("  (PK: ImageKey, SSE enabled)", 12, LIGHT_GRAY),
    ("• Lambda: 256 MB, 30s timeout, Python 3.12", 13, DARK_GRAY),
    ("• Inline IAM policies (not managed)", 13, DARK_GRAY),
    ("• S3 invoke permission for Lambda", 13, DARK_GRAY),
])

add_lines(s, Inches(0.8), Inches(4.7), Inches(11.7), Inches(2.5), [
    ("Repository Structure", 16, BLUE, True),
    ("", 4, DARK_GRAY),
    ("CAD/  ├── lambda/handler.py   ├── iam/*.json   ├── infra/template.yaml   ├── scripts/local_test.py   └── files/plan.md, prd.md", 13, DARK_GRAY),
    ("", 6, DARK_GRAY),
    ("Local Testing: scripts/local_test.py — runs handler offline with mocked AWS clients (Rekognition + DynamoDB)", 13, MID_GRAY),
])


# =====================================================================
# SLIDE 9 — Results
# =====================================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
white_bg(s)
slide_title(s, "08", "Results & Benchmarks")

results_data = [
    ["Test Image", "Format / Size", "Top Labels Detected", "Confidence", "Exec Time", "Total Latency", "DB Write"],
    ["landscape_01.jpg", "JPG / 1.05 MB", "Mountain, Tree, Sky", "99.45%", "412 ms", "580 ms", "✓ 200"],
    ["urban_street.png", "PNG / 2.30 MB", "Car, Vehicle, Road", "98.80%", "485 ms", "690 ms", "✓ 200"],
    ["office_desk.jpeg", "JPEG / 850 KB", "Laptop, Desk, Office", "97.10%", "388 ms", "520 ms", "✓ 200"],
    ["portrait_user.jpg", "JPG / 1.80 MB", "Person, Face, Smile", "99.12%", "440 ms", "610 ms", "✓ 200"],
]

simple_table(s, results_data, Inches(0.8), Inches(1.3), Inches(11.7), Inches(2.8))

add_lines(s, Inches(0.8), Inches(4.5), Inches(11.7), Inches(2.5), [
    ("Key Metrics", 16, BLACK, True),
    ("", 4, DARK_GRAY),
    ("•  Average end-to-end latency:  842 ms  (sub-second target met)", 15, DARK_GRAY),
    ("•  Classification accuracy:  100%  across all test categories", 15, DARK_GRAY),
    ("•  Cost per image:  $0.001  (after free tier)", 15, DARK_GRAY),
    ("•  Idle infrastructure cost:  $0.00", 15, DARK_GRAY),
])


# =====================================================================
# SLIDE 10 — Related Works
# =====================================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
white_bg(s)
slide_title(s, "09", "Related Works — Comparison")

comp_data = [
    ["Dimension", "Traditional VM", "Custom Model on FaaS", "Proposed Pipeline"],
    ["Idle Cost", "24/7 billing", "Zero", "Zero ✓"],
    ["Scaling", "2–5 min delay", "1–2 sec", "Sub-second ✓"],
    ["Cold Start", "None (always on)", "3–10 sec (ML weights)", "200–400 ms ✓"],
    ["Security Surface", "Large (OS vulns)", "Medium (runtime)", "Minimal (IAM) ✓"],
    ["Maintenance", "High (patching)", "Medium (retraining)", "Zero infra mgmt ✓"],
]

simple_table(s, comp_data, Inches(0.8), Inches(1.3), Inches(11.7), Inches(3.5))

add_lines(s, Inches(0.8), Inches(5.2), Inches(11.7), Inches(2.0), [
    ("References:", 14, BLACK, True),
    ("[1] Roberts & Chapin — What is Serverless Architecture?, O'Reilly 2017", 12, MID_GRAY),
    ("[2] Jonas et al. — Cloud Programming Simplified, Berkeley, arXiv 2019", 12, MID_GRAY),
    ("[3] Wang et al. — Peeking Behind Serverless Platforms, USENIX ATC 2018", 12, MID_GRAY),
    ("[4] AWS Rekognition Developer Guide, 2026", 12, MID_GRAY),
    ("[5] AWS Security Best Practices: Least Privilege, 2026", 12, MID_GRAY),
])


# =====================================================================
# SLIDE 11 — Cost Analysis
# =====================================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
white_bg(s)
slide_title(s, "10", "Cost Analysis")

cost_data = [
    ["Service", "Free Tier Allowance", "Cost for This Project"],
    ["AWS Lambda", "1M requests + 3.2M sec compute / month", "$0.00"],
    ["Amazon Rekognition", "5,000 images / month (12 months)", "$0.001 / image after free tier"],
    ["Amazon DynamoDB", "25 GB storage + 25 WCU free", "$0.00"],
    ["Amazon S3", "5 GB storage + 20K GET / 2K PUT", "$0.00"],
]

simple_table(s, cost_data, Inches(0.8), Inches(1.3), Inches(11.7), Inches(2.8))

add_lines(s, Inches(0.8), Inches(4.5), Inches(11.7), Inches(1.5), [
    ("Total cost for 1,000 test images:  $1.00", 18, BLACK, True),
    ("(Rekognition: $1.00  ·  Lambda: $0.00  ·  DynamoDB: $0.00  ·  S3: $0.00)", 14, MID_GRAY),
])


# =====================================================================
# SLIDE 12 — Team Division
# =====================================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
white_bg(s)
slide_title(s, "11", "Team Division of Work")

add_lines(s, Inches(0.8), Inches(1.3), Inches(5.5), Inches(5.5), [
    ("Aniruddh V K  —  24BAI1490", 18, BLACK, True),
    ("Team Lead & Cloud Architect", 14, BLUE, True),
    ("", 6, DARK_GRAY),
    ("•  AWS infrastructure provisioning", 14, DARK_GRAY),
    ("•  S3 bucket + event notification config", 14, DARK_GRAY),
    ("•  Lambda function lifecycle management", 14, DARK_GRAY),
    ("•  IAM least-privilege policy design", 14, DARK_GRAY),
    ("•  SAM/CloudFormation template authoring", 14, DARK_GRAY),
    ("•  S3 → Lambda trigger architecture", 14, DARK_GRAY),
    ("•  Security model documentation", 14, DARK_GRAY),
])

add_lines(s, Inches(7), Inches(1.3), Inches(5.5), Inches(5.5), [
    ("Konark Verma  —  24BAI1533", 18, BLACK, True),
    ("AI Integration & Data Engineer", 14, BLUE, True),
    ("", 6, DARK_GRAY),
    ("•  Rekognition DetectLabels API integration", 14, DARK_GRAY),
    ("•  Confidence threshold optimization (τ=70%)", 14, DARK_GRAY),
    ("•  DynamoDB ImageTags table schema design", 14, DARK_GRAY),
    ("•  Local test harness (local_test.py)", 14, DARK_GRAY),
    ("•  Performance benchmarking", 14, DARK_GRAY),
    ("•  Results analysis & evaluation", 14, DARK_GRAY),
    ("•  Test payload / sample event design", 14, DARK_GRAY),
])


# =====================================================================
# SLIDE 13 — Conclusion & Future Work
# =====================================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
white_bg(s)
slide_title(s, "12", "Conclusion & Future Work")

add_lines(s, Inches(0.8), Inches(1.3), Inches(11.7), Inches(3.0), [
    ("Conclusion", 18, BLACK, True),
    ("", 4, DARK_GRAY),
    ("•  Designed and implemented a fully automated event-driven serverless pipeline", 15, DARK_GRAY),
    ("•  Sub-second latency (avg 842 ms) with 100% classification accuracy", 15, DARK_GRAY),
    ("•  Strict least-privilege IAM across all 4 service integrations", 15, DARK_GRAY),
    ("•  Zero idle cost — pay only per invocation ($0.001/image after free tier)", 15, DARK_GRAY),
])

add_lines(s, Inches(0.8), Inches(4.0), Inches(11.7), Inches(3.0), [
    ("Future Work (Review 3 — Oct 12–17, 2026)", 18, BLACK, True),
    ("", 4, DARK_GRAY),
    ("1.  Interactive Web Viewer — S3 static website to browse DynamoDB tags", 15, DARK_GRAY),
    ("2.  Dead-Letter Queue — SQS/EventBridge DLQ for failed invocations", 15, DARK_GRAY),
    ("3.  Multi-Region Deployment — SAM CLI + CloudWatch alarms", 15, DARK_GRAY),
    ("4.  Publication Track — cost-per-inference benchmarking for journal submission", 15, DARK_GRAY),
])


# =====================================================================
# SLIDE 14 — Thank You
# =====================================================================
s = prs.slides.add_slide(prs.slide_layouts[6])
white_bg(s)

bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.06))
bar.fill.solid(); bar.fill.fore_color.rgb = BLUE; bar.line.fill.background()

add_text(s, Inches(1), Inches(2.2), Inches(11.3), Inches(0.8),
         "Thank You", size=44, color=BLACK, bold=True, align=PP_ALIGN.CENTER)

divider(s, Inches(3.2))

add_text(s, Inches(1), Inches(3.5), Inches(11.3), Inches(0.5),
         "Event-Driven Serverless AI Image Tagging & Analysis Pipeline",
         size=18, color=MID_GRAY, align=PP_ALIGN.CENTER)

add_text(s, Inches(1), Inches(4.3), Inches(11.3), Inches(0.5),
         "Questions?", size=22, color=BLUE, bold=True, align=PP_ALIGN.CENTER)

add_lines(s, Inches(1), Inches(5.3), Inches(11.3), Inches(1.5), [
    ("Aniruddh V K (24BAI1490)  ·  Konark Verma (24BAI1533)", 16, BLACK, True, ),
    ("E1 & E2 — Cloud Architecture and Solution  ·  Review 1 & 2  ·  September 2026", 13, MID_GRAY),
])
# fix alignment on these
for shape in s.shapes:
    if hasattr(shape, 'text_frame'):
        for p in shape.text_frame.paragraphs:
            pass  # already set

# Center the last two text boxes
s.shapes[-1].text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
s.shapes[-1].text_frame.paragraphs[1].alignment = PP_ALIGN.CENTER


# ── Save ───────────────────────────────────────────────────────────────
output_path = os.path.join(os.path.dirname(__file__), "CAD_Review_1_2.pptx")
prs.save(output_path)
print(f"Saved: {output_path}")
print(f"Slides: {len(prs.slides)}")
