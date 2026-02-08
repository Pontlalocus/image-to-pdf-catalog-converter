# Image to PDF Converter for Catalog Generation

A Python script that converts images to PDF format, specifically designed for creating catalogs from image collections.

## Features

- **Multiple Layout Options**: Single image per page, grid layout, or catalog layout with captions
- **Automatic Image Processing**: Handles EXIF orientation, color space conversion, and aspect ratio preservation
- **Flexible Page Settings**: Support for A4 and Letter page sizes with customizable margins
- **Batch Processing**: Convert all images in a directory at once
- **Multiple Image Formats**: Supports JPG, PNG, BMP, TIFF, and GIF formats

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Convert all images in the current directory to a PDF:

```bash
python image_to_pdf_converter.py
```

### Advanced Usage

```bash
# Convert images from a specific directory
python image_to_pdf_converter.py -d /path/to/images -o catalog.pdf

# Create a catalog with 4 images per page in grid layout
python image_to_pdf_converter.py -d images -o catalog.pdf -l grid -n 4

# Create a catalog with captions (filename below each image)
python image_to_pdf_converter.py -d photos -o catalog.pdf -l catalog -n 6

# Use Letter page size with custom margins
python image_to_pdf_converter.py -d . -o catalog.pdf -p letter -m 1.0

# Don't maintain aspect ratio (stretch to fit)
python image_to_pdf_converter.py -d . -o catalog.pdf --no-aspect
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-d, --directory` | Input directory containing images | `.` (current directory) |
| `-o, --output` | Output PDF filename | `catalog.pdf` |
| `-l, --layout` | Layout mode: `single`, `grid`, or `catalog` | `single` |
| `-n, --images-per-page` | Number of images per page (grid/catalog) | `1` |
| `-p, --page-size` | Page size: `A4` or `letter` | `A4` |
| `-m, --margin` | Margin in inches | `0.5` |
| `--no-aspect` | Don't maintain aspect ratio | `False` |
| `--dpi` | Output DPI | `300` |

### Layout Modes

1. **Single**: One image per page, centered and scaled to fit
2. **Grid**: Multiple images per page in a grid layout
3. **Catalog**: Grid layout with filename captions below each image

## Examples

### Product Catalog
Create a product catalog with 6 items per page:

```bash
python image_to_pdf_converter.py -d product_images -o product_catalog.pdf -l catalog -n 6
```

### Photo Album
Create a photo album with one photo per page:

```bash
python image_to_pdf_converter.py -d vacation_photos -o photo_album.pdf -l single
```

### Quick Reference Sheet
Create a compact reference sheet with 9 images per page:

```bash
python image_to_pdf_converter.py -d reference_images -o reference.pdf -l grid -n 9
```

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff)
- GIF (.gif)

## Requirements

- Python 3.7+
- Pillow >= 10.0.0
- ReportLab >= 4.0.0

## Error Handling

The script includes robust error handling:
- Skips corrupted or unreadable images with warnings
- Validates input directory and parameters
- Provides clear error messages for common issues

## Tips

1. **Image Quality**: Use high-resolution images for best results in PDF output
2. **Organization**: Sort images alphabetically by filename for consistent ordering
3. **Memory Usage**: For large collections, consider processing in batches
4. **Aspect Ratio**: Maintain aspect ratio for professional-looking catalogs

## License

This project is open source and available under the MIT License.
