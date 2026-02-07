import os
import subprocess
import torch

# 1. FFmpeg Check
ffmpeg_dir = os.path.join(os.path.dirname(__file__), 'bin')
os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]

print("--- System Check ---")
try:
    subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("[OK] FFmpeg wurde im bin-Ordner gefunden.")
except FileNotFoundError:
    print("[FEHLER] FFmpeg nicht gefunden. Liegt die ffmpeg.exe in /bin?")

# 2. GPU Check
if torch.cuda.is_available():
    print(f"[OK] GPU erkannt: {torch.cuda.get_device_name(0)}")
    print(f"[INFO] VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
else:
    print("[FEHLER] Keine NVIDIA GPU gefunden oder CUDA nicht installiert.")

# 3. Bibliothek Check
try:
    from faster_whisper import WhisperModel
    print("[OK] faster-whisper ist bereit.")
except ImportError:
    print("[FEHLER] faster-whisper fehlt in der Conda-Umgebung.")

print("--------------------")