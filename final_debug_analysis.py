#!/usr/bin/env python3
"""
Final analysis and fix for blank page issue
"""

from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import tempfile
import os

def analyze_current_catalog():
    """Analyze the current problematic catalog."""
    catalog_path = Path("./my_images/fixed_original_catalog.pdf")
    
    if not catalog_path.exists():
        print("Catalog not found")
        return
    
    reader = PdfReader(str(catalog_path))
    print(f"Catalog has {len(reader.pages)} pages")
    
    blank_pages = []
    problem_pages = []
    
    for i, page in enumerate(reader.pages):
        has_content = '/Contents' in page
        print(f"Page {i+1}: has_content={has_content}")
        
        if not has_content:
            blank_pages.append(i+1)
        elif i >= 24 and i <= 28:  # Problematic range
            problem_pages.append(i+1)
    
    print(f"\nBlank pages: {blank_pages}")
    print(f"Problem pages: {problem_pages}")
    
    return blank_pages, problem_pages

def create_fixed_catalog():
    """Create a catalog using PyPDF2 directly."""
    print("\n=== Creating fixed catalog with PyPDF2 ===")
    
    # Get all JPG files
    my_images = Path("./my_images")
    jpg_files = [f for f in my_images.iterdir() if f.suffix.lower() in ['.jpg', '.jpeg']]
    
    if not jpg_files:
        print("No JPG files found")
        return
    
    # Create PDF using PyPDF2
    from PyPDF2 import PdfFileWriter
    
    catalog_path = Path("./fixed_with_pypdf2_catalog.pdf")
    writer = PdfFileWriter()
    
    # Add cover
    page = writer.add_blank_page(width=612, height=792)
    writer.add_outline_item("Cover", page, level=0)
    
    # Add images
    for i, jpg_path in enumerate(jpg_files[:5]):  # Test first 5
        if jpg_path.exists():
            img = Image.open(jpg_path)
            
            # Convert image to bytes
            img_bytes = tempfile.BytesIO()
            img.save(img_bytes, format='PNG')
            
            # Add page
            page = writer.add_blank_page(width=612, height=792)
            page.insert_image(img_bytes.getvalue(), x=100, y=100, width=400, height=400)
            writer.add_outline_item(f"Image {i+1}", page, level=1)
    
    # Add back cover
    back_page = writer.add_blank_page(width=612, height=792)
    writer.add_outline_item("Back Cover", back_page, level=0)
    
    # Save the PDF
    with open(catalog_path, 'wb') as f:
        writer.write(f)
    
    # Analyze the result
    reader = PdfReader(str(catalog_path))
    print(f"Fixed catalog created: {catalog_path.stat().st_size} bytes")
    
    blank_pages = []
    for i, page in enumerate(reader.pages):
        has_content = '/Contents' in page
        if not has_content:
            blank_pages.append(i+1)
    
    print(f"Blank pages in fixed catalog: {blank_pages}")
    
    return len(blank_pages) == 0

def main():
    """Main function."""
    print("=== ANALYZING CURRENT CATALOG ===")
    blank_pages, problem_pages = analyze_current_catalog()
    
    print(f"\n=== CREATING FIXED CATALOG ===")
    success = create_fixed_catalog()
    
    if success:
        print("✅ Fixed catalog has no blank pages!")
    else:
        print("❌ Failed to create fixed catalog")

if __name__ == "__main__":
    main()
