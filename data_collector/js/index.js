/**
 * Kinematic Handwriting Data Collector & Diagnostic Client
 *
 * Two collection pathways share one canvas:
 *  - Moderated Guided Collection (default): semi-gamified, pseudorandom Indonesian stimulus sessions.
 *  - Free Data Collection: manual label / prompt entry.
 *
 * Full Bilingual Support (ID / EN) synchronized via localStorage.
 * Saved filenames keep the legacy schema consumed by scripts/universal_pipeline.py:
 *   ${dataset}_${mode}_${label}_${annotator}_${timestamp}
 */

const EXTERNAL_TTS_API_URL = "";

// ---------------------------------------------------------------------------
// BILINGUAL TRANSLATION DICTIONARY
// ---------------------------------------------------------------------------
const COLLECTOR_TRANSLATIONS = {
    id: {
        collectorTitle: "Kinematic Handwriting Data Collector",
        subPill: "Platform Riset Elkinematics",
        navToScreening: "Live Screening →",
        tabGuided: "Moderated Guided Collection",
        tabFree: "Free Data Collection",
        guideTag: "PANDUAN RISET / RESEARCH GUIDE",
        guideTitle: "Panduan Penggunaan Pengumpulan Data:",
        guide1: "Pilih <strong>Jenis Dataset</strong> (Train/Validation) dan isikan <strong>Nama Anda</strong> di field <strong>Anotator</strong>.",
        guide2: "Pilih <strong>Mode (klasifikasi)</strong> (Normal/Dyslexia/Dysgraphia) dan isikan <strong>Label</strong> sesuai dengan data yang akan dikumpulkan.",
        guide3: "Klik tombol <strong>Start Writing</strong> sebelum Anda mulai menulis untuk menghitung waktu jeda kognitif (<strong>cognitive latency</strong>).",
        guide4: "<strong>Tuliskan huruf/kata</strong> pada area kanvas di bawah (disarankan menggunakan stylus/pen tablet). Kanvas akan mengumpulkan data terkait: <strong>arah coretan, kecepatan, tekanan, dan jeda antar-coretan</strong>.",
        guide5: "Jika tulisan dirasa sudah selesai, klik <strong>Save Sample (In Server)</strong>. Aplikasi akan secara otomatis menyimpan data tulisan dan data kinematic di server.",
        guide6: "Gunakan tombol <strong>Clear Canvas</strong> untuk membersihkan layar dan mengulang tulisan (sekaligus mengulang pencatat waktu).",

        setupTitle: "Konfigurasi Sesi Pengumpulan Terpandu",
        setupSubtitle: "Atur parameter annotator, dataset, mode stimulus, dan jumlah item sebelum memulai.",

        labelAnnotator: "Anotator:",
        labelDataset: "Dataset:",
        labelClassification: "Klasifikasi:",
        labelExecutionMode: "Mode Eksekusi:",
        labelTierFocus: "Fokus Kategori:",
        labelItemCount: "Jumlah Item:",
        labelReference: "Label:",

        optTrain: "Train",
        optValidation: "Validation",
        optNormal: "Normal",
        optDyslexia: "Dyslexia",
        optDysgraphia: "Dysgraphia",
        optVisualCopying: "Visual Copying (Salin Teks)",
        optSpokenDictation: "Dikte Lisan Penguji (Target Disembunyikan)",
        optTierAll: "Semua Tingkat (Seimbang)",
        optTierLetters: "Hanya Huruf (Level 1)",
        optTierRegular: "Hanya Kata Reguler (Level 2A)",
        optTierAnagram: "Hanya Kata Anagram (Level 2B)",
        optTierPseudo: "Hanya Kata Tanpa Makna (Level 2C)",
        optTierSentences: "Hanya Kalimat (Level 3)",

        btnStartGuided: "Mulai Sesi Terpandu",
        btnReplayAudio: "Putar Ulang Suara",
        btnPlayBrowserAudio: "Putar Suara (Browser)",
        btnStartWriting: "Start Writing",
        btnStartOralTiming: "Mulai Ukur Latency (Spasi)",
        oralTimingStarted: "Waktu Berjalan (Menunggu sentuhan pena...)",
        btnSaveSample: "Save Sample (In Server)",
        btnClearCanvas: "Clear Canvas",
        btnSaveAndNext: "Save Sample (Next →)",
        btnSkip: "Skip",
        btnEndSession: "End Session",

        examinerSpokenTag: "Instruksi Penguji: Ucapkan kata berikut ke anak:",
        freePromptDesc: "Prompt: Tulis teks acuan sesuai Label (huruf, kata, atau kalimat)",
        latencyWaiting: "Latency: menunggu...",
        latencyMeasuring: "Latency: mengukur jeda...",
        latencyWaitingToStart: "Latency: Menunggu mulai...",
        latencyTimingDelay: "Latency: Mengukur jeda kognitif...",
        dictationInstruction: "Dengarkan kata yang diucapkan penguji lalu tuliskan di kanvas",

        alertNeedAnnotator: "Isi nama Anotator terlebih dahulu.",
        alertNeedDrawing: "Tulis sesuatu pada kanvas terlebih dahulu.",
        alertSaveError: "Gagal menyimpan ke server. Coba lagi.",
        confirmSwitchTab: "Sesi terpandu sedang berjalan. Akhiri sesi dan beralih ke mode bebas?",

        summaryTitle: "Sesi Selesai",
        summarySaved: "Sampel tersimpan:",
        summaryAvgLatency: "Rata-rata latency:",
        summarySessionId: "ID Sesi:"
    },
    en: {
        collectorTitle: "Kinematic Handwriting Data Collector",
        subPill: "Elkinematics Research Platform",
        navToScreening: "Live Screening →",
        tabGuided: "Moderated Guided Collection",
        tabFree: "Free Data Collection",
        guideTag: "PANDUAN RISET / RESEARCH GUIDE",
        guideTitle: "Data Collection User Guide:",
        guide1: "Select <strong>Dataset Type</strong> (Train/Validation) and enter your name in the <strong>Annotator</strong> field.",
        guide2: "Select <strong>Classification Mode</strong> (Normal/Dyslexia/Dysgraphia) and specify the <strong>Label</strong> matching your collected data.",
        guide3: "Click <strong>Start Writing</strong> before writing to measure cognitive reaction time (<strong>cognitive latency</strong>).",
        guide4: "<strong>Write the letters/words</strong> on the canvas below (active stylus/pen tablet recommended). The canvas records: <strong>stroke direction, velocity, pressure, and inter-stroke hesitation</strong>.",
        guide5: "When finished writing, click <strong>Save Sample (In Server)</strong>. The system automatically stores kinematic trajectories and stroke images on the server.",
        guide6: "Use <strong>Clear Canvas</strong> to wipe the drawing area and restart latency timing for the current item.",

        setupTitle: "Guided Collection Session Setup",
        setupSubtitle: "Configure annotator, dataset, stimulus mode, and session items before starting.",

        labelAnnotator: "Annotator:",
        labelDataset: "Dataset:",
        labelClassification: "Classification:",
        labelExecutionMode: "Execution Mode:",
        labelTierFocus: "Category Focus:",
        labelItemCount: "Session Items:",
        labelReference: "Label:",

        optTrain: "Train",
        optValidation: "Validation",
        optNormal: "Normal",
        optDyslexia: "Dyslexia",
        optDysgraphia: "Dysgraphia",
        optVisualCopying: "Visual Copying (Show Target)",
        optSpokenDictation: "Examiner Spoken Dictation (Target Hidden)",
        optTierAll: "All Levels (Balanced)",
        optTierLetters: "Letters Only (Level 1)",
        optTierRegular: "Regular Words Only (Level 2A)",
        optTierAnagram: "Anagram Words Only (Level 2B)",
        optTierPseudo: "Pseudowords Only (Level 2C)",
        optTierSentences: "Sentences Only (Level 3)",

        btnStartGuided: "Start Guided Session",
        btnReplayAudio: "Replay Audio",
        btnPlayBrowserAudio: "Play Browser Audio",
        btnStartWriting: "Start Writing",
        btnStartOralTiming: "Start Latency Timing (Space)",
        oralTimingStarted: "Timing Active (Waiting for stylus touch...)",
        btnSaveSample: "Save Sample (In Server)",
        btnClearCanvas: "Clear Canvas",
        btnSaveAndNext: "Save Sample (Next →)",
        btnSkip: "Skip",
        btnEndSession: "End Session",

        examinerSpokenTag: "Examiner: Speak the following word aloud to the participant:",
        freePromptDesc: "Prompt: Write the reference text according to Label (letters, words, or sentences)",
        latencyWaiting: "Latency: waiting...",
        latencyMeasuring: "Latency: timing reaction delay...",
        latencyWaitingToStart: "Latency: Waiting to start...",
        latencyTimingDelay: "Latency: Timing cognitive delay...",
        dictationInstruction: "Listen to the word spoken by the examiner and write it on canvas",

        alertNeedAnnotator: "Please enter Annotator name first.",
        alertNeedDrawing: "Please draw something on the canvas first.",
        alertSaveError: "Failed to save to server. Please try again.",
        confirmSwitchTab: "Guided session is active. End current session and switch to free mode?",

        summaryTitle: "Session Completed",
        summarySaved: "Samples saved:",
        summaryAvgLatency: "Average latency:",
        summarySessionId: "Session ID:"
    }
};

let currentLang = localStorage.getItem('elkinematics_lang') || 'id';

function switchLanguage(lang) {
    if (!COLLECTOR_TRANSLATIONS[lang]) return;
    currentLang = lang;
    localStorage.setItem('elkinematics_lang', lang);

    document.querySelectorAll('[data-i18n]').forEach((el) => {
        const key = el.getAttribute('data-i18n');
        if (COLLECTOR_TRANSLATIONS[lang][key]) {
            el.innerHTML = COLLECTOR_TRANSLATIONS[lang][key];
        }
    });

    const btnId = document.getElementById('langIdBtn');
    const btnEn = document.getElementById('langEnBtn');
    if (btnId && btnEn) {
        btnId.classList.toggle('active', lang === 'id');
        btnEn.classList.toggle('active', lang === 'en');
    }

    if (guidedState.running) {
        updateHud();
        const item = guidedState.plan[guidedState.index];
        if (item) setPromptHeader(item);
    }
}

// ---------------------------------------------------------------------------
// TTS ENGINES
// ---------------------------------------------------------------------------
class BrowserTTSEngine {
    speak(text) {
        return new Promise((resolve) => {
            if (!('speechSynthesis' in window)) return resolve();
            window.speechSynthesis.cancel();
            const utter = new SpeechSynthesisUtterance(text);
            utter.lang = currentLang === 'en' ? 'en-US' : 'id-ID';
            utter.rate = 0.85;
            utter.onend = () => resolve();
            utter.onerror = () => resolve();
            window.speechSynthesis.speak(utter);
        });
    }

    cancel() {
        if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    }
}

class ExternalTTSEngine {
    constructor(apiUrl) {
        this.apiUrl = apiUrl;
        this.currentAudio = null;
        this.fallback = new BrowserTTSEngine();
    }

    base64ToBlob(base64, mimeType) {
        const byteCharacters = atob(base64);
        const bytes = new Uint8Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            bytes[i] = byteCharacters.charCodeAt(i);
        }
        return new Blob([bytes], { type: mimeType });
    }

    async speak(text) {
        try {
            this.cancel();
            const response = await fetch(`${this.apiUrl}/text-to-speech`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, lang: currentLang })
            });
            const data = await response.json();
            const base64Audio = data.audioContent || (data.data && data.data.audioContent) || data.audio;
            if (!base64Audio) throw new Error('TTS API returned no audioContent.');

            const audioUrl = URL.createObjectURL(this.base64ToBlob(base64Audio, 'audio/mpeg'));
            this.currentAudio = new Audio(audioUrl);
            return await new Promise((resolve) => {
                this.currentAudio.onended = () => resolve();
                this.currentAudio.onerror = () => resolve();
                this.currentAudio.play().catch(() => resolve());
            });
        } catch (error) {
            console.warn('External TTS failed, falling back to browser speech:', error);
            return this.fallback.speak(text);
        }
    }

    cancel() {
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio.currentTime = 0;
            this.currentAudio = null;
        }
        this.fallback.cancel();
    }
}

const ttsEngine = EXTERNAL_TTS_API_URL
    ? new ExternalTTSEngine(EXTERNAL_TTS_API_URL)
    : new BrowserTTSEngine();

// ---------------------------------------------------------------------------
// INDONESIAN STIMULUS REPOSITORY & BANK LOADER
// ---------------------------------------------------------------------------
const DEFAULT_STIMULUS_BANK = {
    alphabet: {
        lowercase: [
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
        ],
        uppercase: [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
        ],
        chiral_priority: [
            'b', 'd', 'p', 'q', 'B', 'D', 'E', 'S', 'N', 'C', 'J', 'L', 'P', 'R', 'Z'
        ]
    },
    high_frequency_regular_words: [
        'kuda', 'sapi', 'ayam', 'bebek', 'kucing', 'katak', 'cicak', 'burung', 'gajah', 'rusa', 'ikan', 'semut',
        'buku', 'meja', 'kursi', 'pintu', 'kasur', 'lampu', 'topi', 'baju', 'roda', 'bola', 'sapu', 'piring',
        'ibu', 'ayah', 'adik', 'kakak', 'teman', 'guru', 'batu', 'daun', 'pohon', 'hujan', 'air', 'api',
        'nasi', 'roti', 'susu', 'madu', 'kopi', 'apel', 'jeruk'
    ],
    anagram_pairs: [
        { target: 'batu', counterpart: 'buta' },
        { target: 'tali', counterpart: 'liat' },
        { target: 'kasur', counterpart: 'rusak' },
        { target: 'kapal', counterpart: 'pakal' },
        { target: 'bakar', counterpart: 'kabar' },
        { target: 'palu', counterpart: 'lupa' },
        { target: 'kuda', counterpart: 'duka' },
        { target: 'pasar', counterpart: 'paras' },
        { target: 'tarik', counterpart: 'rakit' },
        { target: 'tebal', counterpart: 'lebat' }
    ],
    minimal_pairs: [
        { target: 'buku', counterpart: 'kuku' },
        { target: 'tari', counterpart: 'lari' },
        { target: 'bata', counterpart: 'data' },
        { target: 'pola', counterpart: 'bola' },
        { target: 'sapu', counterpart: 'satu' },
        { target: 'daun', counterpart: 'gaun' }
    ],
    pseudowords: [
        'kumo', 'mado', 'beka', 'tuko', 'dapi', 'fodi', 'wena', 'solu', 'leki', 'nura',
        'somi', 'poti', 'duba', 'gopu', 'selu', 'wabi', 'jeno', 'ropu', 'bami', 'lusi',
        'kinu', 'tupin', 'medas', 'rokat', 'simap'
    ],
    short_sentences: [
        'Saya suka baca buku.',
        'Ibu masak nasi di dapur.',
        'Budi bermain bola di lapangan.',
        'Adik minum susu setiap pagi.',
        'Kakak mencuci sepeda roda dua.',
        'Ayah membaca koran di teras.',
        'Kucing belang tidur di kasur.',
        'Baju baru adik warna biru.'
    ]
};

let stimulusBank = null;

async function loadStimulusBank() {
    try {
        const response = await fetch('vocabularies/stimuli_id.json');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        stimulusBank = await response.json();
    } catch (err) {
        console.warn('Could not load stimuli_id.json, using embedded fallback:', err);
        stimulusBank = DEFAULT_STIMULUS_BANK;
    }
}

const TIER_DEFS = {
    L1: {
        code: 'L1',
        label: { id: 'Level 1: Huruf Alfabet (Kiral & Acak)', en: 'Level 1: Alphabet Letters (Chiral & General)' },
        share: 0.25
    },
    L2A: {
        code: 'L2A',
        label: { id: 'Level 2A: Kata Reguler Frekuensi Tinggi', en: 'Level 2A: High-Frequency Regular Words' },
        share: 0.25
    },
    L2B: {
        code: 'L2B',
        label: { id: 'Level 2B: Kata Rawan Migrasi Huruf (Anagram)', en: 'Level 2B: Letter Migration Anagram Words' },
        share: 0.20
    },
    L2C: {
        code: 'L2C',
        label: { id: 'Level 2C: Kata Tanpa Makna (Pseudoword)', en: 'Level 2C: Pseudowords (Sublexical)' },
        share: 0.15
    },
    L3: {
        code: 'L3',
        label: { id: 'Level 3: Kalimat Pendek Standar', en: 'Level 3: Short Standardized Sentences' },
        share: 0.15
    }
};

function getRecentStimuli() {
    try {
        const stored = sessionStorage.getItem('elkinematics_recent_stimuli');
        return stored ? JSON.parse(stored) : [];
    } catch {
        return [];
    }
}

function recordRecentStimuli(prompts) {
    try {
        let recent = getRecentStimuli().concat(prompts);
        if (recent.length > 80) {
            recent = recent.slice(recent.length - 80);
        }
        sessionStorage.setItem('elkinematics_recent_stimuli', JSON.stringify(recent));
    } catch (e) {
        console.warn('Could not save recent stimuli to sessionStorage', e);
    }
}

function fisherYates(array) {
    const arr = array.slice();
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
}

function getPoolForTier(tierKey, bank) {
    const b = bank || DEFAULT_STIMULUS_BANK;
    if (tierKey === 'L1') {
        const chiral = b.alphabet.chiral_priority || [];
        const lower = b.alphabet.lowercase || [];
        const upper = b.alphabet.uppercase || [];
        // Combine chiral with double weighting and full alphabet; strictly zero digits
        return [...chiral, ...chiral, ...lower, ...upper];
    }
    if (tierKey === 'L2A') {
        return b.high_frequency_regular_words || [];
    }
    if (tierKey === 'L2B') {
        const items = [];
        (b.anagram_pairs || []).forEach((p) => {
            if (p.target) items.push(p.target);
            if (p.counterpart) items.push(p.counterpart);
        });
        (b.minimal_pairs || []).forEach((p) => {
            if (p.target) items.push(p.target);
            if (p.counterpart) items.push(p.counterpart);
        });
        return Array.from(new Set(items));
    }
    if (tierKey === 'L2C') {
        return b.pseudowords || [];
    }
    if (tierKey === 'L3') {
        return b.short_sentences || [];
    }
    return [];
}

function drawFromPoolWithAntiRepetition(candidates, count) {
    const recent = new Set(getRecentStimuli());
    const uniqueCandidates = Array.from(new Set(candidates));

    let fresh = uniqueCandidates.filter((item) => !recent.has(item));
    if (fresh.length === 0) {
        fresh = uniqueCandidates.slice();
    }

    let bag = fisherYates(fresh);
    const chosen = [];
    const usedInSession = new Set();

    while (chosen.length < count) {
        if (bag.length === 0) {
            const remaining = uniqueCandidates.filter((item) => !usedInSession.has(item));
            if (remaining.length > 0) {
                bag = fisherYates(remaining);
            } else {
                usedInSession.clear();
                bag = fisherYates(uniqueCandidates);
            }
        }
        const item = bag.pop();
        chosen.push(item);
        usedInSession.add(item);
    }
    return chosen;
}

function generateSessionPlan(total, tierFocus = 'all') {
    const bank = stimulusBank || DEFAULT_STIMULUS_BANK;
    let targetTiers = [];

    if (tierFocus === 'letters') {
        targetTiers = ['L1'];
    } else if (tierFocus === 'regular_words') {
        targetTiers = ['L2A'];
    } else if (tierFocus === 'anagram_words') {
        targetTiers = ['L2B'];
    } else if (tierFocus === 'pseudowords') {
        targetTiers = ['L2C'];
    } else if (tierFocus === 'sentences') {
        targetTiers = ['L3'];
    } else {
        targetTiers = ['L1', 'L2A', 'L2B', 'L2C', 'L3'];
    }

    const counts = {};
    if (targetTiers.length === 1) {
        counts[targetTiers[0]] = total;
    } else {
        let assigned = 0;
        targetTiers.forEach((k) => {
            counts[k] = Math.max(1, Math.round(total * TIER_DEFS[k].share));
            assigned += counts[k];
        });
        while (assigned > total) {
            const k = targetTiers.reduce((a, b) => (counts[a] >= counts[b] ? a : b));
            counts[k]--;
            assigned--;
        }
        while (assigned < total) {
            const k = targetTiers.reduce((a, b) => (counts[a] <= counts[b] ? a : b));
            counts[k]++;
            assigned++;
        }
    }

    let plan = [];
    targetTiers.forEach((k) => {
        const pool = getPoolForTier(k, bank);
        const drawn = drawFromPoolWithAntiRepetition(pool, counts[k]);
        drawn.forEach((prompt) => {
            plan.push({ tier: k, labelObj: TIER_DEFS[k].label, prompt });
        });
    });

    plan = fisherYates(plan);

    const isMultiTier = targetTiers.length > 1;
    for (let i = 1; i < plan.length; i++) {
        const clash = (a, b) => a.prompt === b.prompt || (isMultiTier && a.tier === b.tier);
        if (clash(plan[i], plan[i - 1])) {
            for (let j = i + 1; j < plan.length; j++) {
                if (!clash(plan[j], plan[i - 1]) && (i + 1 >= plan.length || !clash(plan[j], plan[i + 1] || {}))) {
                    [plan[i], plan[j]] = [plan[j], plan[i]];
                    break;
                }
            }
        }
    }

    recordRecentStimuli(plan.map((p) => p.prompt));
    return plan;
}

// ---------------------------------------------------------------------------
// CANVAS & POINTER DYNAMICS TRACKER
// ---------------------------------------------------------------------------
const canvas = document.getElementById('drawCanvas');
const ctx = canvas.getContext('2d');
ctx.lineWidth = 4;
ctx.lineCap = 'round';

let isDrawing = false;
let promptStartTime = 0;
let latencyMs = 0;
let hasStartedWriting = false;
let strokeData = [];

function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    strokeData = [];
}

function normalizePressure(raw) {
    if (raw === undefined || raw === null || Number.isNaN(raw)) return 0.5;
    let p = Number(raw);
    if (p > 1.0) {
        // Guard against uncalibrated Android/Huawei drivers emitting values exceeding standard 1.0
        p = Math.min(1.0, p / 2.5);
    }
    return Math.min(1.0, Math.max(0.0, p));
}

function getDeviceMetadata() {
    return {
        user_agent: navigator.userAgent,
        platform: navigator.platform || 'unknown',
        screen_width: window.innerWidth,
        screen_height: window.innerHeight,
        device_pixel_ratio: window.devicePixelRatio || 1.0,
        max_touch_points: navigator.maxTouchPoints || 0
    };
}

function recordPoint(e, isTouching) {
    strokeData.push({
        time: e.timeStamp,
        x: e.offsetX,
        y: e.offsetY,
        pressure: e.pressure !== undefined ? e.pressure : 0.5,
        tiltX: e.tiltX || 0,
        tiltY: e.tiltY || 0,
        touching: isTouching
    });
}

function onFirstTouchLatency() {
    if (!hasStartedWriting) {
        if (promptStartTime === 0) {
            promptStartTime = Date.now() - 350;
        }
        latencyMs = Math.max(50, Date.now() - promptStartTime);
        hasStartedWriting = true;
        const text = `Latency: ${latencyMs} ms`;
        const freeEl = document.getElementById('latencyDisplay');
        const liveEl = document.getElementById('liveLatencyDisplay');
        if (freeEl) freeEl.innerText = text;
        if (liveEl) liveEl.innerText = text;
        const timingBtn = el('startOralTimingBtn');
        if (timingBtn) {
            timingBtn.disabled = true;
            timingBtn.innerText = COLLECTOR_TRANSLATIONS[currentLang].oralTimingStarted;
        }
    }
}

function computeLineWidth(pressure) {
    // Base 2.0px + 8.0px multiplier, hard-capped at 10.0px for firm pressure
    return Math.min(10.0, 2.0 + pressure * 8.0);
}

let lastX = 0;
let lastY = 0;

canvas.addEventListener('pointerdown', (e) => {
    onFirstTouchLatency();
    isDrawing = true;
    lastX = e.offsetX;
    lastY = e.offsetY;
    const p = normalizePressure(e.pressure);
    const initialWidth = computeLineWidth(p);
    ctx.lineWidth = initialWidth;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.strokeStyle = '#000000';
    ctx.beginPath();
    ctx.arc(lastX, lastY, Math.max(1.0, initialWidth / 2), 0, Math.PI * 2);
    ctx.fillStyle = '#000000';
    ctx.fill();
    recordPoint(e, 1);

    const pressEl = document.getElementById('livePressureDisplay');
    if (pressEl) pressEl.innerText = `Pressure: ${p.toFixed(2)}`;
});

canvas.addEventListener('pointermove', (e) => {
    if (isDrawing) {
        const p = normalizePressure(e.pressure);
        const currentWidth = computeLineWidth(p);

        ctx.beginPath();
        ctx.moveTo(lastX, lastY);
        ctx.lineTo(e.offsetX, e.offsetY);
        ctx.lineWidth = currentWidth;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.strokeStyle = '#000000';
        ctx.stroke();

        lastX = e.offsetX;
        lastY = e.offsetY;
        recordPoint(e, 1);

        const pressEl = document.getElementById('livePressureDisplay');
        if (pressEl) pressEl.innerText = `Pressure: ${p.toFixed(2)}`;
    }
});

canvas.addEventListener('pointerup', (e) => {
    if (isDrawing) {
        isDrawing = false;
        recordPoint(e, 0);
        const pressEl = document.getElementById('livePressureDisplay');
        if (pressEl) pressEl.innerText = 'Pressure: 0.00';
    }
});

canvas.addEventListener('pointerout', (e) => {
    if (isDrawing) {
        isDrawing = false;
        recordPoint(e, 0);
        const pressEl = document.getElementById('livePressureDisplay');
        if (pressEl) pressEl.innerText = 'Pressure: 0.00';
    }
});

// ---------------------------------------------------------------------------
// SERVER PAYLOAD & FILE CONVENTION
// ---------------------------------------------------------------------------
function sanitizeLabel(text) {
    return (text || 'UnknownSubj').replace(/[^a-zA-Z0-9]+/g, '_').replace(/^_+|_+$/g, '').substring(0, 40) || 'UnknownSubj';
}

function getExportImageDataUrl() {
    const exportCanvas = document.createElement('canvas');
    exportCanvas.width = canvas.width;
    exportCanvas.height = canvas.height;
    const expCtx = exportCanvas.getContext('2d');
    expCtx.fillStyle = '#ffffff';
    expCtx.fillRect(0, 0, exportCanvas.width, exportCanvas.height);
    expCtx.drawImage(canvas, 0, 0);
    return exportCanvas.toDataURL('image/png');
}

async function postSample({ dataset, mode, label, annotator, metadata }) {
    const timestamp = Date.now();
    const prefix = `${dataset}_${mode}_${sanitizeLabel(label)}_${annotator}_${timestamp}`;
    const payload = {
        mode: mode,
        prefix: prefix,
        strokes: strokeData.map((point) => ({ ...point, latency: latencyMs })),
        image: getExportImageDataUrl(),
        metadata: {
            ...metadata,
            latency_ms: latencyMs,
            dataset,
            mode,
            annotator,
            prompt: label,
            client_timestamp: timestamp,
            ui_language: currentLang,
            device: getDeviceMetadata()
        }
    };

    const response = await fetch('/save_data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    return response.json();
}

// ---------------------------------------------------------------------------
// FREE DATA COLLECTION
// ---------------------------------------------------------------------------
document.getElementById('startTimerBtn').addEventListener('click', () => {
    promptStartTime = Date.now();
    hasStartedWriting = false;
    document.getElementById('latencyDisplay').innerText = COLLECTOR_TRANSLATIONS[currentLang].latencyTimingDelay;
    clearCanvas();
});

document.getElementById('downloadBtn').addEventListener('click', async () => {
    const resultText = document.getElementById('resultText');

    if (strokeData.length === 0) {
        resultText.style.color = '#d97706';
        resultText.innerText = COLLECTOR_TRANSLATIONS[currentLang].alertNeedDrawing;
        return;
    }

    try {
        const result = await postSample({
            dataset: document.getElementById('datasetSelect').value,
            mode: document.getElementById('modeSelect').value,
            label: document.getElementById('labelInput').value || 'UnknownSubj',
            annotator: document.getElementById('annotatorInput').value || 'UnknownAnno',
            metadata: { collection_type: 'free', task_level: 'free', execution_mode: 'free' }
        });
        alert(result.message);
        clearCanvas();
    } catch (error) {
        alert(COLLECTOR_TRANSLATIONS[currentLang].alertSaveError);
    }
});

document.getElementById('clearBtn').addEventListener('click', clearCanvas);

// ---------------------------------------------------------------------------
// MODERATED GUIDED SESSION
// ---------------------------------------------------------------------------
const guidedState = {
    running: false,
    saving: false,
    plan: [],
    index: 0,
    sessionId: '',
    config: null,
    savedCount: 0,
    latencies: [],
    presentToken: 0
};

const el = (id) => document.getElementById(id);

function setPromptHeader(item) {
    const header = el('promptDisplayHeader');
    const oralCard = el('examinerOralCard');
    const spokenTarget = el('examinerSpokenTarget');
    const timingBtn = el('startOralTimingBtn');

    if (guidedState.config.execution === 'spoken_dictation') {
        header.innerText = COLLECTOR_TRANSLATIONS[currentLang].dictationInstruction;
        header.className = 'prompt-header prompt-header-masked';
        if (oralCard) oralCard.style.display = 'flex';
        if (spokenTarget) spokenTarget.innerText = item.prompt;
        if (timingBtn) {
            timingBtn.disabled = false;
            timingBtn.innerText = COLLECTOR_TRANSLATIONS[currentLang].btnStartOralTiming;
        }
    } else {
        header.innerText = item.prompt;
        header.className = 'prompt-header';
        if (oralCard) oralCard.style.display = 'none';
    }
}

function startOralLatencyTiming() {
    if (promptStartTime > 0 || hasStartedWriting) return;
    promptStartTime = Date.now();
    el('liveLatencyDisplay').innerText = COLLECTOR_TRANSLATIONS[currentLang].latencyMeasuring;
    const timingBtn = el('startOralTimingBtn');
    if (timingBtn) {
        timingBtn.disabled = true;
        timingBtn.innerText = COLLECTOR_TRANSLATIONS[currentLang].oralTimingStarted;
    }
}

function updateHud() {
    if (!guidedState.running || !guidedState.plan.length) return;
    const total = guidedState.plan.length;
    const item = guidedState.plan[guidedState.index];
    el('sessionProgressText').innerText = `Item ${guidedState.index + 1} of ${total}`;
    el('sessionLevelText').innerText = item.labelObj[currentLang] || item.labelObj.id;
    el('sessionProgressBar').style.width = `${(guidedState.index / total) * 100}%`;
}

function presentCurrentItem() {
    const item = guidedState.plan[guidedState.index];
    clearCanvas();
    latencyMs = 0;
    hasStartedWriting = false;
    promptStartTime = 0;
    el('liveLatencyDisplay').innerText = COLLECTOR_TRANSLATIONS[currentLang].latencyWaiting;
    setPromptHeader(item);

    if (guidedState.config.execution === 'visual_copying') {
        promptStartTime = Date.now();
        el('liveLatencyDisplay').innerText = COLLECTOR_TRANSLATIONS[currentLang].latencyMeasuring;
    }
}

function showGuidedUi(active) {
    el('sessionSetupCard').style.display = active ? 'none' : 'block';
    el('sessionHud').style.display = active ? 'block' : 'none';
    el('guidedControls').style.display = active ? 'flex' : 'none';
}

function startGuidedSession() {
    const annotator = el('modAnnotatorInput').value.trim();
    if (!annotator) {
        alert(COLLECTOR_TRANSLATIONS[currentLang].alertNeedAnnotator);
        return;
    }

    const total = parseInt(el('modSessionLength').value, 10);
    const tierFocus = el('modTierFocus') ? el('modTierFocus').value : 'all';
    guidedState.config = {
        annotator,
        dataset: el('modDatasetSelect').value,
        mode: el('modModeSelect').value,
        execution: el('modExecutionMode').value,
        tierFocus
    };
    guidedState.plan = generateSessionPlan(total, tierFocus);
    guidedState.index = 0;
    guidedState.savedCount = 0;
    guidedState.latencies = [];
    guidedState.sessionId = `sess_${Date.now()}`;
    guidedState.running = true;

    el('sessionSummaryCard').style.display = 'none';
    el('resultText').innerText = '';
    showGuidedUi(true);
    updateHud();
    presentCurrentItem();
}

function finishGuidedSession() {
    guidedState.running = false;
    guidedState.presentToken++;
    ttsEngine.cancel();
    clearCanvas();
    showGuidedUi(false);

    const lats = guidedState.latencies.filter((v) => v > 0);
    const avg = lats.length ? Math.round(lats.reduce((a, b) => a + b, 0) / lats.length) : 0;
    const card = el('sessionSummaryCard');
    const t = COLLECTOR_TRANSLATIONS[currentLang];
    card.style.display = 'block';
    card.innerHTML = `<strong>${t.summaryTitle}</strong><br>` +
        `${t.summarySaved} ${guidedState.savedCount} / ${guidedState.plan.length}<br>` +
        `${t.summaryAvgLatency} ${avg} ms<br>` +
        `${t.summarySessionId} ${guidedState.sessionId}`;
}

function advanceGuidedItem() {
    guidedState.index++;
    if (guidedState.index >= guidedState.plan.length) {
        el('sessionProgressBar').style.width = '100%';
        finishGuidedSession();
        return;
    }
    updateHud();
    presentCurrentItem();
}

async function saveAndNext() {
    if (!guidedState.running || guidedState.saving) return;
    if (strokeData.length === 0) {
        el('resultText').style.color = '#d97706';
        el('resultText').innerText = COLLECTOR_TRANSLATIONS[currentLang].alertNeedDrawing;
        return;
    }

    guidedState.saving = true;
    el('saveAndNextBtn').disabled = true;
    const item = guidedState.plan[guidedState.index];
    const cfg = guidedState.config;

    try {
        await postSample({
            dataset: cfg.dataset,
            mode: cfg.mode,
            label: item.prompt,
            annotator: cfg.annotator,
            metadata: {
                collection_type: 'moderated',
                language: 'id',
                task_tier: item.tier,
                task_level: item.labelObj.en,
                tier_focus: cfg.tierFocus || 'all',
                execution_mode: cfg.execution,
                session_id: guidedState.sessionId,
                item_index: guidedState.index + 1,
                total_items: guidedState.plan.length
            }
        });
        guidedState.savedCount++;
        guidedState.latencies.push(latencyMs);
        el('resultText').innerText = '';
        advanceGuidedItem();
    } catch (error) {
        el('resultText').style.color = '#dc2626';
        el('resultText').innerText = COLLECTOR_TRANSLATIONS[currentLang].alertSaveError;
    } finally {
        guidedState.saving = false;
        el('saveAndNextBtn').disabled = false;
    }
}

el('startSessionBtn').addEventListener('click', startGuidedSession);
el('saveAndNextBtn').addEventListener('click', saveAndNext);
el('guidedClearBtn').addEventListener('click', () => {
    if (guidedState.running) presentCurrentItem();
});
el('skipBtn').addEventListener('click', () => {
    if (guidedState.running && !guidedState.saving) advanceGuidedItem();
});
el('endSessionBtn').addEventListener('click', () => {
    if (guidedState.running) finishGuidedSession();
});

const startOralTimingBtn = el('startOralTimingBtn');
if (startOralTimingBtn) {
    startOralTimingBtn.addEventListener('click', startOralLatencyTiming);
}

el('replayAudioBtn').addEventListener('click', async () => {
    if (guidedState.running) {
        const item = guidedState.plan[guidedState.index];
        await ttsEngine.speak(item.prompt);
        if (promptStartTime === 0) {
            startOralLatencyTiming();
        }
    }
});

window.addEventListener('keydown', (e) => {
    if (e.code === 'Space' && guidedState.running && guidedState.config && guidedState.config.execution === 'spoken_dictation') {
        if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'SELECT' && e.target.tagName !== 'TEXTAREA') {
            e.preventDefault();
            startOralLatencyTiming();
        }
    }
});

// ---------------------------------------------------------------------------
// TAB SWITCHING
// ---------------------------------------------------------------------------
function switchTab(toGuided) {
    if (guidedState.running && !toGuided) {
        if (!confirm(COLLECTOR_TRANSLATIONS[currentLang].confirmSwitchTab)) return;
        finishGuidedSession();
    }
    el('tabGuided').classList.toggle('tab-active', toGuided);
    el('tabFree').classList.toggle('tab-active', !toGuided);
    el('guidedPanel').style.display = toGuided ? 'block' : 'none';
    el('freePanel').style.display = toGuided ? 'none' : 'block';
    el('freeControls').style.display = toGuided ? 'none' : 'flex';
    el('guidedControls').style.display = toGuided && guidedState.running ? 'flex' : 'none';
    clearCanvas();
    el('resultText').innerText = '';
}

el('tabGuided').addEventListener('click', () => switchTab(true));
el('tabFree').addEventListener('click', () => switchTab(false));

// Apply language on initial load
switchLanguage(currentLang);

// Restore saved tier focus preference and load stimulus bank
const savedTierFocus = localStorage.getItem('elkinematics_tier_focus');
const tierSelect = el('modTierFocus');
if (savedTierFocus && tierSelect) {
    tierSelect.value = savedTierFocus;
}
if (tierSelect) {
    tierSelect.addEventListener('change', (e) => {
        localStorage.setItem('elkinematics_tier_focus', e.target.value);
    });
}
loadStimulusBank();
