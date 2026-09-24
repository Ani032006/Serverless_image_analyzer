# Project Plan — Event-Driven Serverless AI Image Analyzer

## 1. Overview

This plan sequences work against the two graded checkpoints: the combined
Review 1 & 2 (design + partial build) and Review 3 (completed, demoed
project). Everything below assumes an **AWS** implementation — S3, Lambda,
Rekognition, DynamoDB — since it lines up with the AWS for Cloud Computing
coursework already in progress. The equivalent GCP/Azure services are noted
in the tech stack doc if the course later requires a switch.

## 2. Review Schedule (from the course circular)

| Milestone | Marks | Window | Where |
|---|---|---|---|
| Review 1 & 2 (combined) | 20 | Mon 21-09-2026 → Thu 24-09-2026 | Class hours or cabin (outside class) |
| Review 3 | 10 | Mon 12-10-2026 → Sat 17-10-2026 | Class hours or cabin (outside class) |

Marks are only given during these windows, so both milestones below are
built backward from those dates, not from the total project length.

## 3. Phase Breakdown

### Phase 0 — Setup (before ~15-09-2026)
- Create AWS account / use existing sandbox; enable billing alerts.
- Install AWS CLI, configure a named profile (never the root user).
- Create a private GitHub repo for code + the consolidated document.
- Draft the architecture diagram (draw.io or Lucidchart) — this alone
  covers a large chunk of "Proposed Methodology" and "Architecture
  Diagram" in the report.

### Phase 1 — Design + Early Build (target: ready by 21-09-2026)
Goal for Review 1 & 2: show you understand the *architecture* and *IAM*
model, even if the pipeline isn't fully wired end-to-end yet.
- Finalize S3 bucket structure (e.g. `incoming/` prefix for uploads).
- Write the least-privilege IAM policies (see tech stack doc) —
  this is explicitly called out as the hard part, so having it done and
  explainable is worth disproportionate marks.
- Stand up the Lambda function skeleton with the S3 event trigger wired
  (even if it just logs the event for now).
- Design the DynamoDB table schema (partition key, attributes).
- Draft Abstract, Introduction, Related Works, and the Architecture
  Diagram/Workflow sections of the consolidated document.

**Review 1 & 2 deliverable checklist:**
- [ ] Architecture diagram (Storage → Function → AI Service → Database)
- [ ] IAM roles/policies written and explainable (not "Admin")
- [ ] S3 → Lambda trigger demonstrably firing
- [ ] DynamoDB table created with schema justified
- [ ] Document sections: Title, Keywords, Abstract, Introduction,
      Related Works, Proposed Methodology (draft), Architecture Diagram

### Phase 2 — Full Implementation (22-09-2026 → early Oct)
- Complete the Lambda handler: download image from S3, call Rekognition
  `DetectLabels`, write results to DynamoDB.
- Add error handling (unsupported file types, Rekognition throttling,
  partial write failures).
- Add basic observability: CloudWatch Logs, maybe a metric or alarm.
- Test with a batch of varied images (people, objects, low quality) and
  record accuracy/confidence observations for the "Results and
  Discussion" section.

### Phase 3 — Polish + Review 3 Prep (target: ready by 12-10-2026)
- Record a short demo path: upload → tags appear in DynamoDB, ideally
  with a small viewer (CLI script or minimal web page) that queries
  DynamoDB and displays tags per image.
- Fill in Implementation, Results and Discussion, Conclusion, Future
  Work, and IEEE-formatted References in the consolidated document.
- Number every figure/table/equation consistently (Fig. 1, Table 1,
  Eq. 1) and cross-check captions against in-text references.
- Re-read the whole document once for consistency (formatting, tense,
  terminology) since it's Turnitin/AI-checked once, as a whole.

### Phase 4 — Optional: Publication Track
- If the pipeline works cleanly and results are interesting (e.g.
  accuracy across image categories, cost-per-inference analysis), this
  is a candidate for the conference/journal/patent track mentioned in
  the circular — worth raising with the professor once Phase 3 is done.

## 4. Key Risks / Things That Commonly Go Wrong

- **Over-permissioned IAM**: giving the Lambda role `s3:*` or
  `AmazonRekognitionFullAccess` "to save time" — explicitly penalized.
  Scope every permission to the exact bucket/table ARN.
- **S3 trigger recursion**: if the Lambda ever writes back into the same
  bucket/prefix it's triggered on, it can create an infinite loop. Keep
  output out of the trigger prefix.
- **Cold start / timeout**: Rekognition calls plus image download can
  exceed the Lambda default timeout (3s) — bump it to ~30s.
- **Region mismatch**: S3 bucket, Lambda, Rekognition, and DynamoDB must
  be in the same AWS region or calls will silently fail/cost extra.
- **Leaving the document until the end**: the circular is explicit that
  it's one continuously-updated document — drafting sections as each
  phase completes avoids a rushed rewrite before Review 3.

## 5. Single Source of Truth Reminder

Per the circular: **one consolidated document**, updated continuously,
not separate files per review. Treat this plan/PRD/tech-stack doc as
internal working documents — the actual gradable artifact is the single
IEEE-format report (Title → Keywords → Abstract → Introduction → Related
Works → Proposed Methodology → Architecture Diagram → Workflow →
Algorithm/Formulas → Tables and Figures → Implementation, Results and
Discussion → Conclusion → Future Work → References).
