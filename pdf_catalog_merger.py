#!/usr/bin/env python3
"""
PDF Catalog Merger

Merges single PDF files into a multi-page catalog with cover and back cover.
The script searches for cover.pdf and back_cover.pdf files and arranges 
inner pages according to user preference (by name or creation date).

Usage:
    python pdf_catalog_merger.py
    python pdf_catalog_merger.py -d /path/to/pdfs -o catalog.pdf
    python pdf_catalog_merger.py -d documents -s date -o final_catalog.pdf
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple
import argparse
from datetime import datetime

try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    print("Error: PyPDF2 is required. Install with: pip install PyPDF2")
    sys.exit(1)


class PDFCatalogMerger:
    """Merge PDF files into a catalog with cover and back cover."""
    
    def __init__(self):
        """Initialize the PDF catalog merger."""
        self.cover_filename = "cover.pdf"
        self.back_cover_filename = "back_cover.pdf"
    
    def find_cover_files(self, directory: Path) -> Tuple[Optional[Path], Optional[Path]]:
        """
        Find cover and back cover files in the directory.
        
        Args:
            directory: Directory to search for cover files
            
        Returns:
            Tuple of (cover_path, back_cover_path) - None if not found
        """
        cover_path = None
        back_cover_path = None
        
        # Check for cover files (case insensitive)
        for file in directory.iterdir():
            if file.is_file() and file.suffix.lower() == '.pdf':
                if file.name.lower() == self.cover_filename.lower():
                    cover_path = file
                elif file.name.lower() == self.back_cover_filename.lower():
                    back_cover_path = file
        
        return cover_path, back_cover_path
    
    def get_inner_pages(self, directory: Path, sort_by: str = "name") -> List[Path]:
        """
        Get all PDF files excluding cover and back cover.
        
        Args:
            directory: Directory to search for PDF files
            sort_by: Sort method - "name" or "date"
            
        Returns:
            List of PDF file paths sorted according to specified method
        """
        pdf_files = []
        
        # Find all PDF files except cover and back cover
        for file in directory.iterdir():
            if file.is_file() and file.suffix.lower() == '.pdf':
                if (file.name.lower() != self.cover_filename.lower() and 
                    file.name.lower() != self.back_cover_filename.lower()):
                    pdf_files.append(file)
        
        # Sort files
        if sort_by.lower() == "name":
            pdf_files.sort(key=lambda x: x.name.lower())
        elif sort_by.lower() == "date":
            pdf_files.sort(key=lambda x: x.stat().st_ctime)
        else:
            raise ValueError(f"Invalid sort method: {sort_by}. Use 'name' or 'date'.")
        
        return pdf_files
    
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
                    
                    # Validate that the PDF has pages
                    if len(reader.pages) == 0:
                        print(f"⚠ Warning: {pdf_path.name} has no pages, skipping")
                        continue
                    
                    for page in reader.pages:
                        writer.add_page(page)
                    print(f"✓ Added: {pdf_path.name} ({len(reader.pages)} pages)")
                except Exception as e:
                    print(f"✗ Error reading {pdf_path.name}: {e}")
                    continue  # Continue with other files instead of returning False
            
            # Check if any pages were added
            if len(writer.pages) == 0:
                print("✗ No valid pages were added to the PDF")
                return False
            
            # Write the merged PDF with proper error handling
            try:
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                # Verify the file was created and has content
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
        Create a catalog by merging PDF files with cover and back cover.
        
        Args:
            input_directory: Directory containing PDF files
            output_file: Output PDF filename
            sort_by: Sort method for inner pages ("name" or "date")
            
        Returns:
            True if successful, False otherwise
        """
        print(f"Creating catalog from: {input_directory}")
        print(f"Sorting inner pages by: {sort_by}")
        print("-" * 50)
        
        # Find cover files
        cover_path, back_cover_path = self.find_cover_files(input_directory)
        
        if cover_path:
            print(f"✓ Found cover: {cover_path.name}")
        else:
            print("⚠ Cover file (cover.pdf) not found")
        
        if back_cover_path:
            print(f"✓ Found back cover: {back_cover_path.name}")
        else:
            print("⚠ Back cover file (back_cover.pdf) not found")
        
        # Get inner pages
        inner_pages = self.get_inner_pages(input_directory, sort_by)
        
        if not inner_pages:
            print("⚠ No inner page PDF files found")
            if not cover_path and not back_cover_path:
                print("✗ No PDF files found in directory")
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
            print(f"\n✓ Catalog created successfully: {output_path}")
            print(f"Total pages: {len(pdf_order)} files merged")
            return True
        else:
            return False


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Merge PDF files into a catalog with cover and back cover",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create catalog from current directory (sorted by name)
  python pdf_catalog_merger.py
  
  # Create catalog from specific directory (sorted by creation date)
  python pdf_catalog_merger.py -d /path/to/pdfs -s date -o catalog.pdf
  
  # Create catalog with custom output name
  python pdf_catalog_merger.py -d documents -o my_catalog.pdf
        """
    )
    
    parser.add_argument("-d", "--directory", type=str, default=".",
                        help="Input directory containing PDF files (default: current directory)")
    parser.add_argument("-o", "--output", type=str, default="catalog.pdf",
                        help="Output catalog filename (default: catalog.pdf)")
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
        merger = PDFCatalogMerger()
        success = merger.create_catalog(
            input_directory=input_dir,
            output_file=args.output,
            sort_by=args.sort
        )
        
        if success:
            print("\n🎉 Catalog creation completed successfully!")
        else:
            print("\n❌ Catalog creation failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nCatalog creation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
