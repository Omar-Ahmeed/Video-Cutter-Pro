# 🎬 Video Cutter Pro

**Video Cutter Pro** is a modern, lightweight, and efficient desktop application for video editing tasks. Built with **Python**, it leverages the power of `MoviePy` for processing and `CustomTkinter` for a sleek, dark-themed user interface.

## 📥 Download
**Get the latest version for Windows:**
[👉 Download Video Cutter Pro (.exe)](https://github.com/Omar-Ahmeed/Video-Cutter-Pro/releases/latest)
---

## ✨ Features

- **🎨 Modern Dark UI:** A clean, eye-friendly interface built with `CustomTkinter`.
- **👁️ Live Frame Preview:** Real-time visual feedback while dragging the timeline sliders.
- **✂️ Precise Trimming:** Easily select start and end points with accuracy.
- **🎵 Audio Extraction:** Convert video segments directly to **MP3** format.
- **🔇 Mute Option:** Remove audio tracks from your video clips.
- **⏩ Speed Control:** Adjust playback speed (0.5x, 1.0x, 1.5x, 2.0x).
- **📊 Real-time Progress:** Accurate progress bar tracking for rendering status.
- **📂 Auto-Open:** Automatically opens the output folder upon completion.

---

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher.
- `pip` package manager.

### 1. Clone the Repository
```bash
git clone [https://github.com/YourUsername/Video-Cutter-Pro](https://github.com/Omar-Ahmeed/Video-Cutter-Pro).git
cd Video-Cutter-Pro
```

### 2. Install Dependencies
Install all required libraries using the provided requirements file:
```bash
pip install -r requirements.txt
```

---

## 🚀 Usage

To run the application from the source code:

```bash
python main.py
```

### How to use:
1. Click **"Select Video File"** to browse and load your video.
2. Drag the **Start** and **End** sliders to choose your clip (watch the preview window).
3. (Optional) Check **"Mute Audio"** if you want a silent video.
4. (Optional) Toggle **"Save as Audio (MP3)"** to extract sound only.
5. Select your desired **Playback Speed**.
6. Click **"Save & Export"** and choose where to save the file.

---

## 📂 Project Structure

```text
Video-Cutter-Pro/
│
├── main.py              # Main application entry point
├── requirements.txt     # List of dependencies
├── README.md            # Project documentation
└── .gitignore           # Git configuration
```

---

## 📝 Dependencies

This project relies on the following open-source libraries:
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - UI Framework.
- [MoviePy](https://zulko.github.io/moviepy/) - Video Editing.
- [Pillow](https://python-pillow.org/) - Image Processing.
- [Proglog](https://github.com/Edinburgh-Genome-Foundry/Proglog) - Progress Logging.
- [PyInstaller](https://pyinstaller.org/) - Executable Creation.

---

## 🤝 Contributing

Contributions are welcome! If you have suggestions or improvements:
1. Fork the project.
2. Create your feature branch (`git checkout -b feature/NewFeature`).
3. Commit your changes (`git commit -m 'Add some NewFeature'`).
4. Push to the branch (`git push origin feature/NewFeature`).
5. Open a Pull Request.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

**Developed with ❤️ by Omar Ahmed**
