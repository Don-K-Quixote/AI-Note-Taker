# Invisible Meeting Note Taker

A completely local, private meeting recorder and note generator for Windows. Records both your microphone and system audio (capturing both sides of virtual meetings), transcribes with Whisper on your GPU, and generates structured meeting notes with Ollama.

## Features

- **Invisible Operation**: Runs silently in system tray, no visible windows
- **Dual Audio Capture**: Records microphone + system audio (WASAPI loopback)
- **Hotkey Control**: `Ctrl+Alt+R` to start/stop recording
- **100% Local & Private**: No data leaves your machine
- **GPU Accelerated**: Uses your RTX 4060 for fast transcription
- **Structured Output**: Generates summary, action items, decisions, and follow-ups

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     RECORDING (meeting_recorder.py)            │
├────────────────────────────────────────────────────────────────┤
│  System Tray App (invisible)                                   │
│    │                                                           │
│    ├── Microphone ────┐                                        │
│    │                  ├──► Mix ──► meeting_YYYYMMDD_HHMMSS.wav │
│    └── WASAPI Loopback┘   (16kHz mono)                        │
│        (System Audio)                                          │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                  PROCESSING (process_meeting.py)               │
├────────────────────────────────────────────────────────────────┤
│  WAV ──► Whisper (GPU) ──► Transcript ──► Ollama ──► Notes.md │
│          large-v2           .txt           Llama 3.1           │
└────────────────────────────────────────────────────────────────┘
```

## Prerequisites

1. **Windows 10/11**
2. **Python 3.10+** (3.11 recommended)
3. **NVIDIA GPU with CUDA** (RTX 4060 8GB ✓)
4. **CUDA Toolkit 11.8 or 12.x** installed
5. **Ollama** installed and running

## Installation

### Step 1: Install CUDA (if not already)

Download from: https://developer.nvidia.com/cuda-downloads

Verify installation:
```bash
nvcc --version
nvidia-smi
```

### Step 2: Install Ollama

Download from: https://ollama.ai/download

After installation, pull the model:
```bash
ollama pull llama3.1:8b
```

Verify Ollama is running:
```bash
ollama list
```

### Step 3: Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install PyTorch with CUDA support FIRST
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install other dependencies
pip install -r requirements.txt
```

### Step 4: Verify GPU Detection

```python
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0)}')"
```

Expected output: `CUDA available: True, Device: NVIDIA GeForce RTX 4060`

## Usage

### Recording Meetings

**Start the recorder:**
```bash
# Run normally (console visible for debugging)
python meeting_recorder.py

# Run invisibly (no console window)
pythonw meeting_recorder.py
```

**Controls:**
- `Ctrl+Alt+R` - Start/Stop recording
- Right-click tray icon → Toggle Recording
- Right-click tray icon → Open Recordings Folder
- Right-click tray icon → Quit

**Indicators:**
- Gray icon = Idle
- Red icon = Recording

Recordings are saved to `./recordings/meeting_YYYYMMDD_HHMMSS.wav`

### Processing Recordings

**Basic usage:**
```bash
python process_meeting.py recordings/meeting_20241215_140000.wav
```

**With options:**
```bash
# Specify output directory
python process_meeting.py meeting.wav -o ./notes/

# Use smaller model (faster, less accurate)
python process_meeting.py meeting.wav -m medium

# Specify language (skip auto-detection)
python process_meeting.py meeting.wav -l en

# Transcription only (no summary)
python process_meeting.py meeting.wav --transcript-only

# Use CPU (if GPU issues)
python process_meeting.py meeting.wav --cpu
```

**Output files:**
```
recordings/
├── meeting_20241215_140000.wav           # Original audio
├── meeting_20241215_140000_transcript.txt # Full transcript
├── meeting_20241215_140000_segments.json  # Timestamped segments
└── meeting_20241215_140000_notes.md       # AI-generated meeting notes
```

## Generated Notes Format

```markdown
# Meeting Summary
[Overview of the meeting]

## Key Discussion Points
- Topic 1: Brief description
- Topic 2: Brief description

## Decisions Made
1. Decision with context
2. Decision with context

## Action Items
| Action | Owner | Deadline |
|--------|-------|----------|
| Task description | Person | Date |

## Follow-ups & Open Questions
- Question or item needing follow-up

## Notable Quotes/Points
- "Significant quote" - regarding topic
```

## Auto-Start on Windows Boot (Optional)

Create a shortcut to run invisibly at startup:

1. Press `Win+R`, type `shell:startup`
2. Create a new shortcut with target:
   ```
   pythonw "C:\path\to\meeting_note_taker\meeting_recorder.py"
   ```
3. Name it "Meeting Recorder"

## Configuration Options

### Whisper Models

| Model | VRAM | Speed | Accuracy | Recommended For |
|-------|------|-------|----------|-----------------|
| `tiny` | ~1GB | Fastest | Basic | Quick tests |
| `base` | ~1GB | Fast | Good | Short meetings |
| `small` | ~2GB | Medium | Better | General use |
| `medium` | ~5GB | Slower | Great | Most meetings |
| `large-v2` | ~6GB | Slowest | Best | Important meetings |
| `large-v3` | ~6GB | Slowest | Best | Multi-language |

Your RTX 4060 8GB can run `large-v2` comfortably.

### Ollama Models

```bash
# Smaller, faster
ollama pull llama3.1:8b    # Default, good balance

# Larger, more capable (needs ~8GB VRAM)
ollama pull llama3.1:70b   # Won't fit in 8GB VRAM alongside Whisper

# Alternative models
ollama pull mistral:7b     # Good for summarization
ollama pull phi3:medium    # Microsoft's efficient model
```

## Troubleshooting

### "No loopback device found"
- Ensure you have active audio output devices
- Try playing audio before starting the recorder
- Check Windows sound settings

### "CUDA out of memory"
- Close other GPU-intensive apps
- Use a smaller Whisper model: `-m medium` or `-m small`
- Process after closing the meeting app

### "Cannot connect to Ollama"
- Ensure Ollama is running: `ollama serve`
- Check if model is downloaded: `ollama list`
- Verify URL: http://localhost:11434

### Recording quality issues
- Ensure microphone is set as default input device
- Check audio levels in Windows sound settings
- Test with a short recording first

### Hotkey not working
- Some apps may capture `Ctrl+Alt+R` first
- Try running as administrator
- Check for hotkey conflicts

## Batch Processing

Process multiple recordings:
```bash
for %f in (recordings\*.wav) do python process_meeting.py "%f"
```

## Privacy & Legal Notes

- All processing is 100% local - no data is transmitted
- Recordings are stored only on your machine
- **Important**: Recording laws vary by jurisdiction
  - Some places require all-party consent
  - Use responsibly and ethically
  - Inform participants when required by law

## Project Structure

```
meeting_note_taker/
├── meeting_recorder.py    # System tray recording app
├── process_meeting.py     # Transcription & summarization
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── recordings/           # Output directory (created automatically)
    ├── *.wav             # Audio recordings
    ├── *_transcript.txt  # Full transcripts
    ├── *_segments.json   # Timestamped segments
    └── *_notes.md        # AI meeting notes
```

## License

MIT License - Use freely for personal and commercial purposes.
