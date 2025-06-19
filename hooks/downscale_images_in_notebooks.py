#!/usr/bin/env python

import argparse
import base64
import io
import os
import sys
from typing import Sequence

import nbformat
from PIL import Image


# --- HELPERS ---
def compress_image(encoded_image, image_format, original_mime, max_img_res, convert_to_jpg):
    image_data = base64.b64decode(encoded_image)
    image = Image.open(io.BytesIO(image_data)).convert("RGB")  # Convert all to RGB

    orig_width, orig_height = image.size
    if max(orig_width, orig_height) > max_img_res:
        # Resize
        image.thumbnail((max_img_res, max_img_res), Image.LANCZOS)

    # Re-encode
    buffer = io.BytesIO()
    if convert_to_jpg and original_mime == "image/png":
        image.save(buffer, format="JPEG", quality=90, optimize=True)
        new_mime = "image/jpeg"
    else:
        image.save(buffer, format=image_format, optimize=True)
        new_mime = original_mime

    new_data = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # Add display size metadata
    display_metadata = {new_mime: {"width": orig_width, "height": orig_height}}

    return new_data, new_mime, display_metadata


# --- MAIN PROCESSING FUNCTION ---
def process_notebook(path: str, max_img_res: int, convert_to_jpg: bool) -> bool:
    changed = False
    with open(path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        for output in cell.get("outputs", []):
            if output.output_type != "display_data":
                continue

            data = output.get("data", {})
            for mime in ["image/png", "image/jpeg"]:
                if mime in data:
                    image_format = "PNG" if mime == "image/png" else "JPEG"
                    new_image, new_mime, meta = compress_image(
                        data[mime], image_format, mime, max_img_res, convert_to_jpg
                    )

                    if new_mime != mime:
                        del data[mime]  # Remove old MIME if format changed
                    data[new_mime] = new_image
                    if meta:
                        output.setdefault("metadata", {}).update(meta)

                    changed = True
                    break  # Only handle one image per output

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            nbformat.write(nb, f)
    return changed


# --- SCRIPT ENTRY POINT ---
def main(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", help="Filenames to process.")
    parser.add_argument(
        "--max-img-res", type=int, default=800, help="Resize images that have one side larger than this number."
    )
    parser.add_argument(
        "--max-file-size", type=int, default=512, help="Ignore notebooks smaller than this size (in KB)."
    )
    parser.add_argument("--keep-png", action="store_true", help="Prevent from converting png to jpg.")
    args = parser.parse_args(argv)
    max_file_size = args.max_file_size * 1024
    convert_to_jpg = not args.keep_png

    for notebook in sys.argv[1:]:
        if notebook.endswith(".ipynb") and os.path.isfile(notebook):
            if os.path.getsize(notebook) < max_file_size:
                print(f"Skipping {notebook} (smaller than 512KB)")
                continue  # Skip small notebooks
            if process_notebook(notebook, args.max_img_res, convert_to_jpg):
                print(f"✔ Optimized images in {notebook}")


if __name__ == "__main__":
    main()