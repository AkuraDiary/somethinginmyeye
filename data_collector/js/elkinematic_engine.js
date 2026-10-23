/**
 * Elkinematics Kinematic Inference Engine (Client-Side & Hybrid Server).
 * 
 * Provides standalone handwriting kinematics feature extraction, temporal resampling (60 Hz),
 * z-score standardization, and direct browser-native inference using ONNX Runtime Web.
 * 
 * Complies with the 8 standard kinematic features contract:
 * [delta_x, delta_y, pressure, tiltX, tiltY, velocity, acceleration, jerk],
 * with secondary scalar latency (Sumner et al., 2013; Brescia et al., 2026).
 * 
 * Theoretical Framework & Architectural Citations:
 * - V2 Bidirectional LSTM Kinematic Architecture (Asselborn et al., 2018; Danna et al., 2023)
 * - 60 Hz In-Memory Hardware-Agnostic Temporal Resampling
 * - Precomputed Scaler Standardization (models/feature_scalers.npz / feature_scalers.json)
 */

(function (global) {
    'use strict';

    // Built-in precomputed scaler values synchronized with models/feature_scalers.json
    const DEFAULT_SCALER = {
        feature_names: [
            "delta_x", "delta_y", "pressure", "tiltX", "tiltY",
            "velocity", "acceleration", "jerk"
        ],
        means: [
            0.1781700900371392,
            0.1660135680083527,
            0.10151600463897975,
            2.4273620623415026,
            1.355142610117506,
            0.07463612708145165,
            3.892847328019602e-05,
            -2.2752280615728288e-06
        ],
        stds: [
            4.183146163825784,
            5.988303641328324,
            0.22525478868930518,
            7.896276600645911,
            5.922492948780155,
            0.21118844601744835,
            0.004647821916123836,
            0.0006626971364633859
        ],
        max_timesteps: 500,
        features_dim: 8
    };

    let activeScaler = { ...DEFAULT_SCALER };
    let ortSession = null;
    let isInitializing = false;
    let backendPreference = 'server_keras'; // 'server_keras' | 'server_onnx' | 'client_onnx'

    /**
     * Resamples stroke points onto a uniform 60 Hz temporal grid (dt = 16.67 ms).
     * Mirrors scripts/universal_pipeline.py:resample_stroke_trajectory.
     */
    function resampleStrokeTrajectory(rawPoints, targetHz = 60.0) {
        if (!rawPoints || rawPoints.length < 2) {
            return rawPoints ? [...rawPoints] : [];
        }

        const targetDtMs = 1000.0 / targetHz;

        // Clean, sanitize, and partition points into continuous strokes
        const cleaned = rawPoints.map(p => {
            let pressure = p.pressure !== undefined ? Number(p.pressure) : 0.5;
            if (pressure > 1.0) pressure = Math.min(1.0, pressure / 2.5);
            pressure = Math.max(0.0, Math.min(1.0, pressure));

            return {
                time: Number(p.time || 0),
                x: Number(p.x || 0),
                y: Number(p.y || 0),
                pressure: pressure,
                tiltX: Number(p.tiltX || 0),
                tiltY: Number(p.tiltY || 0),
                touching: p.touching !== undefined ? Boolean(p.touching) : true,
                latency: Number(p.latency || 0)
            };
        });

        // Split into stroke clusters when pen lifts or time gap > 200 ms
        const strokes = [];
        let currentStroke = [];

        for (let i = 0; i < cleaned.length; i++) {
            const pt = cleaned[i];
            const dtRaw = i > 0 ? (pt.time - cleaned[i - 1].time) : 0;
            const isBreak = !pt.touching || dtRaw > 200.0;

            if (isBreak && currentStroke.length > 0) {
                strokes.push(currentStroke);
                currentStroke = [];
            }
            currentStroke.push(pt);
        }
        if (currentStroke.length > 0) {
            strokes.push(currentStroke);
        }

        const resampled = [];

        for (const stroke of strokes) {
            const sLen = stroke.length;
            if (sLen === 0) continue;

            const t0 = stroke[0].time;
            const tEnd = stroke[sLen - 1].time;
            const duration = tEnd - t0;

            if (duration < targetDtMs || sLen < 2) {
                for (const pt of stroke) {
                    resampled.push({ ...pt });
                }
                continue;
            }

            // Linear interpolation helper
            const strokeTimes = stroke.map(p => p.time);
            const interp = (t, key) => {
                if (t <= strokeTimes[0]) return stroke[0][key];
                if (t >= strokeTimes[sLen - 1]) return stroke[sLen - 1][key];
                // Find bounding interval
                let idx = 0;
                while (idx < sLen - 1 && strokeTimes[idx + 1] < t) idx++;
                const tA = strokeTimes[idx];
                const tB = strokeTimes[idx + 1];
                const span = tB - tA;
                if (span <= 1e-6) return stroke[idx][key];
                const frac = (t - tA) / span;
                return stroke[idx][key] + frac * (stroke[idx + 1][key] - stroke[idx][key]);
            };

            for (let t = t0; t <= tEnd; t += targetDtMs) {
                resampled.push({
                    time: t,
                    x: interp(t, 'x'),
                    y: interp(t, 'y'),
                    pressure: interp(t, 'pressure'),
                    tiltX: interp(t, 'tiltX'),
                    tiltY: interp(t, 'tiltY'),
                    touching: true,
                    latency: stroke[0].latency
                });
            }
        }

        return resampled.length > 0 ? resampled : cleaned;
    }

    /**
     * Extracts the 8 standard kinematic features from trajectory points.
     * [delta_x, delta_y, pressure, tiltX, tiltY, velocity, acceleration, jerk]
     * Mirrors scripts/universal_pipeline.py:extract_universal_features.
     */
    function extractKinematicFeatures(points, resample = true) {
        const pts = resample ? resampleStrokeTrajectory(points) : points;
        const n = pts.length;
        const features = [];

        let prevVelocity = 0.0;
        let prevAccel = 0.0;

        for (let i = 0; i < n; i++) {
            const curr = pts[i];
            const prev = i > 0 ? pts[i - 1] : curr;

            let dt = i > 0 ? (curr.time - prev.time) : 1.0;
            if (dt <= 0.0) dt = 1.0;

            const delta_x = i > 0 ? (curr.x - prev.x) : 0.0;
            const delta_y = i > 0 ? (curr.y - prev.y) : 0.0;
            const dist = Math.hypot(delta_x, delta_y);
            const velocity = dist / dt;

            const accel = i > 0 ? ((velocity - prevVelocity) / dt) : 0.0;
            const jerk = i > 0 ? ((accel - prevAccel) / dt) : 0.0;

            prevVelocity = velocity;
            prevAccel = accel;

            features.push([
                delta_x,
                delta_y,
                curr.pressure !== undefined ? curr.pressure : 0.5,
                curr.tiltX !== undefined ? curr.tiltX : 0.0,
                curr.tiltY !== undefined ? curr.tiltY : 0.0,
                velocity,
                accel,
                jerk
            ]);
        }

        return features;
    }

    /**
     * Prepares normalized tensors for model input.
     * Sequence padding to MAX_TIMESTEPS (500) and z-score scaling.
     */
    function prepareModelInputs(rawPoints, latencyMs = 0.0) {
        const rawFeatures = extractKinematicFeatures(rawPoints, true);
        const maxT = activeScaler.max_timesteps;
        const dim = activeScaler.features_dim;
        const means = activeScaler.means;
        const stds = activeScaler.stds;

        const seqLen = rawFeatures.length;
        const flatTensor = new Float32Array(maxT * dim);

        // 1. Scaled active timesteps
        const copyLen = Math.min(seqLen, maxT);
        for (let t = 0; t < copyLen; t++) {
            for (let f = 0; f < dim; f++) {
                const rawVal = rawFeatures[t][f];
                const safeVal = isNaN(rawVal) || !isFinite(rawVal) ? 0.0 : rawVal;
                flatTensor[t * dim + f] = (safeVal - means[f]) / stds[f];
            }
        }

        // 2. Scaled zero-padding timesteps (0.0 scaled through z-score)
        for (let t = copyLen; t < maxT; t++) {
            for (let f = 0; f < dim; f++) {
                flatTensor[t * dim + f] = (0.0 - means[f]) / stds[f];
            }
        }

        // 3. Scaled latency scalar (seconds)
        const latencySec = (Number(latencyMs) || 0.0) / 1000.0;
        const latencyTensor = new Float32Array([latencySec]);

        return {
            kinematicsBuffer: flatTensor,
            latencyBuffer: latencyTensor,
            sequenceLength: seqLen
        };
    }

    /**
     * Loads the ONNX Runtime Web session for elkinematicV2.onnx.
     */
    async function initModel(modelPath = 'models/elkinematicV2.onnx') {
        if (ortSession) return ortSession;
        if (isInitializing) {
            while (isInitializing) {
                await new Promise(resolve => setTimeout(resolve, 50));
            }
            return ortSession;
        }

        if (typeof ort === 'undefined') {
            console.warn('ONNX Runtime Web (ort) is not loaded in this environment.');
            return null;
        }

        isInitializing = true;
        try {
            // Attempt to load external scaler JSON if available
            try {
                const res = await fetch('models/feature_scalers.json');
                if (res.ok) {
                    const scalerData = await res.json();
                    if (scalerData.means && scalerData.stds) {
                        activeScaler = { ...DEFAULT_SCALER, ...scalerData };
                        console.log('ElkinematicEngine: Loaded external scaler configuration.');
                    }
                }
            } catch (e) {
                console.log('ElkinematicEngine: Using built-in precomputed scaler configuration.');
            }

            ortSession = await ort.InferenceSession.create(modelPath, {
                executionProviders: ['wasm']
            });
            console.log('ElkinematicEngine: ONNX model initialized successfully from:', modelPath);
        } catch (err) {
            console.error('ElkinematicEngine: Failed to load ONNX model:', err);
            ortSession = null;
        } finally {
            isInitializing = false;
        }

        return ortSession;
    }

    /**
     * Executes direct client-side ONNX inference.
     */
    async function predictDirect(rawPoints, latencyMs = 0.0) {
        if (!ortSession) {
            await initModel();
        }
        if (!ortSession) {
            throw new Error('ONNX Runtime session is not initialized.');
        }

        const { kinematicsBuffer, latencyBuffer } = prepareModelInputs(rawPoints, latencyMs);

        const kinematicsTensor = new ort.Tensor('float32', kinematicsBuffer, [1, activeScaler.max_timesteps, activeScaler.features_dim]);
        const latencyTensor = new ort.Tensor('float32', latencyBuffer, [1, 1]);

        const feeds = {
            kinematics_input: kinematicsTensor,
            latency_input: latencyTensor
        };

        const results = await ortSession.run(feeds);
        const outputTensor = results.heatmap_output;
        if (!outputTensor) {
            throw new Error('Missing heatmap_output in ONNX inference result.');
        }

        const heatmap = Array.from(outputTensor.data);
        const globalScore = heatmap.reduce((sum, v) => sum + v, 0) / heatmap.length;
        const dysgraphiaRiskPercentage = globalScore * 100.0;

        return {
            backend_used: 'client_onnx',
            engine_type: 'Client ONNX Runtime Web (WASM)',
            kinematic_score: globalScore,
            dysgraphia_risk_percentage: Number(dysgraphiaRiskPercentage.toFixed(1)),
            dyslexia_risk_percentage: 0.0,
            is_dysgraphic: Boolean(dysgraphiaRiskPercentage >= 50.0),
            is_dyslexic: false,
            probability: globalScore,
            heatmap: heatmap,
            stream_breakdown: {
                kinematic_score: Number(globalScore.toFixed(4)),
                orthographic_error_score: 0.0,
                levenshtein_normalized: 0.0,
                raw_edit_distance: 0,
                reversal_flag: 0.0,
                latency_risk_score: 0.0
            },
            dyslexia_flags: {
                orthographic_error: 0.0,
                raw_edit_distance: 0,
                reversal_flag: 0.0,
                reversal_detected: false,
                latency_risk: 0.0,
                latency_exceeds_threshold: false,
                is_dyslexic: false
            }
        };
    }

    /**
     * Executes server-side inference via /analyze.
     */
    async function predictServer(payload, requestedBackend) {
        const backend = requestedBackend || (backendPreference === 'server_onnx' ? 'onnx' : 'keras');
        const reqPayload = { ...payload, backend: backend };

        const res = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(reqPayload)
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({ error: 'Server error' }));
            throw new Error(err.error || `HTTP Error ${res.status}`);
        }

        return await res.json();
    }

    /**
     * Unified evaluation dispatcher respecting the active backend preference.
     * Supports 'client_onnx', 'server_onnx', and 'server_keras'.
     */
    async function evaluate(options = {}) {
        const mode = options.mode || backendPreference;
        const strokes = options.strokes || [];
        const prompt = options.prompt || 'bebek';
        const decodedText = options.decoded_text || null;
        const latency = options.latency || 0.0;

        if (mode === 'client_onnx') {
            // Direct browser inference for kinematic motoric stream
            const directKinematics = await predictDirect(strokes, latency);

            // Fetch orthographic and SLD differential integration from server
            // with precomputed kinematic score or pure backend pass-through
            try {
                const serverResult = await predictServer({
                    strokes: strokes,
                    prompt: prompt,
                    decoded_text: decodedText,
                    latency: latency,
                    backend: 'onnx'
                }, 'onnx');

                // Overwrite with locally executed kinematic score and heatmap
                serverResult.backend_used = 'client_onnx';
                serverResult.engine_type = 'Client ONNX Runtime Web (WASM)';
                serverResult.dysgraphia_risk_percentage = directKinematics.dysgraphia_risk_percentage;
                serverResult.probability = directKinematics.probability;
                serverResult.heatmap = directKinematics.heatmap;
                if (serverResult.stream_breakdown) {
                    serverResult.stream_breakdown.kinematic_score = Number(directKinematics.kinematic_score.toFixed(4));
                }
                serverResult.is_dysgraphic = Boolean(directKinematics.dysgraphia_risk_percentage >= 50.0);

                return serverResult;
            } catch (err) {
                // If server is offline, return pure kinematic client inference
                return directKinematics;
            }
        }

        // Server-side execution (either Keras or ONNX)
        const serverBackend = mode === 'server_onnx' ? 'onnx' : 'keras';
        return await predictServer({
            strokes: strokes,
            prompt: prompt,
            decoded_text: decodedText,
            latency: latency,
            backend: serverBackend
        }, serverBackend);
    }

    /**
     * Queries server for active backend and capabilities.
     */
    async function fetchServerBackend() {
        try {
            const res = await fetch('/backend');
            if (res.ok) return await res.json();
        } catch (e) {
            console.warn('ElkinematicEngine: Could not query /backend:', e);
        }
        return null;
    }

    /**
     * Toggles server active default backend.
     */
    async function setServerBackend(backend) {
        try {
            const res = await fetch('/backend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ backend: backend })
            });
            if (res.ok) return await res.json();
        } catch (e) {
            console.warn('ElkinematicEngine: Could not set server backend:', e);
        }
        return null;
    }

    // Public API
    const ElkinematicEngine = {
        init: initModel,
        isReady: () => ortSession !== null,
        resampleTrajectory: resampleStrokeTrajectory,
        extractFeatures: extractKinematicFeatures,
        prepareInputs: prepareModelInputs,
        predictDirect: predictDirect,
        predictServer: predictServer,
        evaluate: evaluate,
        getScaler: () => ({ ...activeScaler }),
        setBackendPreference: (mode) => {
            if (['client_onnx', 'server_onnx', 'server_keras'].includes(mode)) {
                backendPreference = mode;
                console.log('ElkinematicEngine: Backend preference set to:', mode);
            }
        },
        getBackendPreference: () => backendPreference,
        fetchServerBackend: fetchServerBackend,
        setServerBackend: setServerBackend
    };

    // Expose to window or module exports
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = ElkinematicEngine;
    }
    if (typeof global !== 'undefined') {
        global.ElkinematicEngine = ElkinematicEngine;
    }

})(typeof window !== 'undefined' ? window : this);
