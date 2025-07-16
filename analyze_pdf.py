import fitz

pdf_path = "book_summaries_for_mcp.pdf"
doc = fitz.open(pdf_path)

print("Analyzing PDF structure...")
print("=" * 60)

# Look at first 5 pages in detail
for page_num in range(min(5, len(doc))):
    page = doc[page_num]
    text = page.get_text()
    
    print(f"\n=== Page {page_num + 1} ===")
    lines = text.split('\n')
    
    # Print first 20 non-empty lines
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    for i, line in enumerate(non_empty_lines[:20]):
        print(f"{i+1}: {line}")
    
    if len(non_empty_lines) > 20:
        print("...")

doc.close()