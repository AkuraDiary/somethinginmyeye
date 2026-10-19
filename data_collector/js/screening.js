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

let lastSegmentationDiagnostics = null;
const toggleBoundingBoxes = document.getElementById('toggleBoundingBoxes');

function redrawCanvasBase() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // Baseline guide
    ctx.beginPath();
    ctx.moveTo(canvas.width * 0.05, canvas.height * 0.75);
    ctx.lineTo(canvas.width * 0.95, canvas.height * 0.75);
    ctx.strokeStyle = "#ecf0f1";
    ctx.lineWidth = 3;
    ctx.stroke();
}

function redrawAllUserStrokes() {
    redrawCanvasBase();
    if (strokeData.length === 0) return;

    let inStroke = false;
    for (let i = 0; i < strokeData.length; i++) {
        const pt = strokeData[i];
        if (pt.touching === 1 || pt.touching === true) {
            if (!inStroke) {
                ctx.beginPath();
                ctx.moveTo(pt.x, pt.y);
                inStroke = true;
            } else {
                ctx.lineWidth = Math.max((pt.pressure || 0.5) * 5, 2.5);
                ctx.strokeStyle = "#2c3e50";
                ctx.lineTo(pt.x, pt.y);
                ctx.stroke();
            }
        } else {
            inStroke = false;
        }
    }
}

const togglePhraseBox = document.getElementById('togglePhraseBox');

function renderBoundingBoxesOverlay() {
    if (!lastSegmentationDiagnostics || lastSegmentationDiagnostics.length === 0) return;

    redrawAllUserStrokes();

    const showIndividualBoxes = toggleBoundingBoxes ? toggleBoundingBoxes.checked : true;
    const showPhraseBox = togglePhraseBox ? togglePhraseBox.checked : false;

    // Optional: Draw whole phrase bounding box only if explicitly checked
    if (showPhraseBox && lastSegmentationDiagnostics.length > 1) {
        const allXs = lastSegmentationDiagnostics.map(d => [d.bbox.x, d.bbox.x + d.bbox.w]).flat();
        const allYs = lastSegmentationDiagnostics.map(d => [d.bbox.y, d.bbox.y + d.bbox.h]).flat();
        const pXMin = Math.min(...allXs) - 14;
        const pYMin = Math.min(...allYs) - 14;
        const pW = (Math.max(...allXs) - Math.min(...allXs)) + 28;
        const pH = (Math.max(...allYs) - Math.min(...allYs)) + 28;

        ctx.save();
        ctx.lineWidth = 1;
        ctx.strokeStyle = "#94a3b8";
        ctx.setLineDash([4, 4]);
        ctx.strokeRect(pXMin, pYMin, pW, pH);
        ctx.fillStyle = "#64748b";
        ctx.font = "italic 11px -apple-system, sans-serif";
        ctx.fillText(`Whole Phrase (${lastSegmentationDiagnostics.length} clusters)`, pXMin + 6, pYMin - 4);
        ctx.restore();
    }

    if (!showIndividualBoxes) return;

    const CLUSTER_PALETTE = [
        { border: "#2563eb", fill: "rgba(37, 99, 235, 0.12)", stroke: "#1d4ed8" }, // Blue
        { border: "#059669", fill: "rgba(5, 150, 105, 0.12)", stroke: "#047857" }, // Emerald
        { border: "#d97706", fill: "rgba(217, 119, 6, 0.12)", stroke: "#b45309" }, // Amber
        { border: "#7c3aed", fill: "rgba(124, 58, 237, 0.12)", stroke: "#6d28d9" }, // Violet
        { border: "#0891b2", fill: "rgba(8, 145, 178, 0.12)", stroke: "#0e7490" }, // Cyan
        { border: "#db2777", fill: "rgba(219, 39, 119, 0.12)", stroke: "#be185d" }, // Pink
    ];

    const padding = 8;
    lastSegmentationDiagnostics.forEach((d, idx) => {
        if (!d.bbox) return;

        const bx = Math.max(0, d.bbox.x - padding);
        const by = Math.max(0, d.bbox.y - padding);
        const bw = d.bbox.w + (padding * 2);
        const bh = d.bbox.h + (padding * 2);

        const isRev = d.isReversed;
        const palette = CLUSTER_PALETTE[idx % CLUSTER_PALETTE.length];
        const boxColor = isRev ? "rgba(220, 38, 38, 0.95)" : palette.border;
        const boxFill = isRev ? "rgba(254, 226, 226, 0.22)" : palette.fill;

        // Draw bounding box rectangle
        ctx.save();
        ctx.lineWidth = 2;
        ctx.strokeStyle = boxColor;
        ctx.setLineDash([6, 3]);
        ctx.strokeRect(bx, by, bw, bh);

        ctx.fillStyle = boxFill;
        ctx.fillRect(bx, by, bw, bh);

        // Header label badge on top of the bounding box
        const labelText = `C#${d.clusterIndex}: '${d.onnxCanonicalChar}' → ${d.resolvedGlyph} (${d.onnxCharConfidence}%)`;
        ctx.font = "bold 12px -apple-system, BlinkMacSystemFont, sans-serif";
        const textWidth = ctx.measureText(labelText).width;
        const badgeW = textWidth + 14;
        const badgeH = 20;
        const badgeY = Math.max(2, by - badgeH - 2);

        ctx.setLineDash([]);
        ctx.fillStyle = boxColor;
        ctx.fillRect(bx, badgeY, badgeW, badgeH);

        ctx.fillStyle = "#ffffff";
        ctx.fillText(labelText, bx + 7, badgeY + 14);

        // Sub-badge at bottom showing reversal score
        const revText = isRev ? `REVERSED ${d.reversalProbability}%` : `NORMAL ${d.reversalProbability}%`;
        ctx.font = "600 11px -apple-system, BlinkMacSystemFont, sans-serif";
        const revWidth = ctx.measureText(revText).width;
        const subBadgeW = revWidth + 10;
        const subBadgeH = 17;
        const subBadgeY = by + bh + 3;

        ctx.fillStyle = isRev ? "#991b1b" : "#334155";
        ctx.fillRect(bx, subBadgeY, subBadgeW, subBadgeH);

        ctx.fillStyle = "#ffffff";
        ctx.fillText(revText, bx + 5, subBadgeY + 12);

        ctx.restore();
    });
}

if (toggleBoundingBoxes) {
    toggleBoundingBoxes.addEventListener('change', () => {
        if (lastSegmentationDiagnostics && lastSegmentationDiagnostics.length > 0) {
            renderBoundingBoxesOverlay();
        }
    });
}
if (togglePhraseBox) {
    togglePhraseBox.addEventListener('change', () => {
        if (lastSegmentationDiagnostics && lastSegmentationDiagnostics.length > 0) {
            renderBoundingBoxesOverlay();
        }
    });
}

function clearCanvas() {
    lastSegmentationDiagnostics = null;
    redrawCanvasBase();
    strokeData = [];
    hasStartedWriting = false;
    promptStartTime = Date.now();
    currentStrokeCount = 0;
    latencyMs = 0;

    document.getElementById('transcriptionCard').style.display = 'none';
    document.getElementById('resultsDashboard').style.display = 'none';

    // Clear and hide Model Diagnostics & Inference Cards
    const diagCard = document.getElementById('modelDiagnosticsCard');
    const diagDetails = document.getElementById('diagnosticsDetails');
    const diagSummaryTag = document.getElementById('diagnosticsSummaryTag');
    if (diagCard) {
        diagCard.style.display = 'none';
    }
    if (diagDetails) {
        diagDetails.innerHTML = '';
    }
    if (diagSummaryTag) {
        diagSummaryTag.className = 'diag-tag diag-tag-normal';
        diagSummaryTag.innerText = 'OK';
    }

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

    // Filter out accidental micro-taps (< 5px in both dimensions)
    const cleanStrokes = strokes.filter(s => {
        if (!s || s.length === 0) return false;
        const xs = s.map(p => p.x), ys = s.map(p => p.y);
        return (Math.max(...xs) - Math.min(...xs) > 4) || (Math.max(...ys) - Math.min(...ys) > 4);
    });

    if (cleanStrokes.length === 0) return strokes;

    // Helper 1: Resample a single stroke by equidistant spatial arc length (step = 3.5px)
    // Decouples stroke geometry from writing velocity and hardware polling rate fluctuations.
    function resampleStrokeEquidistant(strokePts, stepSize = 3.5) {
        if (!strokePts || strokePts.length < 2) return strokePts;
        const cumDist = [0];
        for (let i = 1; i < strokePts.length; i++) {
            const d = Math.hypot(strokePts[i].x - strokePts[i - 1].x, strokePts[i].y - strokePts[i - 1].y);
            cumDist.push(cumDist[i - 1] + d);
        }
        const totalL = cumDist[cumDist.length - 1];
        if (totalL < stepSize) return strokePts;

        const numSteps = Math.max(Math.floor(totalL / stepSize), 2);
        const resampled = [];
        for (let j = 0; j <= numSteps; j++) {
            const targetDist = (j / numSteps) * totalL;
            let idx = cumDist.findIndex(d => d >= targetDist);
            if (idx <= 0) {
                resampled.push({ ...strokePts[0] });
            } else {
                const p0 = strokePts[idx - 1];
                const p1 = strokePts[idx];
                const segmentSpan = cumDist[idx] - cumDist[idx - 1];
                const t = segmentSpan > 1e-5 ? (targetDist - cumDist[idx - 1]) / segmentSpan : 0;
                resampled.push({
                    x: p0.x + t * (p1.x - p0.x),
                    y: p0.y + t * (p1.y - p0.y),
                    pressure: (p0.pressure || 0.5) + t * ((p1.pressure || 0.5) - (p0.pressure || 0.5)),
                    tiltX: (p0.tiltX || 0) + t * ((p1.tiltX || 0) - (p0.tiltX || 0)),
                    tiltY: (p0.tiltY || 0) + t * ((p1.tiltY || 0) - (p0.tiltY || 0)),
                    time: p0.time + t * (p1.time - p0.time),
                    touching: p0.touching
                });
            }
        }
        return resampled;
    }

    // Helper 2: Spatial moving-average smoothing on arc-length points to suppress slow-writing motor tremor
    function smoothStrokeSpatial(pts, radius = 2) {
        if (!pts || pts.length < 2 * radius + 1) return pts;
        return pts.map((p, idx) => {
            if (idx === 0 || idx === pts.length - 1) return { ...p };
            let sx = 0, sy = 0, cnt = 0;
            const r = Math.min(radius, idx, pts.length - 1 - idx);
            for (let k = -r; k <= r; k++) {
                sx += pts[idx + k].x;
                sy += pts[idx + k].y;
                cnt++;
            }
            return { ...p, x: sx / cnt, y: sy / cnt };
        });
    }

    // Helper 3: Detect if a stroke segment contains a retrograde loop (dx < 0) characteristic of character bodies
    function hasLoopOrTurn(seg) {
        if (!seg || seg.length < 10) return false;
        let negDxSteps = 0;
        for (let i = 2; i < seg.length - 2; i++) {
            if (seg[i + 1].x - seg[i - 1].x < -1.5) negDxSteps++;
        }
        return negDxSteps >= 3;
    }

    // Helper 4: Compute total spatial arc-length of a stroke
    function strokeArcLength(s) {
        let L = 0;
        for (let i = 1; i < s.length; i++) {
            L += Math.hypot(s[i].x - s[i - 1].x, s[i].y - s[i - 1].y);
        }
        return L;
    }

    // Helper 5: Minimum Euclidean distance between endpoints of two strokes (shared vertex detection)
    function minEndpointDist(s1, s2) {
        const ends1 = [s1[0], s1[s1.length - 1]];
        const ends2 = [s2[0], s2[s2.length - 1]];
        let minD = Infinity;
        for (const p1 of ends1) {
            for (const p2 of ends2) {
                const d = Math.hypot(p1.x - p2.x, p1.y - p2.y);
                if (d < minD) minD = d;
            }
        }
        return minD;
    }

    // Step 1: Equidistant spatial resampling + spatial smoothing + single-pass neck cursive ligature splitting
    const refinedStrokes = [];
    cleanStrokes.forEach((rawS, origStrokeIdx) => {
        const resampled = resampleStrokeEquidistant(rawS, 3.5);
        const s = smoothStrokeSpatial(resampled, 2);
        if (s.length < 30) {
            refinedStrokes.push({ pts: resampled, origId: origStrokeIdx, splitPart: 0 });
            return;
        }

        const xs = s.map(p => p.x), ys = s.map(p => p.y);
        const sW = Math.max(...xs) - Math.min(...xs);
        const sH = Math.max(Math.max(...ys) - Math.min(...ys), 1);
        const yMin = Math.min(...ys);

        if (sW >= 110 && sW >= 1.05 * sH) {
            const splitIndices = [];
            const baselineThreshold = yMin + 0.35 * sH;

            for (let i = 8; i < s.length - 8; i++) {
                const curr = s[i];
                // 1. Must be moving rightward along an inter-character bridge
                if (s[i + 3].x - s[i - 3].x <= 3.5) continue;
                // 2. Must lie in the lower 65% of the stroke vertical span
                if (curr.y < baselineThreshold) continue;
                // 3. Must be a local valley (y-maximum) over a +-4 step (14px) window
                let isValley = true;
                for (let k = -4; k <= 4; k++) {
                    if (k !== 0 && s[i + k].y > curr.y + 0.5) {
                        isValley = false;
                        break;
                    }
                }
                if (!isValley) continue;

                // 4. Single-pass neck invariant: ensure point is NOT inside the bottom of a closed loop
                let multiPass = false;
                for (let j = 0; j < s.length; j++) {
                    if (Math.abs(j - i) > 7 && Math.abs(s[j].x - curr.x) < 5.0) {
                        multiPass = true;
                        break;
                    }
                }
                if (multiPass) continue;

                // 5. Both left and right segments must form complete character bodies
                const lastSplit = splitIndices.length > 0 ? splitIndices[splitIndices.length - 1] : 0;
                const leftSeg = s.slice(lastSplit, i);
                const rightSeg = s.slice(i + 1);
                const leftW = Math.max(...leftSeg.map(p => p.x)) - Math.min(...leftSeg.map(p => p.x));
                const rightW = Math.max(...rightSeg.map(p => p.x)) - Math.min(...rightSeg.map(p => p.x));
                const leftH = Math.max(...leftSeg.map(p => p.y)) - Math.min(...leftSeg.map(p => p.y));
                const rightH = Math.max(...rightSeg.map(p => p.y)) - Math.min(...rightSeg.map(p => p.y));

                if (leftW >= 32 && rightW >= 32 && leftH >= 0.32 * sH && rightH >= 0.32 * sH &&
                    hasLoopOrTurn(leftSeg) && hasLoopOrTurn(rightSeg)) {
                    splitIndices.push(i);
                }
            }

            if (splitIndices.length > 0) {
                let startIdx = 0;
                splitIndices.forEach((splitIdx, partIdx) => {
                    refinedStrokes.push({
                        pts: resampled.slice(startIdx, splitIdx),
                        origId: origStrokeIdx,
                        splitPart: partIdx
                    });
                    startIdx = splitIdx + 1;
                });
                if (startIdx < resampled.length - 1) {
                    refinedStrokes.push({
                        pts: resampled.slice(startIdx),
                        origId: origStrokeIdx,
                        splitPart: splitIndices.length
                    });
                }
            } else {
                refinedStrokes.push({ pts: resampled, origId: origStrokeIdx, splitPart: 0 });
            }
        } else {
            refinedStrokes.push({ pts: resampled, origId: origStrokeIdx, splitPart: 0 });
        }
    });

    if (refinedStrokes.length === 1) {
        return [[refinedStrokes[0].pts]];
    }

    // Step 2: Compute geometric and tortuosity metadata per stroke and sort horizontally by xMin
    const strokeMeta = refinedStrokes.map(item => {
        const s = item.pts;
        const xs = s.map(p => p.x), ys = s.map(p => p.y), ts = s.map(p => p.time);
        const xMin = Math.min(...xs), xMax = Math.max(...xs);
        const yMin = Math.min(...ys), yMax = Math.max(...ys);
        const width = Math.max(xMax - xMin, 1);
        const height = Math.max(yMax - yMin, 1);
        const arcLen = strokeArcLength(s);
        return {
            stroke: s,
            origId: item.origId,
            splitPart: item.splitPart,
            xMin, xMax, yMin, yMax,
            width, height, arcLen,
            tortuosity: arcLen / height,
            cx: (xMin + xMax) / 2,
            tStart: Math.min(...ts),
            tEnd: Math.max(...ts)
        };
    });

    strokeMeta.sort((a, b) => a.xMin - b.xMin);

    // Step 3: Cluster strokes into individual characters using tortuosity, overlap, and vertex geometry
    const clusters = [];
    let currentCluster = [strokeMeta[0]];

    for (let i = 1; i < strokeMeta.length; i++) {
        const currItem = strokeMeta[i];
        const nextItem = i + 1 < strokeMeta.length ? strokeMeta[i + 1] : null;

        // Never re-merge sub-strokes that were explicitly split from the same continuous cursive stroke
        const wasExplicitlySplit = currentCluster.some(m => m.origId === currItem.origId && m.splitPart !== currItem.splitPart);
        if (wasExplicitlySplit) {
            currentCluster.sort((a, b) => a.tStart - b.tStart);
            clusters.push(currentCluster.map(m => m.stroke));
            currentCluster = [currItem];
            continue;
        }

        const cXMin = Math.min(...currentCluster.map(m => m.xMin));
        const cXMax = Math.max(...currentCluster.map(m => m.xMax));
        const cYMin = Math.min(...currentCluster.map(m => m.yMin));
        const cYMax = Math.max(...currentCluster.map(m => m.yMax));
        const cW = Math.max(cXMax - cXMin, 1);
        const cH = Math.max(cYMax - cYMin, 1);
        const cCx = (cXMin + cXMax) / 2;
        const cArcLen = currentCluster.reduce((acc, m) => acc + m.arcLen, 0);
        const cTortuosity = cArcLen / cH;
        const refH = Math.max(cH, currItem.height);

        const gapX = currItem.xMin - cXMax;
        const overlapX = Math.max(0, Math.min(cXMax, currItem.xMax) - Math.max(cXMin, currItem.xMin));
        const overlapRatioX = overlapX / Math.min(cW, currItem.width);

        const overlapY = Math.max(0, Math.min(cYMax, currItem.yMax) - Math.max(cYMin, currItem.yMin));
        const overlapRatioY = overlapY / Math.min(cH, currItem.height);

        // Diacritic / Dot ownership check: if currItem is a dot, check if it sits over nextItem (e.g. stem of 'i'/'j')
        const isSmallDot = (currItem.height < 22 && currItem.width < 22);
        const overlapWithNext = nextItem ? Math.max(0, Math.min(currItem.xMax, nextItem.xMax) - Math.max(currItem.xMin, nextItem.xMin)) : 0;
        const dotBelongsToNext = isSmallDot && (overlapWithNext > overlapX);

        let minVertexD = Infinity;
        for (const m of currentCluster) {
            const d = minEndpointDist(m.stroke, currItem.stroke);
            if (d < minVertexD) minVertexD = d;
        }

        // Case A: Shared vertex for straight/diagonal-stroke letters (A, M, N, V, W, K, X, Y)
        const isSharedVertex = (minVertexD <= Math.max(14, 0.10 * refH)) &&
                               (overlapRatioY >= 0.50) &&
                               (cW + currItem.width <= 1.25 * refH) &&
                               (cTortuosity < 1.35 && currItem.tortuosity < 1.45);

        // Case B: Diacritic dot belonging to current cluster
        const isDotForCurrent = isSmallDot && !dotBelongsToNext && (overlapX > 0 || Math.abs(currItem.cx - cCx) <= 15);

        // Case C: Strong horizontal overlap (crossbars, multi-stroke E, F, H, t, f, k leg)
        const hasStrongXOverlap = !dotBelongsToNext && (overlapRatioX >= 0.25 || (currItem.cx >= cXMin && currItem.cx <= cXMax) || (cCx >= currItem.xMin && cCx <= currItem.xMax));

        // Case D1: Isolated straight vertical stem on left attaching to right bowl/arch/arm (b, p, k, n, h, B, D, P, R)
        const clusterIsStraightStem = !isSmallDot && (cW < 0.25 * cH || cW < 20) && (cTortuosity < 1.55);
        const isLeftStemAttach = clusterIsStraightStem && (gapX <= Math.max(22, 0.22 * refH)) && (overlapRatioY >= 0.20);

        // Case D2: Straight vertical spine on right attaching to left-bulging belly/bowl (reversed D 'ᗡ', reversed B 'ꓭ', d, q)
        const currIsStraightStem = !isSmallDot && (currItem.width < 0.25 * currItem.height || currItem.width < 20) && (currItem.tortuosity < 1.55);
        const hasDotOrArmNext = nextItem && (
            (nextItem.height < 22 && nextItem.width < 22 && nextItem.xMin <= currItem.xMax + 12) ||
            (nextItem.xMin - currItem.xMax <= 4)
        );
        // Check if left cluster is a right-open belly (both endpoints on right side facing the vertical spine, as in reversed D/B)
        const firstStroke = currentCluster[0].stroke;
        const fStart = firstStroke[0], fEnd = firstStroke[firstStroke.length - 1];
        const isRightOpenBelly = currentCluster.length === 1 &&
                                 fStart.x >= cXMax - 0.35 * cW &&
                                 fEnd.x >= cXMax - 0.35 * cW &&
                                 cTortuosity >= 1.30;
        const maxRightStemGap = isRightOpenBelly ? Math.max(18, 0.16 * refH) : 2;
        const isRightStemAttach = currIsStraightStem && !hasDotOrArmNext && (gapX <= maxRightStemGap) && (cW < 0.85 * refH) && (overlapRatioY >= 0.20);

        if (isDotForCurrent || hasStrongXOverlap || isLeftStemAttach || isRightStemAttach || isSharedVertex) {
            currentCluster.push(currItem);
        } else {
            // Re-sort strokes within cluster chronologically (tStart) so ONNX receives authentic drawing order
            currentCluster.sort((a, b) => a.tStart - b.tStart);
            clusters.push(currentCluster.map(m => m.stroke));
            currentCluster = [currItem];
        }
    }

    if (currentCluster.length > 0) {
        currentCluster.sort((a, b) => a.tStart - b.tStart);
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
        return { isReversed: false, reversalProb: 0.0, topChar: '?', topProb: 0, top3: [] };
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

        const candidates = [];
        for (let i = 0; i < charData.length; i++) {
            candidates.push({ char: VOCABULARY_62[i] || '?', prob: charData[i] });
        }
        candidates.sort((a, b) => b.prob - a.prob);

        const topChar = candidates[0].char;
        const topProb = candidates[0].prob;
        const top3 = candidates.slice(0, 3);

        return {
            isReversed: revProb >= 0.50,
            reversalProb: revProb,
            topChar: topChar,
            topProb: topProb,
            top3: top3
        };
    } catch (e) {
        console.warn("ONNX inference failed on cluster:", e);
        return { isReversed: false, reversalProb: 0.0, topChar: '?', topProb: 0, top3: [] };
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
        return { winner: "?", rawWinner: "?", candidates: [], isReversal: false, notice: "", diagnostics: [], clustersCount: 0 };
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
    const diagnostics = [];

    for (let k = 0; k < clusters.length; k++) {
        const clusterStrokes = clusters[k];
        const onnxRes = await evaluateClusterWithONNX(clusterStrokes);

        // Identify intended canonical letter:
        // Priority 1: In Prompted Mode, the expected letter from promptTarget (e.g. "D" or "b")
        // Priority 2: In Free Writing, the In-House ONNX Head 1 predicted letter (e.g. "D", "B", "b")
        // Priority 3: Google Digital Ink's raw letter
        const canonicalChar = (isPrompted && k < promptTarget.length) 
            ? promptTarget[k] 
            : (onnxRes.topChar || rawWinner[k] || '');

        let revSymbol = canonicalChar;
        let clusterIsReversed = false;

        if (onnxRes.isReversed) {
            // Domain mask check: suppress numeric reversals in alphabetic context
            if (!(isAlphabeticContext && numericReversalKeys.includes(canonicalChar))) {
                clusterIsReversed = true;
                isReversal = true;
                reversedPositions.push({
                    index: k + 1,
                    prob: onnxRes.reversalProb,
                    rawChar: rawWinner[k] || '?',
                    onnxChar: onnxRes.topChar
                });

                // Map to the canonical reversed glyph: e.g. D -> ᗡ, B -> ꓭ, b -> d, E -> Ǝ, N -> И, S -> Ƨ
                revSymbol = asymmetricReversible[canonicalChar] || 
                            asymmetricReversible[canonicalChar.toUpperCase()] || 
                            asymmetricReversible[canonicalChar.toLowerCase()] || 
                            canonicalChar;

                if (k < displayChars.length) {
                    displayChars[k] = revSymbol;
                } else {
                    displayChars.push(revSymbol);
                }
            }
        }

        const resolvedGlyph = clusterIsReversed ? revSymbol : (displayChars[k] || canonicalChar);

        const allClusterPts = clusterStrokes.flat();
        const cXs = allClusterPts.map(p => p.x);
        const cYs = allClusterPts.map(p => p.y);
        const boxXMin = Math.min(...cXs);
        const boxXMax = Math.max(...cXs);
        const boxYMin = Math.min(...cYs);
        const boxYMax = Math.max(...cYs);

        diagnostics.push({
            clusterIndex: k + 1,
            strokeCount: clusterStrokes.length,
            pointCount: clusterStrokes.reduce((s, st) => s + st.length, 0),
            bbox: {
                x: boxXMin,
                y: boxYMin,
                w: Math.max(boxXMax - boxXMin, 1),
                h: Math.max(boxYMax - boxYMin, 1)
            },
            clusterStrokes: clusterStrokes,
            googleInkChar: rawWinner[k] || '?',
            onnxCanonicalChar: onnxRes.topChar,
            onnxCharConfidence: (onnxRes.topProb * 100).toFixed(1),
            onnxTop3: onnxRes.top3,
            reversalProbability: (onnxRes.reversalProb * 100).toFixed(1),
            isReversed: clusterIsReversed,
            resolvedGlyph: resolvedGlyph
        });
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
        notice: notice,
        diagnostics: diagnostics,
        clustersCount: clusters.length
    };
}

// --- STEP 1: TRANSCRIBE TEXT (ISOLATED - NO BACKEND INFERENCE) ---
transcribeBtn.addEventListener('click', async () => {
    const transcriptionCard = document.getElementById('transcriptionCard');
    const decodedTextDisplay = document.getElementById('decodedTextDisplay');
    const alternativeCandidates = document.getElementById('alternativeCandidates');
    const reversalNotice = document.getElementById('reversalNotice');
    const diagCard = document.getElementById('modelDiagnosticsCard');
    const diagDetails = document.getElementById('diagnosticsDetails');
    const diagSummaryTag = document.getElementById('diagnosticsSummaryTag');

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

        // Render Model Transparency & Pipeline Diagnostics Drawer
        if (diagCard && diagDetails && result.diagnostics) {
            diagCard.style.display = 'block';
            if (diagSummaryTag) {
                diagSummaryTag.className = result.isReversal ? 'diag-tag diag-tag-reversed' : 'diag-tag diag-tag-normal';
                diagSummaryTag.innerText = result.isReversal ? 'REVERSAL FLAGGED' : 'CANONICAL NORMAL';
            }

            let html = `<div style="margin-bottom:8px; font-size:12px;"><strong>Clusters Found:</strong> ${result.clustersCount} | <strong>Google Ink Output:</strong> "${result.rawWinner}" | <strong>Final Rendered Text:</strong> "${result.winner}"</div>`;

            result.diagnostics.forEach(d => {
                const tagClass = d.isReversed ? 'diag-tag diag-tag-reversed' : 'diag-tag diag-tag-normal';
                const tagText = d.isReversed ? `REVERSED (${d.reversalProbability}%)` : `NORMAL (${(100 - parseFloat(d.reversalProbability)).toFixed(1)}%)`;
                const top3Str = d.onnxTop3 ? d.onnxTop3.map(c => `'${c.char}': ${(c.prob*100).toFixed(1)}%`).join(' | ') : '';

                const routingBadge = `<span style="background:#e0f2fe; color:#0369a1; padding:2px 8px; border-radius:3px; font-weight:600; font-size:11px;">Tensor Input: (1, 64, 8)</span>`;

                html += `
                <div class="diagnostics-cluster-row" style="margin-bottom:12px; padding:10px 12px; border-left: 4px solid ${d.isReversed ? '#dc2626' : '#2563eb'};">
                    <div class="diagnostics-cluster-title" style="margin-bottom:6px;">
                        <span style="font-size:14px;">Character #${d.clusterIndex} (Bounding Box: ${Math.round(d.bbox.w)}×${Math.round(d.bbox.h)}px | ${d.strokeCount} stroke(s), ${d.pointCount} pts)</span>
                        <div style="display:flex; gap:6px; align-items:center;">
                            ${routingBadge}
                            <span class="${tagClass}">${tagText}</span>
                        </div>
                    </div>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-top:6px; background:#f1f5f9; padding:8px; border-radius:4px; font-size:12px;">
                        <div>
                            <div><strong>Head 1 (Character Identity):</strong></div>
                            <div style="font-size:14px; font-weight:700; color:#1e293b; margin:2px 0;">'${d.onnxCanonicalChar}' <span style="font-size:12px; font-weight:400; color:#475569;">(${d.onnxCharConfidence}%)</span></div>
                            <div style="color:#64748b;">Top-3 Candidates: ${top3Str}</div>
                        </div>
                        <div>
                            <div><strong>Head 2 (Clinical Reversal):</strong></div>
                            <div style="font-size:14px; font-weight:700; color:${d.isReversed ? '#dc2626' : '#166534'}; margin:2px 0;">${d.reversalProbability}% Reversal Probability</div>
                            <div style="color:#64748b;">Status: ${d.isReversed ? 'Mirror / Inverted' : 'Authentic Canonical'}</div>
                        </div>
                    </div>
                    <div style="margin-top:6px; font-size:12px; display:flex; justify-content:space-between; align-items:center;">
                        <span><strong>Lexical Reference (Google Ink):</strong> '${d.googleInkChar}'</span>
                        <span><strong>Resolved Output Glyph:</strong> <span style="font-weight:bold; color:${d.isReversed ? '#b91c1c' : '#15803d'}; font-size:18px;">'${d.resolvedGlyph}'</span></span>
                    </div>
                </div>`;
            });
            diagDetails.innerHTML = html;
        }

        transcriptionCard.style.display = 'block';
        updateMovementMetrics();

        // Render bounding boxes directly on canvas for immediate visual transparency
        lastSegmentationDiagnostics = result.diagnostics || [];
        renderBoundingBoxesOverlay();

        transcriptionCard.scrollIntoView({ behavior: "smooth" });

    } catch (error) {
        console.error("Transcription error:", error);
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
