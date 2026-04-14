# 🖼️ ImageEnchancer Pro

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat&logo=python)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-Web_App-red?style=flat&logo=flask)](https://flask.palletsprojects.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Image_Processing-green?style=flat&logo=opencv)](https://opencv.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**ImageEnchancer Pro** is a powerful Python-based utility for upscaling, denoising, and professionally enhancing images. It features both a modern web interface and a lightweight desktop GUI, making high-quality image processing accessible to everyone.

---

## ⚡ Key Features

- **🚀 AI-Driven Upscaling**: Increase image resolution without losing clarity.
- **🎨 Noise Reduction**: Remove grain and artifacts from low-light photos.
- **🌐 Web Dashboard**: Upload and enhance images directly through a sleek web UI.
- **🖥️ Desktop GUI**: A standalone Tkinter-based application for local processing.
- **🔄 Bulk Processing**: Enhance entire folders of images in one pass.

## 🛠️ Tech Stack

- **Core Engine**: Python, OpenCV, PIL (Pillow)
- **Web App**: Flask, HTML5, CSS3, JavaScript
- **Desktop UI**: Tkinter
- **Packaging**: NPM (for frontend assets)

## 📂 Project Structure

```text
.
├── enhancer.py        # Core processing logic
├── enhancer_gui.py    # Desktop GUI application
├── web/               # Flask Web Application
│   ├── app.py         # Web server
│   ├── static/        # Styles and Scripts
│   └── templates/     # UI layouts
└── requirements.txt   # Python dependencies
```

## 📖 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nivas1899/image_enchancer.git
   cd image_enchancer
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Web App**:
   ```bash
   cd web && python app.py
   ```
4. **Run the Desktop App**:
   ```bash
   python enhancer_gui.py
   ```

---
Created with ❤️ by [nivas1899](https://github.com/nivas1899)
