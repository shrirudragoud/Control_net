import os
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

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize image processor
CHECKPOINT_PATH = "sam_vit_h_4b8939.pth"
image_processor = None

def init_image_processor():
    global image_processor
    try:
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
            
            # Process the image
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
                
                return jsonify({
                    'success': True,
                    'original_image': filename,
                    'mask_image': mask_filename,
                    'masked_image': masked_filename
                })
                
            except Exception as e:
                logger.error(f"Error processing image: {str(e)}")
                return jsonify({'error': f'Error processing image: {str(e)}'}), 500
                
        except Exception as e:
            logger.error(f"Error handling upload: {str(e)}")
            return jsonify({'error': f'Error handling upload: {str(e)}'}), 500
            
    return jsonify({'error': 'Invalid file type'}), 400

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

if __name__ == '__main__':
    try:
        init_image_processor()
        app.run(debug=True)
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")