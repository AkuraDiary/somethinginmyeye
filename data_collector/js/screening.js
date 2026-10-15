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
    try { scrollTrack.releasePointerCapture(e.pointerId); } catch(err){}
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

// --- ALGORITHMIC HORIZONTAL REFLECTION TEST (UNIVERSAL MIRROR DETECTOR) ---
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
        return { winner: "?", candidates: [], isReversal: false, notice: "" };
    }

    // Bounding box for horizontal reflection
    const allPts = strokes.flat();
    const xs = allPts.map(p => p.x);
    const xMin = Math.min(...xs);
    const xMax = Math.max(...xs);

    // Compute horizontally mirrored strokes: x_mirrored = xMax - (x - xMin)
    const mirroredStrokes = strokes.map(s => s.map(pt => ({
        ...pt,
        x: Math.round(xMax - (pt.x - xMin))
    })));

    // Run raw trajectory and horizontal reflection concurrently
    const [rawResult, mirrorResult] = await Promise.all([
        queryGoogleInk(strokes),
        queryGoogleInk(mirroredStrokes)
    ]);

    const rawWinner = rawResult.winner;
    const mirrorWinner = mirrorResult.winner;
    const rawCandidates = rawResult.candidates || [];
    const mirrorCandidates = mirrorResult.candidates || [];

    // Asymmetric reversal dictionary
    const asymmetricReversible = {
        'N': 'И', 'n': 'и',
        'S': 'Ƨ', 's': 'ƨ',
        'E': 'Ǝ', 'e': 'ɘ',
        'B': '𐤡', 'D': 'ᗡ',
        'b': 'd', 'd': 'b',
        'p': 'q', 'q': 'p',
        'C': 'Ɔ', 'c': 'ɔ',
        'J': 'ᒐ', 'j': 'ϳ',
        'Z': 'S',
        '3': 'Ɛ',
        '7': 'г'
    };

    let isReversal = false;
    let displayWinner = rawWinner;
    let notice = "";

    const isPrompted = modePrompted.checked;
    const promptTarget = promptSelect.value.toLowerCase().trim();
    const rawUpper = rawWinner.toUpperCase();

    // Letters with bilateral vertical symmetry cannot be mirror-reversed
    const symmetricLetters = ['A', 'H', 'I', 'M', 'O', 'T', 'U', 'V', 'W', 'X', 'Y'];
    const isSymmetric = symmetricLetters.includes(rawUpper);

    if (!isSymmetric) {
        // Case 1: Reciprocal letter pairs (b vs d, p vs q) - evaluate against prompt
        if (isPrompted && ['b', 'd', 'p', 'q'].includes(promptTarget)) {
            if (promptTarget === 'b' && (rawWinner.toLowerCase() === 'd' || mirrorWinner.toLowerCase() === 'b')) {
                isReversal = true;
                displayWinner = "d (Reversed b)";
                notice = "Letter Observation: Mirror reversal detected ('b' written as 'd').";
            } else if (promptTarget === 'd' && (rawWinner.toLowerCase() === 'b' || mirrorWinner.toLowerCase() === 'd')) {
                isReversal = true;
                displayWinner = "b (Reversed d)";
                notice = "Letter Observation: Mirror reversal detected ('d' written as 'b').";
            } else if (promptTarget === 'p' && (rawWinner.toLowerCase() === 'q' || mirrorWinner.toLowerCase() === 'p')) {
                isReversal = true;
                displayWinner = "q (Reversed p)";
                notice = "Letter Observation: Mirror reversal detected ('p' written as 'q').";
            } else if (promptTarget === 'q' && (rawWinner.toLowerCase() === 'p' || mirrorWinner.toLowerCase() === 'q')) {
                isReversal = true;
                displayWinner = "p (Reversed q)";
                notice = "Letter Observation: Mirror reversal detected ('q' written as 'p').";
            }
        }
        // Case 2: Non-character chiral reversals (N -> И, S -> Ƨ, E -> Ǝ, B -> ᙠ, 3 -> Ɛ)
        else if (mirrorWinner in asymmetricReversible && mirrorWinner.toUpperCase() !== rawUpper && !['b', 'd', 'p', 'q'].includes(mirrorWinner)) {
            isReversal = true;
            const symbol = asymmetricReversible[mirrorWinner] || `Reversed ${mirrorWinner}`;
            displayWinner = `${symbol}`;//(Reversed ${mirrorWinner})`;
            notice = `Letter Observation: Mirror reversal detected (drawn as mirror image of '${mirrorWinner}').`;
        }
        // Case 3: Geometric verification fallback for inverted N
        else {
            const geom = inspectOrthographicReversals(rawStrokes, rawCandidates);
            if (geom && geom.detected) {
                isReversal = true;
                displayWinner = geom.winner;
                notice = geom.notice;
            }
        }
    }

    return {
        winner: displayWinner,
        rawWinner: rawWinner,
        mirrorWinner: mirrorWinner,
        candidates: rawCandidates,
        mirrorCandidates: mirrorCandidates,
        isReversal: isReversal,
        notice: notice
    };
}

// --- GEOMETRIC TRAJECTORY INSPECTION: INVERTED 'N' ---
function inspectOrthographicReversals(rawStrokes, candidates) {
    const pts = rawStrokes.filter(p => p.touching === 1 || p.touching === true);
    if (pts.length < 8) return null;

    const xs = pts.map(p => p.x);
    const ys = pts.map(p => p.y);
    const xMin = Math.min(...xs);
    const xMax = Math.max(...xs);
    const yMin = Math.min(...ys);
    const yMax = Math.max(...ys);
    const width = Math.max(xMax - xMin, 1);
    const height = Math.max(yMax - yMin, 1);

    const hasN = candidates.some(c => c === 'N' || c === 'n' || c === 'H' || c === 'M');
    if (hasN && height > 25 && width > 15) {
        const midPoints = pts.filter(p => p.x > xMin + 0.20 * width && p.x < xMax - 0.20 * width);
        if (midPoints.length >= 2) {
            const leftMid = midPoints.filter(p => p.x < xMin + 0.45 * width);
            const rightMid = midPoints.filter(p => p.x > xMin + 0.55 * width);

            if (leftMid.length > 0 && rightMid.length > 0) {
                const avgYLeft = leftMid.reduce((s, p) => s + p.y, 0) / leftMid.length;
                const avgYRight = rightMid.reduce((s, p) => s + p.y, 0) / rightMid.length;

                if (avgYLeft > avgYRight + 0.12 * height) {
                    return {
                        detected: true,
                        winner: "И",
                        notice: "Letter Observation: Inverted 'N' detected (ascending diagonal from bottom-left to top-right)."
                    };
                }
            }
        }
    }
    return null;
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
            if (result.mirrorWinner && result.mirrorWinner !== result.rawWinner) {
                text += ` (Mirror reflection: '${result.mirrorWinner}')`;
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
                if (res.mirrorWinner && res.mirrorWinner !== res.rawWinner) {
                    text += ` (Mirror reflection: '${res.mirrorWinner}')`;
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
