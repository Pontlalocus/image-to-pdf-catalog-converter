# PDF Catalog Merger (Images + PDFs)

Create a single catalog PDF from a folder containing:

- A cover PDF (optional)
- A back cover PDF (optional)
- Inner pages as PDFs and/or JPG/JPEG images

The main script is `pdf_catalog_merger.py`.

This project uses **pikepdf/qpdf** (recommended) to avoid “blank page” rendering issues that can happen with some PDF mergers.

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### 1) Prepare your input folder

Put your files in a folder (example: `my_pdf/`):

- `Cover.pdf` (optional)
- `back_cover.pdf` (optional)
- Inner pages as `*.pdf` and/or `*.jpg` / `*.jpeg`

The script will:

- Put the cover first
- Sort inner pages by name (default) or date
- Put the back cover last

### 2) Create the catalog

Default output is `Catalog.pdf` inside the input folder.

```bash
python pdf_catalog_merger.py -d ./my_pdf
```

### Recommended (most reliable) merge engine

```bash
python pdf_catalog_merger.py -d ./my_pdf --engine pikepdf
```

### Choose output name

```bash
python pdf_catalog_merger.py -d ./my_pdf -o Catalog.pdf --engine pikepdf
```

### Notes

- The script **will not** merge previously-generated outputs like `Catalog.pdf` or `working_catalog.pdf` back into your new catalog.
- When saving the merged PDF, you will see a warning that the save step may take **several minutes** depending on the number of pages and file sizes.

## Other scripts

- `image_to_pdf_converter.py`
  - Convert a folder of images into a PDF.
- `jpg_to_pdf_converter.py`
  - Convert JPG/JPEG images to PDFs.

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff)
- GIF (.gif)

## Requirements

- Python 3.8+
- Pillow >= 10.0.0
- ReportLab >= 4.0.0
- PyPDF2 >= 3.0.0
- pikepdf >= 8.0.0 (recommended for reliable merging)

## Tips

- Keep inner page filenames prefixed with numbers (`01_...`, `02_...`) for stable ordering.
- If you ever see blank pages in the merged output, prefer `--engine pikepdf`.

## License

This project is open source and available under the MIT License.
