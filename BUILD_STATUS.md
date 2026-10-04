# Build Status

## Implemented and validated

- Modular FastAPI backend with typed Pydantic delivery contracts.
- Seeded RK4 ball physics with gravity, drag, swing, spin, seam, bounce and friction.
- Hidden physics ground truth separated from noisy observations and reconstructed track.
- Observation confidence, missing frames and outlier injection.
- Robust piecewise trajectory reconstruction and projection confidence.
- Simplified geometric bat/pad contact model.
- Dynamic synthetic audio per delivery with bat/pad/ground/bat-pad signatures.
- DSP pipeline: filtering, energy envelope, peak detection, spectral feature extraction and explainable transient classification.
- Contact evidence fusion with geometry, timing, audio, synchronization and tracking quality.
- Educational LBW module with ball-radius wicket overlap and uncertainty-sensitive simulated marginal review.
- Ten deterministic training/fault scenarios.
- REST API, delivery history, operator-review submission, session performance summary, calibration endpoint and WebSocket replay feed.
- React/TypeScript/React Three Fiber operator UI source with Operator, Edge Review, Broadcast and Developer modes.
- Synchronized delivery scrubber and waveform cursor.
- Six preset tracking camera views plus contact close-up behavior.
- JSON and WAV exports.
- Docker, GitHub Actions CI, Render config, Vercel SPA config and deployment docs.
- Interview guide and engineering documentation.
- Backend test suite: 13/13 passing in the build environment.

## Environment validation limitation

The build environment cannot resolve `registry.npmjs.org` (`EAI_AGAIN`). Because frontend dependencies cannot be downloaded here, the React production build and ESLint job could not be executed locally. GitHub Actions is configured to run both once the repository is pushed to an environment with npm network access.

## Not yet equivalent to the full aspirational master specification

The current repository is a strong deployable portfolio baseline, but it deliberately does **not** claim every aspirational item is complete. Further phases can add:

- real uploaded-video computer-vision tracking;
- real synchronized uploaded audio/video review;
- spectrogram/combined display;
- persistent database-backed match/session storage;
- richer match scoreboard/over history UI;
- dedicated front-foot/no-ball review screen;
- full calibration workstation with camera transforms and residual plots;
- advanced covariance/Kalman or physics-state estimation;
- measured frontend/render latency diagnostics;
- Playwright browser tests and visual regression;
- richer batter/bat animation and high-fidelity stadium/broadcast assets.

This status is intentionally explicit so the project does not present unfinished capability as implemented functionality.

## One-terminal launcher update

The repository now includes `start.py`, `START_SIMULATOR.bat`, `SETUP_PROJECT.bat`, a root `package.json`, and `QUICK_START.md`.

Normal local startup is now:

```powershell
python start.py
```

The launcher manages `.venv`, Python requirements, frontend npm dependencies, FastAPI, Vite, browser launch, and joint shutdown from one terminal. Separate backend/frontend terminals are no longer required.
