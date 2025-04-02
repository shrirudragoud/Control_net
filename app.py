import os
import sys
import urllib.request
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from utils.image_processor import ImageProcessor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Model configuration
MODEL_DIR = 'models'
CHECKPOINT_PATH = os.path.join(MODEL_DIR, "sam_vit_h_4b8939.pth")
CONTROLNET_PATH = os.path.join(MODEL_DIR, "control_v11p_sd15_inpaint.pth")

# Ensure required directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# Initialize image processor
image_processor = None

# Store processed images for the session
processed_images = {}

def verify_models():
    """Verify required model files exist."""
    required_models = [CHECKPOINT_PATH, CONTROLNET_PATH]
    missing_models = [model for model in required_models if not os.path.exists(model)]
    
    if missing_models:
        logger.error(f"Missing required models: {', '.join(missing_models)}")
        return False
    return True

def init_image_processor():
    """Initialize the image processor, verifying models first."""
    global image_processor
    try:
        if not verify_models():
            raise Exception("Required models are missing. Please run setup.py first.")
        
        image_processor = ImageProcessor(CHECKPOINT_PATH)
        logger.info("Successfully initialized image processor")
    except Exception as e:
        logger.error(f"Failed to initialize image processor: {str(e)}")
        raise

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Save original image
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            logger.info(f"Saved uploaded file: {filepath}")
            
            # Initialize image processor if not already done
            if image_processor is None:
                init_image_processor()
            
            # Process the image for segmentation
            try:
                # Generate mask
                mask = image_processor.process_image(filepath)
                mask_filename = f'mask_{filename}'
                mask_path = os.path.join(app.config['UPLOAD_FOLDER'], mask_filename)
                image_processor.save_mask(mask, mask_path)
                logger.info(f"Generated and saved mask: {mask_path}")
                
                # Apply mask to original image
                masked_filename = f'masked_{filename}'
                masked_path = os.path.join(app.config['UPLOAD_FOLDER'], masked_filename)
                image_processor.apply_mask_to_image(filepath, mask_path, masked_path)
                logger.info(f"Applied mask and saved result: {masked_path}")
                
                # Store the processed image info for later use
                processed_images[filename] = {
                    'original': filepath,
                    'mask': mask_path,
                    'masked': masked_path
                }
                
                return jsonify({
                    'success': True,
                    'original_image': filename,
                    'mask_image': mask_filename,
                    'masked_image': masked_filename,
                    'message': 'Segmentation complete. Ready for try-on generation.'
                })
                
            except Exception as e:
                logger.error(f"Error processing image: {str(e)}")
                return jsonify({'error': f'Error processing image: {str(e)}'}), 500
                
        except Exception as e:
            logger.error(f"Error handling upload: {str(e)}")
            return jsonify({'error': f'Error handling upload: {str(e)}'}), 500
            
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/generate', methods=['POST'])
def generate_tryon():
    """Generate try-on image using processed mask and custom prompt."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        filename = data.get('filename')
        clothing_type = data.get('clothing_type', 'default')
        custom_prompt = data.get('prompt', '')
        
        if not filename or filename not in processed_images:
            return jsonify({'error': 'No processed image found'}), 400
            
        # Get stored image paths
        image_info = processed_images[filename]
        
        # Generate try-on image
        prompt = custom_prompt if custom_prompt else CLOTHING_PROMPTS.get(clothing_type, CLOTHING_PROMPTS['default'])
        tryon_filename = f'tryon_{filename}'
        tryon_path = os.path.join(app.config['UPLOAD_FOLDER'], tryon_filename)
        
        try:
            result_image = image_processor.generate_try_on(
                image_info['original'],
                image_info['mask'],
                prompt
            )
            image_processor.postprocess_result(result_image, tryon_path)
            logger.info(f"Generated and saved try-on image: {tryon_path}")
            
            return jsonify({
                'success': True,
                'tryon_image': tryon_filename,
                'prompt_used': prompt
            })
            
        except Exception as e:
            logger.error(f"Error generating try-on image: {str(e)}")
            return jsonify({'error': f'Error generating try-on image: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error in generate_tryon: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File is too large (max 16MB)'}), 413

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}")
    return jsonify({'error': 'An unexpected error occurred'}), 500

# Default prompts for different clothing types
CLOTHING_PROMPTS = {
    "default": "a photo of a person wearing the clothing, front view, full body shot, high quality, detailed, professional lighting",
    "shirt": "a photo of a person wearing the shirt, front view, professional photo, full body, high quality, studio lighting",
    "dress": "a photo of a person wearing the dress, front view, professional photo, full body, high quality, fashion photography",
    "pants": "a photo of a person wearing the pants, front view, professional photo, full body, high quality, clean background"
}

if __name__ == '__main__':
    try:
        # Verify and initialize
        if not verify_models():
            logger.error("Please run setup.py first to download required models.")
            sys.exit(1)
            
        init_image_processor()
        
        # Get port from environment variable or default to 5000
        port = int(os.environ.get('PORT', 5000))
        
        # Listen on all available network interfaces
        app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)