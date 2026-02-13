"""
Quick test with Brief summary mode - much faster!
"""

from meeting_recorder import MeetingProcessor
from pathlib import Path

def test_brief():
    print("Testing with BRIEF summary mode (faster)...")
    print("="*60)
    
    processor = MeetingProcessor()
    audio_path = Path("recordings/IIML-L6-Supervised-Learning/audio.wav")
    
    if not audio_path.exists():
        print(f"ERROR: Audio file not found: {audio_path}")
        return
    
    # Use BRIEF mode - much faster!
    result = processor.process(
        audio_path=str(audio_path),
        meeting_type="Tutorial/Training",
        summary_length="Brief",  # Changed to Brief!
        title="IIML-L6-Supervised-Learning-BRIEF-TEST"
    )
    
    print("\n" + "="*60)
    print("BRIEF TEST COMPLETE!")
    print("="*60)
    
    # Check action items
    action_items_file = Path(result['mom_file']).parent / 'action_items.md'
    if action_items_file.exists():
        print("\nACTION ITEMS:")
        print("-"*60)
        with open(action_items_file, 'r', encoding='utf-8') as f:
            print(f.read())

if __name__ == "__main__":
    test_brief()
