#!/usr/bin/env python3
"""
Debug script to test PDF merging and identify issues
"""

from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter

def analyze_pdf(pdf_path):
    """Analyze a PDF file to understand its structure."""
    try:
        reader = PdfReader(str(pdf_path))
        print(f"\nAnalyzing: {pdf_path.name}")
        print(f"  Pages: {len(reader.pages)}")
        print(f"  File size: {pdf_path.stat().st_size} bytes")
        
        if len(reader.pages) > 0:
            page = reader.pages[0]
            print(f"  First page size: {page.mediabox}")
            print(f"  First page rotation: {getattr(page, 'rotate', 'None')}")
            
            # Check if page has content
            if '/Contents' in page:
                print(f"  Page has content: Yes")
            else:
                print(f"  Page has content: NO - This might be a blank page!")
        else:
            print("  WARNING: PDF has no pages!")
            
    except Exception as e:
        print(f"  Error reading PDF: {e}")

def test_merge():
    """Test PDF merging with detailed output."""
    my_images = Path("./my_images")
    
    # Find first few PDFs to test
    pdf_files = [f for f in my_images.iterdir() if f.is_file() and f.suffix.lower() == '.pdf'][:5]
    
    print("Testing PDF analysis...")
    for pdf in pdf_files:
        analyze_pdf(pdf)
    
    # Test merging
    print("\n\nTesting merge...")
    writer = PdfWriter()
    
    for i, pdf_path in enumerate(pdf_files):
        try:
            reader = PdfReader(str(pdf_path))
            print(f"\nAdding {pdf_path.name} ({len(reader.pages)} pages)")
            
            for j, page in enumerate(reader.pages):
                print(f"  Adding page {j+1}")
                writer.add_page(page)
                
        except Exception as e:
            print(f"Error with {pdf_path.name}: {e}")
    
    # Write test output
    output_path = Path("./test_merge_debug.pdf")
    with open(output_path, 'wb') as f:
        writer.write(f)
    
    print(f"\nTest merge written to: {output_path}")
    print(f"Total pages in merged PDF: {len(writer.pages)}")

if __name__ == "__main__":
    test_merge()
