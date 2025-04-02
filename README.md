# Virtual Try-On System

A web application that allows users to upload clothing images, segment them using SAM (Segment Anything Model), and virtually try them on using Stable Diffusion with ControlNet.

## Quick Start

### Windows Users
1. Double-click `start.bat`
2. Wait for the setup to complete
3. Open http://localhost:5000 in your browser

### Linux/Mac Users
1. Open Terminal
2. Navigate to the project directory
3. Run:
```bash
chmod +x start.sh
./start.sh
```
4. Open http://localhost:5000 in your browser

## Manual Setup

If you prefer to run commands manually:

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Download models:
```bash
python get_models.py
```

3. Start the application:
```bash
python app.py
```

## Requirements

- Python 3.8 or higher
- CUDA-capable GPU (recommended for faster processing)
- At least 5GB of free disk space
- Good internet connection for downloading models

## Features

- Upload clothing images
- Automatic garment segmentation using SAM2
- Virtual try-on generation with Stable Diffusion and ControlNet
- Support for different clothing types:
  - Shirts/Tops
  - Dresses
  - Pants
- Custom prompt generation
- Real-time progress tracking
- Responsive web interface

## Usage

1. Start the application using one of the methods above
2. Open your web browser and go to http://localhost:5000
3. Upload a clothing image
4. Wait for segmentation to complete
5. Choose clothing type and/or enter custom prompt
6. Generate the try-on result

## Troubleshooting

### Common Issues

1. **Missing Models Error**
   - Run `python get_models.py` to download required models
   - Check if the models directory exists and contains the required files
   - Ensure you have enough disk space

2. **CUDA/GPU Issues**
   - The application will run on CPU if CUDA is not available
   - Update your GPU drivers if CUDA is not detected
   - For better performance, ensure you have a CUDA-capable GPU

3. **Installation Problems**
   - Update pip: `python -m pip install --upgrade pip`
   - Try installing requirements one by one if bulk install fails
   - Check Python version compatibility

4. **Application Won't Start**
   - Check if port 5000 is available
   - Ensure all required models are downloaded
   - Check the logs for specific error messages

### Getting Help

If you encounter issues:
1. Check the error message in the console
2. Verify all requirements are installed
3. Ensure models are properly downloaded
4. Try running the commands manually instead of using start scripts

## License

This project is licensed under the MIT License.

## Acknowledgments

- [Segment Anything Model (SAM)](https://segment-anything.com/) by Meta AI
- [Stable Diffusion](https://stability.ai/blog/stable-diffusion-public-release) by Stability AI
- [ControlNet](https://github.com/lllyasviel/ControlNet) for controlled image generation