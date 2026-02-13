<div align="center">

# AI Meeting Note Taker

**Intelligent, Privacy-First Meeting Transcription & Summarization**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CUDA](https://img.shields.io/badge/CUDA-Enabled-76B900.svg)](https://developer.nvidia.com/cuda-toolkit)
[![Whisper](https://img.shields.io/badge/OpenAI-Whisper-412991.svg)](https://github.com/openai/whisper)
[![Ollama](https://img.shields.io/badge/Ollama-LLaMA_3.1-orange.svg)](https://ollama.ai/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991.svg)](https://openai.com/)

*Automatically capture, transcribe, and summarize your meetings with local or cloud AI*

[Features](#features) | [Installation](#installation) | [Usage](#usage) | [Architecture](#architecture) | [Configuration](#configuration)

</div>

---

## Overview

AI Meeting Note Taker is a **Windows desktop application** that silently records your meetings (Zoom, Teams, Google Meet, or in-person), transcribes them using GPU-accelerated Whisper, and generates structured meeting minutes using your choice of **Ollama (local)** or **OpenAI GPT (cloud)**. All transcription happens locally on your machine.

### Why This Project?

- **Privacy First** - Whisper transcription runs entirely on your local GPU
- **Multi-Provider LLM** - Choose between local Ollama or OpenAI GPT for summarization
- **Zero Manual Effort** - One-click recording with automatic transcription and summarization
- **Professional Output** - Structured Minutes of Meeting (MoM) with action items, PDF export, and email delivery

---

## Features

### Core Functionality
| Feature | Description |
|---------|-------------|
| **Dual Audio Capture** | Records both microphone and system audio (WASAPI loopback) |
| **GPU Transcription** | Uses faster-whisper with CUDA acceleration |
| **Multi-Provider LLM** | Summarize with Ollama (local) or OpenAI GPT-4o / GPT-4o-mini |
| **Auto Email** | Sends meeting notes to your inbox automatically |
| **PDF Export** | Exports professional PDF documents |
| **Action Item Tracking** | Extracts and tracks action items per meeting |
| **Adaptive Audio Mixing** | Smart mic/system mixing with post-recording normalization |

### User Experience
- **Floating Button UI** - Minimal, always-on-top interface
- **LLM Provider Dropdown** - Switch between Ollama and GPT models on the fly
- **Auto Device Detection** - Automatically selects Windows default audio output
- **6 Meeting Templates** - Business, Tutorial, Interview, Brainstorm, 1:1, Presentation
- **Brief/Detailed Modes** - Choose summary length based on your needs
- **Organized Storage** - Each meeting gets its own folder with all artifacts
- **Structured Logging** - loguru-based logging for diagnostics

---

## Demo

<div align="center">

### Floating Button Interface
```
+--------------------------------+
| [Meeting title...            ] |
| [DELL S2725HS (NVIDIA...)   v] |  <-- Auto-detected audio device
| [Business Meeting v] [Detailed]|
| [Ollama                      v]|  <-- LLM provider selector
|            * REC               |
|            Ready               |
+--------------------------------+
```

### Sample Output Structure
```
recordings/
  Project_Standup/
    audio.wav           # Original recording
    transcript.txt      # Full transcription
    MoM.md              # Markdown minutes
    MoM.pdf             # PDF export
    action_items.md     # Extracted action items
```

</div>

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Audio Capture** | PyAudioWPatch + sounddevice | WASAPI loopback for system audio |
| **Transcription** | faster-whisper (large-v2) | GPU-accelerated speech-to-text |
| **Summarization** | Ollama (LLaMA 3.1) or OpenAI GPT | Pluggable LLM provider for meeting notes |
| **LLM Abstraction** | Custom provider pattern | `LLMProvider` ABC with `OllamaProvider` and `OpenAIProvider` |
| **PDF Generation** | fpdf2 | Professional document export |
| **GUI** | Tkinter | Lightweight floating interface |
| **Email** | smtplib (Gmail SMTP) | Automated delivery |
| **Logging** | loguru | Structured logging (replaces print) |
| **Environment** | python-dotenv | `.env` file loading for API keys |

---

## Requirements

### Hardware
- **GPU**: NVIDIA GPU with 6GB+ VRAM (RTX 3060+ recommended)
- **RAM**: 16GB+ recommended
- **Storage**: ~10GB for models

### Software
- Windows 10/11
- Python 3.10+
- CUDA Toolkit 11.8+
- [Ollama](https://ollama.ai/) installed and running (if using local LLM)

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Don-K-Quixote/AI-Note-Taker.git
cd AI-Note-Taker
```

### 2. Create Conda Environment
```bash
conda create -n ai-note-taker python=3.11 -y
conda activate ai-note-taker
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up LLM Provider

**Option A: Ollama (Local, Private)**
```bash
# Download Ollama from https://ollama.ai/
ollama pull llama3.1:8b
ollama serve  # Keep running in background
```

**Option B: OpenAI GPT (Cloud)**
Create a `.env` file in the project root:
```
OPENAI_API_KEY=sk-your-api-key-here
```

### 5. Configure (Optional)
Create `src/config.json` to override defaults:
```json
{
  "llm": {
    "provider": "ollama"
  },
  "whisper": {
    "model": "large-v2",
    "device": "cuda"
  },
  "email": {
    "enabled": true,
    "sender_email": "your@gmail.com",
    "sender_password": "your_app_password",
    "recipient_email": "recipient@email.com"
  }
}
```

### 6. Run
```bash
python src/meeting_recorder.py
```

---

## Usage

### GUI Application
1. **Launch** the application (`python src/meeting_recorder.py`)
2. **Select** your LLM provider (Ollama, GPT-4o, or GPT-4o-mini)
3. **Enter** meeting title (optional)
4. **Select** meeting type and summary length
5. **Click REC** to start recording
6. **Click STOP** when meeting ends
7. **Wait** for automatic transcription, summarization, and email delivery
8. **Check** your email or the `recordings/` folder

### CLI Post-Processing
Process a previously recorded audio file:
```bash
# With Ollama (default)
python src/process_meeting.py recording.wav

# With OpenAI GPT
python src/process_meeting.py recording.wav --provider openai --openai-model gpt-4o-mini

# Transcription only
python src/process_meeting.py recording.wav --transcript-only

# Use CPU instead of GPU
python src/process_meeting.py recording.wav --cpu
```

### Meeting Types

| Type | Best For | Key Sections Generated |
|------|----------|----------------------|
| **Business Meeting** | Team meetings, standups | Action Items, Decisions, Risks |
| **Tutorial/Training** | Learning sessions | Key Concepts, Steps, Exercises |
| **Interview** | Candidate interviews | Assessment, Strengths, Recommendation |
| **Brainstorm** | Ideation sessions | Ideas, Themes, Top Picks |
| **1:1 / Check-in** | Personal meetings | Updates, Blockers, Goals |
| **Presentation/Demo** | Product demos | Key Points, Q&A, Takeaways |

---

## Architecture

```
+-------------------------------------------------------------+
|                    AI Meeting Note Taker                     |
+-------------------------------------------------------------+
|                                                              |
|  +--------------+    +--------------+    +--------------+    |
|  |   Audio      |    |   Whisper    |    | LLM Provider |    |
|  |   Capture    |--->|   (GPU)      |--->|  Abstraction |    |
|  |              |    |              |    |              |    |
|  | * Mic Input  |    | * STT        |    | * Ollama     |    |
|  | * Loopback   |    | * Language   |    | * OpenAI GPT |    |
|  | * Adaptive   |    |   Detection  |    | * Factory    |    |
|  |   Mixing     |    |              |    |   Pattern    |    |
|  +--------------+    +--------------+    +--------------+    |
|         |                   |                   |            |
|         v                   v                   v            |
|  +----------------------------------------------------+     |
|  |                  Output Pipeline                    |     |
|  |  audio.wav -> transcript.txt -> MoM.md -> MoM.pdf  |     |
|  |  action_items.md extraction                         |     |
|  |  Email delivery (optional)                          |     |
|  +----------------------------------------------------+     |
|                                                              |
+-------------------------------------------------------------+
```

---

## Project Structure

```
AI-Note-Taker/
  .env                        # API keys (gitignored)
  .gitignore
  requirements.txt            # Python dependencies
  requirements-dev.txt        # Dev dependencies
  CLAUDE.md                   # AI coding instructions
  README.md
  LICENSE
  CONTRIBUTING.md
  src/
    meeting_recorder.py       # Main GUI application
    process_meeting.py        # CLI post-processing tool
    llm_providers.py          # LLM provider abstraction layer
  docs/
    ARCHITECTURE.md           # Technical documentation
    SETUP.md                  # Detailed setup guide
  notebooks/
    experiments.ipynb          # Model experiments
  tasks/
    todo.md                   # Task tracking
  .github/
    ISSUE_TEMPLATE/
      bug_report.md
      feature_request.md
```

---

## Configuration

### config.json Reference

Create `src/config.json` to override any defaults:

```json
{
  "recording": {
    "output_dir": "recordings",
    "sample_rate": 16000
  },
  "llm": {
    "provider": "ollama"
  },
  "whisper": {
    "model": "large-v2",
    "device": "cuda",
    "compute_type": "float16"
  },
  "ollama": {
    "model": "llama3.1:8b",
    "url": "http://localhost:11434/api/generate",
    "temperature": 0.3,
    "context_window": 8192
  },
  "openai": {
    "model": "gpt-4o-mini",
    "api_key": "",
    "temperature": 0.3,
    "max_tokens": 4096
  },
  "email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your@gmail.com",
    "sender_password": "app_password",
    "recipient_email": "recipient@email.com"
  }
}
```

### Environment Variables

API keys are loaded from `.env` in the project root (via python-dotenv):

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required for GPT provider) |

The `.env` file takes priority over `config.json` for API keys.

### LLM Provider Selection

| Provider | Pros | Cons |
|----------|------|------|
| **Ollama** (default) | Free, private, no internet needed | Requires local GPU, slower |
| **GPT-4o** | Highest quality summaries | Requires API key, costs money, sends data to cloud |
| **GPT-4o-mini** | Good quality, low cost | Requires API key, sends data to cloud |

Switch providers at runtime via the UI dropdown, or set `llm.provider` in config.json.

---

## Performance

| Metric | Value |
|--------|-------|
| Transcription Speed | ~10x real-time (RTX 4060) |
| Summarization Time | ~30-60s (Ollama) / ~10-15s (GPT) |
| Memory Usage | ~4GB VRAM |
| Accuracy | 95%+ (English) |

---

## Roadmap

- [x] Multi-device audio capture
- [x] 6 meeting type templates
- [x] PDF export
- [x] Action item tracking
- [x] OpenAI GPT integration (multi-provider LLM)
- [x] Adaptive audio mixing & normalization
- [x] Structured logging (loguru)
- [ ] Speaker diarization (who said what)
- [ ] Search across past meetings
- [ ] Real-time transcription preview
- [ ] Multi-language support

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
git clone https://github.com/Don-K-Quixote/AI-Note-Taker.git
cd AI-Note-Taker
git checkout -b feat/your-feature-name
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) - Optimized inference
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [OpenAI](https://openai.com/) - GPT API
- [PyAudioWPatch](https://github.com/s0d3s/PyAudioWPatch) - WASAPI loopback
- [loguru](https://github.com/Delgan/loguru) - Structured logging

---

<div align="center">

**Built by Khalid Siddiqui**

[Back to Top](#ai-meeting-note-taker)

</div>
