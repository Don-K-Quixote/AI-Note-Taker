# Detailed Setup Guide

This guide provides step-by-step instructions for setting up AI Meeting Note Taker on Windows.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [CUDA Setup](#2-cuda-setup)
3. [Python Environment](#3-python-environment)
4. [Ollama Installation](#4-ollama-installation)
5. [Application Setup](#5-application-setup)
6. [Email Configuration](#6-email-configuration)
7. [VS Code Integration](#7-vs-code-integration)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Prerequisites

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU | NVIDIA GTX 1060 6GB | RTX 3060 12GB+ |
| RAM | 8GB | 16GB+ |
| Storage | 10GB free | 20GB+ free |
| OS | Windows 10 | Windows 11 |

### Software Requirements

- Windows 10/11 (64-bit)
- NVIDIA GPU with CUDA support
- Python 3.10 or 3.11
- Git

---

## 2. CUDA Setup

### 2.1 Check GPU Compatibility

Open Command Prompt and run:
```cmd
nvidia-smi
```

You should see your GPU model and driver version. If not, install NVIDIA drivers first.

### 2.2 Install CUDA Toolkit

1. Download CUDA Toolkit 11.8 from [NVIDIA CUDA Downloads](https://developer.nvidia.com/cuda-11-8-0-download-archive)
2. Choose: Windows → x86_64 → 11 → exe (local)
3. Run installer with default options
4. Restart your computer

### 2.3 Install cuDNN

1. Download cuDNN from [NVIDIA cuDNN](https://developer.nvidia.com/cudnn) (requires NVIDIA account)
2. Extract the ZIP file
3. Copy files to CUDA installation:
   ```
   Copy cudnn\bin\*.dll     → C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin\
   Copy cudnn\include\*.h   → C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\include\
   Copy cudnn\lib\x64\*.lib → C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\lib\x64\
   ```

### 2.4 Verify CUDA Installation

```cmd
nvcc --version
```

Expected output:
```
nvcc: NVIDIA (R) Cuda compiler driver
Cuda compilation tools, release 11.8, V11.8.xxx
```

---

## 3. Python Environment

### 3.1 Install Miniconda

1. Download from [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
2. Run installer
3. Check "Add to PATH" option
4. Restart terminal

### 3.2 Create Conda Environment

```cmd
conda create -n ai-note-taker python=3.10 -y
conda activate ai-note-taker
```

### 3.3 Install PyTorch with CUDA

```cmd
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 3.4 Verify PyTorch CUDA

```python
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

Expected output: `CUDA available: True`

---

## 4. Ollama Installation

### 4.1 Install Ollama

1. Download from [ollama.ai](https://ollama.ai/)
2. Run the installer
3. Ollama runs as a system service

### 4.2 Pull LLaMA Model

```cmd
ollama pull llama3.1:8b
```

This downloads ~4.7GB. Wait for completion.

### 4.3 Verify Ollama

```cmd
ollama list
```

You should see `llama3.1:8b` in the list.

### 4.4 Test Ollama

```cmd
curl http://localhost:11434/api/generate -d "{\"model\": \"llama3.1:8b\", \"prompt\": \"Hello\", \"stream\": false}"
```

---

## 5. Application Setup

### 5.1 Clone Repository

```cmd
cd C:\Users\YourUsername\Projects
git clone https://github.com/yourusername/AI-Note-Taker.git
cd AI-Note-Taker
```

### 5.2 Install Dependencies

```cmd
conda activate ai-note-taker
pip install -r requirements.txt
```

### 5.3 First Run (Model Download)

The first run will download the Whisper model (~3GB):

```cmd
python meeting_recorder.py
```

Wait for "Meeting Note Taker - Ready" message.

### 5.4 Create Desktop Shortcut

1. Right-click `Start_Meeting_Recorder.vbs`
2. Select "Create shortcut"
3. Move shortcut to Desktop
4. (Optional) Right-click → Properties → Change Icon

---

## 6. Email Configuration

### 6.1 Create Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification (if not already)
3. Go to "App passwords"
4. Select "Mail" and "Windows Computer"
5. Click "Generate"
6. Copy the 16-character password

### 6.2 Update config.json

```json
{
  "email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your.email@gmail.com",
    "sender_password": "xxxx xxxx xxxx xxxx",
    "recipient_email": "recipient@email.com"
  }
}
```

### 6.3 Test Email

Record a short test meeting and verify email delivery.

---

## 7. VS Code Integration

### 7.1 Install VS Code

Download from [code.visualstudio.com](https://code.visualstudio.com/)

### 7.2 Install Extensions

Open VS Code and install:
- **Python** (Microsoft)
- **GitLens** (GitKraken)
- **Git Graph** (mhutchie)
- **Markdown Preview Enhanced** (Yiyi Wang)

### 7.3 Open Project in VS Code

```cmd
cd C:\Users\YourUsername\Projects\AI-Note-Taker
code .
```

### 7.4 Configure Python Interpreter

1. Press `Ctrl+Shift+P`
2. Type "Python: Select Interpreter"
3. Choose `ai-note-taker` conda environment

### 7.5 Git Integration

VS Code automatically detects the `.git` folder. You'll see:
- Source Control icon in sidebar (Ctrl+Shift+G)
- Branch name in status bar
- Changed files highlighting

### 7.6 Useful Git Commands in VS Code

| Action | Method |
|--------|--------|
| View changes | Click file in Source Control |
| Stage changes | Click `+` on file |
| Commit | Enter message, click ✓ |
| Push | Click `...` → Push |
| Pull | Click `...` → Pull |
| Switch branch | Click branch name in status bar |
| Create branch | Click branch → Create new branch |

### 7.7 Terminal Integration

Open integrated terminal: `` Ctrl+` ``

Set default terminal to Command Prompt:
1. `Ctrl+Shift+P` → "Terminal: Select Default Profile"
2. Choose "Command Prompt"

---

## 8. Troubleshooting

### CUDA Not Available

**Symptom**: `CUDA available: False`

**Solutions**:
1. Verify NVIDIA driver: `nvidia-smi`
2. Reinstall PyTorch with CUDA:
   ```cmd
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```
3. Check CUDA version matches PyTorch version

### Ollama Connection Error

**Symptom**: `Cannot connect to Ollama`

**Solutions**:
1. Check Ollama is running: `ollama list`
2. Start Ollama service: `ollama serve`
3. Check port: `netstat -an | findstr 11434`

### No Audio Captured

**Symptom**: Empty transcript

**Solutions**:
1. Check Windows default audio output device
2. Verify correct loopback device selected
3. Test audio is playing through selected speaker
4. Check volume isn't muted

### PDF Export Fails

**Symptom**: `PDF export failed`

**Solutions**:
1. Install fpdf2: `pip install fpdf2`
2. Check for special characters in meeting content
3. Verify write permissions to output folder

### Import Errors

**Symptom**: `ModuleNotFoundError`

**Solutions**:
1. Activate conda environment: `conda activate ai-note-taker`
2. Reinstall requirements: `pip install -r requirements.txt`
3. Check Python version: `python --version` (should be 3.10+)

### Out of GPU Memory

**Symptom**: `CUDA out of memory`

**Solutions**:
1. Close other GPU applications
2. Use smaller Whisper model in config.json:
   ```json
   "whisper": {
     "model": "medium"  // Instead of large-v2
   }
   ```
3. Use `int8` compute type:
   ```json
   "whisper": {
     "compute_type": "int8"
   }
   ```

---

## Quick Reference

### Start Application
```cmd
conda activate ai-note-taker
cd C:\Users\YourUsername\Projects\AI-Note-Taker
python meeting_recorder.py
```

### Update Application
```cmd
cd C:\Users\YourUsername\Projects\AI-Note-Taker
git pull origin main
pip install -r requirements.txt
```

### Check GPU Status
```cmd
nvidia-smi
```

### Check Ollama Status
```cmd
ollama list
curl http://localhost:11434/api/tags
```

---

## Support

If you encounter issues not covered here:
1. Check [GitHub Issues](https://github.com/yourusername/AI-Note-Taker/issues)
2. Open a new issue with:
   - Error message
   - Steps to reproduce
   - System info (GPU, OS, Python version)
