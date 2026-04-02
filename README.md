# Bird Sound Recognition System

Upload or record bird sounds in the browser and identify the bird species via a FastAPI + PyTorch endpoint.

## Local run (no Docker)

1. Start the backend

```bash
cd bird-sound-recognition
python -m venv .venv
# Activate venv:
# Windows (PowerShell): .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# librosa/audioread may require ffmpeg installed on your OS.
# If audio decoding fails, install `ffmpeg` and retry.
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

2. Start the frontend

```bash
cd bird-sound-recognition/frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Docker (recommended)

```bash
cd bird-sound-recognition
docker-compose up --build
```

Open `http://localhost:3000`.

## Training the Model

To train the model with real data:

1. Prepare your dataset:
   - Collect bird sound recordings (WAV/MP3 format)
   - Organize in folders by species: `data/train/sparrow/`, `data/train/robin/`, etc.
   - Each species folder should contain audio files for that bird

2. Install training dependencies:
```bash
pip install scikit-learn tqdm
```

3. Run training:
```bash
python train.py
```

The trained model will be saved to `backend/model/model.pt`.

## Testing

Run the test suite:
```bash
python test.py
```

## Notes

- The first time the backend starts, it will create a lightweight placeholder `model.pt` if none exists.
- Image assets are shipped as text-only SVG placeholders. The API returns `.jpg` URLs as specified, and the backend dynamically serves the matching SVG.

