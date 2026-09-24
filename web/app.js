// Preset Scenarios
const SAMPLES = {
  landscape: {
    name: "sample_landscape.jpg",
    bucket: "image-analyzer-dev-bucket",
    key: "incoming/sample_landscape.jpg",
    size: 1048576,
    valid: true,
    svg: `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300"><rect width="400" height="300" fill="%230f172a"/><path d="M0 200 L120 100 L200 160 L300 80 L400 200 Z" fill="%231e3a8a"/><path d="M0 240 L150 140 L260 210 L400 130 L400 300 L0 300 Z" fill="%23065f46"/><circle cx="340" cy="60" r="30" fill="%23f59e0b"/></svg>`,
    labels: [
      { name: "Mountain", confidence: 99.45 },
      { name: "Tree", confidence: 96.12 },
      { name: "Sky", confidence: 94.80 },
      { name: "Outdoors", confidence: 92.30 }
    ]
  },
  traffic: {
    name: "city_traffic.png",
    bucket: "image-analyzer-dev-bucket",
    key: "incoming/city_traffic.png",
    size: 2097152,
    valid: true,
    svg: `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300"><rect width="400" height="300" fill="%2318181b"/><rect x="0" y="180" width="400" height="120" fill="%2327272a"/><line x1="0" y1="240" x2="400" y2="240" stroke="%23eab308" stroke-width="4" stroke-dasharray="20 10"/><rect x="80" y="190" width="120" height="50" rx="6" fill="%23ef4444"/><rect x="240" y="170" width="130" height="60" rx="6" fill="%233b82f6"/></svg>`,
    labels: [
      { name: "Vehicle", confidence: 98.90 },
      { name: "Car", confidence: 97.50 },
      { name: "Asphalt", confidence: 93.40 },
      { name: "Street", confidence: 91.20 }
    ]
  },
  pizza: {
    name: "pizza_dish.jpg",
    bucket: "image-analyzer-dev-bucket",
    key: "incoming/pizza_dish.jpg",
    size: 1572864,
    valid: true,
    svg: `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300"><rect width="400" height="300" fill="%23451a03"/><circle cx="200" cy="150" r="110" fill="%23d97706"/><circle cx="200" cy="150" r="95" fill="%23fbbf24"/><circle cx="160" cy="120" r="16" fill="%23dc2626"/><circle cx="240" cy="140" r="15" fill="%23dc2626"/></svg>`,
    labels: [
      { name: "Pizza", confidence: 99.10 },
      { name: "Cheese", confidence: 95.30 },
      { name: "Pepperoni", confidence: 92.40 }
    ]
  },
  dog: {
    name: "pet_portrait.jpeg",
    bucket: "image-analyzer-dev-bucket",
    key: "incoming/pet_portrait.jpeg",
    size: 1258291,
    valid: true,
    svg: `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300"><rect width="400" height="300" fill="%230284c7"/><circle cx="200" cy="160" r="65" fill="%23b45309"/><ellipse cx="140" cy="120" rx="18" ry="35" fill="%2378350f"/><ellipse cx="260" cy="120" rx="18" ry="35" fill="%2378350f"/></svg>`,
    labels: [
      { name: "Dog", confidence: 98.70 },
      { name: "Canine", confidence: 98.50 },
      { name: "Pet", confidence: 94.20 }
    ]
  },
  invalid_pdf: {
    name: "annual_report.pdf",
    bucket: "image-analyzer-dev-bucket",
    key: "incoming/annual_report.pdf",
    size: 3145728,
    valid: false,
    svg: `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300"><rect width="400" height="300" fill="%231e293b"/><rect x="150" y="60" width="100" height="150" rx="4" fill="%23ef4444"/><text x="170" y="145" fill="%23fff" font-family="sans-serif" font-weight="bold" font-size="24">PDF</text></svg>`,
    labels: []
  }
};

let currentSampleKey = 'landscape';
let minConfidence = 70;
let maxLabels = 10;
let isExecuting = false;

document.addEventListener('DOMContentLoaded', () => {
  selectSample('landscape');
});

function selectSample(key) {
  if (isExecuting) return;
  currentSampleKey = key;

  document.querySelectorAll('.sample-btn').forEach(b => b.classList.remove('active'));
  const btn = document.querySelector(`.sample-btn[onclick*="${key}"]`);
  if (btn) btn.classList.add('active');

  const sample = SAMPLES[key];
  document.getElementById('image-display').src = sample.svg;
  document.getElementById('rejection-banner').style.display = sample.valid ? 'none' : 'flex';

  document.getElementById('labels-list').innerHTML = `<div class="empty-state">Click "Run Pipeline Trigger" to analyze file.</div>`;
  document.getElementById('json-view').textContent = `// DynamoDB put_item payload will appear here...`;
  
  const statusElem = document.getElementById('status-indicator');
  statusElem.textContent = 'Ready';
  statusElem.className = 'status-indicator';

  appendLog(`[SELECT] Chosen file "${sample.name}" (${(sample.size / 1024 / 1024).toFixed(2)} MB)`, 'info');
}

function handleFileUpload(e) {
  const file = e.target.files[0];
  if (!file) return;

  const ext = '.' + file.name.split('.').pop().toLowerCase();
  const isValid = ['.jpg', '.jpeg', '.png'].includes(ext);

  // Generate varied mock labels based on file name hints or random selection
  let labels = [];
  if (isValid) {
    const nameLower = file.name.toLowerCase();
    if (nameLower.includes('dog') || nameLower.includes('cat') || nameLower.includes('pet')) {
      labels = [
        { name: "Animal", confidence: 98.3 },
        { name: "Pet", confidence: 95.7 },
        { name: "Mammal", confidence: 93.1 },
        { name: "Portrait", confidence: 87.4 },
        { name: "Indoor", confidence: 78.2 }
      ];
    } else if (nameLower.includes('car') || nameLower.includes('road') || nameLower.includes('city') || nameLower.includes('street')) {
      labels = [
        { name: "Vehicle", confidence: 97.6 },
        { name: "Car", confidence: 96.2 },
        { name: "Road", confidence: 91.8 },
        { name: "Urban", confidence: 85.5 },
        { name: "Transportation", confidence: 80.3 }
      ];
    } else if (nameLower.includes('food') || nameLower.includes('pizza') || nameLower.includes('meal')) {
      labels = [
        { name: "Food", confidence: 98.1 },
        { name: "Dish", confidence: 94.5 },
        { name: "Meal", confidence: 90.2 },
        { name: "Plate", confidence: 86.7 },
        { name: "Table", confidence: 76.4 }
      ];
    } else {
      // Default labels for any uploaded image
      labels = [
        { name: "Photograph", confidence: 97.8 },
        { name: "Image", confidence: 95.4 },
        { name: "Color", confidence: 91.6 },
        { name: "Art", confidence: 84.2 },
        { name: "Visual Media", confidence: 78.9 },
        { name: "Digital", confidence: 72.1 }
      ];
    }
  }

  SAMPLES['custom'] = {
    name: file.name,
    bucket: "image-analyzer-dev-bucket",
    key: `incoming/${file.name}`,
    size: file.size,
    valid: isValid,
    svg: URL.createObjectURL(file),
    labels: labels
  };

  selectSample('custom');

  // Auto-trigger pipeline after upload so user sees results immediately
  setTimeout(() => executePipeline(), 300);
}

function updateConfig() {
  minConfidence = parseInt(document.getElementById('conf-slider').value);
  maxLabels = parseInt(document.getElementById('max-slider').value);

  document.getElementById('conf-val').textContent = `${minConfidence}%`;
  document.getElementById('max-val').textContent = maxLabels;
}

function appendLog(msg, type = 'info') {
  const terminal = document.getElementById('terminal-log');
  const row = document.createElement('div');
  row.className = `log-row ${type}`;
  const now = new Date().toTimeString().split(' ')[0];
  row.textContent = `[${now}] ${msg}`;
  terminal.appendChild(row);
  terminal.scrollTop = terminal.scrollHeight;
}

function setStep(stepId, state = 'active') {
  const step = document.getElementById(`step-${stepId}`);
  if (step) {
    step.className = `step ${state}`;
  }
}

function setConnector(connId, state = 'active') {
  const conn = document.getElementById(`conn-${connId}`);
  if (conn) {
    conn.className = `connector ${state}`;
  }
}

function resetPipelineUI() {
  ['s3', 'lambda', 'rekognition', 'dynamodb'].forEach(s => setStep(s, ''));
  ['1', '2', '3'].forEach(c => setConnector(c, ''));
}

async function executePipeline() {
  if (isExecuting) return;
  isExecuting = true;
  document.getElementById('btn-run').disabled = true;

  const sample = SAMPLES[currentSampleKey];
  const statusElem = document.getElementById('status-indicator');

  resetPipelineUI();
  statusElem.textContent = 'Processing...';
  statusElem.className = 'status-indicator running';

  appendLog(`------------------------------------------------------------`, 'info');
  appendLog(`[S3] ObjectCreated:Put event triggered for bucket "image-analyzer-dev-bucket"`, 'info');

  setStep('s3', 'active');
  await delay(400);

  setConnector('1', 'active');
  setStep('lambda', 'active');
  appendLog(`[LAMBDA] Invoking handler.py with S3 event record`, 'info');
  await delay(400);

  const ext = '.' + sample.name.split('.').pop().toLowerCase();
  appendLog(`[LAMBDA] Validating file extension "${ext}" against allowed list`, 'info');

  if (!sample.valid) {
    await delay(300);
    setStep('lambda', 'error');
    appendLog(`[WARN] Extension "${ext}" is not supported. Skipping Rekognition call.`, 'warn');
    appendLog(`[SUCCESS] Lambda handler completed with 0 errors (Graceful skip)`, 'success');

    statusElem.textContent = 'Rejected (.pdf)';
    statusElem.className = 'status-indicator error';
    renderJSON(sample, false);

    isExecuting = false;
    document.getElementById('btn-run').disabled = false;
    return;
  }

  appendLog(`[LAMBDA] Extension "${ext}" is valid. Calling Rekognition API.`, 'success');
  await delay(400);

  setConnector('2', 'active');
  setStep('rekognition', 'active');
  appendLog(`[REKOGNITION] detect_labels(S3Object={Bucket: "${sample.bucket}", Name: "${sample.key}"})`, 'info');
  await delay(600);

  const filteredLabels = sample.labels
    .filter(l => l.confidence >= minConfidence)
    .slice(0, maxLabels);

  appendLog(`[REKOGNITION] Returned ${filteredLabels.length} labels with confidence >= ${minConfidence}%`, 'success');
  await delay(400);

  setConnector('3', 'active');
  setStep('dynamodb', 'active');
  appendLog(`[DYNAMODB] put_item(Table="ImageTags", Key="${sample.key}")`, 'info');
  await delay(400);

  appendLog(`[DYNAMODB] Record created successfully. Execution duration: 42ms.`, 'success');
  statusElem.textContent = '200 OK';
  statusElem.className = 'status-indicator success';

  renderLabels(filteredLabels);
  renderJSON(sample, true, filteredLabels);

  isExecuting = false;
  document.getElementById('btn-run').disabled = false;
}

function renderLabels(labels) {
  const container = document.getElementById('labels-list');
  if (!labels || labels.length === 0) {
    container.innerHTML = `<div class="empty-state">No labels matched the confidence threshold.</div>`;
    return;
  }

  container.innerHTML = labels.map(l => `
    <div class="label-row">
      <div class="label-info">
        <span>${l.name}</span>
        <span>${l.confidence}%</span>
      </div>
      <div class="bar-bg">
        <div class="bar-fill" style="width: ${l.confidence}%"></div>
      </div>
    </div>
  `).join('');
}

function renderJSON(sample, success, labels = []) {
  const jsonView = document.getElementById('json-view');
  if (!success) {
    jsonView.textContent = `// File "${sample.name}" rejected during format validation.\n// No record written to DynamoDB.`;
    return;
  }

  const record = {
    "ImageKey": sample.key,
    "SourceBucket": sample.bucket,
    "FileSize": sample.size,
    "ProcessedAt": new Date().toISOString(),
    "LabelCount": labels.length,
    "Labels": labels
  };

  jsonView.textContent = JSON.stringify(record, null, 2);
}

function setTab(tabName) {
  document.querySelectorAll('.tab-item').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-view').forEach(v => v.classList.remove('active'));

  const btn = document.querySelector(`.tab-item[onclick*="${tabName}"]`);
  if (btn) btn.classList.add('active');

  const view = document.getElementById(`view-${tabName}`);
  if (view) view.classList.add('active');
}

function delay(ms) {
  return new Promise(r => setTimeout(r, ms));
}
