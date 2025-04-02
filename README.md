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

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download the SAM checkpoint:
Download `sam_vit_h_4b8939.pth` from Meta AI and place it in the project root directory.
You can download it from: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth

## Running the Application

### Local Development
```bash
python app.py
```
Then visit: http://localhost:5000

### Cloud Environment
1. Make the run script executable:
```bash
chmod +x run.sh
```

2. Start the application:
```bash
./run.sh
```

The application will be available at the cloud platform's provided URL.

## Configuration

The application uses several configuration settings that can be modified:

- Maximum file size: 16MB (configurable in app.py)
- Allowed file types: .jpg, .jpeg, .png
- Model checkpoint path: sam_vit_h_4b8939.pth

## Project Structure

```
virtual-tryon-system/
├── app.py              # Main Flask application
├── run.sh             # Cloud environment startup script
├── requirements.txt   # Python dependencies
├── static/           # Static files
│   ├── css/         # CSS styles
│   └── js/          # JavaScript files
├── templates/        # HTML templates
├── uploads/         # Uploaded and processed images
└── utils/           # Utility modules
    └── image_processor.py  # Image processing logic
```

## Usage

1. Access the application through your web browser
2. Click "Choose File" to select a clothing image
3. Click "Process Image" to upload and process the image
4. The system will:
   - Upload the image
   - Generate a segmentation mask using SAM
   - Process the segmented garment
   - Display the results

## Error Handling

The application includes comprehensive error handling for:
- Invalid file types
- File size limits
- Processing failures
- Server errors

## Cloud Environment Notes

When running in a cloud environment:
- The application binds to 0.0.0.0 to accept external connections
- Uses port 5000 by default
- Creates necessary directories with appropriate permissions
- Logs all operations for debugging

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