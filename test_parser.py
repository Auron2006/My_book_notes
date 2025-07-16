from pdf_parser import BookSummaryParser
import logging

# Set up logging to see any errors
logging.basicConfig(level=logging.DEBUG)

# Test the parser
parser = BookSummaryParser("book_summaries_for_mcp.pdf")

print("Testing PDF parser...")
print("-" * 50)

try:
    summaries = parser.parse()
    print(f"Found {len(summaries)} summaries\n")
    
    if summaries:
        print("First 3 summaries:")
        for i, summary in enumerate(summaries[:3]):
            print(f"\n{i+1}. {summary}")
    else:
        print("No summaries found!")
        
    print("\n" + "-" * 50)
    print("Testing random summary:")
    print(parser.get_random_summary())
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()