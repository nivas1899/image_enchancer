#!/usr/bin/env python3
"""
Advanced Image Enhancer Pro - 4K/8K with AI-like enhancements
Features: Multiple algorithms, sharpening, denoising, color correction, presets
"""

import sys
import os
import argparse
from PIL import Image, ImageFilter, ImageEnhance, ExifTags
from pathlib import Path
import time

# Resolution definitions
RESOLUTIONS = {
    '4k': (3840, 2160),
    '8k': (7680, 4320),
    '2k': (2560, 1440),
    '1080p': (1920, 1080),
    '720p': (1280, 720)
}

# Upscaling algorithms
ALGORITHMS = {
    'lanczos': Image.Resampling.LANCZOS,      # Best quality
    'bicubic': Image.Resampling.BICUBIC,       # Good balance
    'bilinear': Image.Resampling.BILINEAR,     # Fast
    'nearest': Image.Resampling.NEAREST,       # Pixelated (retro)
    'box': Image.Resampling.BOX                # Smooth
}

# Enhancement presets
PRESETS = {
    'photo': {
        'algorithm': 'lanczos',
        'sharpen': 1.5,
        'contrast': 1.1,
        'saturation': 1.05,
        'brightness': 1.0,
        'denoise': True
    },
    'artwork': {
        'algorithm': 'lanczos',
        'sharpen': 1.8,
        'contrast': 1.15,
        'saturation': 1.1,
        'brightness': 1.0,
        'denoise': False
    },
    'text': {
        'algorithm': 'bicubic',
        'sharpen': 2.0,
        'contrast': 1.3,
        'saturation': 1.0,
        'brightness': 1.05,
        'denoise': True
    },
    'soft': {
        'algorithm': 'lanczos',
        'sharpen': 1.0,
        'contrast': 1.0,
        'saturation': 1.0,
        'brightness': 1.0,
        'denoise': True
    },
    'vivid': {
        'algorithm': 'lanczos',
        'sharpen': 1.6,
        'contrast': 1.2,
        'saturation': 1.3,
        'brightness': 1.05,
        'denoise': False
    },
    'hdr': {
        'algorithm': 'lanczos',
        'sharpen': 1.4,
        'contrast': 1.4,
        'saturation': 1.2,
        'brightness': 1.02,
        'denoise': True
    }
}

def apply_denoise(img, strength=1.0):
    """Apply denoising filter"""
    if strength <= 0:
        return img
    # Use median filter for denoising
    radius = int(strength)
    if radius > 0:
        return img.filter(ImageFilter.MedianFilter(size=radius * 2 + 1))
    return img

def apply_sharpen(img, factor=1.5):
    """Apply sharpening"""
    if factor <= 1.0:
        return img
    enhancer = ImageEnhance.Sharpness(img)
    return enhancer.enhance(factor)

def apply_color_enhancements(img, contrast=1.0, saturation=1.0, brightness=1.0):
    """Apply color enhancements"""
    # Contrast
    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast)
    
    # Saturation
    if saturation != 1.0:
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(saturation)
    
    # Brightness
    if brightness != 1.0:
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(brightness)
    
    return img

def auto_rotate_by_exif(img):
    """Auto-rotate image based on EXIF orientation"""
    try:
        exif = img._getexif()
        if exif is not None:
            # Find orientation tag
            orientation = None
            for tag_id, tag_name in ExifTags.TAGS.items():
                if tag_name == 'Orientation':
                    orientation = tag_id
                    break
            
            if orientation is not None:
                orientation_value = exif.get(orientation)
                if orientation_value == 3:
                    img = img.rotate(180, expand=True)
                elif orientation_value == 6:
                    img = img.rotate(270, expand=True)
                elif orientation_value == 8:
                    img = img.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        pass
    return img

def calculate_target_size(original_size, target_resolution, fit_mode='fit'):
    """
    Calculate target size maintaining aspect ratio
    
    fit_mode:
    - 'fit': Fit within resolution (may have black bars)
    - 'fill': Fill resolution (may crop)
    - 'stretch': Stretch to exact resolution
    """
    orig_w, orig_h = original_size
    target_w, target_h = target_resolution
    
    if fit_mode == 'stretch':
        return target_resolution
    
    # Calculate aspect ratios
    orig_ratio = orig_w / orig_h
    target_ratio = target_w / target_h
    
    if fit_mode == 'fit':
        # Fit within target (letterbox)
        if orig_ratio > target_ratio:
            new_w = target_w
            new_h = int(target_w / orig_ratio)
        else:
            new_h = target_h
            new_w = int(target_h * orig_ratio)
    else:  # fill
        # Fill target (crop)
        if orig_ratio > target_ratio:
            new_h = target_h
            new_w = int(target_h * orig_ratio)
        else:
            new_w = target_w
            new_h = int(target_w / orig_ratio)
    
    return (new_w, new_h)

def enhance_image_pro(input_path, args):
    """
    Advanced image enhancement with multiple features
    
    Args:
        input_path: Path to input image
        args: argparse namespace with all parameters
    """
    start_time = time.time()
    
    # Validate input
    if not os.path.exists(input_path):
        print(f"❌ Error: File '{input_path}' not found")
        return False
    
    # Load preset or custom settings
    if args.preset and args.preset in PRESETS:
        preset = PRESETS[args.preset]
        algorithm = preset['algorithm']
        sharpen = preset['sharpen']
        contrast = preset['contrast']
        saturation = preset['saturation']
        brightness = preset['brightness']
        denoise = preset['denoise']
    else:
        algorithm = args.algorithm
        sharpen = args.sharpen
        contrast = args.contrast
        saturation = args.saturation
        brightness = args.brightness
        denoise = args.denoise
    
    # Generate output path
    if args.output:
        output_path = args.output
    else:
        input_path_obj = Path(input_path)
        suffix = f"_{args.resolution}"
        if args.preset:
            suffix += f"_{args.preset}"
        output_path = f"{input_path_obj.stem}{suffix}{input_path_obj.suffix}"
    
    try:
        print(f"\n📷 Processing: {os.path.basename(input_path)}")
        print(f"   Resolution: {args.resolution.upper()}")
        print(f"   Algorithm: {algorithm.upper()}")
        if args.preset:
            print(f"   Preset: {args.preset.upper()}")
        
        # Open image
        with Image.open(input_path) as img:
            original_size = img.size
            print(f"   Original: {original_size[0]}x{original_size[1]}")
            
            # Auto-rotate based on EXIF
            if args.auto_rotate:
                img = auto_rotate_by_exif(img)
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P', 'LA'):
                # Handle transparency
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                else:
                    img = img.convert('RGB')
            
            # Calculate target size
            target_resolution = RESOLUTIONS.get(args.resolution, RESOLUTIONS['4k'])
            
            if args.fit == 'stretch':
                target_size = target_resolution
                print(f"   Target: {target_size[0]}x{target_size[1]} (STRETCH)")
            else:
                target_size = calculate_target_size(img.size, target_resolution, args.fit)
                print(f"   Target: {target_size[0]}x{target_size[1]} (FIT)")
            
            # Step 1: Resize
            print("   → Resizing...", end='', flush=True)
            img = img.resize(target_size, ALGORITHMS[algorithm])
            print(" ✓")
            
            # Step 2: Denoise (before sharpening)
            if denoise:
                print("   → Denoising...", end='', flush=True)
                img = apply_denoise(img, strength=1.5)
                print(" ✓")
            
            # Step 3: Sharpen
            if sharpen != 1.0:
                print(f"   → Sharpening ({sharpen}x)...", end='', flush=True)
                img = apply_sharpen(img, sharpen)
                print(" ✓")
            
            # Step 4: Color enhancements
            if contrast != 1.0 or saturation != 1.0 or brightness != 1.0:
                print("   → Color enhancement...", end='', flush=True)
                img = apply_color_enhancements(img, contrast, saturation, brightness)
                print(" ✓")
            
            # Step 5: Additional filters
            if args.blur > 0:
                print(f"   → Applying blur ({args.blur})...", end='', flush=True)
                img = img.filter(ImageFilter.GaussianBlur(radius=args.blur))
                print(" ✓")
            
            if args.edge_enhance:
                print("   → Edge enhancement...", end='', flush=True)
                img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
                print(" ✓")
            
            # Step 6: Save
            print(f"   → Saving...", end='', flush=True)
            
            # Determine save options based on format
            save_kwargs = {}
            if args.format or Path(input_path).suffix.lower() in ['.jpg', '.jpeg']:
                save_kwargs['quality'] = args.quality
                save_kwargs['optimize'] = True
                save_kwargs['progressive'] = True
            
            if args.format:
                output_path = str(Path(output_path).with_suffix(f'.{args.format}'))
            
            img.save(output_path, **save_kwargs)
            print(" ✓")
            
            # Calculate file size
            file_size = os.path.getsize(output_path) / (1024 * 1024)
            elapsed_time = time.time() - start_time
            
            print(f"\n✅ Enhanced successfully!")
            print(f"   Output: {output_path}")
            print(f"   Size: {file_size:.2f} MB")
            print(f"   Time: {elapsed_time:.2f}s")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def batch_process(args):
    """Process multiple images"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif'}
    files = []
    
    # Get files from directory
    if os.path.isdir(args.input):
        for filename in os.listdir(args.input):
            if Path(filename).suffix.lower() in image_extensions:
                files.append(os.path.join(args.input, filename))
    # Single file
    elif os.path.isfile(args.input):
        files.append(args.input)
    # Multiple files (glob pattern)
    else:
        import glob
        files = glob.glob(args.input)
    
    if not files:
        print("❌ No images found")
        return
    
    print(f"\n🚀 Batch Processing {len(files)} images\n")
    print("=" * 50)
    
    success_count = 0
    for i, file_path in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}]")
        if enhance_image_pro(file_path, args):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"\n📊 Summary: {success_count}/{len(files)} images enhanced")

def print_presets():
    """Print available presets"""
    print("\n🎨 Available Presets:")
    for name, settings in PRESETS.items():
        print(f"\n  {name.upper()}:")
        for key, value in settings.items():
            print(f"    • {key}: {value}")

def main():
    parser = argparse.ArgumentParser(
        description='Advanced Image Enhancer Pro - 4K/8K with AI-like enhancements',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic 4K enhancement
  python enhancer_pro.py photo.jpg
  
  # 8K with vivid colors
  python enhancer_pro.py photo.jpg -r 8k --preset vivid
  
  # Custom settings
  python enhancer_pro.py photo.jpg -r 4k -a lanczos --sharpen 2.0 --contrast 1.3
  
  # Batch processing
  python enhancer_pro.py ./images --batch -r 8k --preset photo
  
  # List presets
  python enhancer_pro.py --list-presets
        """
    )
    
    # Input/Output
    parser.add_argument('input', nargs='?', help='Input image file or directory')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('--batch', action='store_true', help='Batch process directory')
    
    # Resolution
    parser.add_argument('-r', '--resolution', default='4k',
                       choices=['720p', '1080p', '2k', '4k', '8k'],
                       help='Target resolution (default: 4k)')
    
    # Algorithm
    parser.add_argument('-a', '--algorithm', default='lanczos',
                       choices=['lanczos', 'bicubic', 'bilinear', 'nearest', 'box'],
                       help='Upscaling algorithm (default: lanczos)')
    
    # Fit mode
    parser.add_argument('--fit', default='fit',
                       choices=['fit', 'fill', 'stretch'],
                       help='How to fit image to resolution (default: fit)')
    
    # Presets
    parser.add_argument('--preset', 
                       choices=list(PRESETS.keys()),
                       help='Use enhancement preset')
    parser.add_argument('--list-presets', action='store_true',
                       help='List available presets')
    
    # Enhancements
    parser.add_argument('--sharpen', type=float, default=1.0,
                       help='Sharpen factor (1.0 = no change, default: 1.0)')
    parser.add_argument('--contrast', type=float, default=1.0,
                       help='Contrast factor (1.0 = no change, default: 1.0)')
    parser.add_argument('--saturation', type=float, default=1.0,
                       help='Saturation factor (1.0 = no change, default: 1.0)')
    parser.add_argument('--brightness', type=float, default=1.0,
                       help='Brightness factor (1.0 = no change, default: 1.0)')
    parser.add_argument('--denoise', action='store_true',
                       help='Apply denoising filter')
    parser.add_argument('--blur', type=float, default=0,
                       help='Apply Gaussian blur (radius, default: 0)')
    parser.add_argument('--edge-enhance', action='store_true',
                       help='Apply edge enhancement')
    
    # Processing options
    parser.add_argument('--auto-rotate', action='store_true', default=True,
                       help='Auto-rotate based on EXIF (default: True)')
    parser.add_argument('--no-auto-rotate', dest='auto_rotate',
                       action='store_false',
                       help='Disable auto-rotation')
    
    # Output options
    parser.add_argument('-q', '--quality', type=int, default=95,
                       help='JPEG quality 1-100 (default: 95)')
    parser.add_argument('-f', '--format', choices=['jpg', 'png', 'tiff', 'bmp'],
                       help='Output format (default: same as input)')
    
    args = parser.parse_args()
    
    # List presets
    if args.list_presets:
        print_presets()
        return
    
    # Check input
    if not args.input:
        parser.print_help()
        print("\n❌ Error: Please specify an input file or directory")
        sys.exit(1)
    
    # Process
    if args.batch or os.path.isdir(args.input):
        batch_process(args)
    else:
        enhance_image_pro(args.input, args)

if __name__ == "__main__":
    main()
