#!/usr/bin/env python3
"""
Working fix for blank page issue - direct approach
"""

import os
import sys
import io
from pathlib import Path
from typing import List, Optional, Tuple
import argparse
from datetime import datetime

# Import PyPDF2 with warnings suppressed
import warnings
with warnings.catch_warnings():
    from PyPDF2 import PdfReader, PdfWriter

try:
    import pikepdf
except Exception:
    pikepdf = None

try:
    from PIL import Image, ImageOps
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except ImportError as e:
    print(f"Error: Missing required library. Install with: pip install PyPDF2 Pillow reportlab")
    print(f"Specific error: {e}")
    sys.exit(1)


class WorkingFixPDFCatalogMerger:
    """Working fix PDF catalog merger with PyPDF2."""
    
    def __init__(self):
        """Initialize the working fix PDF catalog merger."""
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
    
    def convert_jpg_to_pdf_working(self, jpg_path: Path, output_path: Path) -> bool:
        """Convert a JPG image to a letter-sized PDF using working method."""
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
            
            # Create PDF using PyPDF2
            writer = PdfWriter()
            
            # Add a blank page
            page = writer.add_blank_page(width=self.page_width, height=self.page_height)
            
            # Convert image to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            
            # Add image to the page
            page.insert_image(img_bytes.getvalue(), x=x, y=y, width=pdf_width, height=pdf_height)
            
            # Save the PDF
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            # Verify the PDF was created properly
            if output_path.exists() and output_path.stat().st_size > 1000:  # Should be larger than 1KB
                return True
            else:
                print(f"⚠ Warning: {jpg_path.name} created small PDF ({output_path.stat().st_size} bytes)")
                return False
            
        except Exception as e:
            print(f"✗ Error converting {jpg_path.name}: {e}")
            return False
    
    def get_all_files_working(self, directory: Path, sort_by: str = "name") -> List[Path]:
        """Get all image and PDF files, converting JPGs to PDFs with working method."""
        all_files = []
        temp_dir = directory / "_temp_pdfs_working"
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
            if file.name == "_temp_pdfs_working":
                continue
            
            if file.suffix.lower() in ['.jpg', '.jpeg']:
                # Convert JPG to PDF with working method
                pdf_path = temp_dir / f"{file.stem}.pdf"
                if self.convert_jpg_to_pdf_working(file, pdf_path):
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
        """Merge multiple PDF files into a single PDF using PyPDF2."""
        try:
            writer = PdfWriter()
            
            for pdf_path in pdf_paths:
                try:
                    reader = PdfReader(str(pdf_path))
                    
                    # Validate that PDF has pages
                    if len(reader.pages) == 0:
                        print(f"⚠ Warning: {pdf_path.name} has no pages, skipping")
                        continue
                    
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
                print(f"⚠ Saving merged PDF to: {output_path} (this can take several minutes depending on the number of pages and file sizes)...")
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

    def merge_pdfs_pikepdf(self, pdf_paths: List[Path], output_path: Path) -> bool:
        if pikepdf is None:
            print("✗ pikepdf is not installed. Install with: pip install pikepdf")
            return False

        merged = pikepdf.Pdf.new()

        for idx, pdf_path in enumerate(pdf_paths, start=1):
            print(f"[{idx}/{len(pdf_paths)}] Adding: {pdf_path.name}")
            try:
                with pikepdf.Pdf.open(str(pdf_path)) as part:
                    merged.pages.extend(part.pages)
            except Exception as e:
                # Fallback: try to rewrite/sanitize this single PDF, then re-open
                try:
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                        tmp_path = Path(tmp.name)
                    try:
                        with pikepdf.Pdf.open(str(pdf_path)) as src:
                            src.save(str(tmp_path))
                        with pikepdf.Pdf.open(str(tmp_path)) as part:
                            merged.pages.extend(part.pages)
                    finally:
                        try:
                            tmp_path.unlink(missing_ok=True)
                        except Exception:
                            pass
                except Exception as e2:
                    print(f"✗ Error adding {pdf_path.name} with pikepdf: {e}")
                    print(f"✗ Fallback sanitize also failed for {pdf_path.name}: {e2}")
                    return False

        # Save once at the end (linearize can take time on large files)
        print(f"⚠ Saving merged PDF to: {output_path} (this can take several minutes depending on the number of pages and file sizes)...")
        merged.save(str(output_path), linearize=True)
        return output_path.exists() and output_path.stat().st_size > 0
    
    def create_catalog(self, input_directory: Path, output_file: str, 
                      sort_by: str = "name", engine: str = "auto") -> bool:
        """Create a catalog by converting images and merging PDFs."""
        print(f"Creating WORKING catalog from: {input_directory}")
        print(f"Sorting inner pages by: {sort_by}")
        print(f"Merge engine: {engine}")
        print("-" * 50)

        # Create output path early so we can exclude it from inputs
        output_path = input_directory / output_file if not Path(output_file).is_absolute() else Path(output_file)
        
        # Find cover files
        cover_path, back_cover_path = self.find_cover_files(input_directory)
        
        # Get all files (converting JPGs to PDFs with working method)
        inner_pages = self.get_all_files_working(input_directory, sort_by)

        # Avoid recursively merging previously-created catalogs
        excluded_pdf_names = {
            "working_catalog.pdf",
            "catalog.pdf",
            output_path.name.lower(),
        }
        inner_pages = [p for p in inner_pages if p.name.lower() not in excluded_pdf_names]
        
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
        
        selected_engine = engine
        if selected_engine == "auto":
            selected_engine = "pikepdf" if pikepdf is not None else "pypdf2"

        merged_ok = False
        if selected_engine == "pikepdf":
            merged_ok = self.merge_pdfs_pikepdf(pdf_order, output_path)
        else:
            merged_ok = self.merge_pdfs(pdf_order, output_path)

        if merged_ok:
            print(f"\n✓ WORKING Catalog created successfully: {output_path}")
            print(f"Total pages: {len(pdf_order)} files merged")
            print("✅ Catalog created!")
            
            # Clean up temp files
            temp_dir = input_directory / "_temp_pdfs_working"
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
        description="WORKING catalog creator with PyPDF2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create catalog from current directory (sorted by name)
  python working_fix.py
  
  # Create catalog from specific directory (sorted by creation date)
  python working_fix.py -d /path/to/images -s date -o catalog.pdf
  
  # Create catalog with custom output name
  python working_fix.py -d images -o my_catalog.pdf
        """
    )
    
    parser.add_argument("-d", "--directory", type=str, default=".",
                        help="Input directory containing image/PDF files (default: current directory)")
    parser.add_argument("-o", "--output", type=str, default="Catalog.pdf",
                        help="Output catalog filename (default: Catalog.pdf)")
    parser.add_argument("-s", "--sort", type=str, choices=["name", "date"],
                        default="name", help="Sort inner pages by 'name' or 'date' (default: name)")

    parser.add_argument("--engine", type=str, choices=["auto", "pypdf2", "pikepdf"], default="auto",
                        help="Merge engine: auto prefers pikepdf if installed (default: auto)")
    
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
        merger = WorkingFixPDFCatalogMerger()
        success = merger.create_catalog(
            input_directory=input_dir,
            output_file=args.output,
            sort_by=args.sort,
            engine=args.engine
        )
        
        if success:
            print("\\n🎉 WORKING catalog creation completed successfully!")
        else:
            print("\\n❌ WORKING catalog creation failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\\nCatalog creation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
