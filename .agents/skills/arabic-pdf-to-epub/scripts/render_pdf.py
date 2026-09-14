#!/usr/bin/env python3
"""
Renders pages of a PDF into high-resolution PNG images.
Usage:
    python render_pdf.py <pdf_path> [--out-dir pages] [--start 1] [--end 20] [--dpi 200]
"""
import argparse
import os
import sys

def render_pdf(pdf_path, out_dir="pages", start_page=1, end_page=None, dpi=200):
    try:
        import pymupdf
    except ImportError:
        try:
            import fitz as pymupdf
        except ImportError:
            print("Error: PyMuPDF is required. Install via: pip install pymupdf", file=sys.stderr)
            sys.exit(1)

    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(out_dir, exist_ok=True)
    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)
    
    start_idx = max(0, start_page - 1)
    end_idx = min(total_pages, end_page) if end_page else total_pages

    print(f"Rendering pages {start_idx + 1} to {end_idx} of {total_pages} from '{pdf_path}' at {dpi} DPI...")

    for i in range(start_idx, end_idx):
        page = doc[i]
        pix = page.get_pixmap(dpi=dpi)
        out_file = os.path.join(out_dir, f"page_{i+1:03d}.png")
        pix.save(out_file)
        print(f"  [✓] Page {i+1:03d} -> {out_file}")

    print(f"Successfully rendered {end_idx - start_idx} pages into '{out_dir}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render PDF pages to PNG.")
    parser.add_argument("pdf_path", help="Path to the input PDF file")
    parser.add_argument("--out-dir", default="pages", help="Output directory for images (default: pages)")
    parser.add_argument("--start", type=int, default=1, help="Starting page number (1-based, default: 1)")
    parser.add_argument("--end", type=int, default=None, help="Ending page number (1-based, optional)")
    parser.add_argument("--dpi", type=int, default=200, help="Render DPI (default: 200)")
    
    args = parser.parse_args()
    render_pdf(args.pdf_path, args.out_dir, args.start, args.end, args.dpi)
