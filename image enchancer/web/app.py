from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from PIL import Image, ImageFilter, ImageEnhance, ExifTags
from werkzeug.utils import secure_filename
import os
import uuid
import threading
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ENHANCED_FOLDER = 'enhanced'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ENHANCED_FOLDER'] = ENHANCED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ENHANCED_FOLDER, exist_ok=True)

# Resolution definitions
RESOLUTIONS = {
    '720p': (1280, 720),
    '1080p': (1920, 1080),
    '2k': (2560, 1440),
    '4k': (3840, 2160),
    '8k': (7680, 4320)
}

ALGORITHMS = {
    'lanczos': Image.Resampling.LANCZOS,
    'bicubic': Image.Resampling.BICUBIC,
    'bilinear': Image.Resampling.BILINEAR,
    'nearest': Image.Resampling.NEAREST,
    'box': Image.Resampling.BOX
}

PRESETS = {
    'photo': {'algorithm': 'lanczos', 'sharpen': 1.5, 'contrast': 1.1, 'saturation': 1.05, 'brightness': 1.0, 'denoise': True},
    'artwork': {'algorithm': 'lanczos', 'sharpen': 1.8, 'contrast': 1.15, 'saturation': 1.1, 'brightness': 1.0, 'denoise': False},
    'text': {'algorithm': 'bicubic', 'sharpen': 2.0, 'contrast': 1.3, 'saturation': 1.0, 'brightness': 1.05, 'denoise': True},
    'soft': {'algorithm': 'lanczos', 'sharpen': 1.0, 'contrast': 1.0, 'saturation': 1.0, 'brightness': 1.0, 'denoise': True},
    'vivid': {'algorithm': 'lanczos', 'sharpen': 1.6, 'contrast': 1.2, 'saturation': 1.3, 'brightness': 1.05, 'denoise': False},
    'hdr': {'algorithm': 'lanczos', 'sharpen': 1.4, 'contrast': 1.4, 'saturation': 1.2, 'brightness': 1.02, 'denoise': True}
}

# Store job status
jobs = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def auto_rotate_by_exif(img):
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
    if strength <= 0:
        return img
    radius = int(strength)
    if radius > 0:
        return img.filter(ImageFilter.MedianFilter(size=radius * 2 + 1))
    return img

def apply_sharpen(img, factor=1.5):
    if factor <= 1.0:
        return img
    enhancer = ImageEnhance.Sharpness(img)
    return enhancer.enhance(factor)

def apply_color_enhancements(img, contrast=1.0, saturation=1.0, brightness=1.0):
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

def enhance_image_task(job_id, input_path, settings):
    """Process image in background thread"""
    try:
        jobs[job_id]['status'] = 'processing'
        jobs[job_id]['progress'] = 10
        
        # Load settings
        resolution = settings.get('resolution', '4k')
        preset_name = settings.get('preset', 'photo')
        fit_mode = settings.get('fit', 'fit')
        
        if preset_name in PRESETS:
            preset = PRESETS[preset_name]
            algorithm = preset['algorithm']
            sharpen = preset['sharpen']
            contrast = preset['contrast']
            saturation = preset['saturation']
            brightness = preset['brightness']
            denoise = preset['denoise']
        else:
            algorithm = settings.get('algorithm', 'lanczos')
            sharpen = float(settings.get('sharpen', 1.5))
            contrast = float(settings.get('contrast', 1.1))
            saturation = float(settings.get('saturation', 1.05))
            brightness = float(settings.get('brightness', 1.0))
            denoise = settings.get('denoise', True)
        
        edge_enhance = settings.get('edge_enhance', False)
        quality = int(settings.get('quality', 95))
        
        jobs[job_id]['progress'] = 20
        
        with Image.open(input_path) as img:
            original_size = img.size
            
            # Auto-rotate
            if settings.get('auto_rotate', True):
                img = auto_rotate_by_exif(img)
            
            # Convert mode
            if img.mode in ('RGBA', 'P', 'LA'):
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                else:
                    img = img.convert('RGB')
            
            jobs[job_id]['progress'] = 30
            
            # Resize
            target_resolution = RESOLUTIONS.get(resolution, RESOLUTIONS['4k'])
            target_size = calculate_target_size(img.size, target_resolution, fit_mode)
            img = img.resize(target_size, ALGORITHMS[algorithm])
            
            jobs[job_id]['progress'] = 50
            
            # Enhancements
            if denoise:
                img = apply_denoise(img, strength=1.5)
            
            jobs[job_id]['progress'] = 60
            
            if sharpen != 1.0:
                img = apply_sharpen(img, sharpen)
            
            jobs[job_id]['progress'] = 70
            
            img = apply_color_enhancements(img, contrast, saturation, brightness)
            
            jobs[job_id]['progress'] = 80
            
            if edge_enhance:
                img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
            
            jobs[job_id]['progress'] = 90
            
            # Save
            output_filename = f"{job_id}_{resolution}_{preset_name}.jpg"
            output_path = os.path.join(app.config['ENHANCED_FOLDER'], output_filename)
            img.save(output_path, quality=quality, optimize=True, progressive=True)
            
            jobs[job_id]['status'] = 'completed'
            jobs[job_id]['progress'] = 100
            jobs[job_id]['output_file'] = output_filename
            jobs[job_id]['output_size'] = target_size
            jobs[job_id]['file_size'] = os.path.getsize(output_path) / (1024 * 1024)
            
    except Exception as e:
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        job_id = str(uuid.uuid4())[:8]
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}_{filename}")
        file.save(input_path)
        
        # Get image info
        with Image.open(input_path) as img:
            width, height = img.size
            format_type = img.format
        
        return jsonify({
            'job_id': job_id,
            'filename': filename,
            'input_path': input_path,
            'original_size': {'width': width, 'height': height},
            'format': format_type
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/enhance', methods=['POST'])
def enhance_image():
    data = request.json
    job_id = data.get('job_id')
    input_path = data.get('input_path')
    settings = data.get('settings', {})
    
    if not job_id or not input_path:
        return jsonify({'error': 'Missing job_id or input_path'}), 400
    
    # Initialize job
    jobs[job_id] = {
        'id': job_id,
        'status': 'queued',
        'progress': 0,
        'created_at': datetime.now().isoformat()
    }
    
    # Start processing in background
    thread = threading.Thread(target=enhance_image_task, args=(job_id, input_path, settings))
    thread.daemon = True
    thread.start()
    
    return jsonify({'job_id': job_id, 'status': 'started'})

@app.route('/api/status/<job_id>')
def get_status(job_id):
    if job_id in jobs:
        return jsonify(jobs[job_id])
    return jsonify({'error': 'Job not found'}), 404

@app.route('/api/download/<job_id>')
def download_file(job_id):
    if job_id in jobs and jobs[job_id].get('output_file'):
        filename = jobs[job_id]['output_file']
        return send_from_directory(app.config['ENHANCED_FOLDER'], filename, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/presets')
def get_presets():
    return jsonify(PRESETS)

@app.route('/api/resolutions')
def get_resolutions():
    return jsonify({k: {'width': v[0], 'height': v[1]} for k, v in RESOLUTIONS.items()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
