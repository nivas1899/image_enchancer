#!/usr/bin/env python3
"""
Advanced Image Enhancer Pro with GUI
Features: 4K/8K upscaling, presets, enhancements, Tkinter GUI
"""

import sys
import os
import argparse
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageFilter, ImageEnhance, ExifTags
from pathlib import Path
import threading
import time

# Resolution definitions
RESOLUTIONS = {
    '720p': (1280, 720),
    '1080p': (1920, 1080),
    '2k': (2560, 1440),
    '4k': (3840, 2160),
    '8k': (7680, 4320)
}

# Upscaling algorithms
ALGORITHMS = {
    'lanczos': Image.Resampling.LANCZOS,
    'bicubic': Image.Resampling.BICUBIC,
    'bilinear': Image.Resampling.BILINEAR,
    'nearest': Image.Resampling.NEAREST,
    'box': Image.Resampling.BOX
}

# Enhancement presets
PRESETS = {
    'photo': {'algorithm': 'lanczos', 'sharpen': 1.5, 'contrast': 1.1, 'saturation': 1.05, 'brightness': 1.0, 'denoise': True},
    'artwork': {'algorithm': 'lanczos', 'sharpen': 1.8, 'contrast': 1.15, 'saturation': 1.1, 'brightness': 1.0, 'denoise': False},
    'text': {'algorithm': 'bicubic', 'sharpen': 2.0, 'contrast': 1.3, 'saturation': 1.0, 'brightness': 1.05, 'denoise': True},
    'soft': {'algorithm': 'lanczos', 'sharpen': 1.0, 'contrast': 1.0, 'saturation': 1.0, 'brightness': 1.0, 'denoise': True},
    'vivid': {'algorithm': 'lanczos', 'sharpen': 1.6, 'contrast': 1.2, 'saturation': 1.3, 'brightness': 1.05, 'denoise': False},
    'hdr': {'algorithm': 'lanczos', 'sharpen': 1.4, 'contrast': 1.4, 'saturation': 1.2, 'brightness': 1.02, 'denoise': True}
}

def ensure_output_folder(base_path=None):
    """Create and return enhanced images folder"""
    if base_path and os.path.isdir(base_path):
        output_folder = os.path.join(base_path, 'enhanced')
    else:
        output_folder = os.path.join(os.getcwd(), 'enhanced')
    
    os.makedirs(output_folder, exist_ok=True)
    return output_folder

def auto_rotate_by_exif(img):
    """Auto-rotate image based on EXIF orientation"""
    try:
        exif = img._getexif()
        if exif is not None:
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

def apply_denoise(img, strength=1.0):
    """Apply denoising filter"""
    if strength <= 0:
        return img
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
    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast)
    
    if saturation != 1.0:
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(saturation)
    
    if brightness != 1.0:
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(brightness)
    
    return img

def calculate_target_size(original_size, target_resolution, fit_mode='fit'):
    """Calculate target size maintaining aspect ratio"""
    orig_w, orig_h = original_size
    target_w, target_h = target_resolution
    
    if fit_mode == 'stretch':
        return target_resolution
    
    orig_ratio = orig_w / orig_h
    target_ratio = target_w / target_h
    
    if fit_mode == 'fit':
        if orig_ratio > target_ratio:
            new_w = target_w
            new_h = int(target_w / orig_ratio)
        else:
            new_h = target_h
            new_w = int(target_h * orig_ratio)
    else:
        if orig_ratio > target_ratio:
            new_h = target_h
            new_w = int(target_h * orig_ratio)
        else:
            new_w = target_w
            new_h = int(target_w / orig_ratio)
    
    return (new_w, new_h)

def enhance_image_pro(input_path, args, progress_callback=None, output_folder=None):
    """Advanced image enhancement"""
    start_time = time.time()
    
    if not os.path.exists(input_path):
        return False, f"File not found: {input_path}"
    
    # Load preset or custom settings
    if hasattr(args, 'preset') and args.preset in PRESETS:
        preset = PRESETS[args.preset]
        algorithm = preset['algorithm']
        sharpen = preset['sharpen']
        contrast = preset['contrast']
        saturation = preset['saturation']
        brightness = preset['brightness']
        denoise = preset['denoise']
    else:
        algorithm = getattr(args, 'algorithm', 'lanczos')
        sharpen = getattr(args, 'sharpen', 1.5)
        contrast = getattr(args, 'contrast', 1.1)
        saturation = getattr(args, 'saturation', 1.05)
        brightness = getattr(args, 'brightness', 1.0)
        denoise = getattr(args, 'denoise', True)
    
    # Generate output path in enhanced folder
    input_path_obj = Path(input_path)
    if output_folder is None:
        output_folder = ensure_output_folder(input_path_obj.parent)
    
    suffix = f"_{getattr(args, 'resolution', '4k')}"
    if hasattr(args, 'preset') and args.preset:
        suffix += f"_{args.preset}"
    
    output_path = os.path.join(output_folder, f"{input_path_obj.stem}{suffix}{input_path_obj.suffix}")
    
    try:
        if progress_callback:
            progress_callback(5, f"Loading {input_path_obj.name}...")
        
        with Image.open(input_path) as img:
            original_size = img.size
            
            if getattr(args, 'auto_rotate', True):
                img = auto_rotate_by_exif(img)
            
            if img.mode in ('RGBA', 'P', 'LA'):
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                else:
                    img = img.convert('RGB')
            
            target_resolution = RESOLUTIONS.get(getattr(args, 'resolution', '4k'), RESOLUTIONS['4k'])
            fit_mode = getattr(args, 'fit', 'fit')
            target_size = calculate_target_size(img.size, target_resolution, fit_mode)
            
            if progress_callback:
                progress_callback(20, "Resizing...")
            img = img.resize(target_size, ALGORITHMS[algorithm])
            
            if denoise and progress_callback:
                progress_callback(40, "Denoising...")
            if denoise:
                img = apply_denoise(img, strength=1.5)
            
            if sharpen != 1.0 and progress_callback:
                progress_callback(50, f"Sharpening ({sharpen}x)...")
            if sharpen != 1.0:
                img = apply_sharpen(img, sharpen)
            
            if (contrast != 1.0 or saturation != 1.0 or brightness != 1.0) and progress_callback:
                progress_callback(70, "Color enhancement...")
            img = apply_color_enhancements(img, contrast, saturation, brightness)
            
            if getattr(args, 'edge_enhance', False) and progress_callback:
                progress_callback(85, "Edge enhancement...")
            if getattr(args, 'edge_enhance', False):
                img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
            
            if progress_callback:
                progress_callback(90, "Saving...")
            
            quality = getattr(args, 'quality', 95)
            img.save(output_path, quality=quality, optimize=True, progressive=True)
            
            file_size = os.path.getsize(output_path) / (1024 * 1024)
            elapsed_time = time.time() - start_time
            
            if progress_callback:
                progress_callback(100, f"Complete! ({elapsed_time:.1f}s)")
            
            return True, f"Saved: {os.path.basename(output_path)} ({file_size:.2f} MB)"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

# ==================== GUI ====================

class EnhancerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Enhancer Pro")
        self.root.geometry("700x600")
        self.root.minsize(700, 600)
        
        # Variables
        self.files = []
        self.processing = False
        
        # Style
        self.style = ttk.Style()
        self.style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        self.style.configure('Header.TLabel', font=('Helvetica', 10, 'bold'))
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title = ttk.Label(main_frame, text="🚀 Image Enhancer Pro", style='Title.TLabel')
        title.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File Selection
        ttk.Label(main_frame, text="Images:", style='Header.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(0, weight=1)
        
        self.file_entry = ttk.Entry(file_frame)
        self.file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(file_frame, text="Browse", command=self.browse_files).grid(row=0, column=1)
        ttk.Button(file_frame, text="Folder", command=self.browse_folder).grid(row=0, column=2, padx=(5, 0))
        
        # Resolution
        ttk.Label(main_frame, text="Resolution:", style='Header.TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.resolution_var = tk.StringVar(value='4k')
        resolution_combo = ttk.Combobox(main_frame, textvariable=self.resolution_var, 
                                       values=list(RESOLUTIONS.keys()), state='readonly', width=15)
        resolution_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Algorithm
        ttk.Label(main_frame, text="Algorithm:", style='Header.TLabel').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.algorithm_var = tk.StringVar(value='lanczos')
        algorithm_combo = ttk.Combobox(main_frame, textvariable=self.algorithm_var,
                                      values=list(ALGORITHMS.keys()), state='readonly', width=15)
        algorithm_combo.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Preset
        ttk.Label(main_frame, text="Preset:", style='Header.TLabel').grid(row=4, column=0, sticky=tk.W, pady=5)
        self.preset_var = tk.StringVar(value='photo')
        preset_combo = ttk.Combobox(main_frame, textvariable=self.preset_var,
                                   values=list(PRESETS.keys()), state='readonly', width=15)
        preset_combo.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Fit Mode
        ttk.Label(main_frame, text="Fit Mode:", style='Header.TLabel').grid(row=5, column=0, sticky=tk.W, pady=5)
        self.fit_var = tk.StringVar(value='fit')
        fit_combo = ttk.Combobox(main_frame, textvariable=self.fit_var,
                                values=['fit', 'fill', 'stretch'], state='readonly', width=15)
        fit_combo.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)
        
        # Enhancement Sliders
        ttk.Label(main_frame, text="Sharpen:", style='Header.TLabel').grid(row=7, column=0, sticky=tk.W, pady=5)
        self.sharpen_var = tk.DoubleVar(value=1.5)
        ttk.Scale(main_frame, from_=1.0, to=3.0, variable=self.sharpen_var, orient=tk.HORIZONTAL).grid(row=7, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(main_frame, textvariable=self.sharpen_var).grid(row=7, column=2, sticky=tk.W, padx=5)
        
        ttk.Label(main_frame, text="Contrast:", style='Header.TLabel').grid(row=8, column=0, sticky=tk.W, pady=5)
        self.contrast_var = tk.DoubleVar(value=1.1)
        ttk.Scale(main_frame, from_=0.5, to=2.0, variable=self.contrast_var, orient=tk.HORIZONTAL).grid(row=8, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(main_frame, textvariable=self.contrast_var).grid(row=8, column=2, sticky=tk.W, padx=5)
        
        ttk.Label(main_frame, text="Saturation:", style='Header.TLabel').grid(row=9, column=0, sticky=tk.W, pady=5)
        self.saturation_var = tk.DoubleVar(value=1.05)
        ttk.Scale(main_frame, from_=0.5, to=2.0, variable=self.saturation_var, orient=tk.HORIZONTAL).grid(row=9, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(main_frame, textvariable=self.saturation_var).grid(row=9, column=2, sticky=tk.W, padx=5)
        
        # Checkboxes
        checkbox_frame = ttk.Frame(main_frame)
        checkbox_frame.grid(row=10, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        self.denoise_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(checkbox_frame, text="Denoise", variable=self.denoise_var).pack(side=tk.LEFT, padx=(0, 15))
        
        self.edge_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(checkbox_frame, text="Edge Enhance", variable=self.edge_var).pack(side=tk.LEFT)
        
        # Quality
        ttk.Label(main_frame, text="Quality:", style='Header.TLabel').grid(row=11, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.IntVar(value=95)
        ttk.Scale(main_frame, from_=50, to=100, variable=self.quality_var, orient=tk.HORIZONTAL).grid(row=11, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(main_frame, textvariable=self.quality_var).grid(row=11, column=2, sticky=tk.W, padx=5)
        
        # Output Folder
        ttk.Label(main_frame, text="Output Folder:", style='Header.TLabel').grid(row=12, column=0, sticky=tk.W, pady=5)
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=12, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(0, weight=1)
        
        self.output_var = tk.StringVar()
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_var)
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(output_frame, text="Browse", command=self.browse_output).grid(row=0, column=1)
        
        # Progress
        ttk.Separator(main_frame, orient='horizontal').grid(row=13, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=14, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=15, column=0, columnspan=3, sticky=tk.W)
        
        # Log
        ttk.Label(main_frame, text="Log:", style='Header.TLabel').grid(row=16, column=0, sticky=tk.W, pady=(10, 5))
        self.log_text = scrolledtext.ScrolledText(main_frame, height=8, wrap=tk.WORD)
        self.log_text.grid(row=17, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(17, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=18, column=0, columnspan=3, pady=15)
        
        ttk.Button(button_frame, text="🚀 Enhance", command=self.start_processing, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Open Folder", command=self.open_output_folder).pack(side=tk.LEFT, padx=5)
        
        # Set default output folder
        self.output_var.set(os.path.join(os.getcwd(), 'enhanced'))
        
    def browse_files(self):
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"), ("All files", "*.*")]
        )
        if files:
            self.files = list(files)
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, f"{len(files)} file(s) selected")
            self.log(f"Selected {len(files)} file(s)")
            
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Folder with Images")
        if folder:
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
            self.files = [os.path.join(folder, f) for f in os.listdir(folder) 
                         if Path(f).suffix.lower() in image_extensions]
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, f"Folder: {len(self.files)} image(s)")
            self.log(f"Selected folder with {len(self.files)} image(s)")
            
    def browse_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_var.set(folder)
            self.log(f"Output folder: {folder}")
            
    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        
    def open_output_folder(self):
        folder = self.output_var.get()
        if os.path.exists(folder):
            os.startfile(folder)
        else:
            messagebox.showinfo("Info", "Output folder doesn't exist yet. Process an image first.")
            
    def update_progress(self, value, message):
        self.progress_var.set(value)
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def get_args(self):
        """Convert GUI values to args object"""
        class Args:
            def __init__(self):
                self.resolution = '4k'
                self.algorithm = 'lanczos'
                self.preset = 'photo'
                self.fit = 'fit'
                self.sharpen = 1.5
                self.contrast = 1.1
                self.saturation = 1.05
                self.brightness = 1.0
                self.denoise = True
                self.edge_enhance = False
                self.quality = 95
                self.auto_rotate = True
        
        args = Args()
        args.resolution = self.resolution_var.get()
        args.algorithm = self.algorithm_var.get()
        args.preset = self.preset_var.get()
        args.fit = self.fit_var.get()
        args.sharpen = self.sharpen_var.get()
        args.contrast = self.contrast_var.get()
        args.saturation = self.saturation_var.get()
        args.brightness = 1.0
        args.denoise = self.denoise_var.get()
        args.edge_enhance = self.edge_var.get()
        args.quality = self.quality_var.get()
        args.auto_rotate = True
        return args
        
    def process_files(self):
        """Process all files in background thread"""
        if not self.files:
            self.processing = False
            self.status_var.set("No files selected")
            return
            
        output_folder = self.output_var.get()
        os.makedirs(output_folder, exist_ok=True)
        
        args = self.get_args()
        
        success_count = 0
        for i, file_path in enumerate(self.files):
            if not self.processing:
                break
                
            self.log(f"\n[{i+1}/{len(self.files)}] Processing: {os.path.basename(file_path)}")
            
            def progress_callback(value, message):
                overall = (i / len(self.files) * 100) + (value / len(self.files))
                self.root.after(0, lambda: self.update_progress(overall, f"[{i+1}/{len(self.files)}] {message}"))
            
            try:
                success, msg = enhance_image_pro(file_path, args, progress_callback, output_folder)
                if success:
                    success_count += 1
                    self.root.after(0, lambda m=msg: self.log(f"✓ {m}"))
                else:
                    self.root.after(0, lambda m=msg: self.log(f"✗ {m}"))
            except Exception as e:
                self.root.after(0, lambda e=str(e): self.log(f"✗ Error: {e}"))
        
        self.processing = False
        self.root.after(0, lambda: self.update_progress(100, f"Complete! {success_count}/{len(self.files)} images enhanced"))
        self.root.after(0, lambda: messagebox.showinfo("Complete", f"Enhanced {success_count} of {len(self.files)} images!\n\nSaved to: {output_folder}"))
        
    def start_processing(self):
        if self.processing:
            return
            
        if not self.files:
            messagebox.showwarning("Warning", "Please select image(s) first!")
            return
            
        self.processing = True
        self.progress_var.set(0)
        self.log("\n" + "="*50)
        self.log("Starting enhancement...")
        
        # Run in separate thread
        thread = threading.Thread(target=self.process_files)
        thread.daemon = True
        thread.start()

# ==================== CLI ====================

def cli_main():
    parser = argparse.ArgumentParser(
        description='Advanced Image Enhancer Pro with GUI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch GUI
  python enhancer_gui.py
  
  # CLI: Basic 4K enhancement
  python enhancer_gui.py photo.jpg
  
  # CLI: 8K with vivid colors
  python enhancer_gui.py photo.jpg -r 8k --preset vivid
  
  # CLI: Batch processing
  python enhancer_gui.py ./images --batch -r 8k --preset photo
        """
    )
    
    parser.add_argument('input', nargs='?', help='Input image file or directory')
    parser.add_argument('-o', '--output', help='Output folder (default: ./enhanced)')
    parser.add_argument('--batch', action='store_true', help='Batch process directory')
    parser.add_argument('--gui', action='store_true', help='Launch GUI mode')
    
    parser.add_argument('-r', '--resolution', default='4k',
                       choices=list(RESOLUTIONS.keys()),
                       help='Target resolution (default: 4k)')
    parser.add_argument('-a', '--algorithm', default='lanczos',
                       choices=list(ALGORITHMS.keys()),
                       help='Upscaling algorithm (default: lanczos)')
    parser.add_argument('--fit', default='fit',
                       choices=['fit', 'fill', 'stretch'],
                       help='How to fit image to resolution (default: fit)')
    parser.add_argument('--preset', choices=list(PRESETS.keys()),
                       help='Use enhancement preset')
    parser.add_argument('--list-presets', action='store_true',
                       help='List available presets')
    
    parser.add_argument('--sharpen', type=float, default=1.5,
                       help='Sharpen factor (1.0 = no change, default: 1.5)')
    parser.add_argument('--contrast', type=float, default=1.1,
                       help='Contrast factor (default: 1.1)')
    parser.add_argument('--saturation', type=float, default=1.05,
                       help='Saturation factor (default: 1.05)')
    parser.add_argument('--brightness', type=float, default=1.0,
                       help='Brightness factor (default: 1.0)')
    parser.add_argument('--denoise', action='store_true', default=True,
                       help='Apply denoising (default: True)')
    parser.add_argument('--edge-enhance', action='store_true',
                       help='Apply edge enhancement')
    
    parser.add_argument('-q', '--quality', type=int, default=95,
                       help='JPEG quality 1-100 (default: 95)')
    
    args = parser.parse_args()
    
    # Launch GUI if no arguments or --gui flag
    if args.gui or (not args.input and not args.list_presets):
        root = tk.Tk()
        app = EnhancerGUI(root)
        root.mainloop()
        return
    
    if args.list_presets:
        print("\n🎨 Available Presets:")
        for name, settings in PRESETS.items():
            print(f"\n  {name.upper()}:")
            for key, value in settings.items():
                print(f"    • {key}: {value}")
        return
    
    if not args.input:
        parser.print_help()
        return
    
    # CLI Processing
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    files = []
    
    if os.path.isdir(args.input):
        for filename in os.listdir(args.input):
            if Path(filename).suffix.lower() in image_extensions:
                files.append(os.path.join(args.input, filename))
    elif os.path.isfile(args.input):
        files.append(args.input)
    else:
        import glob
        files = glob.glob(args.input)
    
    if not files:
        print("❌ No images found")
        return
    
    output_folder = args.output if args.output else ensure_output_folder()
    
    print(f"\n🚀 Processing {len(files)} images")
    print(f"📁 Output folder: {output_folder}")
    print("="*50)
    
    success_count = 0
    for i, file_path in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] {os.path.basename(file_path)}")
        success, msg = enhance_image_pro(file_path, args, output_folder=output_folder)
        if success:
            success_count += 1
            print(f"  ✓ {msg}")
        else:
            print(f"  ✗ {msg}")
    
    print("\n" + "="*50)
    print(f"📊 Summary: {success_count}/{len(files)} images enhanced")
    print(f"📁 Saved to: {output_folder}")

if __name__ == "__main__":
    cli_main()
