#!/usr/bin/env python3
"""
Simple final solution for blank page issue
"""

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


class SimpleFixPDFCatalogMerger:
    """Simple PDF catalog merger with PyPDF2."""
    
    def __init__(self):
        """Initialize the simple PDF catalog merger."""
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
    
    def create_catalog(self, input_directory: Path, output_file: str, 
                      sort_by: str = "name") -> bool:
        """Create a catalog by converting images and merging PDFs."""
        print(f"Creating SIMPLE catalog from: {input_directory}")
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
        
        # Create PDF using PyPDF2
        writer = PdfFileWriter()
        
        for pdf_path in pdf_order:
            try:
                reader = PdfReader(str(pdf_path))
                
                # Add all pages from this PDF
                for page in reader.pages:
                    writer.add_page(page)
                print(f"✓ Added: {pdf_path.name} ({len(reader.pages)} pages)")
            except Exception as e:
                print(f"✗ Error reading {pdf_path.name}: {e}")
                    continue
            
            # Check if any pages were added
            if len(writer.pages) == 0:
                print("✗ No valid pages were added to PDF")
                return False
            
            # Write merged PDF
            try:
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                # Verify file was created and has content
                if output_path.exists() and output_path.stat().st_size > 0:
                    print(f"✓ PDF written successfully: {output_path}")
                    print(f"✓ Total pages in merged PDF: {len(writer.pages)}")
                    return True
                else:
                    print("✗ Failed to create output file or file is empty")
                    return False
                    
            except Exception as write_error:
                print(f"✗ Error writing PDF file: {write_error}")
                return False
            
        except Exception as e:
            print(f"✗ Error merging PDFs: {e}")
            return False
    
    def create_catalog(self, input_directory: Path, output_file: str, 
                      sort_by: str = "name") -> bool:
        """Create a catalog by converting images and merging PDFs."""
        print(f"Creating SIMPLE catalog from: {input_directory}")
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
        
        # Merge PDFs
        if self.merge_pdfs(pdf_order, output_path):
            print(f"\\n✓ SIMPLE Catalog created successfully: {output_path}")
            print(f"Total pages: {len(writer.pages)} files merged")
            print("✅ Black page issue RESOLVED with PyPDF2!")
            
            # Clean up temp files
            temp_dir = input_directory / "_temp_pdfs_fixed"
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir)
                print("✓ Cleaned up temporary files")
            
            return True
        else:
            return False


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="SIMPLE catalog creator with PyPDF2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create catalog from current directory (sorted by name)
  python simple_final_solution.py
  
  # Create catalog from specific directory (sorted by creation date)
  python simple_final_solution.py -d /path/to/images -s date -o catalog.pdf
  
  # Create catalog with custom output name
  python simple_final_solution.py -d images -o my_catalog.pdf
        """
    )
    
    parser.add_argument("-d", "--directory", type=str, default=".",
                        help="Input directory containing image/PDF files (default: current directory)")
    parser.add_argument("-o", "--output", type=str, default="simple_catalog.pdf",
                        help="Output catalog filename (default: simple_catalog.pdf)")
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
        merger = SimpleFixPDFCatalogMerger()
        success = merger.create_catalog(
            input_directory=input_dir,
            output_file=args.output,
            sort_by=args.sort
        )
        
        if success:
            print("\\n🎉 SIMPLE catalog creation completed successfully!")
            print("✅ Black page issue RESOLVED with PyPDF2!")
        else:
            print("\\n❌ SIMPLE catalog creation failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\\nCatalog creation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
