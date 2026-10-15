/*
 * Elkinematics Live Screening Interface Logic
 * Dual-stream Kinematic & Orthographic Assessment
 * Strict Zero-Emoji Policy Enforced
 */

const canvas = document.getElementById('drawingCanvas');
const ctx = canvas.getContext('2d');

let isDrawing = false;
let strokeData = [];

let promptStartTime = Date.now();
let hasStartedWriting = false;
let latencyMs = 0;
let currentStrokeCount = 0;

// --- RESPONSIVE CANVAS ---
function resizeCanvas() {
    const container = document.querySelector('.container');
    canvas.width = container.clientWidth - 40;
    canvas.height = window.innerHeight * 0.58;
    clearCanvas();
}

window.addEventListener('resize', resizeCanvas);

// --- EXPLICIT TABLET TOUCH SCROLLBAR LOGIC ---
const scrollContainer = document.querySelector('.app-scroll-container');
const scrollTrack = document.getElementById('tabletScrollTrack');
const scrollThumb = document.getElementById('tabletScrollThumb');
const quickScrollBtn = document.getElementById('quickScrollBtn');

let isDraggingScroll = false;

function updateThumbFromScroll() {
    if (isDraggingScroll) return;
    const maxScroll = scrollContainer.scrollHeight - scrollContainer.clientHeight;
    if (maxScroll <= 10) {
        scrollThumb.style.display = 'none';
        quickScrollBtn.style.display = 'none';
        return;
    }
    scrollThumb.style.display = 'flex';
    quickScrollBtn.style.display = 'block';

    const trackHeight = scrollTrack.clientHeight - scrollThumb.clientHeight - 20;
    const progress = Math.max(0, Math.min(1, scrollContainer.scrollTop / maxScroll));
    scrollThumb.style.top = `${10 + progress * trackHeight}px`;

    if (progress > 0.4) {
        quickScrollBtn.innerHTML = 'Top &#8593;';
    } else {
        quickScrollBtn.innerHTML = 'Results &#8595;';
    }
}

scrollContainer.addEventListener('scroll', updateThumbFromScroll);
window.addEventListener('resize', updateThumbFromScroll);

function handleScrollTrackMove(clientY) {
    const rect = scrollTrack.getBoundingClientRect();
    const maxOffset = rect.height - scrollThumb.clientHeight - 20;
    const offsetY = clientY - rect.top - (scrollThumb.clientHeight / 2) - 10;
    const progress = Math.max(0, Math.min(1, offsetY / maxOffset));
    const maxScroll = scrollContainer.scrollHeight - scrollContainer.clientHeight;
    scrollContainer.scrollTop = progress * maxScroll;
    scrollThumb.style.top = `${10 + progress * maxOffset}px`;
}

scrollTrack.addEventListener('pointerdown', (e) => {
    isDraggingScroll = true;
    scrollThumb.classList.add('dragging');
    scrollTrack.setPointerCapture(e.pointerId);
    handleScrollTrackMove(e.clientY);
});

scrollTrack.addEventListener('pointermove', (e) => {
    if (isDraggingScroll) {
        handleScrollTrackMove(e.clientY);
    }
});

scrollTrack.addEventListener('pointerup', (e) => {
    isDraggingScroll = false;
    scrollThumb.classList.remove('dragging');
    try { scrollTrack.releasePointerCapture(e.pointerId); } catch (err) { }
    updateThumbFromScroll();
});

scrollTrack.addEventListener('pointercancel', () => {
    isDraggingScroll = false;
    scrollThumb.classList.remove('dragging');
});

quickScrollBtn.addEventListener('click', () => {
    const maxScroll = scrollContainer.scrollHeight - scrollContainer.clientHeight;
    if (scrollContainer.scrollTop > maxScroll / 2) {
        scrollContainer.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
        const card = document.getElementById('transcriptionCard');
        if (card && card.style.display !== 'none') {
            card.scrollIntoView({ behavior: 'smooth' });
        } else {
            scrollContainer.scrollTo({ top: maxScroll, behavior: 'smooth' });
        }
    }
});

// Prevent mobile browser pull-to-refresh on downward drag from top of screen
let touchStartY = 0;
window.addEventListener('touchstart', (e) => {
    if (e.touches && e.touches.length > 0) {
        touchStartY = e.touches[0].clientY;
    }
}, { passive: true });

window.addEventListener('touchmove', (e) => {
    if (!e.touches || e.touches.length === 0) return;
    const currentY = e.touches[0].clientY;
    if (window.scrollY <= 0 && currentY > touchStartY && e.target !== canvas) {
        e.preventDefault();
    }
}, { passive: false });

// --- WRITING MODE LOGIC ---
const modeFreeFlow = document.getElementById('modeFreeFlow');
const modePrompted = document.getElementById('modePrompted');
const promptSelectorContainer = document.getElementById('promptSelectorContainer');
const promptSelect = document.getElementById('promptSelect');
const promptDisplay = document.getElementById('promptDisplay');
const transcribeBtn = document.getElementById('transcribeBtn');
const analyzeBtn = document.getElementById('analyzeBtn');

function updateModeUI() {
    if (modeFreeFlow.checked) {
        promptSelectorContainer.style.display = 'none';
        promptDisplay.innerText = '"Write freely on the canvas below"';
        promptDisplay.className = 'instruction prompt-display-free';
    } else {
        promptSelectorContainer.style.display = 'flex';
        promptDisplay.innerText = `"${promptSelect.value}"`;
        promptDisplay.className = 'instruction prompt-display-target';
    }
    clearCanvas();
}

modeFreeFlow.addEventListener('change', updateModeUI);
modePrompted.addEventListener('change', updateModeUI);
promptSelect.addEventListener('change', () => {
    if (modePrompted.checked) {
        promptDisplay.innerText = `"${promptSelect.value}"`;
        clearCanvas();
    }
});

// --- MOVEMENT DYNAMICS TELEMETRY ---
function updateMovementMetrics() {
    if (strokeData.length < 5) return;

    let vels = [];
    let nivCount = 0;
    let lastAccel = 0;

    for (let i = 1; i < strokeData.length; i++) {
        const p0 = strokeData[i - 1];
        const p1 = strokeData[i];
        const dt = Math.max(p1.time - p0.time, 1.0);
        const dist = Math.hypot(p1.x - p0.x, p1.y - p0.y);
        const v = dist / dt;
        vels.push(v);

        if (vels.length >= 2) {
            const accel = v - vels[vels.length - 2];
            if (lastAccel !== 0 && ((accel > 0 && lastAccel < 0) || (accel < 0 && lastAccel > 0))) {
                nivCount++;
            }
            lastAccel = accel;
        }
    }

    document.getElementById('telemetryLatency').innerText = `${Math.round(latencyMs)} ms`;
    document.getElementById('telemetryNIV').innerText = nivCount;
    document.getElementById('telemetryStrokes').innerText = currentStrokeCount;

    const statusEl = document.getElementById('telemetryStatus');
    statusEl.classList.remove('telemetry-value-smooth', 'telemetry-value-variable', 'telemetry-value-hesitant');

    if (nivCount > 55) {
        statusEl.innerText = "Hesitant";
        statusEl.classList.add('telemetry-value-hesitant');
    } else if (nivCount > 30) {
        statusEl.innerText = "Variable";
        statusEl.classList.add('telemetry-value-variable');
    } else {
        statusEl.innerText = "Smooth";
        statusEl.classList.add('telemetry-value-smooth');
    }
}

function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    strokeData = [];
    hasStartedWriting = false;
    promptStartTime = Date.now();
    currentStrokeCount = 0;
    latencyMs = 0;

    document.getElementById('transcriptionCard').style.display = 'none';
    document.getElementById('resultsDashboard').style.display = 'none';
    const reversalNotice = document.getElementById('reversalNotice');
    if (reversalNotice) {
        reversalNotice.style.display = 'none';
        reversalNotice.innerText = '';
    }
    document.getElementById('telemetryLatency').innerText = "0 ms";
    document.getElementById('telemetryNIV').innerText = "0";
    document.getElementById('telemetryStrokes').innerText = "0";
    const statusEl = document.getElementById('telemetryStatus');
    statusEl.innerText = "Smooth";
    statusEl.classList.remove('telemetry-value-variable', 'telemetry-value-hesitant');
    statusEl.classList.add('telemetry-value-smooth');

    // Baseline guide
    ctx.beginPath();
    ctx.moveTo(canvas.width * 0.05, canvas.height * 0.75);
    ctx.lineTo(canvas.width * 0.95, canvas.height * 0.75);
    ctx.strokeStyle = "#ecf0f1";
    ctx.lineWidth = 3;
    ctx.stroke();
}

resizeCanvas();
updateModeUI();

// --- DRAWING LOGIC ---
function recordPoint(e, isTouching) {
    strokeData.push({
        time: e.timeStamp,
        x: e.offsetX,
        y: e.offsetY,
        pressure: e.pressure || 0.5,
        tiltX: e.tiltX || 0,
        tiltY: e.tiltY || 0,
        touching: isTouching
    });
}

canvas.addEventListener('pointerdown', (e) => {
    if (!hasStartedWriting) {
        latencyMs = Date.now() - promptStartTime;
        hasStartedWriting = true;
    }
    isDrawing = true;
    currentStrokeCount++;
    ctx.beginPath();
    ctx.moveTo(e.offsetX, e.offsetY);
    recordPoint(e, 1);
});

canvas.addEventListener('pointermove', (e) => {
    if (isDrawing) {
        ctx.lineWidth = Math.max((e.pressure || 0.5) * 5, 2.5);
        ctx.strokeStyle = "#2c3e50";
        ctx.lineTo(e.offsetX, e.offsetY);
        ctx.stroke();
        recordPoint(e, 1);
    }
});

canvas.addEventListener('pointerup', (e) => {
    if (isDrawing) {
        isDrawing = false;
        recordPoint(e, 0);
        updateMovementMetrics();
    }
});

canvas.addEventListener('pointerout', (e) => {
    if (isDrawing) {
        isDrawing = false;
        recordPoint(e, 0);
        updateMovementMetrics();
    }
});

document.getElementById('clearBtn').addEventListener('click', clearCanvas);

// --- LOW-LEVEL GOOGLE DIGITAL INK QUERY ---
async function queryGoogleInk(strokes) {
    if (strokes.length === 0) return { winner: "?", candidates: [] };

    const inkData = strokes.map(s => [
        s.map(pt => Math.round(pt.x)),
        s.map(pt => Math.round(pt.y)),
        s.map((pt, idx) => Math.round(pt.time - strokes[0][0].time))
    ]);

    const requestPayload = {
        options: "enable_pre_space",
        requests: [{
            writing_guide: {
                writing_area_width: Math.round(canvas.width),
                writing_area_height: Math.round(canvas.height)
            },
            ink: inkData,
            language: "en"
        }]
    };

    try {
        const res = await fetch("https://www.google.com/inputtools/request?ime=handwriting", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestPayload)
        });
        const data = await res.json();
        if (data && data[1] && data[1][0] && data[1][0][1]) {
            const candidates = data[1][0][1];
            return {
                winner: candidates[0] || "?",
                candidates: candidates.slice(0, 6)
            };
        }
    } catch (err) {
        console.warn("Digital ink recognition offline or unreachable.");
    }
    return { winner: "?", candidates: [] };
}

// --- KINEMATIC CHARACTER CLUSTERING & LIGATURE SPLITTING ---
function segmentIntoCharacterClusters(strokes) {
    if (!strokes || strokes.length === 0) return [];

    // Step 1: Pre-process wide strokes with inflection point splitting (for unbroken cursive)
    const refinedStrokes = [];
    strokes.forEach(s => {
        if (s.length < 15) {
            refinedStrokes.push(s);
            return;
        }

        const xs = s.map(p => p.x);
        const ys = s.map(p => p.y);
        const sW = Math.max(...xs) - Math.min(...xs);
        const sH = Math.max(...ys) - Math.min(...ys);
        const yMin = Math.min(...ys);

        // If stroke is exceptionally wide (spans > 1.8x height), inspect ligature valleys
        if (sW > 1.8 * Math.max(sH, 20)) {
            const splitIndices = [];
            const baselineThreshold = yMin + 0.55 * sH;

            for (let i = 2; i < s.length - 2; i++) {
                const prev = s[i - 1];
                const curr = s[i];
                const next = s[i + 1];

                // Valley minimum: descending into ascending in the lower half of stroke
                if (curr.y >= baselineThreshold && curr.y >= prev.y && curr.y >= next.y) {
                    const lastSplitIdx = splitIndices.length > 0 ? splitIndices[splitIndices.length - 1] : 0;
                    if (curr.x - s[lastSplitIdx].x > 0.40 * sH) {
                        splitIndices.push(i);
                    }
                }
            }

            if (splitIndices.length > 0) {
                let startIdx = 0;
                splitIndices.forEach(splitIdx => {
                    refinedStrokes.push(s.slice(startIdx, splitIdx + 1));
                    startIdx = splitIdx;
                });
                if (startIdx < s.length - 1) {
                    refinedStrokes.push(s.slice(startIdx));
                }
            } else {
                refinedStrokes.push(s);
            }
        } else {
            refinedStrokes.push(s);
        }
    });

    // Step 2: Sort strokes by horizontal center
    const strokeMeta = refinedStrokes.map(s => {
        const xs = s.map(p => p.x);
        const ys = s.map(p => p.y);
        const ts = s.map(p => p.time);
        const xMin = Math.min(...xs);
        const xMax = Math.max(...xs);
        const yMin = Math.min(...ys);
        const yMax = Math.max(...ys);
        return {
            stroke: s,
            xMin, xMax, yMin, yMax,
            width: Math.max(xMax - xMin, 1),
            height: Math.max(yMax - yMin, 1),
            cx: (xMin + xMax) / 2,
            tStart: Math.min(...ts),
            tEnd: Math.max(...ts)
        };
    });

    strokeMeta.sort((a, b) => a.xMin - b.xMin);

    // Step 3: Cluster overlapping or temporally contiguous strokes
    const clusters = [];
    let currentCluster = [strokeMeta[0]];

    for (let i = 1; i < strokeMeta.length; i++) {
        const prevItem = currentCluster[currentCluster.length - 1];
        const currItem = strokeMeta[i];

        const clusterXMin = Math.min(...currentCluster.map(m => m.xMin));
        const clusterXMax = Math.max(...currentCluster.map(m => m.xMax));
        const clusterYMin = Math.min(...currentCluster.map(m => m.yMin));
        const clusterYMax = Math.max(...currentCluster.map(m => m.yMax));
        const avgH = Math.max(...currentCluster.map(m => m.height));

        const gapX = currItem.xMin - clusterXMax;
        const timePause = Math.max(0, currItem.tStart - prevItem.tEnd);

        // Calculate vertical overlap to prevent multi-stroke letters from splitting
        const overlapY = Math.max(0, Math.min(clusterYMax, currItem.yMax) - Math.max(clusterYMin, currItem.yMin));
        const minH = Math.min(clusterYMax - clusterYMin, currItem.height);
        const verticalOverlapRatio = minH > 0 ? (overlapY / minH) : 0;

        // Group together if:
        // 1. Strokes have significant vertical overlap and are within the same glyph width (e.g. separated D or b)
        // 2. OR horizontal gap is tiny AND pause is short
        const isSameGlyphComponent = (gapX <= 0.35 * avgH) && (verticalOverlapRatio >= 0.30);
        const isContiguousStroke = (gapX <= 0.18 * avgH) && (timePause < 300 || gapX <= 0);

        if (isSameGlyphComponent || isContiguousStroke) {
            currentCluster.push(currItem);
        } else {
            clusters.push(currentCluster.map(m => m.stroke));
            currentCluster = [currItem];
        }
    }

    if (currentCluster.length > 0) {
        clusters.push(currentCluster.map(m => m.stroke));
    }

    return clusters;
}

// --- LOCAL ONNX RUNTIME DUAL-HEAD REVERSAL CLASSIFIER MODULE ---
let ortReversalSession = null;

const VOCABULARY_62 = (
    "abcdefghijklmnopqrstuvwxyz" +
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ" +
    "0123456789"
).split('');

// Asymmetric Reversal Glyphs Mapping
const asymmetricReversible = {
    // 1. Classic Horizontal Reversals (Left/Right)
    'b': 'd', 'd': 'b',
    'p': 'q', 'q': 'p',

    // 2. Structural Horizontal Flips (Uppercase & Unique)
    'B': 'ꓭ',             // Lisu Bha
    'D': 'ᗡ',             // Canadian Syllabics
    'C': 'Ɔ', 'c': 'ɔ',   // Open O
    'E': 'Ǝ', 'e': 'ɘ',   // Reversed E
    'F': 'ꟻ',             // Epigraphic inverted F
    'G': '⅁',             // Turned G
    'J': 'ᒐ',             // Canadian Syllabics
    'L': '⅃',             // Reversed L
    'N': 'И', 'n': 'и',   // Cyrillic I
    'P': 'ꟼ',             // Reversed P
    'R': 'Я', 'r': 'ɿ',   // Cyrillic Ya / Reversed r
    'S': 'Ƨ', 's': 'ƨ',   // Latin tone 2
    'Z': 'S',

    // 3. Rotational & Vertical Inversions (Top/Bottom)
    'm': 'w', 'w': 'm',
    'u': 'n', 'n': 'u',
    't': 'f', 'f': 't',

    // 4. Numbers
    '2': 'S',
    '3': 'Ɛ',
    '4': 'ᔭ',
    '5': 'Ƨ',
    '6': '9', '9': '6',
    '7': 'г'
};

async function initReversalModel() {
    if (!ortReversalSession && typeof ort !== 'undefined') {
        try {
            ortReversalSession = await ort.InferenceSession.create('models/dual_head_reversal.onnx', {
                executionProviders: ['wasm']
            });
            console.log("Local ONNX Reversal Model initialized successfully.");
        } catch (err) {
            console.warn("Could not load local ONNX reversal model:", err);
        }
    }
    return ortReversalSession;
}

function resampleClusterTo64x8(clusterStrokes) {
    const rawX = [], rawY = [], rawPen = [];
    clusterStrokes.forEach((stroke, sIdx) => {
        if (!stroke || stroke.length === 0) return;
        if (sIdx > 0 && rawX.length > 0) {
            rawX.push(stroke[0].x);
            rawY.push(stroke[0].y);
            rawPen.push(0.0);
        }
        stroke.forEach(pt => {
            rawX.push(pt.x);
            rawY.push(pt.y);
            rawPen.push(1.0);
        });
    });

    if (rawX.length === 0) return new Float32Array(64 * 8);

    const minX = Math.min(...rawX), maxX = Math.max(...rawX);
    const minY = Math.min(...rawY), maxY = Math.max(...rawY);
    const scale = Math.max(maxX - minX, maxY - minY, 1e-4);

    const normX = rawX.map(x => (x - minX) / scale);
    const normY = rawY.map(y => (y - minY) / scale);

    const cumDist = [0];
    for (let i = 1; i < normX.length; i++) {
        const d = Math.hypot(normX[i] - normX[i - 1], normY[i] - normY[i - 1]);
        cumDist.push(cumDist[i - 1] + d);
    }
    const totalDist = cumDist[cumDist.length - 1];

    const targetLen = 64;
    const resX = new Float32Array(targetLen);
    const resY = new Float32Array(targetLen);
    const resPen = new Float32Array(targetLen);

    if (totalDist < 1e-6) {
        resX.fill(normX[0] || 0);
        resY.fill(normY[0] || 0);
        resPen.fill(1.0);
    } else {
        for (let j = 0; j < targetLen; j++) {
            const q = (j / (targetLen - 1)) * totalDist;
            let idx = cumDist.findIndex(d => d >= q);
            if (idx <= 0) idx = 1;
            const dSpan = Math.max(cumDist[idx] - cumDist[idx - 1], 1e-6);
            const t = (q - cumDist[idx - 1]) / dSpan;
            resX[j] = normX[idx - 1] + t * (normX[idx] - normX[idx - 1]);
            resY[j] = normY[idx - 1] + t * (normY[idx] - normY[idx - 1]);
            resPen[j] = (rawPen[idx - 1] + t * (rawPen[idx] - rawPen[idx - 1])) >= 0.5 ? 1.0 : 0.0;
        }
    }

    const tensorData = new Float32Array(targetLen * 8);
    const dx = new Float32Array(targetLen);
    const dy = new Float32Array(targetLen);
    const cosTheta = new Float32Array(targetLen);
    const sinTheta = new Float32Array(targetLen);

    for (let i = 1; i < targetLen; i++) {
        dx[i] = resX[i] - resX[i - 1];
        dy[i] = resY[i] - resY[i - 1];
        const ds = Math.hypot(dx[i], dy[i]) + 1e-7;
        cosTheta[i] = dx[i] / ds;
        sinTheta[i] = dy[i] / ds;
    }

    for (let i = 0; i < targetLen; i++) {
        const dTheta = i > 0 ? (sinTheta[i] * cosTheta[i - 1] - cosTheta[i] * sinTheta[i - 1]) : 0;
        const d2x = i > 0 ? (dx[i] - dx[i - 1]) : 0;
        const d2y = i > 0 ? (dy[i] - dy[i - 1]) : 0;

        const base = i * 8;
        tensorData[base + 0] = dx[i];
        tensorData[base + 1] = dy[i];
        tensorData[base + 2] = cosTheta[i];
        tensorData[base + 3] = sinTheta[i];
        tensorData[base + 4] = dTheta;
        tensorData[base + 5] = d2x;
        tensorData[base + 6] = d2y;
        tensorData[base + 7] = resPen[i];
    }
    return tensorData;
}

async function evaluateClusterWithONNX(clusterStrokes) {
    const session = await initReversalModel();
    if (!session) {
        return { isReversed: false, reversalProb: 0.0, topChar: '?' };
    }

    const flatFeats = resampleClusterTo64x8(clusterStrokes);
    const inputTensor = new ort.Tensor('float32', flatFeats, [1, 64, 8]);
    const feeds = { trajectory_input: inputTensor };

    try {
        const results = await session.run(feeds);
        let charData, revProb;
        if (results.char_output && results.reversal_output) {
            charData = results.char_output.data;
            revProb = results.reversal_output.data[0];
        } else {
            const keys = Object.keys(results);
            if (results[keys[0]].dims.includes(62)) {
                charData = results[keys[0]].data;
                revProb = results[keys[1]].data[0];
            } else {
                revProb = results[keys[0]].data[0];
                charData = results[keys[1]].data;
            }
        }

        let maxIdx = 0, maxVal = -1e9;
        for (let i = 0; i < charData.length; i++) {
            if (charData[i] > maxVal) {
                maxVal = charData[i];
                maxIdx = i;
            }
        }
        const topChar = VOCABULARY_62[maxIdx] || '?';

        return {
            isReversed: revProb >= 0.50,
            reversalProb: revProb,
            topChar: topChar
        };
    } catch (e) {
        console.warn("ONNX inference failed on cluster:", e);
        return { isReversed: false, reversalProb: 0.0, topChar: '?' };
    }
}

// --- DUAL-TRACK RECOGNITION: GLOBAL GOOGLE INK + LOCAL ONNX REVERSAL HEAD ---
async function transcribeWithReflectionAnalysis(rawStrokes) {
    const strokes = [];
    let currentStroke = [];

    rawStrokes.forEach(p => {
        if (p.touching === 1 || p.touching === true) {
            currentStroke.push(p);
        } else {
            if (currentStroke.length > 2) {
                strokes.push(currentStroke);
            }
            currentStroke = [];
        }
    });
    if (currentStroke.length > 2) {
        strokes.push(currentStroke);
    }

    if (strokes.length === 0) {
        return { winner: "?", rawWinner: "?", candidates: [], isReversal: false, notice: "" };
    }

    // Track 1: Query Google Digital Ink ONCE for global lexical word context
    const rawResult = await queryGoogleInk(strokes);
    const rawWinner = rawResult.winner;
    const rawCandidates = rawResult.candidates || [];

    let isReversal = false;
    let notice = "";
    let displayWinner = rawWinner;

    const isPrompted = modePrompted.checked;
    const promptTarget = promptSelect.value.trim();

    // Contextual Domain Masking: Prevents numeral reversals (e.g. 6/9) from polluting alphabetic text
    const isAlphabeticContext = isPrompted ? !/^\d+$/.test(promptTarget) : (rawWinner.length > 0 && /[a-zA-Z]/.test(rawWinner));
    const numericReversalKeys = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];

    // Track 2: Kinematic Clustering into Characters
    const clusters = segmentIntoCharacterClusters(strokes);

    // Evaluate each cluster locally using the In-House ONNX Reversal Model (1-2ms per cluster)
    const reversedPositions = [];
    const displayChars = rawWinner.split('');

    for (let k = 0; k < clusters.length; k++) {
        const clusterStrokes = clusters[k];
        const onnxRes = await evaluateClusterWithONNX(clusterStrokes);

        if (onnxRes.isReversed) {
            const rawChar = rawWinner[k] || (isPrompted && k < promptTarget.length ? promptTarget[k] : '');
            
            // Domain mask check: suppress numeric reversals in alphabetic context
            if (isAlphabeticContext && numericReversalKeys.includes(rawChar)) {
                continue;
            }

            isReversal = true;
            reversedPositions.push({
                index: k + 1,
                prob: onnxRes.reversalProb,
                rawChar: rawChar,
                onnxChar: onnxRes.topChar
            });

            // Map to clean display glyph
            let revSymbol = asymmetricReversible[rawChar] || asymmetricReversible[rawChar.toUpperCase()] || onnxRes.topChar;
            if (k < displayChars.length) {
                displayChars[k] = revSymbol;
            }
        }
    }

    if (isReversal) {
        displayWinner = displayChars.join('');
        const posDescs = reversedPositions.map(p => `position ${p.index} (confidence: ${(p.prob * 100).toFixed(1)}%)`).join(', ');
        notice = `Letter Observation: Mirror / rotational reversal detected at ${posDescs}.`;
    }

    return {
        winner: displayWinner,
        rawWinner: rawWinner,
        candidates: rawCandidates,
        isReversal: isReversal,
        notice: notice
    };
}

// --- STEP 1: TRANSCRIBE TEXT (ISOLATED - NO BACKEND INFERENCE) ---
transcribeBtn.addEventListener('click', async () => {
    const transcriptionCard = document.getElementById('transcriptionCard');
    const decodedTextDisplay = document.getElementById('decodedTextDisplay');
    const alternativeCandidates = document.getElementById('alternativeCandidates');
    const reversalNotice = document.getElementById('reversalNotice');

    if (strokeData.length === 0) {
        alert("Please write something first.");
        return;
    }

    transcribeBtn.innerText = "Transcribing...";
    transcribeBtn.disabled = true;

    try {
        const result = await transcribeWithReflectionAnalysis(strokeData);

        decodedTextDisplay.innerText = `"${result.winner}"`;
        if (result.isReversal && result.notice) {
            reversalNotice.innerText = result.notice;
            reversalNotice.style.display = 'block';
        } else {
            reversalNotice.style.display = 'none';
        }

        if (result.candidates.length > 0) {
            let text = `Alternative Guesses: ${result.candidates.join(" | ")}`;
            if (result.isReversal) {
                text += ` (Local ONNX: Clinical reversal flagged)`;
            }
            alternativeCandidates.innerText = text;
        } else {
            alternativeCandidates.innerText = `Alternative Guesses: [Uncertain Stroke]`;
        }

        transcriptionCard.style.display = 'block';
        updateMovementMetrics();
        transcriptionCard.scrollIntoView({ behavior: "smooth" });

    } catch (error) {
        alert("Could not transcribe text.");
    } finally {
        transcribeBtn.innerText = "Transcribe Text";
        transcribeBtn.disabled = false;
    }
});

// --- STEP 2: RUN ASSESSMENT (OPTIONAL SECONDARY ACTION) ---
analyzeBtn.addEventListener('click', async () => {
    const dashboard = document.getElementById('resultsDashboard');
    const diagBadge = document.getElementById('diagnosisBadge');
    const severityText = document.getElementById('severityText');
    const dysgraphiaRiskText = document.getElementById('dysgraphiaRiskText');
    const dyslexiaRiskText = document.getElementById('dyslexiaRiskText');
    const reversalAlertBox = document.getElementById('reversalAlertBox');
    const reversalAlertText = document.getElementById('reversalAlertText');
    const latencyText = document.getElementById('latencyText');

    if (strokeData.length === 0) {
        alert("Please write something first.");
        return;
    }

    analyzeBtn.innerText = "Evaluating...";
    analyzeBtn.disabled = true;

    try {
        // First check if transcribed
        let decoded = document.getElementById('decodedTextDisplay').innerText.replace(/"/g, '').trim();
        if (decoded === "" || decoded === "..." || decoded === "?") {
            const res = await transcribeWithReflectionAnalysis(strokeData);
            decoded = res.winner;
            document.getElementById('decodedTextDisplay').innerText = `"${decoded}"`;
            if (res.isReversal && res.notice) {
                document.getElementById('reversalNotice').innerText = res.notice;
                document.getElementById('reversalNotice').style.display = 'block';
            } else {
                document.getElementById('reversalNotice').style.display = 'none';
            }
            if (res.candidates.length > 0) {
                let text = `Alternative Guesses: ${res.candidates.join(" | ")}`;
                if (res.isReversal) {
                    text += ` (Local ONNX: Clinical reversal flagged)`;
                }
                document.getElementById('alternativeCandidates').innerText = text;
            }
            document.getElementById('transcriptionCard').style.display = 'block';
        }

        const strokesWithLatency = strokeData.map(point => {
            return { ...point, latency: latencyMs };
        });

        const isFreeFlow = modeFreeFlow.checked;
        const targetPrompt = isFreeFlow ? decoded : promptSelect.value;

        const payload = {
            strokes: strokesWithLatency,
            prompt: targetPrompt,
            decoded_text: decoded
        };

        const response = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (result.error) {
            alert(result.error);
            return;
        }

        // Draw highlight marks for high-variability segments
        if (result.heatmap && result.heatmap.length > 0) {
            result.heatmap.forEach((prob, index) => {
                if (index < strokeData.length && prob > 0.80) {
                    const point = strokeData[index];
                    ctx.beginPath();
                    ctx.arc(point.x, point.y, 8, 0, 2 * Math.PI);
                    ctx.fillStyle = "rgba(231, 76, 60, 0.15)";
                    ctx.fill();
                }
            });
        }

        dashboard.style.display = 'block';

        diagBadge.innerText = result.dsm5_diagnosis || "Typical";
        severityText.innerText = result.clinical_severity || "Standard";

        if (result.is_dysgraphic || result.is_dyslexic) {
            diagBadge.className = "status-badge badge-red";
        } else {
            diagBadge.className = "status-badge badge-green";
        }

        const dysgraphiaPct = (result.dysgraphia_risk_percentage || 0).toFixed(1);
        const dyslexiaPct = (result.dyslexia_risk_percentage || 0).toFixed(1);

        dysgraphiaRiskText.innerText = `${dysgraphiaPct}%`;
        dysgraphiaRiskText.style.color = result.is_dysgraphic ? "#e74c3c" : "#27ae60";

        dyslexiaRiskText.innerText = `${dyslexiaPct}%`;
        dyslexiaRiskText.style.color = result.is_dyslexic ? "#e74c3c" : "#27ae60";

        if (result.reversal_detected) {
            reversalAlertBox.style.display = 'block';
            reversalAlertText.innerText = result.reversal_description;
        } else {
            reversalAlertBox.style.display = 'none';
        }

        latencyText.innerText = `${Math.round(result.cognitive_latency_ms || 0)} ms`;
        dashboard.scrollIntoView({ behavior: "smooth" });

    } catch (error) {
        alert("Could not connect to analysis service.");
    } finally {
        analyzeBtn.innerText = "Run Assessment";
        analyzeBtn.disabled = false;
    }
});
