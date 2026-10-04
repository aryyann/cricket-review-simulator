# Quick Start — One Terminal

This project is configured so you do **not** need separate backend and frontend terminals.

## First run

Requirements installed on the computer:

- Python 3.11 or newer
- Node.js LTS (includes npm)

Open the project folder in VS Code, open **one terminal** in the project root, and run:

```powershell
python start.py
```

On the first run the launcher automatically:

1. creates `.venv` if it does not exist;
2. installs Python packages from `requirements.txt` when needed;
3. installs frontend npm packages when `frontend/node_modules` is missing;
4. starts the FastAPI backend on port 8000;
5. starts the Vite/React frontend on port 5173;
6. waits for both services to become ready;
7. opens the simulator in the default browser.

After setup, the same command starts the simulator:

```powershell
python start.py
```

Stop **both** services with:

```text
Ctrl+C
```

## Windows shortcut

You can also double-click:

```text
START_SIMULATOR.bat
```

For setup only:

```text
SETUP_PROJECT.bat
```

## Alternative npm command

If you prefer, from the root folder:

```powershell
npm run dev
```

This simply calls the same `start.py` launcher.

## URLs

- Simulator: `http://localhost:5173`
- FastAPI documentation: `http://localhost:8000/docs`

## Common errors

### `npm` or `node` is not recognized

Install the current Node.js LTS release, completely close VS Code, reopen it, then run:

```powershell
node --version
npm --version
```

Both commands must return version numbers.

### Port 5173 or 8000 already in use

A previous simulator process may still be running. Close it, or use:

```powershell
python start.py --frontend-port 5174 --backend-port 8001
```

### Do I activate `.venv` manually?

No. The launcher uses the virtual environment directly.

## Windows one-terminal startup

Open the project folder in VS Code and run:

```powershell
py -3.11 start.py
```

You may also double-click `START_SIMULATOR.bat`. The launcher now safely handles Node.js installations under `C:\Program Files\nodejs` and automatically prefers Python 3.11 on Windows when an older Python is the default.

When startup succeeds, the simulator opens at `http://localhost:5173`. Press `Ctrl+C` once to stop both frontend and backend.
