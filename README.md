# Skin Conversion Tool

A simple GUI tool for upscaling or downscaling PNG images using nearest-neighbor interpolation.

## Running the Tool

**Windows** - double-click `run.bat`

**macOS** - double-click `run.command`

**Linux** - double-click `run.desktop`

Alternatively, run from the terminal:

```bash
python3 main.py
```

## Dependencies

Install the required packages with:

```bash
sudo apt install python3-pillow python3-pil.imagetk python3-tk
```

> On macOS, use `pip3 install Pillow` instead. tkinter is included with most Python installs.

## Usage

1. Click **Import** to select one or more PNG images.
2. Click **Output** to choose the export destination folder.
3. Set the desired output width and height. Enable **Lock** to preserve the aspect ratio.
4. Click **Convert**.