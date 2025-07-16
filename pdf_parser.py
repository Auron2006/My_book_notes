import fitz  # PyMuPDF
import re
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class BookSummaryParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.summaries = []
        
    def parse(self) -> List[str]:
        """Parse the PDF and extract book summaries."""
        try:
            doc = fitz.open(self.pdf_path)
            all_text = ""
            
            # Extract all text from the PDF
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                all_text += text + "\n"
            
            doc.close()
            
            # Process the text to extract summaries
            self.summaries = self._extract_summaries(all_text)
            
            return self.summaries
            
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise
    
    def _extract_summaries(self, text: str) -> List[str]:
        """Extract individual book summaries from the text."""
        summaries = []
        
        # Split by common patterns that indicate new book sections
        # Looking for patterns like "1.1", "2.1", etc. followed by book titles
        book_pattern = r'\d+\.\d+\s+([^\.]+by[^\.]+)'
        
        # Find all book titles
        book_matches = re.finditer(book_pattern, text, re.IGNORECASE)
        book_positions = []
        
        for match in book_matches:
            title = match.group(1).strip()
            start_pos = match.start()
            book_positions.append((title, start_pos))
        
        # Extract content for each book
        for i, (title, start_pos) in enumerate(book_positions):
            # Find the end position (start of next book or end of text)
            if i < len(book_positions) - 1:
                end_pos = book_positions[i + 1][1]
            else:
                end_pos = len(text)
            
            # Extract the book section
            book_content = text[start_pos:end_pos].strip()
            
            # Clean up and format the summary
            summary = self._format_summary(title, book_content)
            if summary:
                summaries.append(summary)
        
        # If no structured summaries found, fall back to paragraph extraction
        if not summaries:
            summaries = self._extract_paragraph_summaries(text)
        
        return summaries
    
    def _format_summary(self, title: str, content: str) -> str:
        """Format a book summary from raw content."""
        # Extract the first few meaningful lines after the title
        lines = content.split('\n')
        
        # Skip empty lines and find the first few content lines
        content_lines = []
        for line in lines[1:]:  # Skip the title line
            line = line.strip()
            if line and not line.isdigit() and len(line) > 10:
                content_lines.append(line)
                if len(content_lines) >= 3:  # Get first 3 meaningful lines
                    break
        
        if content_lines:
            # Create a concise summary
            summary_text = ' '.join(content_lines[:2])  # Use first 2 lines
            # Clean up excessive whitespace
            summary_text = re.sub(r'\s+', ' ', summary_text)
            
            # Extract just the book title (remove "by author")
            title_match = re.match(r'(.+?)\s+by\s+', title, re.IGNORECASE)
            if title_match:
                book_name = title_match.group(1).strip()
            else:
                book_name = title.split()[0]  # Fallback to first word
            
            # Create a formatted summary
            return f"{book_name} – {summary_text[:150]}..."
        
        return None
    
    def _extract_paragraph_summaries(self, text: str) -> List[str]:
        """Fallback method to extract summaries from paragraphs."""
        summaries = []
        
        # Look for book-related patterns
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            para = para.strip()
            # Look for paragraphs that mention books or key concepts
            if len(para) > 50 and any(keyword in para.lower() for keyword in ['book', 'author', 'principle', 'habit', 'rule']):
                # Format as a summary
                summary = re.sub(r'\s+', ' ', para)[:200] + "..."
                summaries.append(summary)
                
                if len(summaries) >= 10:  # Limit to 10 summaries
                    break
        
        return summaries

    def get_random_summary(self) -> str:
        """Get a random summary from the parsed summaries."""
        import random
        if not self.summaries:
            self.parse()
        
        if self.summaries:
            return random.choice(self.summaries)
        else:
            return "No summaries available"