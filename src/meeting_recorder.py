"""
Invisible Meeting Note Taker - Full Pipeline
Records meeting → Transcribes with Whisper → Generates MoM → Emails to you

Click the floating button to start/stop recording
"""

import os
import sys
import wave
import threading
import queue
import time
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from pathlib import Path

import numpy as np
import sounddevice as sd
import pyaudiowpatch as pyaudio
import requests
from faster_whisper import WhisperModel


# ============================================================
# CONFIGURATION - Edit config.json or these defaults
# ============================================================
DEFAULT_CONFIG = {
    "recording": {
        "output_dir": "recordings",
        "sample_rate": 16000,
        "hotkey": "ctrl+alt+r"
    },
    "whisper": {
        "model": "large-v2",
        "device": "cuda",
        "compute_type": "float16",
        "language": None
    },
    "ollama": {
        "model": "llama3.1:8b",
        "url": "http://localhost:11434/api/generate",
        "temperature": 0.3,
        "context_window": 8192
    },
    "email": {
        "enabled": True,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "khalidadroit@gmail.com",
        "sender_password": "YOUR_APP_PASSWORD_HERE",
        "recipient_email": "khalidadroit@gmail.com"
    }
}


def load_config() -> dict:
    """Load configuration from config.json or use defaults."""
    config_path = Path(__file__).parent / "config.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            user_config = json.load(f)
            # Merge with defaults
            config = DEFAULT_CONFIG.copy()
            for key, value in user_config.items():
                if isinstance(value, dict) and key in config:
                    config[key].update(value)
                else:
                    config[key] = value
            return config
    return DEFAULT_CONFIG


CONFIG = load_config()


# ============================================================
# MEETING MINUTES TEMPLATES
# ============================================================
MEETING_TYPES = [
    "Business Meeting",
    "Tutorial/Training",
    "Interview",
    "Brainstorm",
    "1:1 / Check-in",
    "Presentation/Demo"
]

MOM_TEMPLATES = {
    "Business Meeting": """You are a professional meeting minutes (MoM) generator. Analyze the following meeting transcript and create comprehensive, structured minutes.

## Instructions:
- Extract ALL important information from the transcript
- If information for a section isn't available, write "None discussed"
- Be thorough but concise
- Use professional business language

## Output Format (use exactly this structure):

# Minutes of Meeting
**Date:** {date}
**Duration:** {duration}
**Type:** Business Meeting

---

## Agenda
[List the main topics/purposes of the meeting based on what was discussed]
- Topic 1
- Topic 2

## Attendees & Participants
[List people who spoke or were mentioned]
- Name / Role (if mentioned)

## Discussion Summary
[Summarize key discussion points for each topic]

### [Topic 1]
- Key points discussed
- Different viewpoints mentioned

## Decisions Made
[List ALL decisions made during the meeting]
1. Decision 1 - Context/Rationale
2. Decision 2 - Context/Rationale

## Action Items
| # | Action Item | Owner | Deadline | Priority |
|---|-------------|-------|----------|----------|
| 1 | [Task] | [Person] | [Date] | [High/Med/Low] |

## Key Metrics & Numbers
[Any budgets, targets, percentages, figures mentioned]
- Metric: Value

## Risks & Concerns
[Issues raised, blockers, warnings]
- Risk/Concern: Impact

## Open Questions
[Questions that need answers or follow-up]
- Question 1
- Question 2

## Parking Lot
[Topics deferred for later discussion]
- Topic deferred

## Key Quotes
[Important statements worth noting verbatim]
- "[Quote]" - Person

## Next Meeting
[Date/time if mentioned, or topics for follow-up]

---
## Transcript:
{transcript}
---
Generate the meeting minutes now:""",

    "Tutorial/Training": """You are an educational content summarizer. Analyze the following tutorial/training transcript and create comprehensive learning notes.

## Instructions:
- Capture ALL key concepts and learning points
- Include step-by-step instructions if demonstrated
- Note examples and best practices
- Be thorough - this is for learning reference

## Output Format (use exactly this structure):

# Tutorial/Training Notes
**Date:** {date}
**Duration:** {duration}
**Type:** Tutorial/Training

---

## Topic Overview
[What is this tutorial about - main subject and objectives]

## Key Concepts
[List and explain each important concept covered]

### Concept 1: [Name]
- **Definition:** What it is
- **Why it matters:** Importance/use case
- **Key points:** Details to remember

### Concept 2: [Name]
- **Definition:** What it is
- **Why it matters:** Importance/use case
- **Key points:** Details to remember

## Step-by-Step Instructions
[If any procedures were demonstrated]

### [Procedure Name]
1. Step 1 - Details
2. Step 2 - Details
3. Step 3 - Details

## Examples Covered
[Specific examples used to illustrate concepts]
- **Example 1:** Description and outcome
- **Example 2:** Description and outcome

## Tips & Best Practices
[Advice, shortcuts, recommendations shared]
- Tip 1
- Tip 2

## Common Mistakes to Avoid
[Pitfalls or errors mentioned]
- Mistake 1: Why it's problematic
- Mistake 2: Why it's problematic

## Tools & Resources Mentioned
[Software, websites, books, tools referenced]
- Resource: Description/Link

## Q&A Summary
[Questions asked and answers given]
- **Q:** Question
- **A:** Answer

## Practice Exercises
[Any homework or practice suggested]
- Exercise 1

## Key Takeaways
[Top 3-5 most important points to remember]
1. Takeaway 1
2. Takeaway 2

## Further Learning
[Topics suggested for deeper study]
- Topic for further exploration

---
## Transcript:
{transcript}
---
Generate the tutorial notes now:""",

    "Interview": """You are an interview summarizer. Analyze the following interview transcript and create a structured interview summary.

## Instructions:
- Capture candidate responses accurately
- Note strengths and areas of concern
- Be objective and factual
- Include specific examples given by candidate

## Output Format (use exactly this structure):

# Interview Summary
**Date:** {date}
**Duration:** {duration}
**Type:** Interview

---

## Candidate Information
- **Name:** [If mentioned]
- **Position Applied For:** [If mentioned]
- **Background:** [Brief summary if discussed]

## Interview Questions & Responses

### Question 1: [Question asked]
- **Response Summary:** Key points from answer
- **Examples Given:** Specific examples mentioned
- **Assessment:** Strong/Adequate/Weak

### Question 2: [Question asked]
- **Response Summary:** Key points from answer
- **Examples Given:** Specific examples mentioned
- **Assessment:** Strong/Adequate/Weak

## Technical/Skills Assessment
[If technical questions were asked]
- Skill 1: Assessment
- Skill 2: Assessment

## Strengths Observed
[Positive qualities demonstrated]
1. Strength with evidence
2. Strength with evidence

## Areas of Concern
[Potential issues or gaps noted]
1. Concern with context
2. Concern with context

## Cultural Fit Indicators
[Alignment with team/company values]
- Positive indicators
- Potential misalignments

## Candidate Questions
[Questions the candidate asked]
- Question 1
- Question 2

## Red Flags
[Any warning signs if present]
- Red flag if any

## Overall Impression
[General assessment of the candidate]

## Recommendation
[ ] Strong Hire
[ ] Hire
[ ] Maybe
[ ] No Hire

**Rationale:** [Brief explanation]

## Follow-up Items
[Next steps, additional interviews needed, references to check]

---
## Transcript:
{transcript}
---
Generate the interview summary now:""",

    "Brainstorm": """You are a brainstorming session summarizer. Analyze the following brainstorm transcript and organize all ideas generated.

## Instructions:
- Capture ALL ideas mentioned, even brief ones
- Group related ideas into themes
- Note any evaluation or voting that occurred
- Preserve creative ideas without judgment

## Output Format (use exactly this structure):

# Brainstorm Summary
**Date:** {date}
**Duration:** {duration}
**Type:** Brainstorming Session

---

## Session Objective
[What problem or opportunity was being brainstormed]

## Participants
[People who contributed ideas]

## All Ideas Generated
[Complete list of every idea mentioned]

### Theme 1: [Category Name]
1. Idea - Brief description
2. Idea - Brief description

### Theme 2: [Category Name]
1. Idea - Brief description
2. Idea - Brief description

### Uncategorized Ideas
- Idea that doesn't fit a theme

## Idea Evaluation
[If ideas were discussed/evaluated]

| Idea | Pros | Cons | Feasibility |
|------|------|------|-------------|
| Idea 1 | Benefits | Drawbacks | High/Med/Low |

## Top Ideas Selected
[Ideas that got most support or were chosen]
1. **Idea Name:** Why it was selected
2. **Idea Name:** Why it was selected

## Ideas for Further Exploration
[Promising ideas needing more research]
- Idea: What needs to be explored

## Parked Ideas
[Ideas saved for later consideration]
- Idea: Why parked

## Constraints Identified
[Limitations or boundaries mentioned]
- Constraint 1
- Constraint 2

## Resources Needed
[What would be required to implement top ideas]
- Resource 1
- Resource 2

## Next Steps
[Actions to move forward with selected ideas]
| Action | Owner | Timeline |
|--------|-------|----------|
| Action 1 | Person | Date |

## Wild Cards
[Unusual or out-of-the-box ideas worth remembering]
- Creative idea

---
## Transcript:
{transcript}
---
Generate the brainstorm summary now:""",

    "1:1 / Check-in": """You are a 1:1 meeting summarizer. Analyze the following check-in transcript and create a structured summary.

## Instructions:
- Capture updates, feedback, and concerns
- Note action items and commitments
- Be concise but thorough
- Maintain confidentiality tone

## Output Format (use exactly this structure):

# 1:1 Check-in Summary
**Date:** {date}
**Duration:** {duration}
**Type:** 1:1 / Check-in

---

## Participants
- [Person 1]
- [Person 2]

## Updates & Progress
[What was shared about current work]

### Project/Task Updates
- **[Project 1]:** Status and progress
- **[Project 2]:** Status and progress

### Wins & Accomplishments
[Successes mentioned]
- Win 1
- Win 2

## Challenges & Blockers
[Issues being faced]
- **Blocker 1:** Description and impact
- **Blocker 2:** Description and impact

## Support Needed
[Help or resources requested]
- Request 1
- Request 2

## Feedback Shared
[Feedback given in either direction]

### Positive Feedback
- Feedback point

### Constructive Feedback
- Feedback point

## Goals & Priorities
[What to focus on going forward]

### Short-term (This Week/Sprint)
- Priority 1
- Priority 2

### Long-term
- Goal 1

## Career & Development
[Growth, learning, career discussions if any]
- Discussion point

## Personal/Wellbeing Check
[If work-life balance or wellbeing was discussed]
- Notes

## Action Items
| Action | Owner | Due Date |
|--------|-------|----------|
| Action 1 | Person | Date |

## Follow-ups for Next 1:1
[Topics to revisit]
- Topic 1

---
## Transcript:
{transcript}
---
Generate the 1:1 summary now:""",

    "Presentation/Demo": """You are a presentation/demo summarizer. Analyze the following presentation transcript and create comprehensive notes.

## Instructions:
- Capture all key points presented
- Note features or capabilities demonstrated
- Include audience questions and feedback
- Be thorough for those who missed it

## Output Format (use exactly this structure):

# Presentation/Demo Summary
**Date:** {date}
**Duration:** {duration}
**Type:** Presentation/Demo

---

## Presentation Overview
- **Title/Topic:** [Main subject]
- **Presenter(s):** [Who presented]
- **Audience:** [Who attended, if mentioned]
- **Objective:** [Purpose of the presentation]

## Executive Summary
[2-3 sentence overview of the entire presentation]

## Key Points Presented

### Section 1: [Topic]
- Main point
- Supporting details
- Data/Evidence shared

### Section 2: [Topic]
- Main point
- Supporting details
- Data/Evidence shared

## Features/Capabilities Demonstrated
[If this was a product demo]

| Feature | Description | Benefit |
|---------|-------------|---------|
| Feature 1 | What it does | Why it matters |

## Live Demo Notes
[What was shown during demonstration]
1. Demo step 1 - What was shown
2. Demo step 2 - What was shown

## Data & Statistics Shared
[Numbers, metrics, research cited]
- Statistic 1
- Statistic 2

## Visuals & Diagrams Described
[Key visuals that were shown]
- Slide/Visual: What it illustrated

## Audience Questions
[Q&A session content]

| Question | Answer |
|----------|--------|
| Question 1 | Response |

## Audience Feedback
[Reactions, comments, concerns raised]
- Positive feedback
- Concerns/Pushback

## Call to Action
[What the presenter asked audience to do]
- Action requested

## Resources & Links Shared
[Materials, links, documents mentioned]
- Resource 1

## Key Takeaways
[Most important points to remember]
1. Takeaway 1
2. Takeaway 2
3. Takeaway 3

## Follow-up Items
[Next steps, additional info promised]
| Item | Owner | Timeline |
|------|-------|----------|
| Follow-up 1 | Person | Date |

---
## Transcript:
{transcript}
---
Generate the presentation summary now:"""
}


# ============================================================
# AUDIO RECORDER
# ============================================================
class AudioRecorder:
    # Virtual/fake devices to skip
    SKIP_KEYWORDS = [
        "VB-Audio", "Virtual Cable", "CABLE", 
        "Voicemeeter", "VoiceMeeter",
        "Aux", "AUX",
        "Line 1", "Line 2",  # Voicemeeter lines
        "Virtual", "VAC",    # Virtual Audio Cable
        "EPSON", "iProjection",  # Projector audio
    ]
    
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or CONFIG["recording"]["output_dir"])
        self.output_dir.mkdir(exist_ok=True)
        
        self.is_recording = False
        self.sample_rate = CONFIG["recording"]["sample_rate"]
        self.channels = 1
        
        self.mic_queue = queue.Queue()
        self.system_queue = queue.Queue()
        self.mixed_audio = []
        
        self.mic_thread = None
        self.system_thread = None
        self.mixer_thread = None
        self.stop_event = threading.Event()
        
        self.pa = pyaudio.PyAudio()
        self.available_devices = self._get_filtered_loopback_devices()
        self.loopback_device = self._auto_select_device()
        
        self.current_filename = ""
        self.current_meeting_folder = None
        self.recording_start_time = None
    
    def _get_filtered_loopback_devices(self) -> list:
        """Get list of real loopback devices (filtered)."""
        try:
            loopback_devices = []
            for i in range(self.pa.get_device_count()):
                try:
                    dev = self.pa.get_device_info_by_index(i)
                    if dev.get("isLoopbackDevice", False):
                        # Check if it's a real device (not virtual)
                        if not any(skip.lower() in dev["name"].lower() for skip in self.SKIP_KEYWORDS):
                            loopback_devices.append(dev)
                except Exception:
                    continue
            return loopback_devices
        except Exception as e:
            print(f"Error getting loopback devices: {e}")
            return []
    
    def _auto_select_device(self) -> dict | None:
        """Automatically select loopback device matching Windows default output."""
        if not self.available_devices:
            return None
        
        try:
            # Get Windows default output device
            default_output = self.pa.get_default_output_device_info()
            default_name = default_output.get("name", "")
            print(f"\nWindows default audio output: {default_name}")
            
            # Find matching loopback device
            # The loopback device name usually contains the output device name
            for dev in self.available_devices:
                # Extract base name (remove [Loopback] suffix for comparison)
                loopback_name = dev["name"].replace(" [Loopback]", "")
                
                # Check if names match (loopback name contains default name or vice versa)
                if (default_name.lower() in loopback_name.lower() or 
                    loopback_name.lower() in default_name.lower()):
                    print(f">>> Auto-selected matching loopback: {dev['name']}")
                    return dev
            
            # Fallback to first available device
            print(f">>> No exact match found, using: {self.available_devices[0]['name']}")
            return self.available_devices[0]
            
        except Exception as e:
            print(f"Auto-detection failed: {e}")
            if self.available_devices:
                return self.available_devices[0]
            return None
    
    def refresh_default_device(self):
        """Refresh and auto-select based on current Windows default."""
        old_device = self.loopback_device
        self.loopback_device = self._auto_select_device()
        if self.loopback_device != old_device:
            print(f"Device changed to: {self.loopback_device['name'] if self.loopback_device else 'None'}")
        return self.loopback_device
    
    def get_device_names(self) -> list:
        """Get list of available device names for UI dropdown."""
        return [dev["name"] for dev in self.available_devices]
    
    def set_loopback_device(self, device_name: str):
        """Set the loopback device by name."""
        for dev in self.available_devices:
            if dev["name"] == device_name:
                self.loopback_device = dev
                print(f">>> Loopback device set to: {device_name}")
                return True
        print(f"Warning: Device '{device_name}' not found")
        return False
    
    def _record_microphone(self):
        """Record from default microphone."""
        def callback(indata, frames, time_info, status):
            if status:
                print(f"Mic status: {status}")
            self.mic_queue.put(indata.copy())
        
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32,
                callback=callback,
                blocksize=1024
            ):
                while not self.stop_event.is_set():
                    time.sleep(0.1)
        except Exception as e:
            print(f"Microphone error: {e}")
    
    def _record_system_audio(self):
        """Record system audio via WASAPI loopback."""
        if not self.loopback_device:
            print("No loopback device - system audio won't be captured")
            return
        
        device_sample_rate = int(self.loopback_device["defaultSampleRate"])
        device_channels = self.loopback_device["maxInputChannels"]
        
        try:
            stream = self.pa.open(
                format=pyaudio.paFloat32,
                channels=device_channels,
                rate=device_sample_rate,
                input=True,
                input_device_index=self.loopback_device["index"],
                frames_per_buffer=1024
            )
            
            while not self.stop_event.is_set():
                data = stream.read(1024, exception_on_overflow=False)
                audio_np = np.frombuffer(data, dtype=np.float32)
                
                if device_channels > 1:
                    audio_np = audio_np.reshape(-1, device_channels).mean(axis=1)
                
                if device_sample_rate != self.sample_rate:
                    ratio = self.sample_rate / device_sample_rate
                    new_length = int(len(audio_np) * ratio)
                    indices = np.linspace(0, len(audio_np) - 1, new_length)
                    audio_np = np.interp(indices, np.arange(len(audio_np)), audio_np)
                
                self.system_queue.put(audio_np.astype(np.float32))
            
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            print(f"System audio error: {e}")
    
    def _mix_audio(self):
        """Mix microphone and system audio streams."""
        while not self.stop_event.is_set():
            mic_data = []
            system_data = []
            
            while not self.mic_queue.empty():
                try:
                    mic_data.append(self.mic_queue.get_nowait().flatten())
                except queue.Empty:
                    break
            
            while not self.system_queue.empty():
                try:
                    system_data.append(self.system_queue.get_nowait())
                except queue.Empty:
                    break
            
            if mic_data or system_data:
                mic_chunk = np.concatenate(mic_data) if mic_data else np.array([])
                sys_chunk = np.concatenate(system_data) if system_data else np.array([])
                
                max_len = max(len(mic_chunk), len(sys_chunk))
                if max_len > 0:
                    if len(mic_chunk) < max_len:
                        mic_chunk = np.pad(mic_chunk, (0, max_len - len(mic_chunk)))
                    if len(sys_chunk) < max_len:
                        sys_chunk = np.pad(sys_chunk, (0, max_len - len(sys_chunk)))
                    
                    mixed = (mic_chunk * 0.5 + sys_chunk * 0.5)
                    
                    max_val = np.max(np.abs(mixed))
                    if max_val > 1.0:
                        mixed = mixed / max_val
                    
                    self.mixed_audio.append(mixed)
            
            time.sleep(0.05)
    
    def start_recording(self, title: str = None) -> str:
        """Start recording audio from all sources."""
        if self.is_recording:
            return ""
        
        self.is_recording = True
        self.stop_event.clear()
        self.mixed_audio = []
        self.recording_start_time = datetime.now()
        
        while not self.mic_queue.empty():
            self.mic_queue.get()
        while not self.system_queue.empty():
            self.system_queue.get()
        
        self.mic_thread = threading.Thread(target=self._record_microphone, daemon=True)
        self.system_thread = threading.Thread(target=self._record_system_audio, daemon=True)
        self.mixer_thread = threading.Thread(target=self._mix_audio, daemon=True)
        
        self.mic_thread.start()
        self.system_thread.start()
        self.mixer_thread.start()
        
        # Create subfolder for this meeting
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if title:
            # Sanitize title for folder name
            safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)
            safe_title = safe_title[:50].strip()
            folder_name = safe_title
            
            # Add timestamp suffix if folder already exists
            if (self.output_dir / folder_name).exists():
                folder_name = f"{safe_title}_{timestamp}"
        else:
            folder_name = f"meeting_{timestamp}"
        
        self.current_meeting_folder = self.output_dir / folder_name
        self.current_meeting_folder.mkdir(exist_ok=True)
        self.current_filename = "audio.wav"
        
        print(f"Recording started: {self.current_meeting_folder}")
        return str(self.current_meeting_folder)
    
    def stop_recording(self) -> tuple[str, float]:
        """Stop recording and save to WAV file. Returns (filepath, duration)."""
        if not self.is_recording:
            return "", 0
        
        self.is_recording = False
        self.stop_event.set()
        
        if self.mic_thread:
            self.mic_thread.join(timeout=2)
        if self.system_thread:
            self.system_thread.join(timeout=2)
        if self.mixer_thread:
            self.mixer_thread.join(timeout=2)
        
        filepath = self.current_meeting_folder / self.current_filename
        duration = 0
        
        if self.mixed_audio:
            audio_data = np.concatenate(self.mixed_audio)
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            with wave.open(str(filepath), 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_int16.tobytes())
            
            duration = len(audio_data) / self.sample_rate
            print(f"Recording saved: {filepath} ({duration:.1f}s)")
        else:
            print("No audio recorded")
            # Remove empty folder
            self.current_meeting_folder.rmdir()
            return "", 0
        
        return str(filepath), duration
    
    def cleanup(self):
        """Clean up resources."""
        self.pa.terminate()


# ============================================================
# MEETING PROCESSOR
# ============================================================
class MeetingProcessor:
    def __init__(self):
        self.whisper = None
        self.ollama_url = CONFIG["ollama"]["url"]
        self.ollama_model = CONFIG["ollama"]["model"]
    
    def _ensure_whisper_loaded(self):
        """Load Whisper model on first use."""
        if self.whisper is None:
            print(f"Loading Whisper model '{CONFIG['whisper']['model']}' on {CONFIG['whisper']['device']}...")
            self.whisper = WhisperModel(
                CONFIG["whisper"]["model"],
                device=CONFIG["whisper"]["device"],
                compute_type=CONFIG["whisper"]["compute_type"]
            )
            print("Whisper model loaded.")
    
    def transcribe(self, audio_path: str) -> dict:
        """Transcribe audio file using Whisper."""
        self._ensure_whisper_loaded()
        print(f"Transcribing: {audio_path}")
        
        segments, info = self.whisper.transcribe(
            audio_path,
            language=CONFIG["whisper"]["language"],
            beam_size=5,
            word_timestamps=True,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500, speech_pad_ms=200)
        )
        
        print(f"Detected language: {info.language} (confidence: {info.language_probability:.2f})")
        
        transcript_segments = []
        full_text_parts = []
        
        for segment in segments:
            transcript_segments.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            })
            full_text_parts.append(segment.text.strip())
            mins, secs = int(segment.start // 60), int(segment.start % 60)
            print(f"  [{mins:02d}:{secs:02d}] {segment.text.strip()[:60]}...")
        
        return {
            "language": info.language,
            "duration": info.duration,
            "text": " ".join(full_text_parts),
            "segments": transcript_segments
        }
    
    def generate_mom(self, transcript: str, date: str, duration: str, 
                     meeting_type: str = "Business Meeting", summary_length: str = "Detailed") -> str:
        """Generate Minutes of Meeting using Ollama."""
        template = MOM_TEMPLATES.get(meeting_type, MOM_TEMPLATES["Business Meeting"])
        prompt = template.format(
            transcript=transcript,
            date=date,
            duration=duration
        )
        
        # Add brief instruction if selected
        if summary_length == "Brief":
            brief_instruction = """

IMPORTANT: Generate a BRIEF, CONCISE summary. Keep each section to 2-3 bullet points maximum. 
Focus only on the most critical information. Skip sections with no significant content.
Total output should be approximately 1 page."""
            prompt = prompt.replace("Generate the meeting minutes now:", 
                                   brief_instruction + "\n\nGenerate the meeting minutes now:")
        
        print(f"Generating MoM ({meeting_type}, {summary_length}) with {self.ollama_model}...")
        
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": CONFIG["ollama"]["temperature"],
                        "num_ctx": CONFIG["ollama"]["context_window"],
                        "top_p": 0.9
                    }
                },
                timeout=900
            )
            response.raise_for_status()
            return response.json().get("response", "Error: No response from Ollama")
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Make sure it's running (ollama serve)"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def process(self, audio_path: str, meeting_type: str = "Business Meeting", 
                summary_length: str = "Detailed", title: str = None) -> dict:
        """Full pipeline: transcribe and generate MoM."""
        audio_path = Path(audio_path)
        output_dir = audio_path.parent  # Meeting subfolder
        
        # Transcribe
        print("\n" + "="*60)
        print("STEP 1: Transcription")
        print("="*60)
        
        transcript_data = self.transcribe(str(audio_path))
        
        # Save transcript
        transcript_file = output_dir / "transcript.txt"
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write(transcript_data['text'])
        print(f"Transcript saved: {transcript_file}")
        
        # CHECK: Is transcript empty or too short?
        transcript_text = transcript_data['text'].strip()
        word_count = len(transcript_text.split())
        
        if not transcript_text or word_count < 10:
            print("\n" + "!"*60)
            print("WARNING: Transcript is empty or too short!")
            print(f"Words captured: {word_count}")
            print("This usually means:")
            print("  1. Audio was not captured from the correct device")
            print("  2. System audio (speaker) loopback is not working")
            print("  3. Meeting audio was very quiet or muted")
            print("!"*60)
            
            # Create error MoM instead of hallucinating
            error_mom = f"""# {title if title else 'Meeting Notes'}

## ⚠️ Transcription Failed

**Date:** {datetime.now().strftime("%B %d, %Y")}
**Duration:** {int(transcript_data['duration'] // 60)} minutes {int(transcript_data['duration'] % 60)} seconds

---

### Problem
No audio was captured from this meeting. The transcript is empty.

### Possible Causes
1. **Wrong audio device** - The system audio (loopback) device may not match your speaker
2. **Audio routing** - Meeting audio may be going to a different output device
3. **Volume too low** - Meeting audio was muted or very quiet

### How to Fix
1. Check which speaker your meeting audio is playing through
2. Run the recorder and check the terminal output for "Selected loopback device"
3. Ensure the loopback device matches your speaker (e.g., DELL S2725HS)

### Audio File
The audio file has been saved: `audio.wav`
You can play it to verify if any audio was captured.
"""
            mom_file = output_dir / "MoM.md"
            with open(mom_file, 'w', encoding='utf-8') as f:
                f.write(error_mom)
            
            return {
                "transcript_file": str(transcript_file),
                "mom_file": str(mom_file),
                "pdf_file": None,
                "mom_content": error_mom,
                "duration": transcript_data['duration'],
                "error": "Empty transcript - no audio captured"
            }
        
        # Generate MoM
        print("\n" + "="*60)
        print(f"STEP 2: Generating {meeting_type} Notes ({summary_length})")
        print("="*60)
        print("="*60)
        
        date_str = datetime.now().strftime("%B %d, %Y")
        duration_mins = int(transcript_data['duration'] // 60)
        duration_secs = int(transcript_data['duration'] % 60)
        duration_str = f"{duration_mins} minutes {duration_secs} seconds"
        
        mom = self.generate_mom(transcript_data['text'], date_str, duration_str, meeting_type, summary_length)
        
        # Add title to MoM if provided
        if title:
            mom = f"# {title}\n\n" + mom
        
        # Save MoM as Markdown
        mom_file = output_dir / "MoM.md"
        with open(mom_file, 'w', encoding='utf-8') as f:
            f.write(mom)
        print(f"MoM saved: {mom_file}")
        
        # Export to PDF
        print("\n" + "="*60)
        print("STEP 3: Exporting to PDF")
        print("="*60)
        pdf_file = self._export_to_pdf(mom, output_dir, title)
        
        # Track action items
        print("\n" + "="*60)
        print("STEP 4: Tracking Action Items")
        print("="*60)
        self._track_action_items(mom, output_dir, title)
        
        return {
            "transcript_file": str(transcript_file),
            "mom_file": str(mom_file),
            "pdf_file": str(pdf_file) if pdf_file else None,
            "mom_content": mom,
            "duration": transcript_data['duration']
        }
    
    def _export_to_pdf(self, mom_content: str, output_dir: Path, title: str = None) -> Path:
        """Export MoM to PDF file."""
        try:
            from fpdf import FPDF
            
            pdf = FPDF(orientation='P', unit='mm', format='A4')
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Page dimensions
            left_margin = 15
            page_width = 210 - 2 * left_margin  # 180mm usable
            
            def safe_text(text):
                """Convert text to latin-1 safe encoding."""
                try:
                    return text.encode('latin-1', 'replace').decode('latin-1')
                except:
                    return text.encode('ascii', 'replace').decode('ascii')
            
            def write_line(text, font_style='', font_size=10, indent=0, line_height=5):
                """Write a line with proper positioning."""
                pdf.set_font('Helvetica', font_style, font_size)
                pdf.set_x(left_margin + indent)
                width = page_width - indent
                if width < 10:  # Safety check
                    width = page_width
                    pdf.set_x(left_margin)
                pdf.multi_cell(width, line_height, safe_text(text))
            
            # Title
            if title:
                write_line(title, 'B', 16, 0, 10)
                pdf.ln(5)
            
            for line in mom_content.split('\n'):
                line = line.rstrip()
                
                if not line.strip():
                    pdf.ln(3)
                    continue
                
                if line.startswith('# '):
                    pdf.ln(5)
                    write_line(line[2:], 'B', 14, 0, 8)
                elif line.startswith('## '):
                    pdf.ln(4)
                    write_line(line[3:], 'B', 12, 0, 7)
                elif line.startswith('### '):
                    pdf.ln(3)
                    write_line(line[4:], 'B', 11, 0, 6)
                elif line.startswith('- **') or line.startswith('* **'):
                    text = line[2:].replace('**', '')
                    write_line('- ' + text, '', 10, 5, 5)
                elif line.startswith('- ') or line.startswith('* '):
                    write_line('- ' + line[2:], '', 10, 5, 5)
                elif line.startswith('|'):
                    if '---' not in line:
                        cells = [c.strip() for c in line.split('|')]
                        cells = [c for c in cells if c]
                        if cells:
                            write_line(' | '.join(cells), '', 10, 0, 5)
                elif line.strip() == '---':
                    pdf.ln(2)
                elif line.strip() and line.strip()[0].isdigit():
                    write_line(line.strip(), '', 10, 5, 5)
                else:
                    clean = line.replace('**', '').replace('`', '')
                    if clean.strip():
                        write_line(clean, '', 10, 0, 5)
            
            pdf_file = output_dir / "MoM.pdf"
            pdf.output(str(pdf_file))
            print(f"PDF saved: {pdf_file}")
            return pdf_file
            
        except ImportError:
            print("PDF export skipped (fpdf2 not installed). Run: pip install fpdf2")
            return None
        except Exception as e:
            print(f"PDF export failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _track_action_items(self, mom_content: str, meeting_folder: Path, title: str = None):
        """
        Extract and save action items to meeting folder.
        
        Uses two-pass approach:
        1. Extract from formal action-oriented sections
        2. Detect conversational action phrases throughout content
        """
        try:
            import re
            
            action_items = []
            in_action_section = False
            
            # Keywords to detect actionable sections (using partial matches)
            action_keywords = [
                'action item', 'next step', 'follow-up', 'follow up',
                'practice exercise', 'practice exercises', 
                'key takeaway', 'key takeaways',
                'further learning', 'recommendation', 
                'to-do', 'todo', 'tasks', 'call to action',
                'resources mentioned', 'tools mentioned'
            ]
            
            # ==================================================================
            # PASS 1: Extract from formal action sections
            # ==================================================================
            lines = mom_content.split('\n')
            for i, line in enumerate(lines):
                line_lower = line.lower()
                
                # Detect action items section (must be a header line)
                if line.startswith('#') and any(kw in line_lower for kw in action_keywords):
                    in_action_section = True
                    continue
                
                # Detect end of section (next header that isn't an actionable section)
                if in_action_section and line.startswith('#'):
                    if not any(kw in line_lower for kw in action_keywords):
                        in_action_section = False
                    continue
                
                # Capture action items
                if in_action_section:
                    stripped = line.strip()
                    if not stripped:
                        continue
                    
                    # Table row (skip header and separator rows)
                    if stripped.startswith('|') and '---' not in stripped:
                        cells = [c.strip() for c in stripped.split('|')]
                        cells = [c for c in cells if c]
                        
                        # Skip header row
                        header_words = ['action', 'item', 'task', 'owner', 'deadline', 'status', 'priority']
                        if cells and any(h in cells[0].lower() for h in header_words):
                            continue
                        # Skip if first cell is just "#"
                        if cells and cells[0] == '#':
                            continue
                        
                        # Handle tables with row number column (e.g., | 1 | Action | Owner |)
                        if cells and cells[0].isdigit() and len(cells) > 1:
                            action_text = cells[1] if len(cells) > 1 else ""
                            if action_text and len(action_text) > 3:
                                action_items.append(cells[1:])  # Skip the # column
                        elif cells and len(cells[0]) > 3:
                            # No row number column
                            action_items.append(cells)
                    
                    # Bullet points (- item or * item)
                    elif stripped.startswith('- ') or stripped.startswith('* '):
                        item = stripped[2:].strip()
                        item = item.replace('**', '').replace('`', '').strip()
                        if item and len(item) > 3:
                            action_items.append([item])
                    
                    # Numbered list (1. Item or 1) Item)
                    elif stripped and stripped[0].isdigit():
                        # Try to extract after "1. " or "1) "
                        item = None
                        if '. ' in stripped[:5]:
                            item = stripped.split('. ', 1)[1].strip()
                        elif ') ' in stripped[:5]:
                            item = stripped.split(') ', 1)[1].strip()
                        
                        if item:
                            item = item.replace('**', '').replace('`', '').strip()
                            if len(item) > 3:
                                action_items.append([item])
            
            # ==================================================================
            # PASS 2: Detect conversational action phrases
            # ==================================================================
            conversational_patterns = [
                r'i want you to ([^.!?]+)',
                r'my suggestion is ([^.!?]+)',
                r'you should ([^.!?]+)',
                r'please try ([^.!?]+)',
                r'make sure to ([^.!?]+)',
                r'don\'t forget to ([^.!?]+)',
                r'remember to ([^.!?]+)',
                r'note this down[:\s]+([^.!?]+)',
                r'note down ([^.!?]+)',
                r'as a challenge[,\s]+([^.!?]+)',
                r'challenge for you[:\s]+([^.!?]+)',
                r'homework[:\s]+([^.!?]+)',
                r'assignment[:\s]+([^.!?]+)',
                r'practice ([^.!?]+)',
                r'try this out[:\s]+([^.!?]+)',
                r'check out ([^.!?]+)',
                r'take a look at ([^.!?]+)',
                r'read about ([^.!?]+)',
                r'learn more about ([^.!?]+)',
                r'explore ([^.!?]+)',
                r'download ([^.!?]+)',
                r'search for ([^.!?]+)',
                r'look into ([^.!?]+)',
            ]
            
            # Search entire content for conversational action items
            full_content = mom_content.lower()
            conversational_items = []
            
            for pattern in conversational_patterns:
                matches = re.finditer(pattern, full_content, re.IGNORECASE)
                for match in matches:
                    if match.group(1):
                        item_text = match.group(1).strip()
                        # Clean up the text
                        item_text = item_text.replace('**', '').replace('`', '')
                        item_text = item_text.replace('\n', ' ').strip()
                        
                        # Skip if too short or too long
                        if len(item_text) > 10 and len(item_text) < 200:
                            # Capitalize first letter
                            item_text = item_text[0].upper() + item_text[1:]
                            conversational_items.append(item_text)
            
            # Deduplicate conversational items (remove very similar ones)
            unique_conversational = []
            for item in conversational_items:
                # Check if this item is substantially different from existing ones
                is_unique = True
                item_words = set(item.lower().split())
                for existing in unique_conversational:
                    existing_words = set(existing.lower().split())
                    # If >70% word overlap, consider it duplicate
                    overlap = len(item_words & existing_words)
                    if overlap / max(len(item_words), 1) > 0.7:
                        is_unique = False
                        break
                
                if is_unique:
                    unique_conversational.append(item)
            
            # Add conversational items (but don't duplicate formal ones)
            for conv_item in unique_conversational:
                # Check if already in formal action items
                is_duplicate = False
                for action_item in action_items:
                    formal_text = action_item[0] if isinstance(action_item, list) else action_item
                    if isinstance(formal_text, str):
                        # Check for substantial overlap
                        formal_words = set(formal_text.lower().split())
                        conv_words = set(conv_item.lower().split())
                        overlap = len(formal_words & conv_words)
                        if overlap / max(len(conv_words), 1) > 0.5:
                            is_duplicate = True
                            break
                
                if not is_duplicate:
                    action_items.append([conv_item])
            
            # ==================================================================
            # Save action items file
            # ==================================================================
            action_file = meeting_folder / "action_items.md"
            meeting_date = datetime.now().strftime("%B %d, %Y %I:%M %p")
            meeting_name = title if title else meeting_folder.name
            
            with open(action_file, 'w', encoding='utf-8') as f:
                f.write(f"# Action Items: {meeting_name}\n")
                f.write(f"*{meeting_date}*\n\n")
                
                if action_items:
                    # Determine if we have tabular data or simple list
                    has_table_data = any(len(item) > 1 for item in action_items)
                    
                    if has_table_data:
                        # Table format
                        f.write("| # | Action | Owner | Deadline | Status |\n")
                        f.write("|---|--------|-------|----------|--------|\n")
                        for i, item in enumerate(action_items, 1):
                            action = item[0] if len(item) > 0 else ""
                            owner = item[1] if len(item) > 1 else "TBD"
                            deadline = item[2] if len(item) > 2 else "TBD"
                            f.write(f"| {i} | {action} | {owner} | {deadline} | ⬜ Pending |\n")
                    else:
                        # Simple list format
                        for i, item in enumerate(action_items, 1):
                            action_text = item[0] if isinstance(item, list) else item
                            f.write(f"{i}. ⬜ {action_text}\n")
                else:
                    f.write("*No action items identified in this meeting.*\n")
                
                f.write("\n---\n")
                f.write("*Status: ⬜ Pending | ✅ Done | ❌ Cancelled*\n")
            
            print(f"Action items saved: {len(action_items)} items → {action_file}")
            
            # Print breakdown for debugging
            formal_count = len([item for item in action_items if isinstance(item, list) and len(item) > 1])
            conversational_count = len(action_items) - formal_count
            if conversational_count > 0:
                print(f"  └─ {formal_count} from formal sections, {conversational_count} from conversational phrases")
                
        except Exception as e:
            print(f"Action item tracking failed: {e}")
            import traceback
            traceback.print_exc()


# ============================================================
# EMAIL SENDER
# ============================================================
class EmailSender:
    def __init__(self):
        self.config = CONFIG["email"]
    
    def send_mom(self, mom_content: str, mom_file: str, meeting_date: str) -> bool:
        """Send MoM via email."""
        if not self.config["enabled"]:
            print("Email disabled in config")
            return False
        
        if self.config["sender_password"] == "YOUR_APP_PASSWORD_HERE":
            print("ERROR: Please set your Gmail App Password in config.json")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config["sender_email"]
            msg['To'] = self.config["recipient_email"]
            msg['Subject'] = f"Meeting Minutes - {meeting_date}"
            
            # Email body
            body = f"""Hi,

Please find attached the Minutes of Meeting for {meeting_date}.

---

{mom_content}

---

This email was automatically generated by AI Meeting Note Taker.
"""
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach MoM file
            with open(mom_file, 'rb') as f:
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload(f.read())
                encoders.encode_base64(attachment)
                attachment.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{Path(mom_file).name}"'
                )
                msg.attach(attachment)
            
            # Send email
            print(f"Sending email to {self.config['recipient_email']}...")
            with smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"]) as server:
                server.starttls()
                server.login(self.config["sender_email"], self.config["sender_password"])
                server.send_message(msg)
            
            print("Email sent successfully!")
            return True
            
        except Exception as e:
            print(f"Email error: {e}")
            return False


# ============================================================
# FLOATING BUTTON APP
# ============================================================
import tkinter as tk
from tkinter import messagebox


class FloatingButton:
    def __init__(self):
        self.recorder = AudioRecorder()
        self.processor = MeetingProcessor()
        self.email_sender = EmailSender()
        self.current_file = ""
        self.processing = False
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Meeting Recorder")
        
        # Remove window decorations, make always-on-top
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.9)  # Slight transparency
        
        # Window size (increased for device dropdown)
        self.width = 220
        self.height = 165
        
        # Position at top-right corner
        screen_width = self.root.winfo_screenwidth()
        x_pos = screen_width - self.width - 20
        y_pos = 20
        self.root.geometry(f"{self.width}x{self.height}+{x_pos}+{y_pos}")
        
        # Create frame
        self.frame = tk.Frame(self.root, bg='#2d2d2d', bd=2, relief='raised')
        self.frame.pack(fill='both', expand=True)
        
        # Meeting title input
        self.title_var = tk.StringVar(value="")
        self.title_entry = tk.Entry(
            self.frame,
            textvariable=self.title_var,
            font=('Arial', 9),
            bg='#3d3d3d',
            fg='white',
            insertbackground='white',
            bd=0,
            highlightthickness=1,
            highlightcolor='#5a5a5a',
            highlightbackground='#4a4a4a'
        )
        self.title_entry.insert(0, "Meeting title...")
        self.title_entry.bind('<FocusIn>', self._on_title_focus_in)
        self.title_entry.bind('<FocusOut>', self._on_title_focus_out)
        self.title_entry.pack(fill='x', padx=3, pady=(3,2))
        
        # Audio device dropdown (full width) - auto-detected
        self.device_names = self.recorder.get_device_names()
        if not self.device_names:
            self.device_names = ["No devices found"]
        
        # Shorten device names for display
        def shorten_name(name, max_len=28):
            return name[:max_len] + "..." if len(name) > max_len else name
        
        self.device_display_names = [shorten_name(n) for n in self.device_names]
        
        # Find auto-detected device index
        selected_idx = 0
        if self.recorder.loopback_device:
            for i, name in enumerate(self.device_names):
                if name == self.recorder.loopback_device['name']:
                    selected_idx = i
                    break
        
        self.device_var = tk.StringVar(value=self.device_display_names[selected_idx] if self.device_display_names else "")
        
        self.device_dropdown = tk.OptionMenu(
            self.frame,
            self.device_var,
            *self.device_display_names,
            command=self._on_device_change
        )
        self.device_dropdown.config(
            font=('Arial', 7),
            bg='#3d3d3d',
            fg='#00ff00',  # Green to indicate audio device
            activebackground='#4d4d4d',
            activeforeground='#00ff00',
            highlightthickness=0,
            bd=0
        )
        self.device_dropdown["menu"].config(
            bg='#3d3d3d',
            fg='white',
            activebackground='#5a5a5a'
        )
        self.device_dropdown.pack(fill='x', padx=3, pady=(0,2))
        
        # Row for meeting type and length dropdowns
        self.dropdown_frame = tk.Frame(self.frame, bg='#2d2d2d')
        self.dropdown_frame.pack(fill='x', padx=3)
        
        # Meeting type dropdown
        self.meeting_type_var = tk.StringVar(value=MEETING_TYPES[0])
        self.type_dropdown = tk.OptionMenu(
            self.dropdown_frame,
            self.meeting_type_var,
            *MEETING_TYPES
        )
        self.type_dropdown.config(
            font=('Arial', 7),
            bg='#3d3d3d',
            fg='white',
            activebackground='#4d4d4d',
            activeforeground='white',
            highlightthickness=0,
            bd=0,
            width=10
        )
        self.type_dropdown["menu"].config(
            bg='#3d3d3d',
            fg='white',
            activebackground='#5a5a5a'
        )
        self.type_dropdown.pack(side='left', fill='x', expand=True)
        
        # Summary length dropdown
        self.summary_lengths = ["Brief", "Detailed"]
        self.summary_length_var = tk.StringVar(value="Detailed")
        self.length_dropdown = tk.OptionMenu(
            self.dropdown_frame,
            self.summary_length_var,
            *self.summary_lengths
        )
        self.length_dropdown.config(
            font=('Arial', 7),
            bg='#3d3d3d',
            fg='white',
            activebackground='#4d4d4d',
            activeforeground='white',
            highlightthickness=0,
            bd=0,
            width=6
        )
        self.length_dropdown["menu"].config(
            bg='#3d3d3d',
            fg='white',
            activebackground='#5a5a5a'
        )
        self.length_dropdown.pack(side='right')
        
        # Create main button
        self.button = tk.Button(
            self.frame,
            text="● REC",
            font=('Arial', 12, 'bold'),
            bg='#4a4a4a',
            fg='white',
            activebackground='#5a5a5a',
            activeforeground='white',
            bd=0,
            cursor='hand2',
            command=self._toggle_recording
        )
        self.button.pack(fill='both', expand=True, padx=3, pady=3)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(
            self.frame,
            textvariable=self.status_var,
            font=('Arial', 8),
            bg='#2d2d2d',
            fg='#888888'
        )
        self.status_label.pack()
        
        # Make window draggable (bind to frame and status label, not button)
        self.frame.bind('<Button-1>', self._start_drag)
        self.frame.bind('<B1-Motion>', self._drag)
        self.status_label.bind('<Button-1>', self._start_drag)
        self.status_label.bind('<B1-Motion>', self._drag)
        
        # Right-click menu
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Open Recordings", command=self._open_folder)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self._quit)
        self.button.bind('<Button-3>', self._show_menu)
        
        # Timer for recording duration
        self.recording_start = None
        self.timer_id = None
        
        # Print startup info
        print("="*60)
        print("Meeting Note Taker - Ready")
        print("="*60)
        print("Click the floating button to start/stop recording")
        print("Audio device auto-detects Windows default output")
        print("Right-click for menu | Drag to reposition")
        print("-"*60)
        print("CONFIGURATION:")
        print(f"  Output folder: {self.recorder.output_dir}")
        print(f"  Whisper model: {CONFIG['whisper']['model']} on {CONFIG['whisper']['device']}")
        print(f"  Ollama model:  {CONFIG['ollama']['model']}")
        print(f"  Email to:      {CONFIG['email']['recipient_email']}")
        print("-"*60)
        print("AUDIO DEVICES (auto-detected):")
        if self.recorder.available_devices:
            for dev in self.recorder.available_devices:
                marker = ">>>" if dev == self.recorder.loopback_device else "   "
                print(f"  {marker} {dev['name']}")
        else:
            print("  ✗ No loopback devices found - only mic will be recorded!")
        print("-"*60)
        print("TIP: Change Windows default audio output to switch devices")
        print("="*60)
    
    def _on_title_focus_in(self, event):
        """Clear placeholder text on focus."""
        if self.title_var.get() == "Meeting title...":
            self.title_entry.delete(0, tk.END)
    
    def _on_title_focus_out(self, event):
        """Restore placeholder if empty."""
        if not self.title_var.get().strip():
            self.title_entry.insert(0, "Meeting title...")
    
    def _on_device_change(self, selected_display_name):
        """Handle device selection change."""
        # Find the full device name from the shortened display name
        for i, display_name in enumerate(self.device_display_names):
            if display_name == selected_display_name:
                full_name = self.device_names[i]
                self.recorder.set_loopback_device(full_name)
                break
    
    def _start_drag(self, event):
        """Start dragging the window."""
        self.drag_x = event.x
        self.drag_y = event.y
    
    def _drag(self, event):
        """Drag the window."""
        x = self.root.winfo_x() + event.x - self.drag_x
        y = self.root.winfo_y() + event.y - self.drag_y
        self.root.geometry(f"+{x}+{y}")
    
    def _show_menu(self, event):
        """Show right-click menu."""
        self.menu.post(event.x_root, event.y_root)
    
    def _update_timer(self):
        """Update recording duration display."""
        if self.recording_start and self.recorder.is_recording:
            elapsed = datetime.now() - self.recording_start
            mins, secs = divmod(int(elapsed.total_seconds()), 60)
            self.status_var.set(f"⏺ {mins:02d}:{secs:02d}")
            self.timer_id = self.root.after(1000, self._update_timer)
    
    def _toggle_recording(self):
        """Toggle recording state."""
        if self.processing:
            self.status_var.set("Processing...")
            return
        
        if self.recorder.is_recording:
            # Stop recording
            self._stop_recording()
        else:
            # Start recording
            self._start_recording()
    
    def _start_recording(self):
        """Start recording."""
        # Auto-refresh device to match current Windows default
        self.recorder.refresh_default_device()
        
        # Update dropdown to show current device
        if self.recorder.loopback_device:
            for i, name in enumerate(self.device_names):
                if name == self.recorder.loopback_device['name']:
                    self.device_var.set(self.device_display_names[i])
                    break
        
        # Capture settings before recording
        self.selected_meeting_type = self.meeting_type_var.get()
        self.selected_summary_length = self.summary_length_var.get()
        
        # Get meeting title
        title = self.title_var.get().strip()
        if title == "Meeting title..." or not title:
            title = None
        self.selected_title = title
        
        self.current_file = self.recorder.start_recording(title)
        self.recording_start = datetime.now()
        
        # Disable inputs during recording
        self.device_dropdown.config(state='disabled')
        self.type_dropdown.config(state='disabled')
        self.length_dropdown.config(state='disabled')
        self.title_entry.config(state='disabled')
        
        # Update UI
        self.button.config(bg='#cc0000', text="■ STOP")
        self.status_var.set("⏺ 00:00")
        self._update_timer()
    
    def _stop_recording(self):
        """Stop recording and process."""
        # Stop timer
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        
        # Stop recording
        self.current_file, duration = self.recorder.stop_recording()
        
        # Update UI
        self.button.config(bg='#cc9900', text="● REC")
        self.status_var.set("Processing...")
        self.processing = True
        
        if self.current_file and duration > 5:
            # Process in background thread
            threading.Thread(target=self._process_recording, daemon=True).start()
        else:
            self.processing = False
            self._enable_inputs()
            self.status_var.set("Too short")
            self.root.after(2000, lambda: self.status_var.set("Ready"))
    
    def _enable_inputs(self):
        """Re-enable all input fields."""
        self.button.config(bg='#4a4a4a')
        self.device_dropdown.config(state='normal')
        self.type_dropdown.config(state='normal')
        self.length_dropdown.config(state='normal')
        self.title_entry.config(state='normal')
    
    def _process_recording(self):
        """Process recording in background."""
        try:
            # Update status
            self.root.after(0, lambda: self.status_var.set("Transcribing..."))
            
            # Process with Whisper + Ollama using selected options
            result = self.processor.process(
                self.current_file,
                self.selected_meeting_type,
                self.selected_summary_length,
                self.selected_title
            )
            
            # Update status
            self.root.after(0, lambda: self.status_var.set("Emailing..."))
            
            # Send email
            meeting_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            email_sent = self.email_sender.send_mom(
                result["mom_content"],
                result["mom_file"],
                meeting_date
            )
            
            # Final status
            if email_sent:
                self.root.after(0, lambda: self.status_var.set("✓ Emailed!"))
            else:
                self.root.after(0, lambda: self.status_var.set("✓ Saved"))
            
        except Exception as e:
            print(f"Processing error: {e}")
            self.root.after(0, lambda: self.status_var.set("Error!"))
        
        finally:
            self.processing = False
            self.root.after(0, self._enable_inputs)
            self.root.after(3000, lambda: self.status_var.set("Ready"))
            # Clear title for next meeting
            self.root.after(0, lambda: self.title_var.set("Meeting title..."))
    
    def _open_folder(self):
        """Open recordings folder."""
        os.startfile(self.recorder.output_dir)
    
    def _quit(self):
        """Quit the application."""
        if self.recorder.is_recording:
            self.recorder.stop_recording()
        self.recorder.cleanup()
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


if __name__ == "__main__":
    app = FloatingButton()
    app.run()
