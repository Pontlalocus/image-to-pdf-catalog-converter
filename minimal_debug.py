#!/usr/bin/env python3
"""
Minimal debugging script to identify blank page issue
"""

from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def minimal_test():
    """Minimal test of PDF creation."""
    
    # Test image
    img_path = Path("./my_images/elpana2076_25_Glistening_Foam_at_Dawn__38a2ff11-a31b-43c8-9256-41d27ac8d307.jpg")
    if not img_path.exists():
        print("Test image not found")
        return
    
    img = Image.open(img_path)
    print(f"Image: {img.size}")
    
    # Create PDF
    pdf_path = Path("minimal_test.pdf")
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    
    # Simple drawImage
    c.drawImage(img, 100, 100, 400, 400)
    c.save()
    
    # Analyze
    reader = PdfReader(str(pdf_path))
    page = reader.pages[0]
    
    print(f"PDF created: {pdf_path.stat().st_size} bytes")
    print(f"Page has contents: {'/Contents' in page}")
    
    if '/Contents' in page:
        contents = page['/Contents']
        print(f"Contents type: {type(contents)}")
        print(f"Contents: {contents}")

if __name__ == "__main__":
    minimal_test()
