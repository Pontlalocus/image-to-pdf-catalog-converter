#!/usr/bin/env python3
"""
Investigate the conversion issue that causes black pages
"""

from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image, ImageOps
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os

def create_test_pdf_with_image(img_path, output_path):
    """Create a PDF with better error handling."""
    try:
        # Open and process the image
        img = Image.open(img_path)
        
        print(f"\n=== Processing {img_path.name} ===")
        print(f"  Original size: {img.size}")
        print(f"  Original mode: {img.mode}")
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
            print(f"  Converted to RGB")
        
        # Auto-orient based on EXIF data
        try:
            img = ImageOps.exif_transpose(img)
            print(f"  Applied EXIF orientation")
        except Exception as e:
            print(f"  EXIF orientation failed: {e}")
        
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
        
        print(f"  Final PDF size: {pdf_width:.1f} x {pdf_height:.1f}")
        
        # Calculate position to center the image
        x = margin + (usable_width - pdf_width) / 2
        y = margin + (usable_height - pdf_height) / 2
        
        print(f"  Position: ({x:.1f}, {y:.1f})")
        
        # Create PDF with explicit settings
        c = canvas.Canvas(str(output_path), pagesize=letter)
        
        # Add the image with explicit parameters
        img_reader = ImageReader(img)
        c.drawImage(img_reader, x, y, pdf_width, pdf_height, 
                   preserveAspectRatio=True, mask='auto')
        
        # Save the PDF
        c.save()
        
        # Verify the created PDF
        if output_path.exists():
            reader = PdfReader(str(output_path))
            print(f"  Created PDF: {len(reader.pages)} pages")
            
            if len(reader.pages) > 0:
                page = reader.pages[0]
                print(f"  PDF page size: {page.mediabox}")
                print(f"  PDF has content: {'/Contents' in page}")
                
                # Check content stream
                if '/Contents' in page:
                    contents = page['/Contents']
                    print(f"  Content stream length: {len(str(contents))}")
                
                return True
            else:
                print("  ERROR: PDF has no pages!")
                return False
        else:
            print("  ERROR: PDF file not created!")
            return False
            
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_problematic_files():
    """Test the specific files that become black pages."""
    my_images = Path("./my_images")
    
    # Get all JPG files sorted
    jpg_files = [f for f in my_images.glob("*.jpg")]
    jpg_files.sort(key=lambda x: x.name.lower())
    
    # Test the problematic indices (0-based)
    problematic_indices = [24, 25, 26, 27, 35, 36, 37, 38, 39, 40, 41, 42, 48, 49, 50, 51, 52, 53, 54, 55, 56]
    
    print("Testing problematic files with improved conversion...")
    
    test_dir = Path("./test_improved_conversion")
    test_dir.mkdir(exist_ok=True)
    
    success_count = 0
    for idx in problematic_indices:
        if idx < len(jpg_files):
            jpg_path = jpg_files[idx]
            pdf_path = test_dir / f"improved_{jpg_path.stem}.pdf"
            
            if create_test_pdf_with_image(jpg_path, pdf_path):
                success_count += 1
                print(f"  ✓ SUCCESS: {pdf_path.name}")
            else:
                print(f"  ✗ FAILED: {pdf_path.name}")
    
    print(f"\nSuccessfully created {success_count}/{len(problematic_indices)} test PDFs")
    
    # Test merging the improved PDFs
    if success_count > 0:
        print("\nTesting merge of improved PDFs...")
        test_files = list(test_dir.glob("improved_*.pdf"))
        test_files.sort(key=lambda x: x.name.lower())
        
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
        test_output = Path("test_improved_merge.pdf")
        with open(test_output, 'wb') as f:
            writer.write(f)
        
        print(f"Improved test merge saved: {test_output}")
        print(f"Total pages: {len(writer.pages)}")

if __name__ == "__main__":
    test_problematic_files()
