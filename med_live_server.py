import os
import sys
import json
import asyncio
import threading
import websockets
import ssl 
import signal
import torch

# --- 1. PFAD-KONFIGURATION ---
base_dir = os.path.dirname(os.path.abspath(__file__))
bin_dir = os.path.join(base_dir, "bin")
os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]

conda_prefix = os.environ.get('CONDA_PREFIX')
if conda_prefix:
    dll_path = os.path.join(conda_prefix, 'Library', 'bin')
    if os.path.exists(dll_path):
        os.add_dll_directory(dll_path)

try:
    from RealtimeSTT import AudioToTextRecorder
except ImportError as e:
    print(f"Fehler: RealtimeSTT konnte nicht geladen werden ({e})")
    sys.exit(1)

# --- GLOBALER RECORDER ---
recorder = None
connected_clients = set()
loop = None

# --- 2. WEBSOCKET LOGIK ---
def broadcast_to_clients(message_dict):
    if not loop or not loop.is_running(): 
        return
    msg = json.dumps(message_dict)
    for client in connected_clients.copy():
        try:
            asyncio.run_coroutine_threadsafe(client.send(msg), loop)
        except Exception:
            connected_clients.discard(client)

def on_realtime_update(text):
    if text.strip().lower() in ["befundbericht.", "bericht.", "www.", "vielen dank."]:
        return
    broadcast_to_clients({"type": "partial", "text": text})

# --- 3. TRANSKRIPTIONS ENGINE ---
def start_recorder():
    global recorder
    gpu_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    
    if any(x in gpu_name for x in ["V100", "ADA", "RTX 30", "RTX 40"]):
        selected_model = "large-v3"
        compute_type = "float16"
    elif any(x in gpu_name for x in ["Titan X", "Quadro", "RTX 20"]):
        selected_model = "turbo" 
        compute_type = "int8_float16"
    else:
        selected_model = "medium"
        compute_type = "int8"

    # Standard-Prompt (wird überschrieben, wenn App sendet)
    initial_prompt = ""

    try:
        recorder = AudioToTextRecorder(
            model=selected_model,
            language="de",
            device="cuda",
            compute_type=compute_type,
            initial_prompt=initial_prompt,
            silero_sensitivity=0.05,
            silero_use_onnx=True,
            post_speech_silence_duration=0.6,
            min_length_of_recording=0.3,
            enable_realtime_transcription=True,
            on_realtime_transcription_update=on_realtime_update,
            spinner=True
        )

        if hasattr(recorder, 'whisper_parameters'):
            recorder.whisper_parameters["condition_on_previous_text"] = False
            recorder.whisper_parameters["no_speech_threshold"] = 0.6
        
        print("\n" + "="*50)
        print(">>> WSS SERVER BEREIT (DYNAMIC PROMPT ENABLED)")
        print(f">>> Hardware: {gpu_name} | Modell: {selected_model}")
        print("="*50 + "\n")

        while True:
            final_text = recorder.text()
            if final_text:
                cleaned_text = final_text.strip()
                if len(cleaned_text) > 3:
                    broadcast_to_clients({"type": "final", "text": cleaned_text})
                
    except Exception as e:
        print(f"Kritischer Fehler: {e}")

# --- 4. SERVER HANDLER ---
async def ws_handler(websocket):
    global recorder
    connected_clients.add(websocket)
    print(f"Client verbunden: {websocket.remote_address}")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                # Prüfen, ob die App einen neuen Prompt schickt
                if data.get("type") == "set_prompt":
                    new_prompt = data.get("text", "")
                    if recorder and new_prompt:
                        print(f">>> Neuer Prompt empfangen: {new_prompt[:50]}...")
                        # Dynamische Aktualisierung des Prompts im laufenden Recorder
                        recorder.initial_prompt = new_prompt
                        # Falls das Modell intern whisper_parameters nutzt:
                        if hasattr(recorder, 'whisper_parameters'):
                            recorder.whisper_parameters["initial_prompt"] = new_prompt
                        
                        await websocket.send(json.dumps({"type": "info", "text": "Prompt aktualisiert"}))
            except json.JSONDecodeError:
                pass
    finally:
        connected_clients.discard(websocket)

async def main():
    global loop
    loop = asyncio.get_running_loop()
    
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    cert_file = os.path.join(base_dir, "server.crt")
    key_file = os.path.join(base_dir, "server.key")
    
    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        print("\nFEHLER: Zertifikate fehlen!")
        return

    ssl_context.load_cert_chain(certfile=cert_file, keyfile=key_file)
    threading.Thread(target=start_recorder, daemon=True).start()
    
    async with websockets.serve(ws_handler, "0.0.0.0", 5001, ssl=ssl_context):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        os._exit(0)