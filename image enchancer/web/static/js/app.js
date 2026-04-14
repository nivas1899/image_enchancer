/**
 * Image Enhancer Pro - Interactive JavaScript with Folder Support
 * Modern UX with drag-drop, batch processing, and folder upload
 */

// Global state
let currentJobs = [];
let selectedFiles = [];
let currentFileIndex = 0;
let progressInterval = null;
let isBatchMode = false;

// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const folderInput = document.getElementById('folderInput');
const uploadSection = document.getElementById('upload');
const workspaceSection = document.getElementById('workspace');
const progressSection = document.getElementById('progressSection');
const resultSection = document.getElementById('resultSection');
const previewImage = document.getElementById('previewImage');
const fileInfo = document.getElementById('fileInfo');
const imageDimensions = document.getElementById('imageDimensions');
const enhanceBtn = document.getElementById('enhanceBtn');
const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toastMessage');

// Settings
const settings = {
    resolution: '4k',
    preset: 'photo',
    algorithm: 'lanczos',
    fit: 'fit',
    sharpen: 1.5,
    contrast: 1.1,
    saturation: 1.05,
    brightness: 1.0,
    denoise: true,
    edgeEnhance: false,
    quality: 95,
    autoRotate: true
};

// ==========================================
// Initialization
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    initParticles();
    initEventListeners();
    initSliders();
});

// Create animated background particles
function initParticles() {
    const container = document.getElementById('particles');
    const particleCount = 25;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.animationDelay = `${Math.random() * 20}s`;
        particle.style.animationDuration = `${15 + Math.random() * 10}s`;
        container.appendChild(particle);
    }
}

// ==========================================
// Event Listeners
// ==========================================

function initEventListeners() {
    // File upload buttons
    dropZone.addEventListener('click', showUploadOptions);
    fileInput.addEventListener('change', (e) => handleFiles(e.target.files));
    folderInput.addEventListener('change', (e) => handleFiles(e.target.files));
    
    // Drag and drop
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);
    
    // Resolution cards
    document.querySelectorAll('.resolution-card').forEach(card => {
        card.addEventListener('click', () => selectResolution(card));
    });
    
    // Preset cards
    document.querySelectorAll('.preset-card').forEach(card => {
        card.addEventListener('click', () => selectPreset(card));
    });
    
    // Fit toggle
    document.querySelectorAll('.fit-btn').forEach(btn => {
        btn.addEventListener('click', () => selectFit(btn));
    });
    
    // Advanced settings toggle
    const advancedToggle = document.getElementById('advancedToggle');
    const advancedSettings = document.getElementById('advancedSettings');
    
    advancedToggle.addEventListener('click', () => {
        advancedToggle.classList.toggle('open');
        advancedSettings.style.display = advancedToggle.classList.contains('open') ? 'block' : 'none';
    });
    
    // Algorithm select
    document.getElementById('algorithm').addEventListener('change', (e) => {
        settings.algorithm = e.target.value;
    });
    
    // Enhance button
    enhanceBtn.addEventListener('click', startEnhancement);
    
    // Download button
    document.getElementById('downloadBtn').addEventListener('click', downloadResults);
    
    // Enhance another button
    document.getElementById('enhanceAnotherBtn').addEventListener('click', resetApp);
    
    // Navbar scroll effect
    window.addEventListener('scroll', handleScroll);
}

// Show upload options (files or folder)
function showUploadOptions() {
    const choice = confirm('Click OK to select a FOLDER\nClick Cancel to select FILES');
    if (choice) {
        folderInput.click();
    } else {
        fileInput.click();
    }
}

function initSliders() {
    // Sharpen slider
    const sharpenSlider = document.getElementById('sharpen');
    const sharpenValue = document.getElementById('sharpenValue');
    sharpenSlider.addEventListener('input', (e) => {
        settings.sharpen = parseFloat(e.target.value);
        sharpenValue.textContent = settings.sharpen.toFixed(1);
    });
    
    // Contrast slider
    const contrastSlider = document.getElementById('contrast');
    const contrastValue = document.getElementById('contrastValue');
    contrastSlider.addEventListener('input', (e) => {
        settings.contrast = parseFloat(e.target.value);
        contrastValue.textContent = settings.contrast.toFixed(1);
    });
    
    // Saturation slider
    const saturationSlider = document.getElementById('saturation');
    const saturationValue = document.getElementById('saturationValue');
    saturationSlider.addEventListener('input', (e) => {
        settings.saturation = parseFloat(e.target.value);
        saturationValue.textContent = settings.saturation.toFixed(2);
    });
    
    // Quality slider
    const qualitySlider = document.getElementById('quality');
    const qualityValue = document.getElementById('qualityValue');
    qualitySlider.addEventListener('input', (e) => {
        settings.quality = parseInt(e.target.value);
        qualityValue.textContent = `${settings.quality}%`;
    });
    
    // Checkboxes
    document.getElementById('denoise').addEventListener('change', (e) => {
        settings.denoise = e.target.checked;
    });
    
    document.getElementById('edgeEnhance').addEventListener('change', (e) => {
        settings.edgeEnhance = e.target.checked;
    });
}

// ==========================================
// Drag and Drop
// ==========================================

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('dragover');
    
    const items = e.dataTransfer.items;
    const files = [];
    
    // Check if dropping a folder
    if (items && items.length > 0) {
        const item = items[0];
        if (item.kind === 'file') {
            const entry = item.webkitGetAsEntry();
            if (entry && entry.isDirectory) {
                processDirectory(entry, files, () => {
                    handleFiles(files);
                });
                return;
            }
        }
    }
    
    // Handle regular files
    const droppedFiles = e.dataTransfer.files;
    if (droppedFiles.length > 0) {
        handleFiles(droppedFiles);
    }
}

// Recursively process directory
function processDirectory(directoryEntry, files, callback) {
    const reader = directoryEntry.createReader();
    
    reader.readEntries((entries) => {
        let pending = entries.length;
        
        if (pending === 0) {
            callback();
            return;
        }
        
        entries.forEach((entry) => {
            if (entry.isFile) {
                entry.file((file) => {
                    if (isValidImageFile(file)) {
                        files.push(file);
                    }
                    pending--;
                    if (pending === 0) callback();
                });
            } else if (entry.isDirectory) {
                processDirectory(entry, files, () => {
                    pending--;
                    if (pending === 0) callback();
                });
            } else {
                pending--;
                if (pending === 0) callback();
            }
        });
    });
}

function isValidImageFile(file) {
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/tiff', 'image/webp'];
    return validTypes.includes(file.type);
}

// ==========================================
// File Processing
// ==========================================

async function handleFiles(files) {
    // Convert FileList to array and filter valid images
    const fileArray = Array.from(files).filter(isValidImageFile);
    
    if (fileArray.length === 0) {
        showToast('No valid image files found', 'error');
        return;
    }
    
    // Limit to 50 files
    if (fileArray.length > 50) {
        showToast('Maximum 50 files allowed. Processing first 50...', 'warning');
        selectedFiles = fileArray.slice(0, 50);
    } else {
        selectedFiles = fileArray;
    }
    
    isBatchMode = selectedFiles.length > 1;
    currentJobs = [];
    currentFileIndex = 0;
    
    // Show preview of first file
    showPreview(selectedFiles[0]);
    
    // Show workspace
    uploadSection.style.display = 'none';
    workspaceSection.style.display = 'block';
    workspaceSection.scrollIntoView({ behavior: 'smooth' });
    
    if (isBatchMode) {
        fileInfo.textContent = `${selectedFiles.length} files selected`;
        showToast(`${selectedFiles.length} images ready for batch processing!`);
        enhanceBtn.querySelector('.btn-text').innerHTML = `
            <i class="fas fa-wand-magic-sparkles"></i>
            Enhance All (${selectedFiles.length} files)
        `;
    } else {
        fileInfo.textContent = `${selectedFiles[0].name} (${formatFileSize(selectedFiles[0].size)})`;
        showToast('Image uploaded successfully!');
        enhanceBtn.querySelector('.btn-text').innerHTML = `
            <i class="fas fa-wand-magic-sparkles"></i>
            Enhance Image
        `;
    }
}

function showPreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
    };
    reader.readAsDataURL(file);
    
    // Get image dimensions
    const img = new Image();
    img.onload = () => {
        imageDimensions.textContent = `${img.width} × ${img.height}px`;
    };
    img.src = URL.createObjectURL(file);
}

// ==========================================
// Settings Selection
// ==========================================

function selectResolution(card) {
    document.querySelectorAll('.resolution-card').forEach(c => c.classList.remove('active'));
    card.classList.add('active');
    settings.resolution = card.dataset.value;
}

function selectPreset(card) {
    document.querySelectorAll('.preset-card').forEach(c => c.classList.remove('active'));
    card.classList.add('active');
    settings.preset = card.dataset.preset;
    
    applyPresetValues(settings.preset);
}

function applyPresetValues(preset) {
    const presets = {
        photo: { sharpen: 1.5, contrast: 1.1, saturation: 1.05, denoise: true },
        artwork: { sharpen: 1.8, contrast: 1.15, saturation: 1.1, denoise: false },
        text: { sharpen: 2.0, contrast: 1.3, saturation: 1.0, denoise: true },
        soft: { sharpen: 1.0, contrast: 1.0, saturation: 1.0, denoise: true },
        vivid: { sharpen: 1.6, contrast: 1.2, saturation: 1.3, denoise: false },
        hdr: { sharpen: 1.4, contrast: 1.4, saturation: 1.2, denoise: true }
    };
    
    const values = presets[preset];
    if (values) {
        settings.sharpen = values.sharpen;
        settings.contrast = values.contrast;
        settings.saturation = values.saturation;
        settings.denoise = values.denoise;
        
        document.getElementById('sharpen').value = values.sharpen;
        document.getElementById('sharpenValue').textContent = values.sharpen.toFixed(1);
        document.getElementById('contrast').value = values.contrast;
        document.getElementById('contrastValue').textContent = values.contrast.toFixed(1);
        document.getElementById('saturation').value = values.saturation;
        document.getElementById('saturationValue').textContent = values.saturation.toFixed(2);
        document.getElementById('denoise').checked = values.denoise;
    }
}

function selectFit(btn) {
    document.querySelectorAll('.fit-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    settings.fit = btn.dataset.fit;
}

// ==========================================
// Enhancement Process
// ==========================================

async function startEnhancement() {
    if (selectedFiles.length === 0) {
        showToast('Please upload images first', 'error');
        return;
    }
    
    // Show button loading state
    const btnText = enhanceBtn.querySelector('.btn-text');
    const btnLoader = enhanceBtn.querySelector('.btn-loader');
    btnText.style.display = 'none';
    btnLoader.style.display = 'flex';
    enhanceBtn.disabled = true;
    
    // Show progress section
    workspaceSection.style.display = 'none';
    progressSection.style.display = 'block';
    progressSection.scrollIntoView({ behavior: 'smooth' });
    
    if (isBatchMode) {
        await processBatch();
    } else {
        await processSingleFile(selectedFiles[0]);
    }
}

async function processBatch() {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const progressStatus = document.getElementById('progressStatus');
    
    const totalFiles = selectedFiles.length;
    let completedFiles = 0;
    let successCount = 0;
    
    for (let i = 0; i < totalFiles; i++) {
        const file = selectedFiles[i];
        currentFileIndex = i;
        
        const overallProgress = (i / totalFiles) * 100;
        progressFill.style.width = `${overallProgress}%`;
        progressText.textContent = `${Math.round(overallProgress)}%`;
        progressStatus.textContent = `Processing ${i + 1} of ${totalFiles}: ${file.name}`;
        
        try {
            const success = await processSingleFile(file, true);
            if (success) successCount++;
        } catch (error) {
            console.error(`Error processing ${file.name}:`, error);
        }
        
        completedFiles++;
    }
    
    progressFill.style.width = '100%';
    progressText.textContent = '100%';
    progressStatus.textContent = 'Complete!';
    
    showBatchResults(successCount, totalFiles);
}

async function processSingleFile(file, isBatch = false) {
    try {
        // Upload file
        const formData = new FormData();
        formData.append('file', file);
        
        if (!isBatch) {
            document.getElementById('progressStatus').textContent = 'Uploading...';
        }
        
        const uploadResponse = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!uploadResponse.ok) throw new Error('Upload failed');
        
        const uploadData = await uploadResponse.json();
        
        // Start enhancement
        if (!isBatch) {
            document.getElementById('progressStatus').textContent = 'Enhancing...';
        }
        
        const enhanceResponse = await fetch('/api/enhance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                job_id: uploadData.job_id,
                input_path: uploadData.input_path,
                settings: settings
            })
        });
        
        if (!enhanceResponse.ok) throw new Error('Enhancement failed');
        
        const enhanceData = await enhanceResponse.json();
        
        // Wait for completion
        await waitForCompletion(enhanceData.job_id, isBatch);
        
        // Get final status
        const statusResponse = await fetch(`/api/status/${enhanceData.job_id}`);
        const statusData = await statusResponse.json();
        
        if (statusData.status === 'completed') {
            currentJobs.push({
                job_id: enhanceData.job_id,
                file: file,
                output_file: statusData.output_file,
                output_size: statusData.output_size,
                file_size: statusData.file_size
            });
            return true;
        }
        
        return false;
        
    } catch (error) {
        console.error('Error:', error);
        return false;
    }
}

function waitForCompletion(jobId, isBatch = false) {
    return new Promise((resolve) => {
        const checkInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/status/${jobId}`);
                const data = await response.json();
                
                if (!isBatch) {
                    const progressFill = document.getElementById('progressFill');
                    const progressText = document.getElementById('progressText');
                    progressFill.style.width = `${data.progress}%`;
                    progressText.textContent = `${Math.round(data.progress)}%`;
                }
                
                if (data.status === 'completed' || data.status === 'error') {
                    clearInterval(checkInterval);
                    resolve();
                }
            } catch (error) {
                clearInterval(checkInterval);
                resolve();
            }
        }, 500);
    });
}

// ==========================================
// Results
// ==========================================

function showBatchResults(successCount, totalFiles) {
    progressSection.style.display = 'none';
    resultSection.style.display = 'block';
    resultSection.scrollIntoView({ behavior: 'smooth' });
    
    // Show first image comparison
    if (currentJobs.length > 0) {
        const firstJob = currentJobs[0];
        showPreview(firstJob.file);
        document.getElementById('originalImage').src = previewImage.src;
        document.getElementById('enhancedImage').src = `/api/download/${firstJob.job_id}`;
    }
    
    // Update stats
    const statsContainer = document.getElementById('resultStats');
    statsContainer.innerHTML = `
        <div class="stat-box">
            <div class="stat-value">${successCount}/${totalFiles}</div>
            <div class="stat-label">Files Processed</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">${settings.resolution.toUpperCase()}</div>
            <div class="stat-label">Resolution</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">${formatTotalSize()}</div>
            <div class="stat-label">Total Size</div>
        </div>
    `;
    
    document.querySelector('.result-header h2').textContent = 'Batch Processing Complete!';
    document.getElementById('downloadBtn').innerHTML = `
        <i class="fas fa-download"></i>
        Download All (${successCount} files)
    `;
    
    showToast(`Successfully enhanced ${successCount} of ${totalFiles} images!`);
}

function formatTotalSize() {
    const totalMB = currentJobs.reduce((sum, job) => sum + (job.file_size || 0), 0);
    if (totalMB > 1024) {
        return `${(totalMB / 1024).toFixed(1)} GB`;
    }
    return `${totalMB.toFixed(1)} MB`;
}

async function downloadResults() {
    if (currentJobs.length === 0) return;
    
    if (currentJobs.length === 1) {
        // Single file download
        downloadSingleFile(currentJobs[0]);
    } else {
        // Batch download as ZIP
        showToast('Preparing ZIP download...');
        
        for (let i = 0; i < currentJobs.length; i++) {
            const job = currentJobs[i];
            setTimeout(() => downloadSingleFile(job, false), i * 500);
        }
        
        showToast('Downloading all files...');
    }
}

async function downloadSingleFile(job, showNotification = true) {
    try {
        const response = await fetch(`/api/download/${job.job_id}`);
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `enhanced_${job.file.name}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            if (showNotification) {
                showToast('Download started!');
            }
        }
    } catch (error) {
        console.error('Download error:', error);
    }
}

// ==========================================
// Utilities
// ==========================================

function resetApp() {
    // Clear state
    currentJobs = [];
    selectedFiles = [];
    currentFileIndex = 0;
    isBatchMode = false;
    
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
    
    // Reset UI
    fileInput.value = '';
    folderInput.value = '';
    previewImage.src = '';
    document.getElementById('progressFill').style.width = '0%';
    document.getElementById('progressText').textContent = '0%';
    
    // Reset button state
    const btnText = enhanceBtn.querySelector('.btn-text');
    const btnLoader = enhanceBtn.querySelector('.btn-loader');
    btnText.style.display = 'flex';
    btnLoader.style.display = 'none';
    btnText.innerHTML = `
        <i class="fas fa-wand-magic-sparkles"></i>
        Enhance Image
    `;
    enhanceBtn.disabled = false;
    
    // Reset result header
    document.querySelector('.result-header h2').textContent = 'Enhancement Complete!';
    document.getElementById('downloadBtn').innerHTML = `
        <i class="fas fa-download"></i>
        Download
    `;
    
    // Show upload section
    resultSection.style.display = 'none';
    progressSection.style.display = 'none';
    workspaceSection.style.display = 'none';
    uploadSection.style.display = 'block';
    uploadSection.scrollIntoView({ behavior: 'smooth' });
}

function showToast(message, type = 'info') {
    toastMessage.textContent = message;
    toast.classList.add('show');
    
    const icon = toast.querySelector('i');
    icon.className = type === 'error' ? 'fas fa-exclamation-circle' : 
                     type === 'success' ? 'fas fa-check-circle' : 
                     type === 'warning' ? 'fas fa-exclamation-triangle' : 'fas fa-info-circle';
    icon.style.color = type === 'error' ? 'var(--error)' : 
                       type === 'success' ? 'var(--success)' : 
                       type === 'warning' ? 'var(--warning)' : 'var(--primary)';
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function handleScroll() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.background = 'rgba(15, 23, 42, 0.95)';
        navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.3)';
    } else {
        navbar.style.background = 'rgba(15, 23, 42, 0.8)';
        navbar.style.boxShadow = 'none';
    }
}

// ==========================================
// Mouse Interactions & Effects
// ==========================================

document.querySelectorAll('.feature-card, .preset-card, .resolution-card').forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-4px)';
    });
    
    card.addEventListener('mouseleave', function() {
        if (!this.classList.contains('active')) {
            this.style.transform = 'translateY(0)';
        }
    });
});

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        if (workspaceSection.style.display !== 'none') {
            startEnhancement();
        }
    }
    
    if (e.key === 'Escape') {
        resetApp();
    }
});
