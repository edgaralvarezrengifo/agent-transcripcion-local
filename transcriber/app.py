from fastapi import FastAPI, UploadFile, File
import subprocess, os, uuid
from faster_whisper import WhisperModel

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Cargar modelo Whisper
model_size = os.environ.get("MODEL", "base")
print(f"Loading Whisper model: {model_size}")
model = WhisperModel(model_size, device="cpu")  # usa "cuda" si tienes GPU

app = FastAPI(title="Transcriber API", description="Transcripción de audio/video usando Whisper")

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...), language: str = None):
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    input_path = os.path.join(UPLOAD_DIR, filename)

    # Guardar archivo temporal
    with open(input_path, "wb") as f:
        f.write(await file.read())

    # Convertir a WAV mono 16kHz
    audio_path = input_path + ".wav"
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-ac", "1", "-ar", "16000", audio_path
    ]
    subprocess.run(cmd, check=True)

    # Transcribir
    segments, info = model.transcribe(audio_path, language=language)
    text = " ".join([segment.text for segment in segments])

    # Respuesta
    return {
        "filename": file.filename,
        "language": info.language,
        "duration": info.duration,
        "transcript": text,
    }