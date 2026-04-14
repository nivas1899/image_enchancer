# Image Enhancer Pro 🚀

Advanced image enhancement tool with **GUI** and **CLI** - now saves to `enhanced/` folder automatically!

## What's New ✨

- 🖥️ **Tkinter GUI** - Easy-to-use graphical interface
- 📁 **Auto Output Folder** - All enhanced images saved to `enhanced/` folder
- 🔄 **Batch Processing** - Process multiple images at once
- 📊 **Progress Bar** - Real-time progress tracking
- 📜 **Activity Log** - See what's happening

## Installation

```bash
pip install Pillow
```

## Usage

### 🖥️ GUI Mode (Easiest)

```bash
python enhancer_gui.py
```

Or simply double-click `enhancer_gui.py`!

**GUI Features:**
- Select multiple files or entire folders
- All settings available via dropdowns and sliders
- Live progress bar
- Activity log
- Open output folder button

### ⌨️ CLI Mode

```bash
# Basic 4K enhancement (saves to ./enhanced/)
python enhancer_gui.py photo.jpg

# 8K with vivid colors
python enhancer_gui.py photo.jpg -r 8k --preset vivid

# Batch process folder
python enhancer_gui.py ./images --batch -r 4k

# Custom output folder
python enhancer_gui.py photo.jpg -o ./my_enhanced
```

## How It Works

1. **Select Images** - Choose files or folder
2. **Choose Settings** - Resolution, preset, enhancements
3. **Click Enhance** - Images saved to `enhanced/` folder automatically
4. **Done!** - Open folder to see results

## Output Structure

```
your-images/
├── photo1.jpg
├── photo2.png
└── enhanced/          ← Auto-created!
    ├── photo1_4k_photo.jpg
    └── photo2_4k_photo.png
```

## GUI Options

**Resolution:**
- 720p → 1280×720
- 1080p → 1920×1080
- 2k → 2560×1440
- 4k → 3840×2160
- 8k → 7680×4320

**Presets:**
- `photo` - Balanced for photos (default)
- `artwork` - Digital art optimized
- `text` - Maximum clarity
- `soft` - Gentle processing
- `vivid` - Saturated colors
- `hdr` - HDR-like effect

**Enhancements:**
- Sharpen (1.0 - 3.0)
- Contrast (0.5 - 2.0)
- Saturation (0.5 - 2.0)
- Denoise toggle
- Edge enhance toggle

**Algorithms:**
- `lanczos` - Best quality (default)
- `bicubic` - Good balance
- `bilinear` - Faster
- `nearest` - Pixelated look
- `box` - Smooth

## Examples

### GUI Workflow
```
1. Click "Browse" → Select your images
2. Set Resolution to "8k"
3. Set Preset to "vivid"
4. Click "🚀 Enhance"
5. Images saved to ./enhanced/
```

### CLI Examples

```bash
# Quick 4K enhancement
python enhancer_gui.py vacation.jpg

# 8K artwork
python enhancer_gui.py art.png -r 8k --preset artwork

# Batch with denoise
python enhancer_gui.py ./photos --batch -r 4k --denoise

# Maximum quality
python enhancer_gui.py photo.jpg -r 8k -a lanczos --preset photo -q 100
```

## Quick Tips 💡

1. **Start with GUI** to test settings
2. **Use presets** for quick results
3. **Batch mode** for multiple photos
4. **Default output** is always `./enhanced/`
5. **Files are renamed** with resolution suffix

## Keyboard Shortcuts (GUI)

- Select files: Click "Browse" button
- Select folder: Click "Folder" button
- Start: Click "🚀 Enhance" button
- Open results: Click "Open Folder" button

## Troubleshooting

**"No module named tkinter"**
- Windows: Should work by default
- Linux: `sudo apt-get install python3-tk`
- Mac: `brew install python-tk`

**"PIL not found"**
```bash
pip install Pillow
```

**Large files slow?**
- Use lower resolution first
- Try `bicubic` algorithm for speed

## Supported Formats

**Input:** JPG, JPEG, PNG, BMP, TIFF, WEBP, GIF

**Output:** JPG (with quality control)

## File Naming

Enhanced files are automatically named:
```
originalname_resolution_preset.jpg

Examples:
photo_4k_photo.jpg
artwork_8k_vivid.png
screenshot_2k_text.jpg
```

## Both Modes Available!

- `enhancer_gui.py` - GUI + CLI combined
- `enhancer_pro.py` - CLI only (original)

Choose whichever you prefer!
