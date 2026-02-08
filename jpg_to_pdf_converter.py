#!/usr/bin/env python3
"""
JPG to PDF Converter for Catalog

Converts JPG images from a folder to individual letter-sized PDF files.
Each image is scaled to fit as large as possible on the letter-sized page
while maintaining aspect ratio.

Usage:
    python jpg_to_pdf_converter.py
    python jpg_to_pdf_converter.py -d /path/to/images
    python jpg_to_pdf_converter.py -d photos -o output_folder
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageOps
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


class JPGToPDFConverter:
    """Convert JPG images to letter-sized PDF files."""
    
    def __init__(self, margin_inches: float = 0.5):
        """
        Initialize the converter.
        
        Args:
            margin_inches: Margin around the image in inches
        """
        self.page_size = letter
        self.page_width, self.page_height = self.page_size
        self.margin = margin_inches * 72  # Convert inches to points
        
    def calculate_image_size(self, img_width: int, img_height: int) -> tuple:
        """
        Calculate the optimal size for an image on a letter-sized page.
        
        Args:
            img_width: Original image width in pixels
            img_height: Original image height in pixels
            
        Returns:
            Tuple of (width, height) in points for the PDF
        """
        # Usable area after margins
        usable_width = self.page_width - (2 * self.margin)
        usable_height = self.page_height - (2 * self.margin)
        
        # Calculate aspect ratios
        img_aspect = img_width / img_height
        page_aspect = usable_width / usable_height
        
        if img_aspect > page_aspect:
            # Image is wider than the page ratio - fit to width
            pdf_width = usable_width
            pdf_height = usable_width / img_aspect
        else:
            # Image is taller than the page ratio - fit to height
            pdf_height = usable_height
            pdf_width = usable_height * img_aspect
            
        return pdf_width, pdf_height
    
    def convert_image_to_pdf(self, image_path: Path, output_path: Path) -> bool:
        """
        Convert a single JPG image to a letter-sized PDF.
        
        Args:
            image_path: Path to the JPG image
            output_path: Path for the output PDF file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Open and process the image
            img = Image.open(image_path)
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Auto-orient based on EXIF data
            img = ImageOps.exif_transpose(img)
            
            # Calculate optimal size for the PDF
            pdf_width, pdf_height = self.calculate_image_size(img.width, img.height)
            
            # Calculate position to center the image
            x = self.margin + (self.page_width - (2 * self.margin) - pdf_width) / 2
            y = self.margin + (self.page_height - (2 * self.margin) - pdf_height) / 2
            
            # Create PDF
            c = canvas.Canvas(str(output_path), pagesize=self.page_size)
            img_reader = ImageReader(img)
            c.drawImage(img_reader, x, y, pdf_width, pdf_height)
            c.save()
            
            print(f"✓ Converted: {image_path.name} -> {output_path.name}")
            return True
            
        except Exception as e:
            print(f"✗ Error converting {image_path.name}: {e}")
            return False
    
    def convert_folder(self, input_folder: Path, output_folder: Path = None) -> None:
        """
        Convert all JPG images in a folder to individual PDF files.
        
        Args:
            input_folder: Folder containing JPG images
            output_folder: Folder for output PDF files (default: same as input)
        """
        if output_folder is None:
            output_folder = input_folder
        
        # Create output folder if it doesn't exist
        output_folder.mkdir(parents=True, exist_ok=True)
        
        # Find all JPG files
        jpg_files = []
        for pattern in ["*.jpg", "*.jpeg"]:
            jpg_files.extend(input_folder.glob(pattern))
            jpg_files.extend(input_folder.glob(pattern.upper()))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_jpg_files = []
        for file in jpg_files:
            if file not in seen:
                seen.add(file)
                unique_jpg_files.append(file)
        jpg_files = unique_jpg_files
        
        if not jpg_files:
            print(f"No JPG files found in {input_folder}")
            return
        
        print(f"Found {len(jpg_files)} JPG files")
        print(f"Converting to letter-sized PDF files...")
        
        success_count = 0
        for jpg_path in sorted(jpg_files):
            # Create output PDF filename
            pdf_filename = jpg_path.stem + ".pdf"
            pdf_path = output_folder / pdf_filename
            
            # Convert the image
            if self.convert_image_to_pdf(jpg_path, pdf_path):
                success_count += 1
        
        print(f"\nConversion complete: {success_count}/{len(jpg_files)} files converted")
        print(f"PDF files saved to: {output_folder}")


def main():
    """Main function to handle command line arguments."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Convert JPG images to letter-sized PDF files for catalog",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert JPG files in current directory
  python jpg_to_pdf_converter.py
  
  # Convert JPG files from a specific folder
  python jpg_to_pdf_converter.py -d /path/to/images
  
  # Convert and save PDFs to a different folder
  python jpg_to_pdf_converter.py -d photos -o pdf_output
        """
    )
    
    parser.add_argument("-d", "--directory", type=str, default=".",
                        help="Input directory containing JPG files (default: current directory)")
    parser.add_argument("-o", "--output", type=str,
                        help="Output directory for PDF files (default: same as input)")
    parser.add_argument("-m", "--margin", type=float, default=0.5,
                        help="Margin around image in inches (default: 0.5)")
    
    args = parser.parse_args()
    
    # Validate input directory
    input_dir = Path(args.directory)
    if not input_dir.exists():
        print(f"Error: Directory {input_dir} does not exist")
        sys.exit(1)
    
    if not input_dir.is_dir():
        print(f"Error: {input_dir} is not a directory")
        sys.exit(1)
    
    # Set output directory
    output_dir = Path(args.output) if args.output else input_dir
    
    # Create converter and process
    try:
        converter = JPGToPDFConverter(margin_inches=args.margin)
        converter.convert_folder(input_dir, output_dir)
        
    except KeyboardInterrupt:
        print("\nConversion cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
