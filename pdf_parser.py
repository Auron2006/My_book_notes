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
        
        # Split into lines for easier processing
        lines = text.split('\n')
        
        # Look for book titles - they typically follow a pattern like:
        # "Book Title by Author" or just appear after section numbers
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check if this line contains "by" (indicating a book title)
            # But skip lines that are just numbered points
            if ' by ' in line.lower() and len(line) > 20 and not re.match(r'^\d+[\.)]\s*', line):
                # Extract the book title and author
                title_line = line
                
                # Look for the first few points/lessons after the title
                points = []
                j = i + 1
                point_count = 0
                
                while j < len(lines) and point_count < 3:
                    point_line = lines[j].strip()
                    # Look for numbered points like "1.)", "2.)", etc.
                    if re.match(r'\d+[\.)]\s*.+', point_line) and len(point_line) > 10:
                        # Clean up the point
                        point_text = re.sub(r'^\d+[\.)]\s*', '', point_line)
                        # Handle multi-line points
                        if j + 1 < len(lines) and not re.match(r'\d+[\.)]\s*.+', lines[j + 1]):
                            next_line = lines[j + 1].strip()
                            if next_line and not ' by ' in next_line.lower():
                                point_text += ' ' + next_line
                                j += 1
                        points.append(point_text.strip())
                        point_count += 1
                    j += 1
                
                # Format the summary
                if points:
                    # Extract book name from title
                    book_match = re.search(r'(.+?)\s+by\s+(.+)', title_line, re.IGNORECASE)
                    if book_match:
                        book_name = book_match.group(1).strip()
                        author = book_match.group(2).strip()
                        # Remove any leading numbers or special characters
                        book_name = re.sub(r'^[\d\.\s\u200b]+', '', book_name)
                        
                        # Create summary with first point or two
                        summary_text = points[0]
                        if len(summary_text) < 100 and len(points) > 1:
                            summary_text += '. ' + points[1]
                        
                        # Truncate if too long
                        if len(summary_text) > 150:
                            summary_text = summary_text[:150] + '...'
                        
                        summary = f"{book_name} – {summary_text}"
                        summaries.append(summary)
                
                # Skip past this book section
                i = j
            else:
                i += 1
        
        # Also look for other book patterns (like "The Subtle Art..." which appears later)
        additional_patterns = [
            r'The\s+Subtle\s+Art[^:]+:(.+?)(?=\n\n|\n[A-Z])',
            r'Sapiens[^:]*:(.+?)(?=\n\n|\n[A-Z])',
            r'Atomic\s+Habits[^:]*:(.+?)(?=\n\n|\n[A-Z])'
        ]
        
        for pattern in additional_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                book_title = match.group(0).split(':')[0].strip()
                content = match.group(1).strip()[:150] + '...'
                summary = f"{book_title} – {content}"
                if summary not in summaries:
                    summaries.append(summary)
        
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