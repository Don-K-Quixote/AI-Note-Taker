<div align="center">

# 🎙️ AI Meeting Note Taker

**Intelligent, Privacy-First Meeting Transcription & Summarization**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CUDA](https://img.shields.io/badge/CUDA-Enabled-76B900.svg)](https://developer.nvidia.com/cuda-toolkit)
[![Whisper](https://img.shields.io/badge/OpenAI-Whisper-412991.svg)](https://github.com/openai/whisper)
[![Ollama](https://img.shields.io/badge/Ollama-LLaMA_3.1-orange.svg)](https://ollama.ai/)

*Automatically capture, transcribe, and summarize your meetings with local AI processing*

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## 🎯 Overview

AI Meeting Note Taker is a **Windows desktop application** that silently records your meetings (Zoom, Teams, Google Meet, or in-person), transcribes them using GPU-accelerated Whisper, and generates structured meeting minutes using local LLMs—all without sending your data to the cloud.

### Why This Project?

- **Privacy First**: All processing happens locally on your machine
- **Zero Manual Effort**: One-click recording with automatic transcription and summarization
- **Professional Output**: Generates structured Minutes of Meeting (MoM) with action items
- **Works Everywhere**: Captures any meeting platform via system audio loopback

---

## ✨ Features

### Core Functionality
| Feature | Description |
|---------|-------------|
| 🎤 **Dual Audio Capture** | Records both microphone and system audio (WASAPI loopback) |
| 🧠 **GPU Transcription** | Uses faster-whisper with CUDA acceleration |
| 📝 **Smart Summarization** | Generates structured MoM using Ollama + LLaMA 3.1 |
| 📧 **Auto Email** | Sends meeting notes to your inbox automatically |
| 📄 **PDF Export** | Exports professional PDF documents |
| ✅ **Action Item Tracking** | Extracts and tracks action items per meeting |

### User Experience
- **Floating Button UI** - Minimal, always-on-top interface
- **Auto Device Detection** - Automatically selects Windows default audio output
- **6 Meeting Templates** - Business, Tutorial, Interview, Brainstorm, 1:1, Presentation
- **Brief/Detailed Modes** - Choose summary length based on your needs
- **Organized Storage** - Each meeting gets its own folder with all artifacts

---

## 🎬 Demo

<div align="center">

### Floating Button Interface
```
┌────────────────────────────────┐
│ [Meeting title...            ] │
│ [DELL S2725HS (NVIDIA...)   ▼] │  ← Auto-detected
│ [Business Meeting▼] [Detailed▼]│
│            ● REC               │
│            Ready               │
└────────────────────────────────┘
```

### Sample Output Structure
```
recordings/
└── Project_Standup/
    ├── audio.wav           # Original recording
    ├── transcript.txt      # Full transcription
    ├── MoM.md             # Markdown minutes
    ├── MoM.pdf            # PDF export
    └── action_items.md    # Extracted action items
```

</div>

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Audio Capture** | PyAudioWPatch + sounddevice | WASAPI loopback for system audio |
| **Transcription** | faster-whisper (large-v2) | GPU-accelerated speech-to-text |
| **Summarization** | Ollama + LLaMA 3.1 8B | Local LLM for meeting notes |
| **PDF Generation** | fpdf2 | Professional document export |
| **GUI** | Tkinter | Lightweight floating interface |
| **Email** | smtplib (Gmail SMTP) | Automated delivery |

---

## 📋 Requirements

### Hardware
- **GPU**: NVIDIA GPU with 6GB+ VRAM (RTX 3060+ recommended)
- **RAM**: 16GB+ recommended
- **Storage**: ~10GB for models

### Software
- Windows 10/11
- Python 3.10+
- CUDA Toolkit 11.8+
- [Ollama](https://ollama.ai/) installed and running

---

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/AI-Note-Taker.git
cd AI-Note-Taker
```

### 2. Create Conda Environment
```bash
conda create -n ai-note-taker python=3.10 -y
conda activate ai-note-taker
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Ollama & Model
```bash
# Download Ollama from https://ollama.ai/
ollama pull llama3.1:8b
ollama serve  # Keep running in background
```

### 5. Configure (Optional)
Edit `config.json` to customize:
```json
{
  "whisper": {
    "model": "large-v2",
    "device": "cuda"
  },
  "email": {
    "enabled": true,
    "recipient_email": "your@email.com"
  }
}
```

### 6. Run
```bash
python meeting_recorder.py
```
Or use the desktop shortcut: `Start_Meeting_Recorder.vbs`

---

## 📖 Usage

### Quick Start
1. **Launch** the application
2. **Enter** meeting title (optional)
3. **Select** meeting type and summary length
4. **Click ● REC** to start recording
5. **Click ■ STOP** when meeting ends
6. **Wait** for automatic processing
7. **Check** your email or recordings folder

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

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Meeting Note Taker                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Audio      │    │   Whisper    │    │   Ollama     │  │
│  │   Capture    │───▶│   (GPU)      │───▶│   (LLaMA)    │  │
│  │              │    │              │    │              │  │
│  │ • Mic Input  │    │ • STT        │    │ • Summarize  │  │
│  │ • Loopback   │    │ • Language   │    │ • Structure  │  │
│  │ • Mixing     │    │   Detection  │    │ • Extract    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    Output Pipeline                    │  │
│  │  • audio.wav → transcript.txt → MoM.md → MoM.pdf     │  │
│  │  • action_items.md extraction                         │  │
│  │  • Email delivery (optional)                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
AI-Note-Taker/
├── src/
│   └── meeting_recorder.py    # Main application
├── docs/
│   ├── ARCHITECTURE.md        # Technical documentation
│   └── SETUP.md              # Detailed setup guide
├── notebooks/
│   └── experiments.ipynb      # Model experiments
├── recordings/                # Output directory
├── config.json               # Configuration file
├── requirements.txt          # Python dependencies
├── LICENSE                   # MIT License
├── CONTRIBUTING.md           # Contribution guidelines
└── README.md                 # This file
```

---

## ⚙️ Configuration

### config.json Reference

```json
{
  "recording": {
    "output_dir": "recordings",
    "sample_rate": 16000
  },
  "whisper": {
    "model": "large-v2",      // tiny, base, small, medium, large-v2
    "device": "cuda",          // cuda or cpu
    "compute_type": "float16"  // float16, int8, int8_float16
  },
  "ollama": {
    "model": "llama3.1:8b",   // Any Ollama model
    "temperature": 0.3,
    "context_window": 8192
  },
  "email": {
    "enabled": true,
    "sender_email": "your@gmail.com",
    "sender_password": "app_password",  // Gmail App Password
    "recipient_email": "recipient@email.com"
  }
}
```

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
git clone https://github.com/yourusername/AI-Note-Taker.git
cd AI-Note-Taker
git checkout -b feature/your-feature-name
```

### Branching Strategy
- `main` - Stable production releases
- `develop` - Integration branch for features
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Urgent production fixes

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| Transcription Speed | ~10x real-time (RTX 4060) |
| Summarization Time | ~30-60 seconds |
| Memory Usage | ~4GB VRAM |
| Accuracy | 95%+ (English) |

---

## 🗺️ Roadmap

- [x] Multi-device audio capture
- [x] 6 meeting type templates
- [x] PDF export
- [x] Action item tracking
- [ ] Speaker diarization (who said what)
- [ ] Search across past meetings
- [ ] Calendar integration
- [ ] Real-time transcription preview
- [ ] Multi-language support

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) - Optimized inference
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [PyAudioWPatch](https://github.com/s0d3s/PyAudioWPatch) - WASAPI loopback

---

<div align="center">

**Built with ❤️ for productive meetings**

[⬆ Back to Top](#-ai-meeting-note-taker)

</div>
