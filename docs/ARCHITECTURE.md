# Architecture Documentation

## System Overview

AI Meeting Note Taker is a Windows desktop application built with Python that provides end-to-end meeting capture and summarization.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           User Interface Layer                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    FloatingButton (Tkinter)                      │   │
│  │  • Always-on-top window                                          │   │
│  │  • Meeting configuration (title, type, length)                   │   │
│  │  • Device selection dropdown                                     │   │
│  │  • Recording state management                                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Core Processing Layer                          │
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │  AudioRecorder   │  │ MeetingProcessor │  │   EmailSender    │      │
│  │                  │  │                  │  │                  │      │
│  │ • Mic capture    │  │ • Whisper STT    │  │ • Gmail SMTP     │      │
│  │ • Loopback       │  │ • Ollama LLM     │  │ • Attachments    │      │
│  │ • Audio mixing   │  │ • PDF export     │  │                  │      │
│  │ • WAV output     │  │ • Action items   │  │                  │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           External Services                              │
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │  WASAPI Audio    │  │  Ollama Server   │  │   Gmail SMTP     │      │
│  │  (Windows API)   │  │  (localhost)     │  │   (optional)     │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. AudioRecorder

**Purpose**: Capture audio from microphone and system output simultaneously.

**Key Features**:
- WASAPI loopback for system audio capture
- Automatic device detection matching Windows default
- Real-time audio mixing (mic + system)
- Thread-safe queue-based processing

**Technology**:
- `pyaudiowpatch` - WASAPI loopback support
- `sounddevice` - Microphone capture
- `numpy` - Audio processing
- `wave` - WAV file output

**Audio Flow**:
```
┌─────────────┐     ┌─────────────┐
│ Microphone  │────▶│  mic_queue  │────┐
└─────────────┘     └─────────────┘    │
                                       ▼
                                 ┌───────────┐     ┌─────────────┐
                                 │  _mix_    │────▶│  audio.wav  │
                                 │  audio()  │     └─────────────┘
                                       ▲
┌─────────────┐     ┌─────────────┐    │
│  Loopback   │────▶│system_queue │────┘
│  (Speaker)  │     └─────────────┘
└─────────────┘
```

**Device Selection Logic**:
```python
def _auto_select_device():
    1. Get Windows default output device
    2. Find matching loopback device by name
    3. Filter out virtual devices (Voicemeeter, etc.)
    4. Return matched or first available device
```

---

### 2. MeetingProcessor

**Purpose**: Transcribe audio and generate structured meeting notes.

**Pipeline**:
```
audio.wav
    │
    ▼
┌──────────────────────────────────┐
│  faster-whisper (GPU)            │
│  • Model: large-v2               │
│  • Language: auto-detect         │
│  • Output: timestamped segments  │
└──────────────────────────────────┘
    │
    ▼
transcript.txt
    │
    ▼
┌──────────────────────────────────┐
│  Ollama (LLaMA 3.1 8B)          │
│  • Template-based prompting      │
│  • Structured output format      │
│  • 8K context window            │
└──────────────────────────────────┘
    │
    ├──▶ MoM.md (Markdown)
    ├──▶ MoM.pdf (PDF export)
    └──▶ action_items.md (extracted)
```

**Meeting Templates**:

| Type | Key Sections |
|------|--------------|
| Business Meeting | Agenda, Attendees, Decisions, Action Items, Risks |
| Tutorial/Training | Concepts, Steps, Examples, Exercises, Takeaways |
| Interview | Q&A, Assessment, Strengths, Concerns, Recommendation |
| Brainstorm | Ideas, Themes, Pros/Cons, Top Picks, Parked |
| 1:1 / Check-in | Updates, Wins, Blockers, Goals, Support |
| Presentation/Demo | Overview, Features, Data, Q&A, Feedback |

---

### 3. PDF Export

**Technology**: fpdf2

**Features**:
- Markdown to PDF conversion
- Header/section formatting
- Table support
- Unicode handling (latin-1 encoding)

**Challenges Solved**:
- Width calculation for proper text wrapping
- Special character encoding
- Multi-page document handling

---

### 4. Action Item Extraction

**Logic**:
```python
def _track_action_items():
    1. Detect section headers containing keywords:
       - "Action Item", "Next Step", "Follow-up"
       - "Practice Exercise", "Key Takeaway"
       - "Recommendation", "To-Do"
    
    2. Extract items from:
       - Markdown tables (handle # column)
       - Bullet points (- or *)
       - Numbered lists (1. or 1))
    
    3. Output to action_items.md with status checkboxes
```

---

## Data Flow

### Recording Phase
```
User clicks REC
    │
    ├──▶ Auto-detect audio device
    ├──▶ Create meeting folder: recordings/{title}/
    ├──▶ Start mic_thread
    ├──▶ Start system_thread
    └──▶ Start mixer_thread
            │
            ▼
    Audio chunks → Queue → Mix → Buffer
```

### Processing Phase
```
User clicks STOP
    │
    ├──▶ Stop threads
    ├──▶ Save audio.wav
    │
    ▼ (Background thread)
    │
    ├──▶ STEP 1: Transcription
    │       └──▶ transcript.txt
    │
    ├──▶ STEP 2: Summarization
    │       └──▶ MoM.md
    │
    ├──▶ STEP 3: PDF Export
    │       └──▶ MoM.pdf
    │
    ├──▶ STEP 4: Action Items
    │       └──▶ action_items.md
    │
    └──▶ STEP 5: Email (optional)
```

---

## Configuration System

### Hierarchy
```
DEFAULT_CONFIG (code) ◀── config.json (file) ◀── Runtime overrides
```

### Key Parameters

| Category | Parameter | Default | Description |
|----------|-----------|---------|-------------|
| Whisper | model | large-v2 | Model size |
| Whisper | device | cuda | GPU or CPU |
| Whisper | compute_type | float16 | Precision |
| Ollama | model | llama3.1:8b | LLM model |
| Ollama | temperature | 0.3 | Creativity |
| Ollama | context_window | 8192 | Max tokens |

---

## Threading Model

```
┌─────────────────────────────────────────────────────────────┐
│                     Main Thread (UI)                         │
│  • Tkinter event loop                                        │
│  • Button clicks, dropdown changes                           │
│  • Timer updates                                             │
└─────────────────────────────────────────────────────────────┘
        │
        ├──▶ mic_thread (daemon)
        │       └──▶ Microphone capture loop
        │
        ├──▶ system_thread (daemon)
        │       └──▶ Loopback capture loop
        │
        ├──▶ mixer_thread (daemon)
        │       └──▶ Audio mixing loop
        │
        └──▶ processing_thread (daemon)
                └──▶ Whisper + Ollama pipeline
```

**Synchronization**:
- `threading.Event` for stop signals
- `queue.Queue` for audio buffers
- `root.after()` for UI updates from threads

---

## Error Handling

### Empty Transcript Protection
```python
if word_count < 10:
    # Don't generate hallucinated MoM
    # Show diagnostic error message instead
    return error_mom_template
```

### Device Detection Fallback
```python
try:
    device = auto_detect_from_windows_default()
except:
    device = first_available_loopback()
```

### Graceful Degradation
- PDF export fails → Continue without PDF
- Email fails → Save locally, show error
- No GPU → Fall back to CPU (slower)

---

## Performance Considerations

### GPU Memory
- Whisper large-v2: ~3GB VRAM
- CUDA operations: ~1GB overhead
- Total: ~4GB minimum

### Optimization Techniques
- faster-whisper uses CTranslate2 (4x faster than original)
- Batched transcription with VAD filtering
- Streaming LLM response (not waiting for full completion)

### Bottlenecks
1. **Transcription**: GPU-bound, ~10x real-time
2. **Summarization**: CPU-bound (Ollama), ~30-60s
3. **PDF Export**: CPU-bound, ~1-2s

---

## Security Considerations

### Local Processing
- All audio processing happens locally
- No cloud transcription services
- Transcripts never leave the machine

### Email Security
- Gmail App Passwords (not main password)
- SMTP over TLS
- Credentials in config.json (add to .gitignore)

### File Security
- Recordings stored locally
- No automatic cloud sync
- User controls data retention

---

## Future Architecture Considerations

### Planned Improvements
1. **Speaker Diarization**: Add pyannote.audio for "who said what"
2. **Plugin System**: Allow custom meeting templates
3. **Database**: SQLite for meeting search/history
4. **Web UI**: Optional browser-based interface

### Modular Refactoring Target
```
src/
├── audio/
│   ├── capture.py
│   ├── devices.py
│   └── mixer.py
├── transcription/
│   └── whisper_client.py
├── summarization/
│   ├── ollama_client.py
│   └── templates/
├── export/
│   ├── pdf.py
│   ├── markdown.py
│   └── email.py
└── ui/
    └── floating_button.py
```
