from pathlib import Path
from PyPDF2 import PdfReader

my_images = Path("./my_images")
pdf_files = [f for f in my_images.iterdir() if f.is_file() and f.suffix.lower() == '.pdf']

print(f"Found {len(pdf_files)} PDF files:")
for pdf in pdf_files[:3]:
    print(f"  {pdf.name}")

if pdf_files:
    try:
        first_pdf = pdf_files[0]
        reader = PdfReader(str(first_pdf))
        print(f"\nAnalyzing {first_pdf.name}:")
        print(f"  Pages: {len(reader.pages)}")
        print(f"  File size: {first_pdf.stat().st_size} bytes")
        
        if len(reader.pages) > 0:
            page = reader.pages[0]
            print(f"  Page mediabox: {page.mediabox}")
            print(f"  Has content: {'/Contents' in page}")
        else:
            print("  WARNING: No pages found!")
            
    except Exception as e:
        print(f"Error: {e}")
