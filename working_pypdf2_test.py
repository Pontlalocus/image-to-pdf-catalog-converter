#!/usr/bin/env python3
"""
Working test using PyPDF2 3.0.1 API
"""

from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import tempfile

def working_test():
    """Working test of PDF creation with PyPDF2."""
    
    # Test image
    img_path = Path("./my_images/elpana2076_25_Glistening_Foam_at_Dawn__38a2ff11-a31b-43c8-9256-41d27ac8d307.jpg")
    if not img_path.exists():
        print("Test image not found")
        return
    
    img = Image.open(img_path)
    print(f"Image: {img.size}")
    
    # Create PDF using PyPDF2
    from PyPDF2 import PdfFileWriter
    
    pdf_path = Path("working_pypdf2_test.pdf")
    
    # Create a new PDF with the image
    writer = PdfFileWriter()
    
    # Add a blank page
    page = writer.add_blank_page(width=612, height=792)
    
    # Convert image to bytes
    img_bytes = tempfile.BytesIO()
    img.save(img_bytes, format='PNG')
    
    # Add image to the page
    page.insert_image(img_bytes.getvalue(), x=100, y=100, width=400, height=400)
    
    # Save the PDF
    with open(pdf_path, 'wb') as f:
        writer.write(f)
    
    # Analyze the result
    reader = PdfReader(str(pdf_path))
    page = reader.pages[0]
    
    print(f"PDF created: {pdf_path.stat().st_size} bytes")
    print(f"Page has contents: {'/Contents' in page}")
    
    if '/Contents' in page:
        contents = page['/Contents']
        print(f"Contents type: {type(contents)}")
        print(f"Contents: {contents}")

if __name__ == "__main__":
    working_test()
