"""
Generate DETAILED MoM from existing transcript
This will take 10-15 minutes but gives comprehensive notes
"""

from meeting_recorder import MeetingProcessor
from pathlib import Path
from datetime import datetime

def detailed_mom():
    print("="*60)
    print("Generating DETAILED MoM")
    print("This will take 10-15 minutes...")
    print("="*60)
    
    # Paths
    meeting_folder = Path("recordings/IIML-L6-Supervised-Learning")
    transcript_file = meeting_folder / "transcript.txt"
    
    # Read transcript
    print(f"Reading transcript: {transcript_file}")
    with open(transcript_file, 'r', encoding='utf-8') as f:
        transcript_text = f.read()
    
    print(f"Transcript: {len(transcript_text)} characters, ~{len(transcript_text.split())} words")
    print()
    
    # Initialize processor
    processor = MeetingProcessor()
    
    # Generate DETAILED MoM
    print("="*60)
    print("Generating DETAILED Tutorial Notes...")
    print("Processing with 32K context window...")
    print("Please wait 10-15 minutes...")
    print("="*60)
    
    date_str = datetime.now().strftime("%B %d, %Y")
    duration_str = "120 minutes"
    
    # Generate MoM with DETAILED mode
    mom = processor.generate_mom(
        transcript=transcript_text,
        date=date_str,
        duration=duration_str,
        meeting_type="Tutorial/Training",
        summary_length="Detailed"  # Full detailed notes!
    )
    
    # Check for errors
    if "Error:" in mom[:100]:
        print("\n" + "!"*60)
        print("ERROR: MoM generation failed!")
        print("!"*60)
        print(mom[:500])
        print("\nPossible issues:")
        print("  1. Ollama timeout (even with 15min limit)")
        print("  2. Out of memory")
        print("  3. Model overloaded")
        return
    
    # Save MoM
    mom_file = meeting_folder / "MoM.md"
    with open(mom_file, 'w', encoding='utf-8') as f:
        f.write(f"# IIML-L6-Supervised-Learning\n\n")
        f.write(mom)
    
    print(f"\n✅ MoM saved: {mom_file}")
    print(f"   Size: {len(mom):,} characters (~{len(mom.split())} words)")
    
    # Extract action items from detailed MoM
    print("\n" + "="*60)
    print("Extracting Action Items from Detailed MoM...")
    print("="*60)
    
    processor._track_action_items(
        mom_content=mom,
        meeting_folder=meeting_folder,
        title="IIML-L6-Supervised-Learning"
    )
    
    # Export to PDF
    print("\n" + "="*60)
    print("Exporting to PDF...")
    print("="*60)
    
    pdf_file = processor._export_to_pdf(mom, meeting_folder, "IIML-L6-Supervised-Learning")
    
    # Show results
    print("\n" + "="*60)
    print("✅ DETAILED MoM COMPLETE!")
    print("="*60)
    print(f"MoM (Markdown): {mom_file}")
    print(f"MoM (PDF):      {pdf_file}")
    print(f"Action Items:   {meeting_folder / 'action_items.md'}")
    print("="*60)
    
    # Show action items
    action_file = meeting_folder / "action_items.md"
    if action_file.exists():
        print("\nACTION ITEMS:")
        with open(action_file, 'r', encoding='utf-8') as f:
            content = f.read()
            item_count = content.count("⬜")
            print(f"Total items: {item_count}")

if __name__ == "__main__":
    detailed_mom()
