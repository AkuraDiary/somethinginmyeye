/*
 * Elkinematics Live Screening Interface Logic
 * Dual-stream Kinematic & Orthographic Assessment
 * Strict Zero-Emoji Policy Enforced
 */

// ---------------------------------------------------------------------------
// BILINGUAL TRANSLATION DICTIONARY (SCREENING)
// ---------------------------------------------------------------------------
const SCREENING_TRANSLATIONS = {
    id: {
        screenTitle: "Kanvas Tulisan Tangan",
        subPillScreen: "Antarmuka Skrining",
        navToCollector: "← Pengumpul Data",
        screenSubtitle: "Tulis secara bebas pada kanvas atau ikuti acuan menjalankan screening.",
        labelMode: "Mode:",
        modeFreeWriting: "Tulisan Bebas",
        modePromptedWriting: "Tulisan Terpandu",
        labelEvaluatorRef: "Acuan Evaluator:",
        optVisCopying: "Salin Visual (Tampilkan Target)",
        optVisDictation: "Dikte Evaluator (Sembunyikan Target)",
        telemStartDelay: "Jeda Inisiasi",
        telemDirChanges: "Perubahan Arah",
        telemStrokeCount: "Jumlah Coretan",
        telemSmoothness: "Kelancaran Gerak",
        smoothStatus: "Lancar",
        variableStatus: "Variatif",
        hesitantStatus: "Ragu-ragu",
        btnClear: "Hapus",
        btnTranscribe: "Transkripsi Teks",
        btnTranscribing: "Mentranskripsi...",
        btnRunAssessment: "Jalankan Penilaian",
        btnEvaluating: "Mengevaluasi...",
        toggleShowBoxes: "Tampilkan Bounding Box Huruf Tersegmentasi",
        toggleShowWholeWord: "Tampilkan Kotak Kata Utuh",
        transcriptionLabel: "Teks Terbaca",
        altGuessesEmpty: "Tebakan Alternatif: —",
        altGuessesPrefix: "Tebakan Alternatif:",
        altUncertainStroke: "Tebakan Alternatif: [Coretan Tidak Pasti]",
        reversalNoticePrefix: "Observasi Karakter: Pembalikan cermin / rotasi terdeteksi pada",
        reversalClinicalFlag: "(ONNX Lokal: Pembalikan klinis terdeteksi)",
        diagHeader: "Inferensi Karakter Individual - Model DHRC",
        dashHeading: "Ringkasan Penilaian",
        dashOverallStatus: "Indikasi Skrining:",
        dashRating: "Peringkat:",
        badgeTypical: "Tipikal",
        badgeAtypical: "Atipikal",
        ratingStandard: "Standar",
        ratingTypical: "Dalam Batas Tipikal",
        ratingElevated: "Indikasi Skrining Meningkat",
        indicationTypical: "Dalam Batas Skrining Tipikal",
        indicationMotor: "Indikasi Potensial: Variabilitas Kinematik Tinggi (Risiko Disgrafia Motorik)",
        indicationOrtho: "Indikasi Potensial: Variansi Ejaan / Pembalikan (Risiko Disgrafia Disleksik)",
        indicationMulti: "Indikasi Potensial: Risiko Skrining Multi-Domain (Motorik & Ortografis)",
        screeningDisclaimer: "Hanya indikasi skrining otomatis. Hasil ini bukan diagnosis klinis dan tidak menggantikan asesmen formal oleh profesional berlisensi.",
        toggleShowHeatmap: "Tampilkan Peta Panas Variabilitas Kinematik",
        stimulusBadge: "STIMULUS TARGET",
        stimulusCopy: "SALIN TARGET",
        stimulusDictation: "DIKTE LISAN",
        stimulusFree: "TULISAN BEBAS",
        riskDysgraphiaTitle: "Ketidakteraturan Gerak",
        riskDysgraphiaFootnote: "Berdasarkan trajektori gerakan",
        riskDyslexiaTitle: "Variansi Ejaan",
        riskDyslexiaFootnote: "Dibandingkan teks target",
        reversalObservation: "Observasi Huruf:",
        dashFooterNote: "Tanda sorotan pada kanvas menunjukkan segmen dengan variabilitas gerakan lebih tinggi.",
        freePromptDisplay: '"Tulis secara bebas pada kanvas di bawah"',
        dictationPromptDisplay: '"Tuliskan huruf atau kata yang diucapkan evaluator"',
        alertNeedWriting: "Silakan tulis sesuatu terlebih dahulu.",
        alertTranscribeFail: "Tidak dapat mentranskripsi teks.",
        alertAnalysisFail: "Tidak dapat terhubung ke layanan analisis."
    },
    en: {
        screenTitle: "Handwriting Canvas",
        subPillScreen: "Live Screening Interface",
        navToCollector: "← Data Collector",
        screenSubtitle: "Write freely on the canvas or follow a prompt to use the screening system.",
        labelMode: "Mode:",
        modeFreeWriting: "Free Writing",
        modePromptedWriting: "Prompted Writing",
        labelEvaluatorRef: "Evaluator Reference:",
        optVisCopying: "Visual Copying (Show Target)",
        optVisDictation: "Evaluator Dictation (Hide Target from Child)",
        telemStartDelay: "Start Delay",
        telemDirChanges: "Direction Changes",
        telemStrokeCount: "Stroke Count",
        telemSmoothness: "Movement Smoothness",
        smoothStatus: "Smooth",
        variableStatus: "Variable",
        hesitantStatus: "Hesitant",
        btnClear: "Clear",
        btnTranscribe: "Transcribe Text",
        btnTranscribing: "Transcribing...",
        btnRunAssessment: "Run Assessment",
        btnEvaluating: "Evaluating...",
        toggleShowBoxes: "Show Segmented Character Bounding Boxes",
        toggleShowWholeWord: "Show Whole Word Box",
        transcriptionLabel: "Recognized Text",
        altGuessesEmpty: "Alternative Guesses: —",
        altGuessesPrefix: "Alternative Guesses:",
        altUncertainStroke: "Alternative Guesses: [Uncertain Stroke]",
        reversalNoticePrefix: "Letter Observation: Mirror / rotational reversal detected at",
        reversalClinicalFlag: "(Local ONNX:  reversal flagged)",
        diagHeader: "Individual Character Inference - DHRC Model",
        dashHeading: "Assessment Summary",
        dashOverallStatus: "Screening Indication:",
        dashRating: "Rating:",
        badgeTypical: "Typical",
        badgeAtypical: "Atypical",
        ratingStandard: "Standard",
        ratingTypical: "Within Typical Limits",
        ratingElevated: "Elevated Screening Indication",
        indicationTypical: "Within Typical Screening Limits",
        indicationMotor: "Potential Indicator: Elevated Kinematic Variance (Dysgraphia Risk)",
        indicationOrtho: "Potential Indicator: Spelling / Reversal Variance (Dyslexia Risk)",
        indicationMulti: "Potential Indicator: Multi-Domain Screening Risk (Motor & Orthographic)",
        screeningDisclaimer: "Automated screening indication only. This result does not constitute a clinical diagnosis and does not replace formal assessment by a licensed professional.",
        toggleShowHeatmap: "Show Kinematic Variability Heatmap",
        stimulusBadge: "TARGET STIMULUS",
        stimulusCopy: "COPY TARGET",
        stimulusDictation: "ORAL DICTATION",
        stimulusFree: "FREE WRITING",
        riskDysgraphiaTitle: "Movement Irregularity",
        riskDysgraphiaFootnote: "Based on movement trajectory",
        riskDyslexiaTitle: "Spelling Variance",
        riskDyslexiaFootnote: "Compared to target text",
        reversalObservation: "Letter Observation:",
        dashFooterNote: "Highlighted marks on the canvas indicate segments with higher movement variability.",
        freePromptDisplay: '"Write freely on the canvas below"',
        dictationPromptDisplay: '"Write the letter or word spoken by the evaluator"',
        alertNeedWriting: "Please write something first.",
        alertTranscribeFail: "Could not transcribe text.",
        alertAnalysisFail: "Could not connect to analysis service."
    }
};

let currentScreeningLang = localStorage.getItem('elkinematics_lang') || 'id';

function switchScreeningLanguage(lang) {
    if (!SCREENING_TRANSLATIONS[lang]) return;
    currentScreeningLang = lang;
    localStorage.setItem('elkinematics_lang', lang);

    document.querySelectorAll('[data-i18n]').forEach((el) => {
        const key = el.getAttribute('data-i18n');
        if (SCREENING_TRANSLATIONS[lang][key]) {
            el.innerHTML = SCREENING_TRANSLATIONS[lang][key];
        }
    });

    const btnId = document.getElementById('langIdBtn');
    const btnEn = document.getElementById('langEnBtn');
    if (btnId && btnEn) {
        btnId.classList.toggle('active', lang === 'id');
        btnEn.classList.toggle('active', lang === 'en');
    }

    refreshPromptDisplayText();
}

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
    const workspace = document.querySelector('.screening-workspace-section');
    const container = document.querySelector('.container');
    const targetWidth = workspace ? workspace.clientWidth : (container ? container.clientWidth - 40 : 1000);

    canvas.width = Math.max(300, Math.floor(targetWidth));
    // Generous canvas height so prompt card + canvas fills the visible tablet screen:
    // When writing, the user only sees prompt and canvas; buttons/telemetry are below fold
    const viewportH = window.innerHeight;
    canvas.height = Math.max(540, Math.floor(viewportH * 0.74));

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
        scrollToWritingPosition();
    } else {
        const card = document.getElementById('transcriptionCard');
        if (card && card.style.display !== 'none') {
            card.scrollIntoView({ behavior: 'smooth', block: 'start' });
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
const promptInput = document.getElementById('promptInput');
const visCopying = document.getElementById('visCopying');
const visDictation = document.getElementById('visDictation');
const promptDisplay = document.getElementById('promptDisplay');
const transcribeBtn = document.getElementById('transcribeBtn');
const analyzeBtn = document.getElementById('analyzeBtn');

function getEvaluatorPrompt() {
    if (!promptInput) return 'bebek';
    const val = promptInput.value.trim();
    return val.length > 0 ? val : 'bebek';
}

function scrollToWritingPosition() {
    const target = document.querySelector('.stimulus-card') || document.querySelector('.screening-workspace-section') || canvas;
    if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function refreshPromptDisplayText() {
    const t = SCREENING_TRANSLATIONS[currentScreeningLang] || SCREENING_TRANSLATIONS.id;
    if (modeFreeFlow.checked) {
        promptSelectorContainer.style.display = 'none';
        promptDisplay.innerText = t.freePromptDisplay;
        promptDisplay.className = 'instruction prompt-display-free';
        if (promptInput) promptInput.classList.remove('prompt-text-input-masked');
    } else {
        promptSelectorContainer.style.display = 'flex';
        const isDictation = visDictation && visDictation.checked;
        if (isDictation) {
            promptDisplay.innerText = t.dictationPromptDisplay;
            promptDisplay.className = 'instruction prompt-display-free';
            if (promptInput) promptInput.classList.add('prompt-text-input-masked');
        } else {
            promptDisplay.innerText = `"${getEvaluatorPrompt()}"`;
            promptDisplay.className = 'instruction prompt-display-target';
            if (promptInput) promptInput.classList.remove('prompt-text-input-masked');
        }
    }
}

function updateModeUI() {
    refreshPromptDisplayText();
    clearCanvas();
    scrollToWritingPosition();
}

modeFreeFlow.addEventListener('change', updateModeUI);
modePrompted.addEventListener('change', updateModeUI);
if (visCopying) visCopying.addEventListener('change', refreshPromptDisplayText);
if (visDictation) visDictation.addEventListener('change', refreshPromptDisplayText);
if (promptInput) {
    promptInput.addEventListener('input', () => {
        if (modePrompted.checked) {
            refreshPromptDisplayText();
        }
    });
    promptInput.addEventListener('change', () => {
        if (modePrompted.checked) {
            refreshPromptDisplayText();
            clearCanvas();
            scrollToWritingPosition();
        }
    });
}

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

    const t = SCREENING_TRANSLATIONS[currentScreeningLang] || SCREENING_TRANSLATIONS.id;
    if (nivCount > 55) {
        statusEl.innerText = t.hesitantStatus;
        statusEl.classList.add('telemetry-value-hesitant');
    } else if (nivCount > 30) {
        statusEl.innerText = t.variableStatus;
        statusEl.classList.add('telemetry-value-variable');
    } else {
        statusEl.innerText = t.smoothStatus;
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
                ctx.strokeStyle = "#000000";
                ctx.lineTo(pt.x, pt.y);
                ctx.stroke();
            }
        } else {
            inStroke = false;
        }
    }
}

const togglePhraseBox = document.getElementById('togglePhraseBox');
const toggleHeatmap = document.getElementById('toggleHeatmap');
let lastHeatmapData = null;

// Unified canvas overlay pipeline: strokes -> heatmap -> bounding boxes.
// Bounding boxes use no fill so they never occlude strokes or heatmap marks.
function renderCanvasOverlays() {
    redrawAllUserStrokes();

    const showHeatmap = toggleHeatmap ? toggleHeatmap.checked : true;
    if (showHeatmap && lastHeatmapData && lastHeatmapData.length > 0) {
        lastHeatmapData.forEach((prob, index) => {
            if (index < strokeData.length && prob > 0.80) {
                const pt = strokeData[index];
                ctx.save();
                ctx.beginPath();
                ctx.arc(pt.x, pt.y, 9, 0, 2 * Math.PI);
                ctx.fillStyle = "rgba(239, 68, 68, 0.28)";
                ctx.fill();
                ctx.beginPath();
                ctx.arc(pt.x, pt.y, 3, 0, 2 * Math.PI);
                ctx.fillStyle = "rgba(220, 38, 38, 0.85)";
                ctx.fill();
                ctx.restore();
            }
        });
    }

    if (!lastSegmentationDiagnostics || lastSegmentationDiagnostics.length === 0) return;

    const showIndividualBoxes = toggleBoundingBoxes ? toggleBoundingBoxes.checked : false;
    const showPhraseBox = togglePhraseBox ? togglePhraseBox.checked : false;

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

    const padding = 8;
    lastSegmentationDiagnostics.forEach((d) => {
        if (!d.bbox) return;

        const bx = Math.max(0, d.bbox.x - padding);
        const by = Math.max(0, d.bbox.y - padding);
        const bw = d.bbox.w + (padding * 2);
        const bh = d.bbox.h + (padding * 2);
        const isRev = d.isReversed;
        const color = isRev ? "#dc2626" : "#2563eb";

        ctx.save();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = color;
        ctx.setLineDash([5, 4]);
        ctx.strokeRect(bx, by, bw, bh);

        const label = isRev
            ? `C#${d.clusterIndex}: ${d.resolvedGlyph} [REV ${d.reversalProbability}%]`
            : `C#${d.clusterIndex}: '${d.onnxCanonicalChar}' (${d.onnxCharConfidence}%)`;
        ctx.font = "bold 11px -apple-system, BlinkMacSystemFont, sans-serif";
        const tw = ctx.measureText(label).width;
        const badgeY = Math.max(2, by - 18);

        ctx.setLineDash([]);
        ctx.fillStyle = color;
        ctx.fillRect(bx, badgeY, tw + 10, 16);
        ctx.fillStyle = "#ffffff";
        ctx.fillText(label, bx + 5, badgeY + 12);
        ctx.restore();
    });
}

// Backward-compatible alias
function renderBoundingBoxesOverlay() {
    renderCanvasOverlays();
}

[toggleBoundingBoxes, togglePhraseBox, toggleHeatmap].forEach((el) => {
    if (el) {
        el.addEventListener('change', () => {
            if (strokeData.length > 0) renderCanvasOverlays();
        });
    }
});

function clearCanvas() {
    lastSegmentationDiagnostics = null;
    lastHeatmapData = null;
    redrawCanvasBase();
    strokeData = [];
    hasStartedWriting = false;
    promptStartTime = Date.now();
    currentStrokeCount = 0;
    latencyMs = 0;

    document.getElementById('transcriptionCard').style.display = 'none';
    document.getElementById('resultsDashboard').style.display = 'none';
    const decodedDisplay = document.getElementById('decodedTextDisplay');
    if (decodedDisplay) {
        decodedDisplay.innerText = '"..."';
        decodedDisplay.removeAttribute('data-clean');
    }

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
function normalizePressure(raw) {
    if (raw === undefined || raw === null || Number.isNaN(raw)) return 0.5;
    let p = Number(raw);
    if (p > 1.0) {
        p = Math.min(1.0, p / 2.5);
    }
    return Math.min(1.0, Math.max(0.0, p));
}

function getCanvasPoint(e) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / (rect.width || 1);
    const scaleY = canvas.height / (rect.height || 1);
    return {
        x: (e.clientX - rect.left) * scaleX,
        y: (e.clientY - rect.top) * scaleY
    };
}

function recordPoint(e, isTouching, pt) {
    const point = pt || getCanvasPoint(e);
    strokeData.push({
        time: e.timeStamp,
        x: point.x,
        y: point.y,
        pressure: e.pressure !== undefined ? e.pressure : 0.5,
        tiltX: e.tiltX || 0,
        tiltY: e.tiltY || 0,
        touching: isTouching
    });
}

function computeLineWidth(pressure) {
    // Base 2.0px + 8.0px multiplier, hard-capped at 10.0px for firm pressure
    return Math.min(10.0, 2.0 + pressure * 8.0);
}

let lastScreeningX = 0;
let lastScreeningY = 0;

canvas.addEventListener('pointerdown', (e) => {
    try {
        canvas.setPointerCapture(e.pointerId);
    } catch (_) {}
    if (!hasStartedWriting) {
        latencyMs = Date.now() - promptStartTime;
        hasStartedWriting = true;
    }
    isDrawing = true;
    currentStrokeCount++;
    const pt = getCanvasPoint(e);
    lastScreeningX = pt.x;
    lastScreeningY = pt.y;

    const p = normalizePressure(e.pressure);
    const initialWidth = computeLineWidth(p);
    ctx.lineWidth = initialWidth;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.strokeStyle = "#000000";
    ctx.beginPath();
    ctx.arc(lastScreeningX, lastScreeningY, Math.max(1.0, initialWidth / 2), 0, Math.PI * 2);
    ctx.fillStyle = "#000000";
    ctx.fill();
    recordPoint(e, 1, pt);
});

canvas.addEventListener('pointermove', (e) => {
    if (isDrawing) {
        const pt = getCanvasPoint(e);
        const p = normalizePressure(e.pressure);
        const currentWidth = computeLineWidth(p);

        ctx.beginPath();
        ctx.moveTo(lastScreeningX, lastScreeningY);
        ctx.lineTo(pt.x, pt.y);
        ctx.lineWidth = currentWidth;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.strokeStyle = "#000000";
        ctx.stroke();

        lastScreeningX = pt.x;
        lastScreeningY = pt.y;
        recordPoint(e, 1, pt);
    }
});

canvas.addEventListener('pointerup', (e) => {
    try {
        canvas.releasePointerCapture(e.pointerId);
    } catch (_) {}
    if (isDrawing) {
        isDrawing = false;
        recordPoint(e, 0);
        updateMovementMetrics();
    }
});

canvas.addEventListener('pointercancel', (e) => {
    try {
        canvas.releasePointerCapture(e.pointerId);
    } catch (_) {}
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

// Suppress context menu, magnifying glass, and text selection on touch/stylus hold
canvas.addEventListener('contextmenu', (e) => e.preventDefault());
canvas.addEventListener('selectstart', (e) => e.preventDefault());

document.getElementById('clearBtn').addEventListener('click', () => {
    clearCanvas();
    scrollToWritingPosition();
});

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
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ" //+
    // "0123456789"
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
    'K': 'Ʞ', 'k': 'ʞ',   // Latin Turned K (Option 1 with Lisu ꓘ fallback)
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
            if (results[keys[0]].dims.includes(52) || results[keys[0]].dims.includes(62)) {
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
    const promptTarget = getEvaluatorPrompt();
    const promptTargetNoSpaces = promptTarget.replace(/\s+/g, '');

    // Contextual Domain Masking: Prevents numeral reversals (e.g. 6/9) from polluting alphabetic text
    const isAlphabeticContext = isPrompted ? !/^\d+$/.test(promptTargetNoSpaces) : (rawWinner.length > 0 && /[a-zA-Z]/.test(rawWinner));
    const numericReversalKeys = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];

    // Track 2: Kinematic Clustering into Characters
    const clusters = segmentIntoCharacterClusters(strokes);

    // Evaluate each cluster locally using the In-House ONNX Reversal Model (1-2ms per cluster)
    const reversedPositions = [];
    const diagnostics = [];

    for (let k = 0; k < clusters.length; k++) {
        const clusterStrokes = clusters[k];
        const allClusterPts = clusterStrokes.flat();
        const cXs = allClusterPts.map(p => p.x);
        const cYs = allClusterPts.map(p => p.y);
        const boxXMin = Math.min(...cXs);
        const boxXMax = Math.max(...cXs);
        const boxYMin = Math.min(...cYs);
        const boxYMax = Math.max(...cYs);
        const boxH = Math.max(boxYMax - boxYMin, 1);
        const boxW = Math.max(boxXMax - boxXMin, 1);

        const onnxRes = await evaluateClusterWithONNX(clusterStrokes);

        // Identify intended canonical letter:
        let canonicalChar = '';
        if (isPrompted && k < promptTargetNoSpaces.length) {
            // Priority 1: In Prompted Mode, use exact character casing from promptTargetNoSpaces
            canonicalChar = promptTargetNoSpaces[k];
        } else {
            // Priority 2: In Free Writing, evaluate ONNX Head 1 with case awareness
            let topChar = onnxRes.topChar || '';
            const inkChar = (k < rawWinner.length && rawWinner[k] !== '?') ? rawWinner[k] : '';

            // If Google Ink recognized an uppercase character and ONNX top3 contains that uppercase character, favor uppercase:
            if (inkChar >= 'A' && inkChar <= 'Z' && onnxRes.top3 && onnxRes.top3.some(c => c.char === inkChar)) {
                topChar = inkChar;
            } else if (boxH >= 55 && onnxRes.top3) {
                // If tall stroke (>55px) and topChar is lowercase 'b'/'d', check if 'B'/'D' is in top3 candidates
                if (topChar === 'b' && onnxRes.top3.some(c => c.char === 'B')) {
                    topChar = 'B';
                } else if (topChar === 'd' && onnxRes.top3.some(c => c.char === 'D')) {
                    topChar = 'D';
                }
            }
            canonicalChar = topChar || inkChar || '?';
        }

        let revSymbol = canonicalChar;
        let clusterIsReversed = false;
        let resolvedGlyph = canonicalChar;

        if (onnxRes.isReversed) {
            // Domain mask check: suppress numeric reversals in alphabetic context
            if (!(isAlphabeticContext && numericReversalKeys.includes(canonicalChar))) {
                clusterIsReversed = true;
                isReversal = true;

                // Map to the canonical reversed glyph
                revSymbol = asymmetricReversible[canonicalChar] || 
                            asymmetricReversible[canonicalChar.toUpperCase()] || 
                            asymmetricReversible[canonicalChar.toLowerCase()] || 
                            canonicalChar;

                // Disambiguate case-sensitive chiral glyphs
                if (canonicalChar.toLowerCase() === 'b' && revSymbol === 'd') {
                    if (canonicalChar === 'B') revSymbol = 'ꓭ';
                } else if (canonicalChar.toLowerCase() === 'd' && revSymbol === 'b') {
                    if (canonicalChar === 'D') revSymbol = 'ᗡ';
                } else if (canonicalChar.toLowerCase() === 'p' && revSymbol === 'q') {
                    if (canonicalChar === 'P') revSymbol = 'ꟼ';
                } else if (canonicalChar.toLowerCase() === 'k') {
                    revSymbol = (canonicalChar === 'K') ? 'Ʞ' : 'ʞ';
                }

                // Show only the resolved character itself (no bracket notation)
                resolvedGlyph = revSymbol;

                reversedPositions.push({
                    index: k + 1,
                    prob: onnxRes.reversalProb,
                    rawChar: (k < rawWinner.length) ? rawWinner[k] : '?',
                    onnxChar: onnxRes.topChar,
                    canonicalChar: canonicalChar,
                    revSymbol: revSymbol
                });
            }
        } else {
            // Not reversed: use Google Ink char if available, otherwise ONNX canonicalChar
            resolvedGlyph = (k < rawWinner.length && rawWinner[k] && rawWinner[k] !== '?') ? rawWinner[k] : canonicalChar;
        }

        diagnostics.push({
            clusterIndex: k + 1,
            strokeCount: clusterStrokes.length,
            pointCount: clusterStrokes.reduce((s, st) => s + st.length, 0),
            bbox: {
                x: boxXMin,
                y: boxYMin,
                w: boxW,
                h: boxH
            },
            clusterStrokes: clusterStrokes,
            googleInkChar: (k < rawWinner.length) ? rawWinner[k] : '?',
            canonicalChar: canonicalChar,
            onnxCanonicalChar: onnxRes.topChar,
            onnxCharConfidence: (onnxRes.topProb * 100).toFixed(1),
            onnxTop3: onnxRes.top3,
            reversalProbability: (onnxRes.reversalProb * 100).toFixed(1),
            isReversed: clusterIsReversed,
            revSymbol: revSymbol,
            resolvedGlyph: resolvedGlyph
        });
    }

    // Arbitration: Build human display text (displayWinner) and clean unannotated text (cleanWinner)
    displayWinner = rawWinner;
    let cleanWinner = rawWinner;

    if (clusters.length === 1) {
        if (isReversal && reversedPositions.length > 0) {
            displayWinner = reversedPositions[0].revSymbol;
            cleanWinner = reversedPositions[0].revSymbol;
        } else {
            displayWinner = (rawWinner && rawWinner !== '?') ? rawWinner : (diagnostics[0]?.canonicalChar || '?');
            cleanWinner = displayWinner;
        }
    } else if (clusters.length > 1) {
        if (isReversal) {
            if (rawWinner.length === clusters.length) {
                const parts = rawWinner.split('');
                reversedPositions.forEach(p => {
                    parts[p.index - 1] = p.revSymbol;
                });
                displayWinner = parts.join('');
                cleanWinner = parts.join('');
            } else {
                const parts = diagnostics.map(d => d.isReversed ? d.revSymbol : (d.googleInkChar !== '?' ? d.googleInkChar : d.canonicalChar));
                displayWinner = parts.join('');
                cleanWinner = parts.join('');
            }
        } else {
            displayWinner = (rawWinner && rawWinner !== '?') ? rawWinner : diagnostics.map(d => d.canonicalChar).join('');
            cleanWinner = displayWinner;
        }
    }

    if (isReversal) {
        const posDescs = reversedPositions.map(p => `pos ${p.index} ('${p.canonicalChar}' reversed as '${p.revSymbol}', confidence: ${(p.prob * 100).toFixed(1)}%)`).join(', ');
        notice = `Letter Observation: Mirror / rotational reversal detected at ${posDescs}.`;
    }

    return {
        winner: displayWinner,
        cleanWinner: cleanWinner,
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

    const t = SCREENING_TRANSLATIONS[currentScreeningLang] || SCREENING_TRANSLATIONS.id;
    if (strokeData.length === 0) {
        alert(t.alertNeedWriting);
        return;
    }

    transcribeBtn.innerText = t.btnTranscribing;
    transcribeBtn.disabled = true;

    try {
        const result = await transcribeWithReflectionAnalysis(strokeData);

        decodedTextDisplay.innerText = `"${result.winner}"`;
        decodedTextDisplay.setAttribute('data-clean', result.cleanWinner || result.winner);
        if (result.isReversal && result.notice) {
            reversalNotice.innerText = result.notice;
            reversalNotice.style.display = 'block';
        } else {
            reversalNotice.style.display = 'none';
        }

        if (result.candidates.length > 0) {
            let text = `${t.altGuessesPrefix} ${result.candidates.join(" | ")}`;
            if (result.isReversal) {
                text += ` ${t.reversalClinicalFlag}`;
            }
            alternativeCandidates.innerText = text;
        } else {
            alternativeCandidates.innerText = t.altUncertainStroke;
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
                            <div><strong>Head 2 (Reversal):</strong></div>
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

    const t = SCREENING_TRANSLATIONS[currentScreeningLang] || SCREENING_TRANSLATIONS.id;
    if (strokeData.length === 0) {
        alert(t.alertNeedWriting);
        return;
    }

    analyzeBtn.innerText = t.btnEvaluating;
    analyzeBtn.disabled = true;

    try {
        // First check if transcribed
        let cleanDecoded = document.getElementById('decodedTextDisplay').getAttribute('data-clean');
        let decoded = cleanDecoded || document.getElementById('decodedTextDisplay').innerText.replace(/"/g, '').trim();
        if (decoded === "" || decoded === "..." || decoded === "?") {
            const res = await transcribeWithReflectionAnalysis(strokeData);
            decoded = res.cleanWinner || res.winner;
            document.getElementById('decodedTextDisplay').innerText = `"${res.winner}"`;
            document.getElementById('decodedTextDisplay').setAttribute('data-clean', res.cleanWinner || res.winner);
            if (res.isReversal && res.notice) {
                document.getElementById('reversalNotice').innerText = res.notice;
                document.getElementById('reversalNotice').style.display = 'block';
            } else {
                document.getElementById('reversalNotice').style.display = 'none';
            }
            if (res.candidates.length > 0) {
                let text = `${t.altGuessesPrefix} ${res.candidates.join(" | ")}`;
                if (res.isReversal) {
                    text += ` ${t.reversalClinicalFlag}`;
                }
                document.getElementById('alternativeCandidates').innerText = text;
            }
            document.getElementById('transcriptionCard').style.display = 'block';
        }

        const strokesWithLatency = strokeData.map(point => {
            return { ...point, latency: latencyMs };
        });

        const isFreeFlow = modeFreeFlow.checked;
        const targetPrompt = isFreeFlow ? decoded : getEvaluatorPrompt();

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

        // Retain heatmap in state and render through the unified overlay pipeline
        lastHeatmapData = (result.heatmap && result.heatmap.length > 0) ? result.heatmap : null;
        renderCanvasOverlays();

        dashboard.style.display = 'block';

        // Softened screening phrasing: map backend indication to localized text
        const isElevated = !!(result.is_dysgraphic || result.is_dyslexic);
        let indicationKey = 'indicationTypical';
        if (result.is_dysgraphic && result.is_dyslexic) indicationKey = 'indicationMulti';
        else if (result.is_dysgraphic) indicationKey = 'indicationMotor';
        else if (result.is_dyslexic) indicationKey = 'indicationOrtho';
        diagBadge.innerText = t[indicationKey];
        diagBadge.removeAttribute('data-i18n');
        severityText.innerText = isElevated ? t.ratingElevated : t.ratingTypical;
        severityText.removeAttribute('data-i18n');

        diagBadge.className = isElevated ? "status-badge badge-amber" : "status-badge badge-green";

        const dysgraphiaPct = (result.dysgraphia_risk_percentage || 0).toFixed(1);
        const dyslexiaPct = (result.dyslexia_risk_percentage || 0).toFixed(1);

        dysgraphiaRiskText.innerText = `${dysgraphiaPct}%`;
        dysgraphiaRiskText.style.color = result.is_dysgraphic ? "#d97706" : "#16a34a";

        dyslexiaRiskText.innerText = `${dyslexiaPct}%`;
        dyslexiaRiskText.style.color = result.is_dyslexic ? "#d97706" : "#16a34a";

        if (result.reversal_detected) {
            reversalAlertBox.style.display = 'block';
            reversalAlertText.innerText = result.reversal_description;
        } else {
            reversalAlertBox.style.display = 'none';
        }

        latencyText.innerText = `${Math.round(result.cognitive_latency_ms || 0)} ms`;
        dashboard.scrollIntoView({ behavior: "smooth" });

    } catch (error) {
        alert(t.alertAnalysisFail);
    } finally {
        analyzeBtn.innerText = t.btnRunAssessment;
        analyzeBtn.disabled = false;
    }
});

// --- DHRC MODEL ACCORDION ---
(function initDiagnosticsAccordion() {
    const header = document.getElementById('modelDiagnosticsHeader');
    const card = document.getElementById('modelDiagnosticsCard');
    if (!header || !card) return;
    const toggle = () => {
        const expanded = card.classList.toggle('expanded');
        header.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    };
    header.addEventListener('click', toggle);
    header.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            toggle();
        }
    });
})();

// Apply language on initial load
switchScreeningLanguage(currentScreeningLang);

