"""
Re-process IIML Lecture to Test Improved Action Item Extraction
Run this from your project src directory
"""

from meeting_recorder import MeetingProcessor
from pathlib import Path

def reprocess_iiml():
    """Re-process the IIML lecture with improved action item extraction."""
    
    print("="*60)
    print("Re-processing IIML L6 Supervised Learning Lecture")
    print("="*60)
    
    # Initialize processor
    processor = MeetingProcessor()
    
    # Path to the audio file
    audio_path = Path("recordings/IIML-L6-Supervised-Learning/audio.wav")
    
    # Check if file exists
    if not audio_path.exists():
        print(f"ERROR: Audio file not found: {audio_path}")
        print("\nPlease update the path to your IIML lecture audio file.")
        return
    
    print(f"Found audio file: {audio_path}")
    print(f"Using improved action item extraction")
    print()
    
    # Re-process with Tutorial/Training template
    result = processor.process(
        audio_path=str(audio_path),
        meeting_type="Tutorial/Training",
        summary_length="Detailed",
        title="IIML-L6-Supervised-Learning"
    )
    
    # Display results
    print("\n" + "="*60)
    print("PROCESSING COMPLETE!")
    print("="*60)
    print(f"Transcript:     {result['transcript_file']}")
    print(f"MoM (Markdown): {result['mom_file']}")
    print(f"MoM (PDF):      {result['pdf_file']}")
    print(f"Action Items:   {Path(result['mom_file']).parent / 'action_items.md'}")
    print("="*60)
    
    # Read and display action items
    action_items_file = Path(result['mom_file']).parent / 'action_items.md'
    if action_items_file.exists():
        print("\nACTION ITEMS EXTRACTED:")
        print("-"*60)
        with open(action_items_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Print just the items, skip header
            lines = content.split('\n')
            for line in lines[3:]:  # Skip title and date
                if line.strip() and not line.startswith('*Status') and not line.startswith('---'):
                    print(line)
        print("-"*60)
    
    return result

if __name__ == "__main__":
    reprocess_iiml()
