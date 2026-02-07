# Whisper-Live Server

A real-time speech recognition server using OpenAI's Whisper model for local transcription via WebSocket connections.

## Overview

Whisper-Live Server is a WebSocket-based server (WSS) that provides real-time speech-to-text transcription using the Whisper AI model. It supports dynamic prompt updates, GPU acceleration, and secure connections via SSL/TLS.

## Features

- **Real-time Transcription**: Live speech-to-text conversion with partial and final results
- **Dynamic Prompt Support**: Update transcription context on-the-fly via WebSocket messages
- **GPU Acceleration**: Automatic model selection based on available GPU hardware
- **Secure WebSocket (WSS)**: SSL/TLS encrypted connections for secure communication
- **Auto Model Selection**: Intelligently chooses the best Whisper model based on GPU capabilities
- **Multi-client Support**: Handle multiple concurrent client connections
- **German Language Support**: Optimized for German language transcription (configurable)

## Requirements

### System Requirements
- **Python**: 3.8 or higher
- **GPU**: NVIDIA GPU with CUDA support (recommended)
  - High-end GPUs (V100, RTX 30/40 series): Uses `large-v3` model
  - Mid-range GPUs (Titan X, Quadro, RTX 20 series): Uses `turbo` model
  - Other GPUs/CPU: Uses `medium` model
- **FFmpeg**: Required for audio processing
- **Operating System**: Windows (PowerShell script included) or Linux

### Python Dependencies
- `RealtimeSTT`: Real-time speech-to-text library
- `websockets`: WebSocket server implementation
- `torch`: PyTorch for GPU acceleration
- `faster-whisper`: Optimized Whisper implementation
- `cryptography`: For SSL certificate generation

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/andreasknopke/Whisper-Live.git
cd Whisper-Live
```

### 2. Set Up Python Environment
Using Conda (recommended):
```bash
conda create -n whisper_live python=3.10
conda activate whisper_live
```

Or using venv:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install RealtimeSTT websockets torch faster-whisper cryptography
```

### 4. Install FFmpeg
Place the FFmpeg executable in a `bin` directory within the project root:
```
Whisper-Live/
├── bin/
│   └── ffmpeg.exe (Windows) or ffmpeg (Linux)
```

Or install FFmpeg system-wide following your OS-specific instructions.

### 5. Generate SSL Certificates
```bash
python create_certs.py
```

This will create `server.crt` and `server.key` files required for secure WebSocket connections.

### 6. Verify Setup
```bash
python check_setup.py
```

This script checks:
- FFmpeg availability
- GPU detection and CUDA support
- faster-whisper installation

## Usage

### Starting the Server

#### Basic Start (Python)
```bash
python med_live_server.py
```

#### Windows PowerShell Monitor (Auto-restart)
For production use on Windows, use the included PowerShell script that monitors and auto-restarts the server:

1. Edit `start_whisperlive.ps1` and configure:
   - `$CONDA_PATH`: Path to your conda executable
   - `$ENV_NAME`: Your conda environment name
   - `$WORKING_DIR`: Path to the Whisper-Live directory
   - `$PORT`: Server port (default: 5001)

2. Run the script:
```powershell
.\start_whisperlive.ps1
```

The server will start on `wss://0.0.0.0:5001` (or your configured port).

### Client Connection

Connect to the server via WebSocket using the WSS protocol:

```javascript
const ws = new WebSocket('wss://localhost:5001');

ws.onopen = () => {
    console.log('Connected to Whisper-Live Server');
    
    // Optional: Set a custom prompt for better transcription context
    ws.send(JSON.stringify({
        type: 'set_prompt',
        text: 'Medical terminology context...'
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'partial') {
        // Real-time transcription updates
        console.log('Partial:', data.text);
    } else if (data.type === 'final') {
        // Final transcription result
        console.log('Final:', data.text);
    } else if (data.type === 'info') {
        // Server information messages
        console.log('Info:', data.text);
    }
};
```

### WebSocket Message Protocol

#### Client to Server

**Set Prompt** (optional):
```json
{
    "type": "set_prompt",
    "text": "Your custom context or prompt text here"
}
```

#### Server to Client

**Partial Transcription**:
```json
{
    "type": "partial",
    "text": "Real-time transcription text..."
}
```

**Final Transcription**:
```json
{
    "type": "final",
    "text": "Complete transcribed sentence."
}
```

**Info Message**:
```json
{
    "type": "info",
    "text": "Prompt updated"
}
```

## Configuration

### Model Selection
The server automatically selects the appropriate Whisper model based on GPU capabilities:

- **High-end GPUs** (V100, RTX 30/40 series, ADA): `large-v3` with `float16`
- **Mid-range GPUs** (Titan X, Quadro, RTX 20 series): `turbo` with `int8_float16`
- **Other GPUs/CPU**: `medium` with `int8`

### Transcription Parameters
Located in the AudioToTextRecorder initialization section of `med_live_server.py`:

```python
recorder = AudioToTextRecorder(
    model=selected_model,           # Auto-selected based on GPU
    language="de",                  # Target language (change as needed)
    device="cuda",                  # Use GPU acceleration
    compute_type=compute_type,      # Auto-selected precision
    initial_prompt="",              # Can be updated via WebSocket
    silero_sensitivity=0.05,        # Voice activity detection sensitivity
    silero_use_onnx=True,          # Use optimized VAD
    post_speech_silence_duration=0.6,  # Silence after speech (seconds)
    min_length_of_recording=0.3,   # Minimum recording length (seconds)
    enable_realtime_transcription=True,  # Enable partial results
    on_realtime_transcription_update=on_realtime_update,
    spinner=True                    # Show processing spinner
)
```

### Whisper Parameters
```python
recorder.whisper_parameters["condition_on_previous_text"] = False
recorder.whisper_parameters["no_speech_threshold"] = 0.6
```

## Troubleshooting

### FFmpeg Not Found
- Ensure FFmpeg is in the `bin` directory or installed system-wide
- Check PATH environment variable includes FFmpeg location

### CUDA/GPU Not Detected
- Install NVIDIA CUDA toolkit
- Verify GPU drivers are up to date
- Check PyTorch CUDA installation: `python -c "import torch; print(torch.cuda.is_available())"`

### Certificate Errors
- Regenerate certificates using `python create_certs.py`
- Ensure `server.crt` and `server.key` exist in the project root
- For development, you may need to accept self-signed certificates in your client

### Connection Issues
- Verify the server is running on the expected port (default: 5001)
- Check firewall settings allow WebSocket connections
- Use `wss://` protocol (not `ws://`) for secure connections

## Project Structure

```
Whisper-Live/
├── med_live_server.py         # Main WebSocket server
├── create_certs.py            # SSL certificate generator
├── check_setup.py             # System requirements checker
├── start_whisperlive.ps1      # PowerShell monitoring script
├── .gitignore                 # Git ignore rules
├── bin/                       # FFmpeg executables (not in repo)
├── server.crt                 # SSL certificate (generated)
└── server.key                 # SSL private key (generated)
```

## Security Notes

- The included SSL certificates are self-signed and intended for development/local use
- For production deployment, use proper SSL certificates from a trusted Certificate Authority
- The `server.key` file contains sensitive private key data - keep it secure
- Certificates and keys are excluded from version control via `.gitignore`

## Language Configuration

By default, the server is configured for German language transcription. To change the language, modify the `language` parameter in the AudioToTextRecorder initialization in `med_live_server.py`:

```python
language="de",  # Change to "en" for English, "es" for Spanish, etc.
```

Supported languages include all languages supported by OpenAI's Whisper model.

## Performance Optimization

- **GPU Memory**: Higher-end GPUs can handle larger models (`large-v3`) for better accuracy
- **Compute Type**: `float16` provides best quality, `int8` reduces memory usage
- **Silence Detection**: Adjust `silero_sensitivity` (0.0-1.0) for your environment
- **Post-speech Duration**: Tune `post_speech_silence_duration` based on speaking pace

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Author

Andreas Knopke

## Acknowledgments

- OpenAI Whisper for the speech recognition model
- RealtimeSTT library for real-time transcription capabilities
- faster-whisper for optimized Whisper inference
