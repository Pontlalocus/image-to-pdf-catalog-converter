#!/usr/bin/env python3
"""
Debug the merge process to identify black page issue
"""

from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter

def analyze_merged_catalog():
    """Analyze the merged catalog to identify issues."""
    catalog_path = Path("./my_images/enhanced_test_catalog.pdf")
    
    if not catalog_path.exists():
        print("Catalog file not found!")
        return
    
    try:
        reader = PdfReader(str(catalog_path))
        print(f"Catalog has {len(reader.pages)} pages")
        
        # Check specific problematic pages
        problematic_pages = [25, 26, 27, 28, 36, 37, 38, 39, 40, 41, 42, 43, 49, 50, 51, 52, 53, 54, 55, 56, 57]
        
        for page_num in problematic_pages:
            if page_num <= len(reader.pages):
                page = reader.pages[page_num - 1]  # 0-based indexing
                print(f"\n=== Page {page_num} ===")
                print(f"  MediaBox: {page.mediabox}")
                print(f"  CropBox: {getattr(page, 'cropbox', 'Not set')}")
                print(f"  Rotate: {getattr(page, 'rotate', 'Not set')}")
                print(f"  Has contents: {'/Contents' in page}")
                
                if '/Contents' in page:
                    contents = page['/Contents']
                    if hasattr(contents, 'get_object'):
                        print(f"  Content object: {contents.get_object()}")
                    else:
                        print(f"  Content type: {type(contents)}")
                else:
                    print("  WARNING: No contents found!")
            else:
                print(f"\n=== Page {page_num} ===")
                print("  Page not found in catalog")
        
        # Check first few pages for comparison
        print(f"\n=== COMPARISON: First 5 pages ===")
        for i in range(min(5, len(reader.pages))):
            page = reader.pages[i]
            print(f"  Page {i+1}: Has contents = {'/Contents' in page}")
            
    except Exception as e:
        print(f"Error analyzing catalog: {e}")

def test_individual_pdfs():
    """Test the individual PDFs that were created."""
    temp_dir = Path("./my_images/_temp_pdfs")
    
    if not temp_dir.exists():
        print("Temp PDF directory not found!")
        return
    
    pdf_files = list(temp_dir.glob("*.pdf"))
    pdf_files.sort(key=lambda x: x.name.lower())
    
    print(f"Found {len(pdf_files)} temp PDF files")
    
    # Test specific problematic ones
    problematic_indices = [24, 25, 26, 27, 35, 36, 37, 38, 39, 40, 41, 42, 48, 49, 50, 51, 52, 53, 54, 55, 56]  # 0-based
    
    for idx in problematic_indices:
        if idx < len(pdf_files):
            pdf_path = pdf_files[idx]
            try:
                reader = PdfReader(str(pdf_path))
                print(f"\n=== {pdf_path.name} (Index {idx+2}) ===")
                print(f"  Pages: {len(reader.pages)}")
                
                if len(reader.pages) > 0:
                    page = reader.pages[0]
                    print(f"  MediaBox: {page.mediabox}")
                    print(f"  Has contents: {'/Contents' in page}")
                    print(f"  File size: {pdf_path.stat().st_size} bytes")
                else:
                    print("  WARNING: No pages!")
                    
            except Exception as e:
                print(f"  Error reading {pdf_path.name}: {e}")

def test_merge_small_batch():
    """Test merging a small batch to isolate the issue."""
    print("\n=== TESTING SMALL BATCH MERGE ===")
    
    # Get a few PDF files to test
    temp_dir = Path("./my_images/_temp_pdfs")
    if not temp_dir.exists():
        print("No temp directory found")
        return
    
    pdf_files = list(temp_dir.glob("*.pdf"))
    pdf_files.sort(key=lambda x: x.name.lower())
    
    # Test pages around the problematic area
    test_indices = [20, 21, 22, 23, 24, 25, 26, 27]  # Around page 25-28
    
    test_files = [pdf_files[i] for i in test_indices if i < len(pdf_files)]
    
    print(f"Testing merge of {len(test_files)} files:")
    for f in test_files:
        print(f"  {f.name}")
    
    # Try merging
    writer = PdfWriter()
    
    for pdf_path in test_files:
        try:
            reader = PdfReader(str(pdf_path))
            for page in reader.pages:
                writer.add_page(page)
            print(f"✓ Added: {pdf_path.name}")
        except Exception as e:
            print(f"✗ Error with {pdf_path.name}: {e}")
    
    # Save test merge
    test_output = Path("test_small_merge.pdf")
    with open(test_output, 'wb') as f:
        writer.write(f)
    
    print(f"Test merge saved: {test_output}")
    print(f"Total pages: {len(writer.pages)}")

if __name__ == "__main__":
    analyze_merged_catalog()
    test_individual_pdfs()
    test_merge_small_batch()
