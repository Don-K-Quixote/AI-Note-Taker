"""
Fast Test - Skip Transcription, Just Test MoM Generation + Action Items
Uses the existing transcript, no need to re-transcribe!
"""

from meeting_recorder import MeetingProcessor
from pathlib import Path
from datetime import datetime

def fast_test():
    print("="*60)
    print("FAST TEST - Using Existing Transcript")
    print("="*60)
    
    # Paths
    meeting_folder = Path("recordings/IIML-L6-Supervised-Learning")
    transcript_file = meeting_folder / "transcript.txt"
    
    # Check if transcript exists
    if not transcript_file.exists():
        print(f"ERROR: Transcript not found: {transcript_file}")
        return
    
    # Read existing transcript
    print(f"Reading existing transcript: {transcript_file}")
    with open(transcript_file, 'r', encoding='utf-8') as f:
        transcript_text = f.read()
    
    print(f"Transcript size: {len(transcript_text)} characters")
    print(f"Word count: ~{len(transcript_text.split())} words")
    print()
    
    # Initialize processor
    processor = MeetingProcessor()
    
    # Generate MoM (skip transcription step)
    print("="*60)
    print("Generating MoM with Brief mode...")
    print("This will take 2-5 minutes...")
    print("="*60)
    
    date_str = datetime.now().strftime("%B %d, %Y")
    duration_str = "120 minutes"  # Approximate
    
    # Generate MoM
    mom = processor.generate_mom(
        transcript=transcript_text,
        date=date_str,
        duration=duration_str,
        meeting_type="Tutorial/Training",
        summary_length="Brief"  # Use Brief for faster processing
    )
    
    # Save MoM
    mom_file = meeting_folder / "MoM_FAST_TEST.md"
    with open(mom_file, 'w', encoding='utf-8') as f:
        f.write(f"# IIML-L6-Supervised-Learning (FAST TEST)\n\n")
        f.write(mom)
    
    print(f"\nMoM saved: {mom_file}")
    print(f"MoM size: {len(mom)} characters")
    
    # Check if it's an error
    if "Error:" in mom[:100] or len(mom) < 500:
        print("\n" + "!"*60)
        print("ERROR: MoM generation failed!")
        print("!"*60)
        print(mom[:500])
        return
    
    # Extract action items
    print("\n" + "="*60)
    print("Extracting Action Items...")
    print("="*60)
    
    processor._track_action_items(
        mom_content=mom,
        meeting_folder=meeting_folder,
        title="IIML-L6-Fast-Test"
    )
    
    # Display results
    print("\n" + "="*60)
    print("FAST TEST COMPLETE!")
    print("="*60)
    
    # Read and show action items
    action_file = meeting_folder / "action_items.md"
    if action_file.exists():
        print("\nACTION ITEMS EXTRACTED:")
        print("-"*60)
        with open(action_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
        print("-"*60)
    
    print(f"\nFiles created:")
    print(f"  MoM: {mom_file}")
    print(f"  Action Items: {action_file}")
    print()
    print("TIP: If you got action items, the fix is working!")
    print("     If not, the MoM might not have action-related content.")

if __name__ == "__main__":
    fast_test()
