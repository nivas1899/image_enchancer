#!/usr/bin/env python3
"""
Image Enhancer - Supports 4K and 8K resolution upscaling
"""

import sys
import os
from PIL import Image
from pathlib import Path

# Resolution definitions
RESOLUTIONS = {
    '4k': (3840, 2160),
    '8k': (7680, 4320)
}

def enhance_image(input_path, resolution='4k', output_path=None):
    """
    Enhance image to specified resolution (4K or 8K)
    
    Args:
        input_path: Path to input image
        resolution: '4k' or '8k'
        output_path: Optional output path (default: input_name_enhanced.jpg)
    """
    if resolution.lower() not in RESOLUTIONS:
        print(f"Error: Resolution must be '4k' or '8k'")
        return False
    
    target_size = RESOLUTIONS[resolution.lower()]
    
    # Check if input file exists
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found")
        return False
    
    # Generate output path if not provided
    if output_path is None:
        input_path_obj = Path(input_path)
        output_path = f"{input_path_obj.stem}_{resolution.lower()}{input_path_obj.suffix}"
    
    try:
        # Open and process image
        with Image.open(input_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Get original dimensions
            original_width, original_height = img.size
            print(f"Original size: {original_width}x{original_height}")
            
            # Resize to target resolution using high-quality Lanczos resampling
            img_resized = img.resize(target_size, Image.Resampling.LANCZOS)
            
            # Save enhanced image with high quality
            img_resized.save(output_path, quality=95, optimize=True)
            
            print(f"Enhanced to {resolution.upper()}: {target_size[0]}x{target_size[1]}")
            print(f"Saved to: {output_path}")
            return True
            
    except Exception as e:
        print(f"Error processing image: {e}")
        return False

def batch_enhance(directory, resolution='4k'):
    """Enhance all images in a directory"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    enhanced_count = 0
    
    for filename in os.listdir(directory):
        ext = Path(filename).suffix.lower()
        if ext in image_extensions:
            input_path = os.path.join(directory, filename)
            print(f"\nProcessing: {filename}")
            if enhance_image(input_path, resolution):
                enhanced_count += 1
    
    print(f"\n✓ Enhanced {enhanced_count} images to {resolution.upper()}")

def main():
    if len(sys.argv) < 2:
        print("""
Image Enhancer - 4K & 8K Resolution Support

Usage:
  python enhancer.py <image_file> [4k|8k] [output_file]
  python enhancer.py --batch <directory> [4k|8k]

Examples:
  python enhancer.py photo.jpg 4k
  python enhancer.py photo.jpg 8k enhanced.jpg
  python enhancer.py --batch ./images 4k
""")
        sys.exit(1)
    
    # Check for batch mode
    if sys.argv[1] == '--batch':
        directory = sys.argv[2] if len(sys.argv) > 2 else '.'
        resolution = sys.argv[3] if len(sys.argv) > 3 else '4k'
        batch_enhance(directory, resolution)
    else:
        # Single file mode
        input_file = sys.argv[1]
        resolution = sys.argv[2] if len(sys.argv) > 2 else '4k'
        output_file = sys.argv[3] if len(sys.argv) > 3 else None
        enhance_image(input_file, resolution, output_file)

if __name__ == "__main__":
    main()
