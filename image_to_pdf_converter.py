#!/usr/bin/env python3
"""
Image to PDF Converter for Catalog Generation

This script converts images to PDF format, suitable for creating catalogs.
It supports multiple image formats and provides options for page layout,
image sizing, and metadata.

Author: AI Assistant
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image, ImageOps
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


class ImageToPDFConverter:
    """Convert images to PDF for catalog purposes."""
    
    def __init__(self, page_size: str = "A4", margin: float = 0.5):
        """
        Initialize the converter.
        
        Args:
            page_size: Page size ("A4" or "letter")
            margin: Margin in inches
        """
        self.page_size = A4 if page_size.upper() == "A4" else letter
        self.margin = margin * 72  # Convert inches to points
        self.page_width, self.page_height = self.page_size
        
    def get_usable_area(self) -> Tuple[float, float]:
        """Get the usable area of the page after margins."""
        width = self.page_width - (2 * self.margin)
        height = self.page_height - (2 * self.margin)
        return width, height
    
    def calculate_image_size(self, img_width: int, img_height: int, 
                            max_width: float, max_height: float,
                            maintain_aspect: bool = True) -> Tuple[float, float]:
        """
        Calculate the optimal size for an image on the page.
        
        Args:
            img_width: Original image width
            img_height: Original image height
            max_width: Maximum width available
            max_height: Maximum height available
            maintain_aspect: Whether to maintain aspect ratio
            
        Returns:
            Tuple of (width, height) for the image
        """
        if not maintain_aspect:
            return max_width, max_height
        
        # Calculate aspect ratios
        img_aspect = img_width / img_height
        max_aspect = max_width / max_height
        
        if img_aspect > max_aspect:
            # Image is wider than available space
            width = max_width
            height = max_width / img_aspect
        else:
            # Image is taller than available space
            height = max_height
            width = max_height * img_aspect
            
        return width, height
    
    def process_image(self, image_path: Path) -> Image.Image:
        """
        Process and prepare an image for PDF conversion.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Processed PIL Image
        """
        try:
            img = Image.open(image_path)
            
            # Convert to RGB if necessary (for PDF compatibility)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Auto-orient based on EXIF data
            img = ImageOps.exif_transpose(img)
            
            return img
            
        except Exception as e:
            raise ValueError(f"Error processing image {image_path}: {e}")
    
    def create_pdf(self, image_paths: List[Path], output_path: Path,
                   layout: str = "single", images_per_page: int = 1,
                   maintain_aspect: bool = True, dpi: int = 300) -> None:
        """
        Create a PDF from a list of images.
        
        Args:
            image_paths: List of image file paths
            output_path: Output PDF file path
            layout: Layout mode ("single", "grid", "catalog")
            images_per_page: Number of images per page (for grid/catalog)
            maintain_aspect: Whether to maintain aspect ratio
            dpi: Output DPI for images
        """
        c = canvas.Canvas(str(output_path), pagesize=self.page_size)
        usable_width, usable_height = self.get_usable_area()
        
        current_page_images = 0
        
        for i, image_path in enumerate(image_paths):
            try:
                img = self.process_image(image_path)
                
                if layout == "single":
                    # One image per page
                    img_width, img_height = self.calculate_image_size(
                        img.width, img.height, usable_width, usable_height, maintain_aspect
                    )
                    
                    # Center the image
                    x = self.margin + (usable_width - img_width) / 2
                    y = self.margin + (usable_height - img_height) / 2
                    
                    # Add image to page
                    img_reader = ImageReader(img)
                    c.drawImage(img_reader, x, y, img_width, img_height)
                    c.showPage()
                    current_page_images = 0
                    
                elif layout in ["grid", "catalog"]:
                    # Multiple images per page
                    if current_page_images == 0:
                        # Start new page
                        current_page_images = 0
                    
                    # Calculate grid position
                    cols = int(images_per_page ** 0.5)
                    rows = (images_per_page + cols - 1) // cols
                    
                    cell_width = usable_width / cols
                    cell_height = usable_height / rows
                    
                    row = current_page_images // cols
                    col = current_page_images % cols
                    
                    # Calculate image size within cell
                    padding = 10  # 10 points padding
                    max_img_width = cell_width - (2 * padding)
                    max_img_height = cell_height - (2 * padding)
                    
                    img_width, img_height = self.calculate_image_size(
                        img.width, img.height, max_img_width, max_img_height, maintain_aspect
                    )
                    
                    # Position image in cell
                    x = self.margin + (col * cell_width) + (cell_width - img_width) / 2
                    y = self.page_height - self.margin - ((row + 1) * cell_height) + (cell_height - img_height) / 2
                    
                    # Add image
                    img_reader = ImageReader(img)
                    c.drawImage(img_reader, x, y, img_width, img_height)
                    
                    # Add filename as caption (catalog mode)
                    if layout == "catalog":
                        caption_y = y - 15
                        c.setFont("Helvetica", 8)
                        c.drawCentredText(x + img_width/2, caption_y, image_path.stem)
                    
                    current_page_images += 1
                    
                    # Start new page if needed
                    if current_page_images >= images_per_page:
                        c.showPage()
                        current_page_images = 0
                        
            except Exception as e:
                print(f"Warning: Skipping {image_path} due to error: {e}")
                continue
        
        # Finalize PDF
        if current_page_images > 0:
            c.showPage()
        
        c.save()
        print(f"PDF created successfully: {output_path}")
    
    def convert_images_to_pdf(self, input_dir: Path, output_file: str,
                             image_extensions: List[str] = None,
                             layout: str = "single", images_per_page: int = 1,
                             maintain_aspect: bool = True, dpi: int = 300) -> None:
        """
        Convert all images in a directory to a PDF.
        
        Args:
            input_dir: Directory containing images
            output_file: Output PDF filename
            image_extensions: List of supported image extensions
            layout: Layout mode ("single", "grid", "catalog")
            images_per_page: Number of images per page
            maintain_aspect: Whether to maintain aspect ratio
            dpi: Output DPI
        """
        if image_extensions is None:
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
        
        # Find all image files
        image_paths = []
        for ext in image_extensions:
            image_paths.extend(input_dir.glob(f"*{ext}"))
            image_paths.extend(input_dir.glob(f"*{ext.upper()}"))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_image_paths = []
        for file in image_paths:
            if file not in seen:
                seen.add(file)
                unique_image_paths.append(file)
        image_paths = unique_image_paths
        
        # Sort images alphabetically
        image_paths.sort(key=lambda x: x.name.lower())
        
        if not image_paths:
            raise ValueError(f"No images found in {input_dir}")
        
        print(f"Found {len(image_paths)} images")
        
        # Create output path
        output_path = input_dir / output_file if not Path(output_file).is_absolute() else Path(output_file)
        
        # Create PDF
        self.create_pdf(image_paths, output_path, layout, images_per_page, maintain_aspect, dpi)


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert images to PDF for catalog generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert all images in current directory to single-page PDF
  python image_to_pdf_converter.py -d . -o catalog.pdf
  
  # Create catalog with 4 images per page in grid layout
  python image_to_pdf_converter.py -d images -o catalog.pdf -l grid -n 4
  
  # Create catalog with captions
  python image_to_pdf_converter.py -d photos -o catalog.pdf -l catalog -n 6
        """
    )
    
    parser.add_argument("-d", "--directory", type=str, default=".",
                        help="Input directory containing images (default: current directory)")
    parser.add_argument("-o", "--output", type=str, default="catalog.pdf",
                        help="Output PDF filename (default: catalog.pdf)")
    parser.add_argument("-l", "--layout", type=str, choices=["single", "grid", "catalog"],
                        default="single", help="Layout mode (default: single)")
    parser.add_argument("-n", "--images-per-page", type=int, default=1,
                        help="Number of images per page for grid/catalog layouts (default: 1)")
    parser.add_argument("-p", "--page-size", type=str, choices=["A4", "letter"],
                        default="A4", help="Page size (default: A4)")
    parser.add_argument("-m", "--margin", type=float, default=0.5,
                        help="Margin in inches (default: 0.5)")
    parser.add_argument("--no-aspect", action="store_true",
                        help="Don't maintain aspect ratio")
    parser.add_argument("--dpi", type=int, default=300,
                        help="Output DPI (default: 300)")
    
    args = parser.parse_args()
    
    # Validate arguments
    input_dir = Path(args.directory)
    if not input_dir.exists():
        print(f"Error: Directory {input_dir} does not exist")
        sys.exit(1)
    
    if not input_dir.is_dir():
        print(f"Error: {input_dir} is not a directory")
        sys.exit(1)
    
    if args.images_per_page < 1:
        print("Error: images-per-page must be at least 1")
        sys.exit(1)
    
    # Create converter and process
    try:
        converter = ImageToPDFConverter(page_size=args.page_size, margin=args.margin)
        converter.convert_images_to_pdf(
            input_dir=input_dir,
            output_file=args.output,
            layout=args.layout,
            images_per_page=args.images_per_page,
            maintain_aspect=not args.no_aspect,
            dpi=args.dpi
        )
        print("Conversion completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
