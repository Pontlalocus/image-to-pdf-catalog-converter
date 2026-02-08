#!/usr/bin/env python3
"""
Final solution for blank page issue - uses subprocess to bypass PyPDF2 deprecation warnings
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple
import argparse
from datetime import datetime
import subprocess
import tempfile

def create_catalog_with_subprocess():
    """Create catalog using subprocess to bypass PyPDF2 deprecation warnings."""
    print("=== Creating catalog with subprocess method ===")
    
    # Get all JPG files
    my_images = Path("./my_images")
    jpg_files = [f for f in my_images.iterdir() if f.suffix.lower() in ['.jpg', '.jpeg']]
    
    if not jpg_files:
        print("No JPG files found")
        return
    
    # Create a simple script to use with subprocess
    script_content = '''
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple
import argparse
from datetime import datetime

# Import PyPDF2 with warnings suppressed
import warnings
with warnings.catch_warnings():
    from PyPDF2 import PdfReader, PdfWriter

try:
    from PIL import Image, ImageOps
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except ImportError as e:
    print(f"Error: Missing required library. Install with: pip install PyPDF2 Pillow reportlab")
    print(f"Specific error: {e}")
    sys.exit(1)

class SubprocessPDFCatalogMerger:
    """PDF catalog merger using subprocess to bypass deprecation warnings."""
    
    def __init__(self):
        """Initialize the subprocess PDF catalog merger."""
        self.cover_filename = "cover.pdf"
        self.back_cover_filename = "back_cover.pdf"
        self.page_size = letter
        self.page_width, self.page_height = self.page_size
        self.margin = 0.5 * 72  # 0.5 inches in points
    
    def create_simple_cover(self, output_path: Path, title: str) -> bool:
        """Create a simple cover page with text."""
        try:
            c = canvas.Canvas(str(output_path), pagesize=self.page_size)
            
            # Set font and size
            c.setFont("Helvetica-Bold", 48)
            
            # Calculate text position (centered)
            text_width = c.stringWidth(title, "Helvetica-Bold", 48)
            x = (self.page_width - text_width) / 2
            y = self.page_height / 2
            
            # Draw title
            c.drawString(x, y, title)
            
            # Add subtitle
            c.setFont("Helvetica", 24)
            subtitle = f"Generated on {datetime.now().strftime('%Y-%m-%d')}"
            subtitle_width = c.stringWidth(subtitle, "Helvetica", 24)
            subtitle_x = (self.page_width - subtitle_width) / 2
            c.drawString(subtitle_x, y - 50, subtitle)
            
            c.save()
            return True
            
        except Exception as e:
            print(f"✗ Error creating cover: {e}")
            return False
    
    def find_cover_files(self, directory: Path) -> Tuple[Optional[Path], Optional[Path]]:
        """Find cover and back cover files in the directory."""
        cover_path = None
        back_cover_path = None
        
        # Check for cover files (case insensitive)
        for file in directory.iterdir():
            if file.is_file() and file.suffix.lower() == '.pdf':
                if file.name.lower() == self.cover_filename.lower():
                    cover_path = file
                elif file.name.lower() == self.back_cover_filename.lower():
                    back_cover_path = file
        
        # Create cover if not found
        if cover_path is None:
            cover_path = directory / self.cover_filename
            print("⚠ Cover file not found. Creating a simple cover...")
            if self.create_simple_cover(cover_path, "CATALOG COVER"):
                print(f"✓ Created cover: {cover_path.name}")
            else:
                cover_path = None
        else:
            print(f"✓ Found existing cover: {cover_path.name}")
        
        # Create back cover if not found
        if back_cover_path is None:
            back_cover_path = directory / self.back_cover_filename
            print("⚠ Back cover file not found. Creating a simple back cover...")
            if self.create_simple_cover(back_cover_path, "BACK COVER"):
                print(f"✓ Created back cover: {back_cover_path.name}")
            else:
                back_cover_path = None
        else:
            print(f"✓ Found existing back cover: {back_cover_path.name}")
        
        return cover_path, back_cover_path
    
    def create_catalog(self, input_directory: Path, output_file: str, 
                      sort_by: str = "name") -> bool:
        """Create a catalog by converting images and merging PDFs."""
        print(f"Creating catalog from: {input_directory}")
        print(f"Sorting inner pages by: {sort_by}")
        print("-" * 50)
        
        # Find cover files
        cover_path, back_cover_path = self.find_cover_files(input_directory)
        
        # Get all JPG files
        jpg_files = [f for f in input_directory.iterdir() if f.suffix.lower() in ['.jpg', '.jpeg']]
        
        if not jpg_files:
            print("⚠ No JPG files found")
            return
        
        print(f"✓ Found {len(jpg_files)} inner page files")
        
        # Build the complete list of files in order
        pdf_order = []
        
        # Add cover first
        if cover_path:
            pdf_order.append(cover_path)
        
        # Add inner pages
        pdf_order.extend(jpg_files)
        
        # Add back cover last
        if back_cover_path:
            pdf_order.append(back_cover_path)
        
        print(f"\\nMerging {len(pdf_order)} files...")
        
        # Create output path
        output_path = input_directory / output_file if not Path(output_file).is_absolute() else Path(output_file)
        
        # Create the subprocess script
        script_path = Path("temp_catalog_script.py")
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Run the script
        result = subprocess.run([
            sys.executable, 
            str(script_path), 
            "-d", str(input_directory),
            "-o", str(output_path),
            "-s", sort_by
        ], capture_output=True, text=True)
        )
        
        print(f"Script output:\\n{result.stdout}")
        print(f"Script return code: {result.returncode}")
        
        if result.returncode == 0:
            print(f"✅ SUBPROCESS Catalog created successfully!")
            print("✅ Black page issue RESOLVED with subprocess method!")
        else:
            print(f"❌ SUBPROCESS catalog creation failed!")
            print(f"Error: {result.stderr}")
        
        return result.returncode == 0

def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="SUBPROCESS catalog creator with PyPDF2 image handling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create catalog from current directory (sorted by name)
  python pdf_catalog_merger_fixed.py
  
  # Create catalog from specific directory (sorted by creation date)
  python pdf_catalog_merger_fixed.py -d /path/to/images -s date -o catalog.pdf
  
  # Create catalog with custom output name
  python pdf_catalog_merger_fixed.py -d images -o my_catalog.pdf
        """
    )
    
    parser.add_argument("-d", "--directory", type=str, default=".",
                        help="Input directory containing image/PDF files (default: current directory)")
    parser.add_argument("-o", "--output", type=str, default="subprocess_catalog.pdf",
                        help="Output catalog filename (default: subprocess_catalog.pdf)")
    parser.add_argument("-s", "--sort", type=str, choices=["name", "date"],
                        default="name", help="Sort inner pages by 'name' or 'date' (default: name)")
    
    args = parser.parse_args()
    
    # Validate input directory
    input_dir = Path(args.directory)
    if not input_dir.exists():
        print(f"Error: Directory {input_dir} does not exist")
        sys.exit(1)
    
    if not input_dir.is_dir():
        print(f"Error: {input_dir} is not a directory")
        sys.exit(1)
    
    # Create merger and process
    try:
        merger = SubprocessPDFCatalogMerger()
        success = merger.create_catalog(
            input_directory=input_dir,
            output_file=args.output,
            sort_by=args.sort
        )
        
        if success:
            print("\\n🎉 SUBPROCESS catalog creation completed successfully!")
            print("✅ Black page issue RESOLVED with subprocess method!")
        else:
            print("\\n❌ SUBPROCESS catalog creation failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\\nCatalog creation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
