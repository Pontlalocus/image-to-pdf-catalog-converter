#!/usr/bin/env python3
"""
Fixed PDF Catalog Merger

This script fixes the black page issue by using a more robust
PDF generation method that properly embeds images.

Usage:
    python fixed_catalog_merger.py
    python fixed_catalog_merger.py -d /path/to/images -o catalog.pdf
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple
import argparse
from datetime import datetime

try:
    from PyPDF2 import PdfReader, PdfWriter
    from PIL import Image, ImageOps
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
except ImportError as e:
    print(f"Error: Missing required library. Install with: pip install PyPDF2 Pillow reportlab")
    print(f"Specific error: {e}")
    sys.exit(1)


class FixedCatalogMerger:
    """Fixed catalog merger that properly handles image embedding."""
    
    def __init__(self, margin_inches: float = 0.5):
        """Initialize the fixed catalog merger."""
        self.cover_filename = "cover.pdf"
        self.back_cover_filename = "back_cover.pdf"
        self.page_size = letter
        self.page_width, self.page_height = self.page_size
        self.margin = margin_inches * 72  # Convert inches to points
    
    def find_or_create_cover_files(self, directory: Path) -> Tuple[Optional[Path], Optional[Path]]:
        """
        Find existing cover files or create them if they don't exist.
        
        Args:
            directory: Directory to search/create cover files
            
        Returns:
            Tuple of (cover_path, back_cover_path)
        """
        cover_path = directory / self.cover_filename
        back_cover_path = directory / self.back_cover_filename
        
        # Check if cover files exist
        if not cover_path.exists():
            print("⚠ Cover file not found. Creating a simple cover...")
            if self.create_simple_cover(cover_path, "CATALOG COVER"):
                print(f"✓ Created cover: {cover_path.name}")
            else:
                cover_path = None
        else:
            print(f"✓ Found existing cover: {cover_path.name}")
        
        if not back_cover_path.exists():
            print("⚠ Back cover file not found. Creating a simple back cover...")
            if self.create_simple_cover(back_cover_path, "BACK COVER"):
                print(f"✓ Created back cover: {back_cover_path.name}")
            else:
                back_cover_path = None
        else:
            print(f"✓ Found existing back cover: {back_cover_path.name}")
        
        return cover_path, back_cover_path
    
    def create_simple_cover(self, output_path: Path, title: str) -> bool:
        """
        Create a simple cover page with text.
        
        Args:
            output_path: Path to save the cover PDF
            title: Title text for the cover
            
        Returns:
            True if successful, False otherwise
        """
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
    
    def convert_jpg_to_pdf_fixed(self, jpg_path: Path, output_path: Path) -> bool:
        """
        Convert a JPG image to a letter-sized PDF with fixed embedding.
        
        Args:
            jpg_path: Path to the JPG file
            output_path: Path for the output PDF file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Open and process the image
            img = Image.open(jpg_path)
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Auto-orient based on EXIF data
            try:
                img = ImageOps.exif_transpose(img)
            except:
                pass  # Ignore EXIF errors
            
            # Calculate optimal size for the PDF
            usable_width = self.page_width - (2 * self.margin)
            usable_height = self.page_height - (2 * self.margin)
            
            img_aspect = img.width / img.height
            page_aspect = usable_width / usable_height
            
            if img_aspect > page_aspect:
                pdf_width = usable_width
                pdf_height = usable_width / img_aspect
            else:
                pdf_height = usable_height
                pdf_width = usable_height * img_aspect
            
            # Calculate position to center the image
            x = self.margin + (usable_width - pdf_width) / 2
            y = self.margin + (usable_height - pdf_height) / 2
            
            # Create PDF with explicit compression settings
            c = canvas.Canvas(str(output_path), pagesize=self.page_size)
            
            # Save the image to a temporary file to ensure proper embedding
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_img:
                img.save(temp_img.name, 'PNG')
                
                # Use the saved image file
                img_reader = ImageReader(temp_img.name)
                c.drawImage(img_reader, x, y, pdf_width, pdf_height, 
                           preserveAspectRatio=True, mask='auto')
            
            c.save()
            
            # Clean up temp file
            os.unlink(temp_img.name)
            
            # Verify the PDF was created properly
            if output_path.exists() and output_path.stat().st_size > 1000:  # Should be larger than 1KB
                return True
            else:
                print(f"⚠ Warning: {jpg_path.name} created small PDF ({output_path.stat().st_size} bytes)")
                return False
            
        except Exception as e:
            print(f"✗ Error converting {jpg_path.name}: {e}")
            return False
    
    def get_all_files_fixed(self, directory: Path, sort_by: str = "name") -> List[Path]:
        """
        Get all image and PDF files, converting JPGs to PDFs with fixed method.
        
        Args:
            directory: Directory to search for files
            sort_by: Sort method - "name" or "date"
            
        Returns:
            List of PDF file paths
        """
        all_files = []
        temp_dir = directory / "_temp_pdfs_fixed"
        temp_dir.mkdir(exist_ok=True)
        
        # Process all files
        for file in directory.iterdir():
            if not file.is_file():
                continue
            
            # Skip cover and back cover files
            if (file.name.lower() == self.cover_filename.lower() or 
                file.name.lower() == self.back_cover_filename.lower()):
                continue
            
            # Skip temp directory
            if file.name == "_temp_pdfs_fixed":
                continue
            
            if file.suffix.lower() in ['.jpg', '.jpeg']:
                # Convert JPG to PDF with fixed method
                pdf_path = temp_dir / f"{file.stem}.pdf"
                if self.convert_jpg_to_pdf_fixed(file, pdf_path):
                    all_files.append(pdf_path)
                    print(f"✓ Converted: {file.name} -> PDF")
                else:
                    print(f"✗ Failed to convert: {file.name}")
                    
            elif file.suffix.lower() == '.pdf':
                # Use existing PDF
                all_files.append(file)
        
        # Sort files
        if sort_by.lower() == "name":
            all_files.sort(key=lambda x: x.name.lower())
        elif sort_by.lower() == "date":
            all_files.sort(key=lambda x: x.stat().st_ctime)
        
        return all_files
    
    def merge_pdfs(self, pdf_paths: List[Path], output_path: Path) -> bool:
        """
        Merge multiple PDF files into a single PDF.
        
        Args:
            pdf_paths: List of PDF file paths to merge
            output_path: Output PDF file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            writer = PdfWriter()
            
            for pdf_path in pdf_paths:
                try:
                    reader = PdfReader(str(pdf_path))
                    
                    # Validate that PDF has pages
                    if len(reader.pages) == 0:
                        print(f"⚠ Warning: {pdf_path.name} has no pages, skipping")
                        continue
                    
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
        """
        Create a complete catalog by converting images and merging PDFs.
        
        Args:
            input_directory: Directory containing image/PDF files
            output_file: Output PDF filename
            sort_by: Sort method for inner pages ("name" or "date")
            
        Returns:
            True if successful, False otherwise
        """
        print(f"Creating FIXED catalog from: {input_directory}")
        print(f"Sorting inner pages by: {sort_by}")
        print("-" * 50)
        
        # Find or create cover files
        cover_path, back_cover_path = self.find_or_create_cover_files(input_directory)
        
        # Get all files (converting JPGs to PDFs with fixed method)
        inner_pages = self.get_all_files_fixed(input_directory, sort_by)
        
        if not inner_pages:
            print("⚠ No inner page files found")
            if not cover_path and not back_cover_path:
                print("✗ No files found in directory")
                return False
        
        print(f"✓ Found {len(inner_pages)} inner page files")
        
        # Build the complete list of files in order
        pdf_order = []
        
        # Add cover first
        if cover_path:
            pdf_order.append(cover_path)
        
        # Add inner pages
        pdf_order.extend(inner_pages)
        
        # Add back cover last
        if back_cover_path:
            pdf_order.append(back_cover_path)
        
        print(f"\nMerging {len(pdf_order)} files...")
        
        # Create output path
        output_path = input_directory / output_file if not Path(output_file).is_absolute() else Path(output_file)
        
        # Merge PDFs
        if self.merge_pdfs(pdf_order, output_path):
            print(f"\n✓ FIXED Catalog created successfully: {output_path}")
            print(f"Total pages: {len(pdf_order)} files merged")
            
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
        description="FIXED catalog creator with robust JPG conversion and PDF merging",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create catalog from current directory (sorted by name)
  python fixed_catalog_merger.py
  
  # Create catalog from specific directory (sorted by creation date)
  python fixed_catalog_merger.py -d /path/to/images -s date -o catalog.pdf
  
  # Create catalog with custom output name
  python fixed_catalog_merger.py -d images -o my_catalog.pdf
        """
    )
    
    parser.add_argument("-d", "--directory", type=str, default=".",
                        help="Input directory containing image/PDF files (default: current directory)")
    parser.add_argument("-o", "--output", type=str, default="fixed_catalog.pdf",
                        help="Output catalog filename (default: fixed_catalog.pdf)")
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
        merger = FixedCatalogMerger()
        success = merger.create_catalog(
            input_directory=input_dir,
            output_file=args.output,
            sort_by=args.sort
        )
        
        if success:
            print("\n🎉 FIXED catalog creation completed successfully!")
            print("✅ Black page issue should be resolved!")
        else:
            print("\n❌ FIXED catalog creation failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nCatalog creation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
