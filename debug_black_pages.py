#!/usr/bin/env python3
"""
Debug script to investigate black pages in catalog
"""

from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image, ImageOps
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

def analyze_original_jpg(jpg_path):
    """Analyze original JPG file."""
    try:
        img = Image.open(jpg_path)
        print(f"\n=== {jpg_path.name} ===")
        print(f"  Format: {img.format}")
        print(f"  Mode: {img.mode}")
        print(f"  Size: {img.size}")
        print(f"  File size: {jpg_path.stat().st_size} bytes")
        
        # Check if image has content
        if img.getbbox():
            print(f"  Has content: Yes")
            bbox = img.getbbox()
            print(f"  Bounding box: {bbox}")
        else:
            print(f"  Has content: NO - This might be the issue!")
            
        return img
    except Exception as e:
        print(f"  Error reading JPG: {e}")
        return None

def test_pdf_conversion(img, jpg_path):
    """Test PDF conversion process."""
    try:
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
            print(f"  Converted to RGB")
        
        # Auto-orient based on EXIF data
        img = ImageOps.exif_transpose(img)
        print(f"  Applied EXIF orientation")
        
        # Calculate optimal size for the PDF
        page_width, page_height = letter
        margin = 0.5 * 72  # 0.5 inches in points
        usable_width = page_width - (2 * margin)
        usable_height = page_height - (2 * margin)
        
        img_aspect = img.width / img.height
        page_aspect = usable_width / usable_height
        
        if img_aspect > page_aspect:
            pdf_width = usable_width
            pdf_height = usable_width / img_aspect
        else:
            pdf_height = usable_height
            pdf_width = usable_height * img_aspect
        
        print(f"  Calculated PDF size: {pdf_width:.1f} x {pdf_height:.1f}")
        
        # Calculate position to center the image
        x = margin + (usable_width - pdf_width) / 2
        y = margin + (usable_height - pdf_height) / 2
        
        print(f"  Position: ({x:.1f}, {y:.1f})")
        
        # Create test PDF
        test_pdf_path = Path(f"test_{jpg_path.stem}.pdf")
        c = canvas.Canvas(str(test_pdf_path), pagesize=letter)
        img_reader = ImageReader(img)
        c.drawImage(img_reader, x, y, pdf_width, pdf_height)
        c.save()
        
        # Verify the created PDF
        reader = PdfReader(str(test_pdf_path))
        print(f"  Created PDF: {len(reader.pages)} pages")
        
        if len(reader.pages) > 0:
            page = reader.pages[0]
            print(f"  PDF page size: {page.mediabox}")
            print(f"  PDF has content: {'/Contents' in page}")
        
        return test_pdf_path
        
    except Exception as e:
        print(f"  Error in conversion: {e}")
        return None

def main():
    """Test specific problematic pages."""
    my_images = Path("./my_images")
    
    # Test the problematic pages mentioned
    problematic_pages = [25, 26, 27, 28, 36, 37, 38, 39, 40, 41, 42, 43, 49, 50, 51, 52, 53, 54, 55, 56, 57]
    
    # Find corresponding files
    all_files = list(my_images.glob("*.jpg"))
    all_files.sort(key=lambda x: x.name.lower())
    
    print("Analyzing problematic pages...")
    
    for i, page_num in enumerate(problematic_pages):
        if i < len(all_files):
            jpg_path = all_files[page_num - 1]  # Adjust for 0-based indexing
            img = analyze_original_jpg(jpg_path)
            
            if img:
                test_pdf = test_pdf_conversion(img, jpg_path)
                if test_pdf:
                    print(f"  ✓ Test PDF created: {test_pdf.name}")
                else:
                    print(f"  ✗ Failed to create test PDF")
        else:
            print(f"\n=== Page {page_num} ===")
            print(f"  File not found (index out of range)")

if __name__ == "__main__":
    main()
