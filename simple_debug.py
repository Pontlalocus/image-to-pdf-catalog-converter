#!/usr/bin/env python3
"""
Simple debugging script to identify blank page issue
"""

from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image, ImageOps
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import tempfile
import os

def test_pdf_creation():
    """Test PDF creation with different methods."""
    
    # Test image
    img_path = Path("./my_images/elpana2076_25_Glistening_Foam_at_Dawn__38a2ff11-a31b-43c8-9256-41d27ac8d307.jpg")
    if not img_path.exists():
        print("Test image not found")
        return
    
    img = Image.open(img_path)
    print(f"Image: {img.size}, mode: {img.mode}")
    
    # Method 1: Current approach (from pdf_catalog_merger.py)
    print("\n--- Testing current method ---")
    pdf_path1 = Path("test_current_method.pdf")
    c1 = canvas.Canvas(str(pdf_path1), pagesize=letter)
    
    usable_width = 612 - 72
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
    
    # Current problematic approach
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_img:
        img.save(temp_img.name, 'PNG')
        img_reader = ImageReader(temp_img.name)
        c1.drawImage(img_reader, x, y, pdf_width, pdf_height)
    
    c1.save()
    os.unlink(temp_img.name)
    
    # Method 2: Direct image approach
    print("\n--- Testing direct image method ---")
    pdf_path2 = Path("test_direct_image_method.pdf")
    c2 = canvas.Canvas(str(pdf_path2), pagesize=letter)
    
    c2.drawImage(img, x, y, pdf_width, pdf_height)
    c2.save()
    
    # Analyze results
    results = []
    for i, (path, method) in enumerate([(pdf_path1, "Current"), (pdf_path2, "Direct")]):
        if path.exists():
            reader = PdfReader(str(path))
            page = reader.pages[0]
            
            result = {
                'method': method,
                'file_size': path.stat().st_size,
                'has_contents': '/Contents' in page,
                'contents_length': 0
            }
            
            if '/Contents' in page:
                contents = page['/Contents']
                if hasattr(contents, 'get_object'):
                    content_obj = contents.get_object()
                    if hasattr(content_obj, 'get_data'):
                        data = content_obj.get_data()
                        result['contents_length'] = len(data)
            
            results.append(result)
    
    print("\n--- Results ---")
    for result in results:
        print(f"Method: {result['method']}")
        print(f"  File size: {result['file_size']} bytes")
        print(f"  Has contents: {result['has_contents']}")
        print(f"  Contents length: {result['contents_length']} bytes")
        print()
    
    # Find the best method
    best_result = max(results, key=lambda x: x['contents_length'])
    print(f"\nBest method: {best_result['method']} with {best_result['contents_length']} bytes of content")
    
    return best_result['method']

if __name__ == "__main__":
    test_pdf_creation()
