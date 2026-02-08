#!/usr/bin/env python3
"""
Deep debugging tool to identify blank page issue in PDF merger
"""

from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image, ImageOps
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import tempfile
import os

def analyze_pdf_structure(pdf_path):
    """Deep analysis of PDF structure."""
    try:
        reader = PdfReader(str(pdf_path))
        print(f"\n=== ANALYZING: {pdf_path.name} ===")
        print(f"Pages: {len(reader.pages)}")
        print(f"File size: {pdf_path.stat().st_size} bytes")
        
        for i, page in enumerate(reader.pages):
            print(f"\n--- Page {i+1} ---")
            print(f"MediaBox: {page.mediabox}")
            print(f"CropBox: {getattr(page, 'cropbox', 'Not set')}")
            print(f"BleedBox: {getattr(page, 'bleedbox', 'Not set')}")
            print(f"Rotate: {getattr(page, 'rotate', 'Not set')}")
            
            # Check contents
            if '/Contents' in page:
                contents = page['/Contents']
                print(f"Contents type: {type(contents)}")
                
                if hasattr(contents, 'get_object'):
                    content_obj = contents.get_object()
                    print(f"Content object: {content_obj}")
                    
                    # Check for streams
                    if hasattr(content_obj, 'get_data'):
                        try:
                            data = content_obj.get_data()
                            print(f"Content data length: {len(data)} bytes")
                            print(f"Content data preview: {data[:100]}...")
                            
                            # Check for image references
                            if hasattr(page, '/Resources'):
                                resources = page['/Resources']
                                print(f"Resources: {resources}")
                                
                                if '/XObject' in resources:
                                    xobjects = resources['/XObject']
                                    print(f"XObjects: {list(xobjects.keys()) if hasattr(xobjects, 'keys') else xobjects}")
                else:
                    print("WARNING: Contents has no get_object method")
            else:
                print("WARNING: Page has no contents")
                
        return reader
        
    except Exception as e:
        print(f"Error analyzing {pdf_path.name}: {e}")
        return None

def test_individual_pdf_creation(jpg_path):
    """Test creating PDF from JPG with multiple methods."""
    try:
        img = Image.open(jpg_path)
        print(f"\n=== TESTING: {jpg_path.name} ===")
        print(f"Original size: {img.size}")
        print(f"Original mode: {img.mode}")
        
        # Method 1: Direct drawImage
        print("\n--- Method 1: Direct drawImage ---")
        pdf_path1 = Path(f"test_method1_{jpg_path.stem}.pdf")
        c1 = canvas.Canvas(str(pdf_path1), pagesize=letter)
        
        # Calculate size
        usable_width = 612 - 72  # 0.5 inch margins
        usable_height = 792 - 72
        
        img_aspect = img.width / img.height
        page_aspect = usable_width / usable_height
        
        if img_aspect > page_aspect:
            pdf_width = usable_width
            pdf_height = usable_width / img_aspect
        else:
            pdf_height = usable_height
            pdf_width = usable_height * img_aspect
        
        x = 36 + (usable_width - pdf_width) / 2
        y = 36 + (usable_height - pdf_height) / 2
        
        c1.drawImage(img, x, y, pdf_width, pdf_height)
        c1.save()
        
        # Method 2: Using ImageReader
        print("\n--- Method 2: Using ImageReader ---")
        pdf_path2 = Path(f"test_method2_{jpg_path.stem}.pdf")
        c2 = canvas.Canvas(str(pdf_path2), pagesize=letter)
        
        img_reader = ImageReader(img)
        c2.drawImage(img_reader, x, y, pdf_width, pdf_height)
        c2.save()
        
        # Method 3: Using temporary PNG file
        print("\n--- Method 3: Using temporary PNG ---")
        pdf_path3 = Path(f"test_method3_{jpg_path.stem}.pdf")
        c3 = canvas.Canvas(str(pdf_path3), pagesize=letter)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_img:
            img.save(temp_img.name, 'PNG')
            img_reader3 = ImageReader(temp_img.name)
            c3.drawImage(img_reader3, x, y, pdf_width, pdf_height)
        
        c3.save()
        os.unlink(temp_img.name)
        
        # Analyze all three
        for i, (path, method) in enumerate([(pdf_path1, "Direct"), (pdf_path2, "ImageReader"), (pdf_path3, "TempPNG")]):
            print(f"\n--- Analysis {method} ---")
            if path.exists():
                reader = PdfReader(str(path))
                page = reader.pages[0]
                print(f"File size: {path.stat().st_size} bytes")
                print(f"Has contents: {'/Contents' in page}")
                
                if '/Contents' in page:
                    contents = page['/Contents']
                    if hasattr(contents, 'get_object'):
                        content_obj = contents.get_object()
                        if hasattr(content_obj, 'get_data'):
                            data = content_obj.get_data()
                            print(f"Content data length: {len(data)} bytes")
                            print(f"Content data preview: {data[:100]}...")
                            raw_data = content_obj.get_data()
                            print(f"Raw data length: {len(raw_data)} bytes")
                            print(f"Raw data preview: {raw_data[:100]}...")
        
        return pdf_path1, pdf_path2, pdf_path3
        
    except Exception as e:
        print(f"Error testing {jpg_path.name}: {e}")
        return None, None, None


def main():
    """Main debugging function."""
    my_images = Path("./my_images")
    
    # Test a few problematic files
    test_files = [
        "elpana2076_25_Glistening_Foam_at_Dawn__38a2ff11-a31b-43c8-9256-41d27ac8d307.jpg",
        "elpana2076_26_Shattered_Identity_in_Color_Boy__f943b5a2-1928-4db3-87ea-da9a57f29f3a.jpg",
        "elpana2076_27_Echoes_of_a_Woman_s_Soul__ce4bd5c9-d1c9-48d3-9dd5-69249b786f83.jpg"
    ]
    
    for filename in test_files:
        jpg_path = my_images / filename
        if jpg_path.exists():
            test_individual_pdf_creation(jpg_path)
        else:
            print(f"File not found: {filename}")


if __name__ == "__main__":
    main()
