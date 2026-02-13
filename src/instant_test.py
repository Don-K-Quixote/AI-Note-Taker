"""
Instant Test - Just Test Action Item Extraction
Creates a fake MoM with conversational action items and tests extraction
Takes 5 seconds!
"""

from meeting_recorder import MeetingProcessor
from pathlib import Path

def instant_test():
    print("="*60)
    print("INSTANT ACTION ITEM EXTRACTION TEST")
    print("="*60)
    
    # Create a test MoM with conversational action items
    test_mom = """# Tutorial Notes - Machine Learning

## Key Concepts

Machine learning is about teaching computers to learn from data.

## Practice Exercises

I want you to take the NCRB crime data and analyze the patterns in defaulters.

My suggestion is to try Azure Machine Learning Studio for a citizen data scientist experience.

You should download the CIBIL defaulters data from suits.sibyl.com and perform analysis.

Please try learning Python through the DataCamp platform.

Make sure to read the 700-page machine learning book I shared in the chat.

Note this down - check your email for Python notebooks with datasets.

## Key Takeaways

1. Start with exploratory data analysis
2. Use visualization tools
3. Practice regularly

## Further Learning

As a challenge, explore the scikit-learn documentation.
"""
    
    # Create test folder
    test_folder = Path("recordings/ACTION_ITEM_TEST")
    test_folder.mkdir(exist_ok=True)
    
    # Test extraction
    print("\nTest MoM Content:")
    print("-"*60)
    print(test_mom[:300] + "...")
    print("-"*60)
    
    print("\nRunning action item extraction...")
    
    processor = MeetingProcessor()
    processor._track_action_items(
        mom_content=test_mom,
        meeting_folder=test_folder,
        title="Action-Item-Extraction-Test"
    )
    
    # Show results
    action_file = test_folder / "action_items.md"
    if action_file.exists():
        print("\n" + "="*60)
        print("RESULTS:")
        print("="*60)
        with open(action_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
        
        # Count items
        item_count = content.count("⬜")
        print("\n" + "="*60)
        if item_count > 0:
            print(f"✅ SUCCESS! Extracted {item_count} action items!")
            print("The improved extraction is working!")
        else:
            print("❌ FAILED! No action items extracted.")
            print("The code changes may not be applied correctly.")
        print("="*60)
    else:
        print("\n❌ ERROR: action_items.md not created!")

if __name__ == "__main__":
    instant_test()
