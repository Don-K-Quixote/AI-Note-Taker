"""
Meeting Note Taker - Post-Processing Module
Transcribes audio with Whisper (local GPU) and summarizes with Ollama.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import requests
from faster_whisper import WhisperModel


class MeetingProcessor:
    def __init__(
        self,
        whisper_model: str = "large-v2",
        ollama_model: str = "llama3.1:8b",
        device: str = "cuda",
        compute_type: str = "float16"
    ):
        """
        Initialize the meeting processor.
        
        Args:
            whisper_model: Whisper model size (tiny, base, small, medium, large-v2, large-v3)
            ollama_model: Ollama model name
            device: Device to use (cuda, cpu)
            compute_type: Compute type (float16, int8, float32)
        """
        self.ollama_model = ollama_model
        self.ollama_url = "http://localhost:11434/api/generate"
        
        print(f"Loading Whisper model '{whisper_model}' on {device}...")
        self.whisper = WhisperModel(
            whisper_model,
            device=device,
            compute_type=compute_type
        )
        print("Whisper model loaded.")
    
    def transcribe(self, audio_path: str, language: str = None) -> dict:
        """
        Transcribe audio file using Whisper.
        
        Args:
            audio_path: Path to audio file
            language: Language code (e.g., 'en', 'es') or None for auto-detect
            
        Returns:
            Dictionary with transcript text and segments
        """
        print(f"Transcribing: {audio_path}")
        
        segments, info = self.whisper.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            word_timestamps=True,
            vad_filter=True,  # Voice activity detection to skip silence
            vad_parameters=dict(
                min_silence_duration_ms=500,
                speech_pad_ms=200
            )
        )
        
        print(f"Detected language: {info.language} (confidence: {info.language_probability:.2f})")
        
        # Collect segments with timestamps
        transcript_segments = []
        full_text_parts = []
        
        for segment in segments:
            seg_data = {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            }
            transcript_segments.append(seg_data)
            full_text_parts.append(segment.text.strip())
            
            # Progress indicator
            print(f"  [{self._format_time(segment.start)} -> {self._format_time(segment.end)}] {segment.text.strip()[:50]}...")
        
        full_text = " ".join(full_text_parts)
        
        return {
            "language": info.language,
            "duration": info.duration,
            "text": full_text,
            "segments": transcript_segments
        }
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds as MM:SS."""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
    
    def summarize_with_ollama(self, transcript: str, custom_prompt: str = None) -> str:
        """
        Generate meeting notes using Ollama.
        
        Args:
            transcript: The full transcript text
            custom_prompt: Optional custom prompt template
            
        Returns:
            Formatted meeting notes
        """
        if custom_prompt:
            prompt = custom_prompt.replace("{transcript}", transcript)
        else:
            prompt = f"""You are a professional meeting note-taker. Analyze the following meeting transcript and create comprehensive meeting notes.

## Instructions:
1. Create a clear, organized summary
2. Extract ALL action items with assignees if mentioned
3. List key decisions made
4. Note any deadlines or dates mentioned
5. Highlight important topics discussed
6. Flag any unresolved questions or follow-ups needed

## Output Format:
Use this exact structure:

# Meeting Summary
[2-3 sentence overview of the meeting's purpose and outcome]

## Key Discussion Points
- [Topic 1]: [Brief description]
- [Topic 2]: [Brief description]
...

## Decisions Made
1. [Decision with context]
2. [Decision with context]
...

## Action Items
| Action | Owner | Deadline |
|--------|-------|----------|
| [Task] | [Person/TBD] | [Date/TBD] |
...

## Follow-ups & Open Questions
- [Question or item needing follow-up]
...

## Notable Quotes/Points
- "[Exact quote if significant]" - regarding [topic]
...

---

## Transcript:
{transcript}

---

Please generate the meeting notes now:"""
        
        print(f"Generating summary with {self.ollama_model}...")
        
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Lower for more factual output
                        "num_ctx": 8192,     # Context window
                        "top_p": 0.9
                    }
                },
                timeout=300  # 5 minute timeout for long meetings
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "Error: No response from Ollama")
            
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Make sure it's running (ollama serve)"
        except requests.exceptions.Timeout:
            return "Error: Ollama request timed out. Try a shorter transcript or increase timeout."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def process_meeting(
        self,
        audio_path: str,
        output_dir: str = None,
        language: str = None,
        custom_prompt: str = None
    ) -> dict:
        """
        Full pipeline: transcribe audio and generate meeting notes.
        
        Args:
            audio_path: Path to audio file
            output_dir: Directory for output files (default: same as audio)
            language: Language code or None for auto-detect
            custom_prompt: Optional custom summarization prompt
            
        Returns:
            Dictionary with paths to generated files
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        output_dir = Path(output_dir) if output_dir else audio_path.parent
        output_dir.mkdir(exist_ok=True)
        
        base_name = audio_path.stem
        
        # Step 1: Transcribe
        print("\n" + "="*60)
        print("STEP 1: Transcription")
        print("="*60)
        
        transcript_data = self.transcribe(str(audio_path), language)
        
        # Save transcript
        transcript_file = output_dir / f"{base_name}_transcript.txt"
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write(f"Meeting Transcript\n")
            f.write(f"Audio: {audio_path.name}\n")
            f.write(f"Duration: {self._format_time(transcript_data['duration'])}\n")
            f.write(f"Language: {transcript_data['language']}\n")
            f.write(f"Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            f.write(transcript_data['text'])
        
        print(f"\nTranscript saved: {transcript_file}")
        
        # Save segments with timestamps (JSON)
        segments_file = output_dir / f"{base_name}_segments.json"
        with open(segments_file, 'w', encoding='utf-8') as f:
            json.dump(transcript_data['segments'], f, indent=2)
        
        print(f"Segments saved: {segments_file}")
        
        # Step 2: Summarize
        print("\n" + "="*60)
        print("STEP 2: Summarization")
        print("="*60)
        
        summary = self.summarize_with_ollama(transcript_data['text'], custom_prompt)
        
        # Save meeting notes
        notes_file = output_dir / f"{base_name}_notes.md"
        with open(notes_file, 'w', encoding='utf-8') as f:
            f.write(f"<!-- Generated from: {audio_path.name} -->\n")
            f.write(f"<!-- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->\n\n")
            f.write(summary)
        
        print(f"\nMeeting notes saved: {notes_file}")
        
        # Summary stats
        print("\n" + "="*60)
        print("PROCESSING COMPLETE")
        print("="*60)
        print(f"Audio duration: {self._format_time(transcript_data['duration'])}")
        print(f"Word count: {len(transcript_data['text'].split())}")
        print(f"Files generated:")
        print(f"  - {transcript_file}")
        print(f"  - {segments_file}")
        print(f"  - {notes_file}")
        
        return {
            "transcript_file": str(transcript_file),
            "segments_file": str(segments_file),
            "notes_file": str(notes_file),
            "duration": transcript_data['duration'],
            "word_count": len(transcript_data['text'].split())
        }


def main():
    parser = argparse.ArgumentParser(
        description="Process meeting recordings: transcribe with Whisper and summarize with Ollama"
    )
    parser.add_argument(
        "audio",
        help="Path to audio file (WAV, MP3, etc.)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output directory (default: same as audio file)"
    )
    parser.add_argument(
        "-m", "--whisper-model",
        default="large-v2",
        choices=["tiny", "base", "small", "medium", "large-v2", "large-v3"],
        help="Whisper model size (default: large-v2)"
    )
    parser.add_argument(
        "--ollama-model",
        default="llama3.1:8b",
        help="Ollama model name (default: llama3.1:8b)"
    )
    parser.add_argument(
        "-l", "--language",
        help="Language code (e.g., 'en', 'es'). Auto-detect if not specified."
    )
    parser.add_argument(
        "--cpu",
        action="store_true",
        help="Use CPU instead of GPU"
    )
    parser.add_argument(
        "--transcript-only",
        action="store_true",
        help="Only transcribe, skip summarization"
    )
    
    args = parser.parse_args()
    
    device = "cpu" if args.cpu else "cuda"
    compute_type = "float32" if args.cpu else "float16"
    
    processor = MeetingProcessor(
        whisper_model=args.whisper_model,
        ollama_model=args.ollama_model,
        device=device,
        compute_type=compute_type
    )
    
    if args.transcript_only:
        transcript_data = processor.transcribe(args.audio, args.language)
        print("\n" + transcript_data['text'])
    else:
        processor.process_meeting(
            args.audio,
            output_dir=args.output,
            language=args.language
        )


if __name__ == "__main__":
    main()
