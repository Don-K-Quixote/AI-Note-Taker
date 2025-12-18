# Contributing to AI Meeting Note Taker

Thank you for your interest in contributing to AI Meeting Note Taker! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Branching Strategy](#branching-strategy)
- [Making Changes](#making-changes)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Development Guidelines](#development-guidelines)

---

## Code of Conduct

Please be respectful and constructive in all interactions. We're all here to build something useful together.

---

## Getting Started

### 1. Fork the Repository
Click the "Fork" button on GitHub to create your own copy.

### 2. Clone Your Fork
```bash
git clone https://github.com/YOUR_USERNAME/AI-Note-Taker.git
cd AI-Note-Taker
```

### 3. Set Up Upstream Remote
```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/AI-Note-Taker.git
```

### 4. Create Development Environment
```bash
conda create -n ai-note-taker-dev python=3.10 -y
conda activate ai-note-taker-dev
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

---

## Branching Strategy

We follow a modified Git Flow strategy:

```
main (stable)
  │
  └── develop (integration)
        │
        ├── feature/audio-improvements
        ├── feature/speaker-diarization
        ├── bugfix/pdf-export-encoding
        └── hotfix/critical-crash-fix
```

### Branch Types

| Branch | Purpose | Base | Merge To |
|--------|---------|------|----------|
| `main` | Stable production releases | - | - |
| `develop` | Integration branch | `main` | `main` |
| `feature/*` | New features | `develop` | `develop` |
| `bugfix/*` | Bug fixes | `develop` | `develop` |
| `hotfix/*` | Urgent production fixes | `main` | `main` & `develop` |
| `docs/*` | Documentation updates | `develop` | `develop` |
| `refactor/*` | Code refactoring | `develop` | `develop` |

### Branch Naming Convention

```
feature/short-description
bugfix/issue-number-description
hotfix/critical-fix-description
docs/update-readme
refactor/audio-module
```

**Examples:**
- `feature/speaker-diarization`
- `feature/calendar-integration`
- `bugfix/123-pdf-encoding-error`
- `hotfix/audio-capture-crash`
- `docs/installation-guide`
- `refactor/split-audio-module`

---

## Making Changes

### 1. Sync with Upstream
```bash
git checkout develop
git fetch upstream
git merge upstream/develop
```

### 2. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Make Your Changes
- Write clean, documented code
- Follow existing code style
- Add tests if applicable
- Update documentation

### 4. Test Locally
```bash
# Run the application
python meeting_recorder.py

# Test your specific feature
```

### 5. Commit Your Changes
```bash
git add .
git commit -m "feat: add speaker diarization support"
```

---

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

### Format
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, missing semicolons, etc. |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf` | Performance improvement |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks |

### Examples

```bash
# Feature
git commit -m "feat(audio): add support for Bluetooth headphones"

# Bug fix
git commit -m "fix(pdf): resolve encoding error for special characters"

# Documentation
git commit -m "docs: update installation guide for CUDA 12"

# Refactor
git commit -m "refactor(transcription): split whisper module into separate file"

# With body
git commit -m "feat(ui): add device selection dropdown

- Auto-detect Windows default audio output
- Filter virtual devices (Voicemeeter, etc.)
- Show device selection in floating button UI

Closes #42"
```

---

## Pull Request Process

### 1. Push Your Branch
```bash
git push origin feature/your-feature-name
```

### 2. Create Pull Request
- Go to GitHub and create a PR from your branch to `develop`
- Fill out the PR template
- Link related issues

### 3. PR Title Format
```
feat(scope): Short description
fix(scope): Short description
```

### 4. PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation
- [ ] Refactoring

## Testing
How was this tested?

## Screenshots (if applicable)

## Checklist
- [ ] Code follows project style
- [ ] Self-reviewed my code
- [ ] Added comments for complex logic
- [ ] Updated documentation
- [ ] No new warnings
```

### 5. Review Process
- At least one approval required
- All CI checks must pass
- Address reviewer feedback

### 6. Merge
- Squash and merge for features
- Rebase and merge for bugfixes

---

## Development Guidelines

### Code Style

```python
# Good: Descriptive names, type hints, docstrings
def transcribe_audio(audio_path: Path, language: str = None) -> dict:
    """
    Transcribe audio file using Whisper.
    
    Args:
        audio_path: Path to the audio file
        language: Optional language code (auto-detect if None)
    
    Returns:
        Dictionary with 'text' and 'duration' keys
    """
    pass

# Bad: Unclear names, no documentation
def trans(p, l=None):
    pass
```

### File Organization

```
src/
├── __init__.py
├── audio/
│   ├── __init__.py
│   ├── capture.py      # Audio recording
│   └── devices.py      # Device management
├── transcription/
│   ├── __init__.py
│   └── whisper.py      # Whisper integration
├── summarization/
│   ├── __init__.py
│   ├── ollama.py       # Ollama client
│   └── templates.py    # Meeting templates
├── export/
│   ├── __init__.py
│   ├── pdf.py          # PDF generation
│   └── email.py        # Email sending
└── ui/
    ├── __init__.py
    └── floating_button.py
```

### Error Handling

```python
# Good: Specific exceptions with context
try:
    result = whisper_model.transcribe(audio_path)
except FileNotFoundError:
    logger.error(f"Audio file not found: {audio_path}")
    raise
except RuntimeError as e:
    logger.error(f"Transcription failed: {e}")
    return {"text": "", "error": str(e)}

# Bad: Catch-all exception
try:
    result = whisper_model.transcribe(audio_path)
except:
    pass
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate levels
logger.debug("Processing audio chunk")
logger.info("Recording started")
logger.warning("No loopback device found")
logger.error("Transcription failed")
```

---

## Feature Requests & Bug Reports

### Feature Request
1. Check existing issues first
2. Open a new issue with `[Feature]` prefix
3. Describe the use case and proposed solution

### Bug Report
1. Check existing issues first
2. Open a new issue with `[Bug]` prefix
3. Include:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - System info (OS, Python version, GPU)
   - Error logs

---

## Questions?

Feel free to open a Discussion on GitHub or reach out via issues.

---

Thank you for contributing! 🎉
