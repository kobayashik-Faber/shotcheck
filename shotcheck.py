#!/usr/bin/env python3
"""
Image Difference Comparison Tool

Compares images from two directories and generates difference visualizations.
Matches images by their prefix (ignoring timestamp suffixes).
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple
from PIL import Image, ImageChops, ImageDraw, ImageFont
import numpy as np


def extract_prefix(filename: str) -> str:
    """
    Extract the prefix from a filename by removing the timestamp suffix.

    Example: mieru-ca.com_solution_ga4_pc_20260116_021751.png
             -> mieru-ca.com_solution_ga4_pc
    """
    # Remove the timestamp pattern: _YYYYMMDD_HHMMSS.png
    pattern = r'_\d{8}_\d{6}\.png$'
    prefix = re.sub(pattern, '', filename)
    return prefix


def collect_images(directory: Path) -> Dict[str, Path]:
    """
    Collect all PNG images from a directory and map them by their prefix.

    Returns:
        Dictionary mapping prefix -> full file path
    """
    images = {}
    for file in directory.glob('*.png'):
        prefix = extract_prefix(file.name)
        images[prefix] = file
    return images


def create_difference_image(img1_path: Path, img2_path: Path) -> Tuple[Image.Image, bool]:
    """
    Create a difference visualization between two images.

    The result shows:
    - Areas that are identical in gray
    - Areas that differ are highlighted in color (red/pink)

    Returns:
        Tuple of (combined_image, has_difference)
    """
    # Load images
    img1 = Image.open(img1_path).convert('RGB')
    img2 = Image.open(img2_path).convert('RGB')

    # Ensure images are the same size
    if img1.size != img2.size:
        # Resize img2 to match img1
        img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)

    # Calculate absolute difference
    diff = ImageChops.difference(img1, img2)

    # Convert to numpy arrays for processing
    diff_array = np.array(diff)
    img1_array = np.array(img1)
    img2_array = np.array(img2)

    # Create a mask where differences exist
    # Any pixel with difference > threshold is considered different
    threshold = 10
    diff_mask = np.any(diff_array > threshold, axis=2)

    # Create result image with desaturated base
    # Convert img1 to grayscale for base, to make differences stand out
    img1_gray = np.dot(img1_array[..., :3], [0.299, 0.587, 0.114])
    result_array = np.stack([img1_gray, img1_gray, img1_gray], axis=2).astype(np.uint8)

    # Highlight differences in bright red
    result_array[diff_mask] = [255, 50, 50]

    # Check if there are any differences
    has_difference = np.any(diff_mask)

    result = Image.fromarray(result_array)

    # Create a side-by-side comparison with the difference overlay
    width, height = img1.size
    combined_width = width * 3
    combined_height = height + 40  # Extra space for labels

    combined = Image.new('RGB', (combined_width, combined_height), 'white')

    # Add labels
    draw = ImageDraw.Draw(combined)
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
    except:
        font = ImageFont.load_default()

    # Paste images
    combined.paste(img1, (0, 40))
    combined.paste(img2, (width, 40))
    combined.paste(result, (width * 2, 40))

    # Draw labels
    draw.text((width // 2 - 50, 10), 'Image 1', fill='black', font=font)
    draw.text((width + width // 2 - 50, 10), 'Image 2', fill='black', font=font)
    draw.text((width * 2 + width // 2 - 70, 10), 'Difference', fill='black', font=font)

    return combined, has_difference


def compare_directories(dir1: Path, dir2: Path, output_dir: Path):
    """
    Compare all matching images from two directories and save results.
    """
    # Create output directory
    output_dir.mkdir(exist_ok=True)

    # Collect images from both directories
    print(f"Scanning directory 1: {dir1}")
    images1 = collect_images(dir1)
    print(f"  Found {len(images1)} images")

    print(f"Scanning directory 2: {dir2}")
    images2 = collect_images(dir2)
    print(f"  Found {len(images2)} images")

    # Find matching prefixes
    common_prefixes = set(images1.keys()) & set(images2.keys())
    print(f"\nFound {len(common_prefixes)} matching image pairs")

    if not common_prefixes:
        print("No matching images found!")
        return

    # Process each matching pair
    processed = 0
    files_with_diff = []
    files_without_diff = []

    for prefix in sorted(common_prefixes):
        img1_path = images1[prefix]
        img2_path = images2[prefix]
        output_path = output_dir / f"{prefix}_diff.png"

        print(f"Processing: {prefix}")
        try:
            diff_image, has_difference = create_difference_image(img1_path, img2_path)
            diff_image.save(output_path, 'PNG')
            processed += 1

            if has_difference:
                files_with_diff.append(prefix)
            else:
                files_without_diff.append(prefix)
        except Exception as e:
            print(f"  Error processing {prefix}: {e}")

    # Write difference report
    report_path = output_dir / "difference_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("Image Difference Comparison Report\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Directory 1: {dir1}\n")
        f.write(f"Directory 2: {dir2}\n")
        f.write(f"Total image pairs: {len(common_prefixes)}\n")
        f.write(f"Processed: {processed}\n")
        f.write(f"Images with differences: {len(files_with_diff)}\n")
        f.write(f"Images without differences: {len(files_without_diff)}\n\n")

        f.write("=" * 60 + "\n")
        f.write("Files with Differences\n")
        f.write("=" * 60 + "\n")
        if files_with_diff:
            for prefix in files_with_diff:
                f.write(f"{prefix}\n")
        else:
            f.write("(None)\n")

        f.write("\n")
        f.write("=" * 60 + "\n")
        f.write("Files without Differences\n")
        f.write("=" * 60 + "\n")
        if files_without_diff:
            for prefix in files_without_diff:
                f.write(f"{prefix}\n")
        else:
            f.write("(None)\n")

    print(f"\nCompleted! Processed {processed}/{len(common_prefixes)} image pairs")
    print(f"  Images with differences: {len(files_with_diff)}")
    print(f"  Images without differences: {len(files_without_diff)}")
    print(f"Results saved to: {output_dir}")
    print(f"Report saved to: {report_path}")


def main():
    if len(sys.argv) != 4:
        print("Usage: python shotcheck.py <dir1> <dir2> <output_dir>")
        print("\nExample:")
        print("  python shotcheck.py screenshots/before screenshots/after output")
        sys.exit(1)

    dir1 = Path(sys.argv[1])
    dir2 = Path(sys.argv[2])
    output_dir = Path(sys.argv[3])

    # Validate input directories
    if not dir1.is_dir():
        print(f"Error: Directory not found: {dir1}")
        sys.exit(1)

    if not dir2.is_dir():
        print(f"Error: Directory not found: {dir2}")
        sys.exit(1)

    print("=" * 60)
    print("Image Difference Comparison Tool")
    print("=" * 60)

    compare_directories(dir1, dir2, output_dir)


if __name__ == '__main__':
    main()
