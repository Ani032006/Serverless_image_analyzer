/**
 * Serverless Image Analyzer — Review 3 Frontend Logic
 * Pipeline simulation with DLQ, metrics, and latency breakdown.
 */

// ─── Sample Data ──────────────────────────────────────────────────────────
const SAMPLES = {
  landscape: {
    name: "sample_landscape.jpg",
    bucket: "image-analyzer-dev-bucket",
    key: "incoming/sample_landscape.jpg",
    size: 1101004,
    valid: true,
    latency: { s3: 72, lambda: 18, rekog: 468, dynamo: 22 },
    svg: `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300"><rect width="400" height="300" fill="%230f172a"/><rect width="400" height="160" y="0" fill="%231e3a8a"/><circle cx="320" cy="55" r="38" fill="%23f59e0b" opacity="0.9"/><path d="M0 220 L80 140 L160 185 L240 110 L320 158 L400 95 L400 300 L0 300Z" fill="%23065f46"/><path d="M0 250 L100 180 L200 225 L300 160 L400 200 L400 300 L0 300Z" fill="%23134e4a"/></svg>`,
    labels: [
      { name: "Mountain",  confidence: 99.45, parents: ["Outdoors", "Nature"] },
      { name: "Tree",      confidence: 96.12, parents: ["Plant"] },
      { name: "Sky",       confidence: 94.80, parents: [] },
      { name: "Outdoors",  confidence: 92.30, parents: ["Nature"] },
      { name: "Landscape", confidence: 89.70, parents: ["Scenery"] }
    ]
  },
  traffic: {
    name: "city_traffic.png",
    bucket: "image-analyzer-dev-bucket",
    key: "incoming/city_traffic.png",
    size: 2411724,
    valid: true,
    latency: { s3: 118, lambda: 22, rekog: 517, dynamo: 33 },
    svg: `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300"><rect width="400" height="300" fill="%2318181b"/><rect x="0" y="170" width="400" height="130" fill="%2327272a"/><line x1="0" y1="235" x2="400" y2="235" stroke="%23eab308" stroke-width="5" stroke-dasharray="22 12"/><rect x="60" y="180" width="110" height="48" rx="8" fill="%23ef4444"/><rect x="60" y="192" width="24" height="14" rx="2" fill="%23fef08a" opacity="0.8"/><rect x="146" y="192" width="24" height="14" rx="2" fill="%23fef08a" opacity="0.8"/><rect x="210" y="160" width="130" height="58" rx="8" fill="%233b82f6"/><rect x="212" y="172" width="30" height="18" rx="2" fill="%23bfdbfe" opacity="0.8"/><rect x="308" y="172" width="30" height="18" rx="2" fill="%23bfdbfe" opacity="0.8"/></svg>`,
    labels: [
      { name: "Vehicle",   confidence: 98.90, parents: ["Transportation"] },
      { name: "Car",       confidence: 97.50, parents: ["Vehicle"] },
      { name: "Asphalt",   confidence: 93.40, parents: ["Road"] },
      { name: "Street",    confidence: 91.20, parents: ["Road"] },
      { name: "Urban",     confidence: 87.60, parents: [] }
    ]
  },
  pizza: {
    name: "pizza_dish.jpg",
    bucket: "image-analyzer-dev-bucket",
    key: "incoming/pizza_dish.jpg",
    size: 1572864,
    valid: true,
    latency: { s3: 65, lambda: 14, rekog: 432, dynamo: 19 },
    svg: `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300"><rect width="400" height="300" fill="%23451a03"/><circle cx="200" cy="148" r="118" fill="%23d97706"/><circle cx="200" cy="148" r="100" fill="%23fbbf24"/><circle cx="155" cy="115" r="18" fill="%23dc2626"/><circle cx="245" cy="135" r="16" fill="%23dc2626"/><circle cx="185" cy="165" r="14" fill="%23dc2626"/><circle cx="220" cy="108" r="12" fill="%2316a34a"/><circle cx="165" cy="175" r="10" fill="%2316a34a"/></svg>`,
    labels: [
      { name: "Pizza",     confidence: 99.10, parents: ["Food"] },
      { name: "Food",      confidence: 98.30, parents: [] },
      { name: "Cheese",    confidence: 95.30, parents: ["Dairy"] },
      { name: "Pepperoni", confidence: 92.40, parents: ["Meat"] },
      { name: "Dish",      confidence: 88.70, parents: ["Food"] }
    ]
  },
  dog: {
    name: "pet_portrait.jpeg",
    bucket: "image-analyzer-dev-bucket",
    key: "incoming/pet_portrait.jpeg",
    size: 1310720,
    valid: true,
    latency: { s3: 88, lambda: 16, rekog: 491, dynamo: 25 },
    svg: `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300"><rect width="400" height="300" fill="%230284c7"/><circle cx="200" cy="168" r="72" fill="%23b45309"/><ellipse cx="134" cy="118" rx="22" ry="40" fill="%2378350f"/><ellipse cx="266" cy="118" rx="22" ry="40" fill="%2378350f"/><circle cx="178" cy="170" r="8" fill="%231e293b"/><circle cx="222" cy="170" r="8" fill="%231e293b"/><ellipse cx="200" cy="194" rx="18" ry="10" fill="%23831843" opacity="0.8"/></svg>`,
    labels: [
      { name: "Dog",    confidence: 98.70, parents: ["Animal"] },
      { name: "Canine", confidence: 98.50, parents: ["Animal"] },
      { name: "Pet",    confidence: 94.20, parents: ["Animal"] },
      { name: "Golden Retriever", confidence: 88.60, parents: ["Dog"] },
      { name: "Animal", confidence: 85.10, parents: [] }
    ]
  },
  invalid_pdf: {
    name: "annual_report.pdf",
    bucket: "image-analyzer-dev-bucket",
    key: "incoming/annual_report.pdf",
    size: 3145728,
    valid: false,
    latency: { s3: 0, lambda: 0, rekog: 0, dynamo: 0 },
    svg: `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300"><rect width="400" height="300" fill="%231e293b"/><rect x="148" y="55" width="104" height="140" rx="6" fill="%23374151"/><rect x="148" y="55" width="104" height="38" rx="6" fill="%23ef4444"/><text x="173" y="82" fill="%23fff" font-family="sans-serif" font-weight="800" font-size="18">PDF</text><rect x="164" y="108" width="72" height="6" rx="3" fill="%234b5563"/><rect x="164" y="122" width="60" height="6" rx="3" fill="%234b5563"/><rect x="164" y="136" width="68" height="6" rx="3" fill="%234b5563"/></svg>`,
    labels: []
  }
};

// ─── State ────────────────────────────────────────────────────────────────
let currentSampleKey = 'landscape';
let minConfidence = 70;
let maxLabels = 10;
let isExecuting = false;
let totalProcessed = 0;
let totalSuccess = 0;
let dlqMessages = [];

// ─── Init ─────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  selectSample('landscape');
});

// ─── Main Tab Switching ───────────────────────────────────────────────────
function switchMainTab(tab) {
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.main-tab').forEach(b => b.classList.remove('active'));
  document.getElementById(`view-${tab}`).classList.add('active');
  document.getElementById(`tab-${tab}`).classList.add('active');
}

// ─── Sample Selection ─────────────────────────────────────────────────────
function selectSample(key) {
  if (isExecuting) return;
  currentSampleKey = key;

  document.querySelectorAll('.sample-btn').forEach(b => b.classList.remove('active'));
  const btn = document.getElementById(`sbtn-${key}`);
  if (btn) btn.classList.add('active');

  const sample = SAMPLES[key];
  document.getElementById('image-display').src = sample.svg;
  document.getElementById('rejection-banner').style.display = sample.valid ? 'none' : 'flex';
  document.getElementById('file-path-display').textContent = sample.key;

  document.getElementById('labels-list').innerHTML =
    `<div class="empty-state">Click "Run Pipeline Trigger" to analyze this file.</div>`;
  document.getElementById('json-view').textContent =
    `// DynamoDB put_item payload will appear here after pipeline runs...`;

  const si = document.getElementById('status-indicator');
  si.textContent = 'Ready';
  si.className = 'status-indicator';

  resetPipelineUI();
  resetLatency();

  appendLog(`[SELECT] Queued "${sample.name}" (${fmtBytes(sample.size)})`, 'info');
}

// ─── File Upload ──────────────────────────────────────────────────────────
function handleFileUpload(e) {
  const file = e.target.files[0];
  if (!file) return;

  const ext = '.' + file.name.split('.').pop().toLowerCase();
  const isValid = ['.jpg', '.jpeg', '.png'].includes(ext);
  const nl = file.name.toLowerCase();

  let labels = [];
  if (isValid) {
    if (nl.includes('dog') || nl.includes('cat') || nl.includes('pet')) {
      labels = [
        { name: "Animal",   confidence: 98.3, parents: [] },
        { name: "Pet",      confidence: 95.7, parents: ["Animal"] },
        { name: "Mammal",   confidence: 93.1, parents: ["Animal"] },
        { name: "Portrait", confidence: 87.4, parents: [] }
      ];
    } else if (nl.includes('car') || nl.includes('road') || nl.includes('street')) {
      labels = [
        { name: "Vehicle",  confidence: 97.6, parents: [] },
        { name: "Car",      confidence: 96.2, parents: ["Vehicle"] },
        { name: "Road",     confidence: 91.8, parents: [] },
        { name: "Urban",    confidence: 85.5, parents: [] }
      ];
    } else if (nl.includes('food') || nl.includes('pizza') || nl.includes('meal')) {
      labels = [
        { name: "Food",  confidence: 98.1, parents: [] },
        { name: "Dish",  confidence: 94.5, parents: ["Food"] },
        { name: "Meal",  confidence: 90.2, parents: ["Food"] },
        { name: "Plate", confidence: 86.7, parents: [] }
      ];
    } else {
      labels = [
        { name: "Photograph",  confidence: 97.8, parents: [] },
        { name: "Image",       confidence: 95.4, parents: [] },
        { name: "Color",       confidence: 91.6, parents: [] },
        { name: "Digital",     confidence: 72.1, parents: [] }
      ];
    }
  }

  SAMPLES['custom'] = {
    name: file.name,
    bucket: "image-analyzer-dev-bucket",
    key: `incoming/${file.name}`,
    size: file.size,
    valid: isValid,
    latency: { s3: 88, lambda: 18, rekog: 490, dynamo: 24 },
    svg: URL.createObjectURL(file),
    labels
  };

  selectSample('custom');
  setTimeout(() => executePipeline(), 350);
}

// ─── Config ───────────────────────────────────────────────────────────────
function updateConfig() {
  minConfidence = parseInt(document.getElementById('conf-slider').value);
  maxLabels     = parseInt(document.getElementById('max-slider').value);
  document.getElementById('conf-val').textContent = `${minConfidence}%`;
  document.getElementById('max-val').textContent  = maxLabels;
}

// ─── Pipeline Execution ───────────────────────────────────────────────────
async function executePipeline() {
  if (isExecuting) return;
  isExecuting = true;

  const btnRun = document.getElementById('btn-run');
  btnRun.disabled = true;

  const sample = SAMPLES[currentSampleKey];
  const si = document.getElementById('status-indicator');
  const dlqSimEnabled = document.getElementById('dlq-toggle').checked;

  resetPipelineUI();
  resetLatency();

  si.textContent = 'Processing…';
  si.className   = 'status-indicator running';
  document.getElementById('image-overlay').classList.add('visible');

  appendLog(`${'─'.repeat(54)}`, 'info');
  appendLog(`[S3]     ObjectCreated:Put event fired`, 'info');
  appendLog(`[S3]     Bucket: "${sample.bucket}"`, 'info');
  appendLog(`[S3]     Key:    "${sample.key}"  (${fmtBytes(sample.size)})`, 'info');

  setStep('s3', 'active');
  await delay(450);

  animateConnector('1');
  setStep('lambda', 'active');
  appendLog(`[LAMBDA] Invoked handler.lambda_handler via S3 trigger`, 'info');
  appendLog(`[LAMBDA] Runtime: Python 3.12 · Memory: 256 MB`, 'info');
  await delay(400);

  const ext = '.' + sample.name.split('.').pop().toLowerCase();
  appendLog(`[LAMBDA] Validating extension "${ext}" against {.jpg, .jpeg, .png}`, 'info');
  await delay(300);

  document.getElementById('image-overlay').classList.remove('visible');

  // ── Invalid file path ─────────────────────────────────────────────────
  if (!sample.valid || dlqSimEnabled) {
    const reason = !sample.valid
      ? `Extension "${ext}" not in allowed set — skipping Rekognition`
      : 'DLQ simulation enabled — forcing error routing';

    appendLog(`[WARN]   ${reason}`, 'warn');
    appendLog(`[DLQ]    Routing failed event to SQS: ImageProcessingDLQ`, 'dlq');
    await delay(350);

    animateConnector('4');
    setStep('dlq', 'error');

    const msg = buildDLQMessage(sample, !sample.valid ? 'UNSUPPORTED_FORMAT' : 'SIMULATED_ERROR');
    addDLQMessage(msg);
    dlqMessages.push(msg);

    totalProcessed++;
    updateCounters(false);

    si.textContent = 'DLQ Routed';
    si.className   = 'status-indicator error';

    appendLog(`[DLQ]    Message enqueued. MessageId: ${msg.id}`, 'dlq');
    appendLog(`[LAMBDA] Returned statusCode: 500 (routed to DLQ)`, 'warn');

    renderJSON(sample, false);

    isExecuting = false;
    btnRun.disabled = false;
    return;
  }

  // ── Valid image path ──────────────────────────────────────────────────
  appendLog(`[LAMBDA] Extension "${ext}" ✓ valid — invoking Rekognition`, 'success');
  await delay(350);

  animateConnector('2');
  setStep('rekognition', 'active');
  appendLog(`[REKOG]  detect_labels(S3Object={Bucket:"${sample.bucket}", Name:"${sample.key}"})`, 'info');
  appendLog(`[REKOG]  Params: MaxLabels=${maxLabels}, MinConfidence=${minConfidence}%`, 'info');
  await delay(700);

  const filtered = sample.labels
    .filter(l => l.confidence >= minConfidence)
    .slice(0, maxLabels);

  appendLog(`[REKOG]  Returned ${filtered.length} label(s) above ${minConfidence}% threshold`, 'success');
  await delay(400);

  animateConnector('3');
  setStep('dynamodb', 'active');
  appendLog(`[DYNAMO] put_item → Table="ImageTags", PK="${sample.key}"`, 'info');
  await delay(400);

  appendLog(`[DYNAMO] Record written successfully. HTTP 200.`, 'success');

  const totalMs = sample.latency.s3 + sample.latency.lambda + sample.latency.rekog + sample.latency.dynamo;
  appendLog(`[LAMBDA] Completed. Total latency: ${totalMs} ms`, 'success');
  appendLog(`[LAMBDA] statusCode: 200 — processed 1 image`, 'success');

  si.textContent = '200 OK';
  si.className   = 'status-indicator success';

  renderLabels(filtered);
  renderJSON(sample, true, filtered);
  animateLatency(sample.latency);

  totalProcessed++;
  totalSuccess++;
  updateCounters(true);

  isExecuting = false;
  btnRun.disabled = false;
}

// ─── Pipeline UI Helpers ──────────────────────────────────────────────────
function setStep(id, state) {
  const el = document.getElementById(`step-${id}`);
  if (el) el.className = `step ${state}`;
}

function resetPipelineUI() {
  ['s3','lambda','rekognition','dynamodb','dlq'].forEach(s => setStep(s, ''));
  ['1','2','3','4'].forEach(c => {
    const el = document.getElementById(`conn-${c}`);
    if (el) el.classList.remove('active');
  });
}

function animateConnector(id) {
  const el = document.getElementById(`conn-${id}`);
  if (!el) return;
  el.classList.add('active');
  const pulse = document.getElementById(`pulse-${id}`);
  if (pulse) {
    pulse.style.animation = 'none';
    pulse.offsetHeight; // reflow
    pulse.style.animation = '';
  }
}

// ─── Latency ──────────────────────────────────────────────────────────────
function animateLatency(lat) {
  const max = 1000;
  const bars = [
    { id: 'lat-s3',     valId: 'latval-s3',     ms: lat.s3,     maxPct: 20  },
    { id: 'lat-lambda', valId: 'latval-lambda',  ms: lat.lambda, maxPct: 10  },
    { id: 'lat-rekog',  valId: 'latval-rekog',   ms: lat.rekog,  maxPct: 70  },
    { id: 'lat-dynamo', valId: 'latval-dynamo',  ms: lat.dynamo, maxPct: 8   }
  ];

  const total = lat.s3 + lat.lambda + lat.rekog + lat.dynamo;

  bars.forEach(b => {
    const pct = Math.min((b.ms / max) * 100, 100);
    document.getElementById(b.id).style.width = `${pct}%`;
    document.getElementById(b.valId).textContent = `${b.ms} ms`;
  });

  document.getElementById('latency-total').textContent = `Total: ${total} ms`;
}

function resetLatency() {
  ['s3','lambda','rekog','dynamo'].forEach(k => {
    const el = document.getElementById(`lat-${k}`);
    if (el) el.style.width = '0%';
    const ve = document.getElementById(`latval-${k}`);
    if (ve) ve.textContent = '—';
  });
  const tot = document.getElementById('latency-total');
  if (tot) tot.textContent = 'Total: —';
}

// ─── Render Results ───────────────────────────────────────────────────────
function renderLabels(labels) {
  const c = document.getElementById('labels-list');
  if (!labels || labels.length === 0) {
    c.innerHTML = `<div class="empty-state">No labels matched the confidence threshold (${minConfidence}%).</div>`;
    return;
  }

  c.innerHTML = labels.map(l => `
    <div class="label-row">
      <div class="label-info">
        <span>${l.name}</span>
        <span>${l.confidence.toFixed(2)}%</span>
      </div>
      <div class="bar-bg">
        <div class="bar-fill" style="width:${l.confidence}%"></div>
      </div>
    </div>
  `).join('');
}

function renderJSON(sample, success, labels = []) {
  const jv = document.getElementById('json-view');
  if (!success) {
    jv.textContent =
      `// File "${sample.name}" rejected — routed to DLQ.\n` +
      `// No DynamoDB record written.\n\n` +
      `// DLQ Message:\n` +
      JSON.stringify({
        messageId: generateId(),
        errorCode: "UNSUPPORTED_FORMAT",
        bucket: sample.bucket,
        key: sample.key,
        timestamp: new Date().toISOString()
      }, null, 2);
    return;
  }

  const record = {
    ImageKey:     { S: sample.key },
    SourceBucket: { S: sample.bucket },
    FileSize:     { N: String(sample.size) },
    ProcessedAt:  { S: new Date().toISOString() },
    LabelCount:   { N: String(labels.length) },
    Labels: {
      L: labels.map(l => ({
        M: {
          Name:       { S: l.name },
          Confidence: { N: l.confidence.toFixed(2) },
          Parents:    { L: (l.parents || []).map(p => ({ S: p })) }
        }
      }))
    }
  };

  jv.textContent = JSON.stringify(record, null, 2);
}

// ─── DLQ ─────────────────────────────────────────────────────────────────
function buildDLQMessage(sample, errorCode) {
  return {
    id: generateId(),
    errorCode,
    bucket: sample.bucket,
    key: sample.key,
    size: sample.size,
    timestamp: new Date().toISOString()
  };
}

function addDLQMessage(msg) {
  const list = document.getElementById('dlq-list');
  const empty = list.querySelector('.empty-state');
  if (empty) empty.remove();

  const el = document.createElement('div');
  el.className = 'dlq-message';
  el.innerHTML = `
    <div class="dlq-msg-header">
      <span>⚠ ${msg.errorCode}</span>
      <span>${new Date(msg.timestamp).toLocaleTimeString()}</span>
    </div>
    <div class="dlq-msg-body">Key: ${msg.key} | MsgId: ${msg.id}</div>
  `;
  list.prepend(el);

  // Switch to DLQ tab
  setTab('dlq');
}

function clearDLQ() {
  dlqMessages = [];
  document.getElementById('dlq-list').innerHTML =
    `<div class="empty-state">Queue cleared. No messages in DLQ.</div>`;
  document.getElementById('dlq-count').textContent = '0';
}

// ─── Counters ─────────────────────────────────────────────────────────────
function updateCounters(success) {
  document.getElementById('total-count').textContent = totalProcessed;
  document.getElementById('success-count').textContent = totalSuccess;
  const dlqCount = totalProcessed - totalSuccess;
  document.getElementById('dlq-count').textContent = dlqCount;
}

// ─── Logs ─────────────────────────────────────────────────────────────────
function appendLog(msg, type = 'info') {
  const t = document.getElementById('terminal-log');
  const row = document.createElement('div');
  row.className = `log-row ${type}`;
  const now = new Date().toTimeString().split(' ')[0];
  row.textContent = `[${now}] ${msg}`;
  t.appendChild(row);
  t.scrollTop = t.scrollHeight;
}

// ─── Tab Switching ────────────────────────────────────────────────────────
function setTab(name) {
  document.querySelectorAll('.tab-item').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-view').forEach(v => v.classList.remove('active'));

  const btn = document.getElementById(`tabbtn-${name}`);
  if (btn) btn.classList.add('active');

  const view = document.getElementById(`view-${name}`);
  if (view) view.classList.add('active');
}

// ─── Utilities ────────────────────────────────────────────────────────────
function fmtBytes(b) {
  if (b >= 1048576) return (b / 1048576).toFixed(2) + ' MB';
  if (b >= 1024)    return (b / 1024).toFixed(0) + ' KB';
  return b + ' B';
}

function generateId() {
  return Math.random().toString(36).slice(2, 10).toUpperCase();
}

function delay(ms) {
  return new Promise(r => setTimeout(r, ms));
}
