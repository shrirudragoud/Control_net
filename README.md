# Virtual Try-On System

A web application that allows users to upload clothing images, segment them using SAM (Segment Anything Model), and virtually try them on using Stable Diffusion with ControlNet.

## Features

- Upload clothing images
- Automatic garment segmentation using SAM2
- Virtual try-on generation with Stable Diffusion and ControlNet
- Real-time progress tracking
- Responsive web interface

## Prerequisites

- Python 3.8 or higher
- CUDA-capable GPU (recommended for faster processing)
- Git

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd virtual-tryon-system
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Run the setup script to install dependencies and download required models:
```bash
python setup.py
```

This will:
- Install required Python packages
- Create necessary directories
- Download the SAM checkpoint file

## Running the Application

1. Ensure your virtual environment is activated

2. Start the Flask application:
```bash
python app.py
```

3. Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Click the "Choose File" button to select a clothing image
2. Click "Process Image" to upload and process the image
3. Wait for the processing to complete:
   - Image segmentation
   - Try-on generation
4. View the results in the results section:
   - Original image
   - Segmented mask
   - Generated try-on result

## Project Structure

```
virtual-tryon-system/
├── app.py              # Main Flask application
├── setup.py           # Setup script
├── requirements.txt   # Python dependencies
├── static/           # Static files
│   ├── css/         # CSS styles
│   └── js/          # JavaScript files
├── templates/        # HTML templates
├── uploads/         # Uploaded and processed images
└── README.md        # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Segment Anything Model (SAM)](https://segment-anything.com/) by Meta AI
- [Stable Diffusion](https://stability.ai/blog/stable-diffusion-public-release) by Stability AI
- [ControlNet](https://github.com/lllyasviel/ControlNet) for controlled image generation