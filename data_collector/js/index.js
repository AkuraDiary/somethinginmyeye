/**
 * Kinematic Handwriting Data Collector & Diagnostic Client
 */

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

document.getElementById('startTimerBtn').addEventListener('click', () => {
    promptStartTime = Date.now();
    hasStartedWriting = false;
    document.getElementById('latencyDisplay').innerText = "Latency: Timing cognitive delay...";
    clearCanvas();
});

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

// Canvas Drawing Listeners
canvas.addEventListener('pointerdown', (e) => {
    if (promptStartTime > 0 && !hasStartedWriting) {
        latencyMs = Date.now() - promptStartTime;
        hasStartedWriting = true;
        document.getElementById('latencyDisplay').innerText = `Latency: ${latencyMs} ms`;
    }

    isDrawing = true;
    ctx.beginPath();
    ctx.moveTo(e.offsetX, e.offsetY);
    recordPoint(e, 1);
});

canvas.addEventListener('pointermove', (e) => {
    if (isDrawing) {
        ctx.lineWidth = Math.max((e.pressure || 0.5) * 5, 2.5);
        ctx.lineTo(e.offsetX, e.offsetY);
        ctx.stroke();
        recordPoint(e, 1);
    }
});

canvas.addEventListener('pointerup', (e) => {
    if (isDrawing) {
        isDrawing = false;
        recordPoint(e, 0);
    }
});

canvas.addEventListener('pointerout', (e) => {
    if (isDrawing) {
        isDrawing = false;
        recordPoint(e, 0);
    }
});

// Controls & Server Transmission
document.getElementById('downloadBtn').addEventListener('click', async () => {
    const resultText = document.getElementById('resultText');

    if (strokeData.length === 0) {
        resultText.style.color = "orange";
        resultText.innerText = "Please draw something on the canvas first.";
        return;
    }

    const dataset = document.getElementById('datasetSelect').value;
    const mode = document.getElementById('modeSelect').value;
    const label = document.getElementById('labelInput').value || 'UnknownSubj';
    const annotator = document.getElementById('annotatorInput').value || 'UnknownAnno';
    const timestamp = Date.now();

    const prefix = `${dataset}_${mode}_${label}_${annotator}_${timestamp}`;
    const imageBase64 = canvas.toDataURL("image/png");
    const strokesWithLatency = strokeData.map(point => ({
        ...point,
        latency: latencyMs
    }));

    const payload = {
        mode: mode,
        prefix: prefix,
        strokes: strokesWithLatency,
        image: imageBase64
    };

    try {
        const response = await fetch('/save_data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        alert(result.message);
        clearCanvas();

    } catch (error) {
        alert("Error saving data to server.");
    }
});

document.getElementById('clearBtn').addEventListener('click', clearCanvas);

// Optional Model Inference Listener
const analyzeBtn = document.getElementById('analyzeBtn');
if (analyzeBtn) {
    analyzeBtn.addEventListener('click', async () => {
        const resultText = document.getElementById('resultText');

        if (strokeData.length === 0) {
            resultText.style.color = "orange";
            resultText.innerText = "Please draw something on the canvas first.";
            return;
        }

        resultText.style.color = "black";
        resultText.innerText = "Analyzing kinematics...";

        try {
            const strokesWithLatency = strokeData.map(point => ({
                time: point.time,
                x: point.x,
                y: point.y,
                pressure: point.pressure,
                touching: point.touching,
                latency: latencyMs
            }));

            const response = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(strokesWithLatency)
            });

            const result = await response.json();
            const confidence = (result.probability * 100).toFixed(1);

            if (result.heatmap && result.heatmap.length > 0) {
                result.heatmap.forEach((prob, index) => {
                    if (index < strokeData.length && prob > 0.80) {
                        const point = strokeData[index];
                        ctx.beginPath();
                        ctx.arc(point.x, point.y, 8, 0, 2 * Math.PI);
                        ctx.fillStyle = "rgba(255, 0, 0, 0.1)";
                        ctx.fill();
                    }
                });
            }

            if (result.is_dyslexic || result.is_dysgraphic) {
                resultText.style.color = "red";
                resultText.innerText = `Atypical Pattern Detected (${confidence}% confidence)`;
            } else {
                resultText.style.color = "green";
                resultText.innerText = `Typical Pattern (${(100 - confidence).toFixed(1)}% confidence)`;
            }
        } catch (error) {
            resultText.style.color = "red";
            resultText.innerText = "Error connecting to AI server.";
        }
    });
}
