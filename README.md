# Cricket Decision Review Simulator

An independent educational simulation of cricket ball-tracking, synchronized audio/contact review, trajectory projection, LBW logic, replay workflow, and broadcast presentation.

> This application is an independent educational simulation of cricket ball-tracking and edge-detection review workflows. It is not affiliated with, endorsed by, or a reproduction of Hawk-Eye, UltraEdge, RTS, ICC, or any commercial decision-review provider.

## Why this project exists

The project is designed as a portfolio-grade systems/operator simulator rather than an LBW animation. It demonstrates how a delivery can move through a structured pipeline: numerical physics → simulated tracking observations → trajectory reconstruction → bat/pad geometry → audio synthesis and signal analysis → synchronized review → wicket projection → educational LBW decision logic → operator/broadcast presentation.

## Features

- Seeded 3D delivery physics using RK4 integration with gravity, aerodynamic drag, swing, spin, seam deviation, bounce restitution and pitch friction.
- Separate hidden ground truth, noisy observations and reconstructed trajectory.
- Multi-camera-style observations with confidence, dropouts and outliers.
- Robust piecewise trajectory fitting and projection confidence metrics.
- Bat and pad collision volumes with bat-face/edge classification.
- Dynamic synthetic delivery audio with event-specific transient signatures.
- Band-pass filtering, energy envelope, peak extraction and explainable transient features.
- Synchronized waveform and frame scrubber.
- Contact evidence fusion using geometry, signal evidence, timing, sync quality and tracking confidence.
- Separate educational LBW rules module with pitching, impact, wicket intersection and a configurable uncertainty band.
- Operator, Edge Review, Broadcast and Developer modes.
- Ten training scenarios including faint edge, bat-pad false positive, ground spike, outside-leg, tracking dropout and audio-sync failure.
- Structured event log, deterministic regression-friendly simulation, API export and WebSocket playback feed.
- FastAPI backend, React + TypeScript + React Three Fiber frontend, Docker and GitHub Actions.

## Architecture

```text
Delivery parameters
      ↓
Physics ground truth
      ↓
Tracking observation generator
      ↓
Robust trajectory reconstruction
      ↓
Bat / pad interaction geometry
      ↓
Synthetic audio generator
      ↓
Signal processing + transient candidates
      ↓
Contact evidence fusion
      ↓
Trajectory projection + wicket intersection
      ↓
Educational LBW rules engine
      ↓
Operator state / replay / broadcast UI
```

The decision layer does not read the hidden ground truth trajectory directly. Ground truth is available only for developer/debug comparison.

## Repository layout

```text
backend/
  api/                 FastAPI routes and WebSocket stream
  audio/               synthetic audio + DSP pipeline
  config/              central geometry/physics/tracking constants
  decision_engine/     contact fusion + LBW rules
  interaction/         bat/pad/ground collision model
  models/              typed Pydantic schemas
  physics/             RK4 ball-flight and bounce model
  services/            scenario library + orchestration/store
  tracking/            noisy observation generation
  trajectory/          reconstruction + projection
frontend/
  src/components/      telemetry, event log, waveform, broadcast overlay
  src/scene/           interactive 3D cricket scene
  src/types/           API types
  src/utils/           API client
tests/                 deterministic backend regression tests
docs/                  engineering and deployment notes
```

## One-terminal local development

You do **not** need separate terminals for FastAPI and React. The repository includes a one-command launcher.

### Requirements

Install these once on the computer:

- Python 3.11+
- Node.js LTS (includes npm)

### Start the complete simulator

Open the repository root in VS Code, open one terminal, and run:

```powershell
python start.py
```

The launcher automatically creates/uses `.venv`, installs missing Python and frontend dependencies, starts the FastAPI backend and Vite frontend together, waits for both services, and opens the browser. No manual virtual-environment activation is required.

After startup:

- Simulator: `http://localhost:5173`
- API documentation: `http://localhost:8000/docs`

Press `Ctrl+C` once to stop both services.

Windows users can alternatively double-click `START_SIMULATOR.bat`. See `QUICK_START.md` for troubleshooting.

### Optional commands

```powershell
python start.py --setup-only
python start.py --no-browser
npm run dev
```

`npm run dev` delegates to the same Python launcher; it does not require a second terminal.

## Docker

```bash
docker compose up --build
```

Frontend: `http://localhost:5173`  
Backend: `http://localhost:8000`

## API highlights

- `GET /scenarios`
- `POST /deliveries/generate`
- `GET /deliveries/{id}`
- `GET /deliveries/{id}/tracking`
- `GET /deliveries/{id}/edge-analysis`
- `GET /deliveries/{id}/lbw-analysis`
- `GET /deliveries/{id}/export.json`
- `GET /deliveries/{id}/audio.wav`
- `WS /ws/deliveries/{id}`
- `GET /system/status`

## Tests

```bash
PYTHONPATH=. pytest -q
```

The suite covers reproducibility, edge/contact behavior, false positives, tracking degradation, sync failure, outside-leg LBW handling, simulated marginal review, and Pydantic input validation.

## Training scenarios

| ID | Scenario | Main purpose |
|---|---|---|
| `EDGE_CLEAR_001` | Clear outside edge | Contact geometry + synchronized high-frequency transient |
| `BAT_PAD_001` | Bat hits pad | False-positive rejection |
| `FAINT_EDGE_001` | Faint edge onto pad | Double-event separation |
| `GROUND_SPIKE_001` | Ground spike | Reject nearby non-ball transient |
| `LBW_HITTING_001` | Straightforward LBW | Tracking / projection / wicket intersection |
| `LBW_MARGIN_001` | Marginal projection | Educational uncertainty threshold |
| `OUTSIDE_LEG_001` | Outside leg | Pitching rule |
| `TRACKING_GAP_001` | Tracking dropout | Quality degradation and warnings |
| `SYNC_ERROR_001` | Audio sync error | Synchronization diagnosis |
| `MULTI_TRANSIENT_001` | Multiple transients | Candidate discrimination |

## Portfolio positioning

Recommended description:

> Developed an independent cricket decision-review technology simulator combining 3D ball tracking, noisy observation reconstruction, trajectory projection, synchronized audio analysis, transient/contact detection, replay workflows, LBW decision logic and broadcast visualization.

Do not describe this project as a reproduction of any commercial DRS product.

## Limitations

This simulator uses synthetic data and deliberately simplified physics, calibration, camera, microphone and uncertainty models. It is for learning, demonstrations and operator-workflow discussion only. It is not suitable for officiating decisions, certification or claims of equivalence to professional sports-technology systems. See `docs/LIMITATIONS.md`.
