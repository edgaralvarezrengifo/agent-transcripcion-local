import os
import shutil
import subprocess
import threading
import time
import uuid
from typing import Optional

from fastapi import FastAPI, File, UploadFile
from faster_whisper import WhisperModel

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Cargar modelo Whisper
model_size = os.environ.get("MODEL", "base")
device = os.environ.get("DEVICE", "cuda")
compute_type = os.environ.get(
    "COMPUTE_TYPE",
    "float16" if device == "cuda" else "int8",
)
num_workers = int(os.environ.get("MODEL_NUM_WORKERS", "2"))
max_concurrent = int(os.environ.get("TRANSCRIBE_MAX_CONCURRENCY", "2"))

print(
    f"Loading Whisper model: model={model_size} device={device} "
    f"compute_type={compute_type} model_workers={num_workers} "
    f"max_concurrent_requests={max_concurrent}"
)

try:
    model = WhisperModel(
        model_size,
        device=device,
        compute_type=compute_type,
        num_workers=num_workers,
    )
except Exception as exc:
    # Fallback keeps service alive if CUDA isn't available.
    print(f"Whisper init failed on '{device}' ({exc}), falling back to CPU/int8")
    model = WhisperModel(model_size, device="cpu", compute_type="int8", num_workers=1)

transcribe_semaphore = threading.BoundedSemaphore(max_concurrent)

app = FastAPI(title="Transcriber API", description="Transcripción de audio/video usando Whisper")


@app.post("/transcribe")
def transcribe(file: UploadFile = File(...), language: Optional[str] = None):
    start_total = time.perf_counter()
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    input_path = os.path.join(UPLOAD_DIR, filename)
    audio_path = input_path + ".wav"

    try:
        # Guardar archivo temporal
        start_save = time.perf_counter()
        with open(input_path, "wb") as dst:
            shutil.copyfileobj(file.file, dst)
        save_seconds = time.perf_counter() - start_save

        # Convertir a WAV mono 16kHz
        start_ffmpeg = time.perf_counter()
        cmd = [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-i",
            input_path,
            "-ac",
            "1",
            "-ar",
            "16000",
            audio_path,
        ]
        subprocess.run(cmd, check=True)
        ffmpeg_seconds = time.perf_counter() - start_ffmpeg

        # Transcribir (limitado para evitar sobrecargar GPU/CPU)
        start_transcribe = time.perf_counter()
        with transcribe_semaphore:
            segments, info = model.transcribe(audio_path, language=language)
            text = " ".join(segment.text for segment in segments)
        transcribe_seconds = time.perf_counter() - start_transcribe

        total_seconds = time.perf_counter() - start_total
        print(
            f"Transcribe done file={file.filename} "
            f"save={save_seconds:.2f}s ffmpeg={ffmpeg_seconds:.2f}s "
            f"asr={transcribe_seconds:.2f}s total={total_seconds:.2f}s"
        )

        # Respuesta
        return {
            "filename": file.filename,
            "language": info.language,
            "duration": info.duration,
            "transcript": text,
            "timings": {
                "save_seconds": round(save_seconds, 2),
                "ffmpeg_seconds": round(ffmpeg_seconds, 2),
                "transcribe_seconds": round(transcribe_seconds, 2),
                "total_seconds": round(total_seconds, 2),
            },
        }
    finally:
        for path in (input_path, audio_path):
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass
