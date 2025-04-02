import os
import sys
import urllib.request
import subprocess
import logging
from tqdm import tqdm
import torch
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DownloadProgressBar:
    def __init__(self, total_size):
        self.pbar = tqdm(total=total_size, unit='iB', unit_scale=True)

    def update(self, block_num, block_size, total_size):
        if total_size != -1:
            self.pbar.total = total_size
        self.pbar.update(block_size)

def download_file(url, save_path):
    """Download a file with progress bar."""
    try:
        response = urllib.request.urlopen(url)
        file_size = int(response.headers['Content-Length'])
        
        logger.info(f"Downloading {save_path} ({file_size/1024/1024:.1f}MB)")
        progress_bar = DownloadProgressBar(file_size)
        
        urllib.request.urlretrieve(
            url, 
            save_path,
            reporthook=progress_bar.update
        )
        progress_bar.pbar.close()
        
        if os.path.exists(save_path):
            actual_size = os.path.getsize(save_path)
            if actual_size == file_size:
                logger.info(f"Successfully downloaded {save_path}")
                return True
            else:
                logger.error(f"File size mismatch for {save_path}")
                os.remove(save_path)
                return False
    except Exception as e:
        logger.error(f"Error downloading {save_path}: {str(e)}")
        if os.path.exists(save_path):
            os.remove(save_path)
        return False

def download_models():
    """Download required model files."""
    models = {
        "sam_vit_h_4b8939.pth": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth",
        "control_v11p_sd15_inpaint.pth": "https://huggingface.co/lllyasviel/control_v11p_sd15_inpaint/resolve/main/diffusion_pytorch_model.bin"
    }
    
    success = True
    model_dir = "models"
    os.makedirs(model_dir, exist_ok=True)
    
    for model_name, url in models.items():
        model_path = os.path.join(model_dir, model_name)
        if not os.path.exists(model_path):
            logger.info(f"Downloading {model_name}...")
            if not download_file(url, model_path):
                success = False
        else:
            logger.info(f"{model_name} already exists")
    
    return success

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        'uploads',
        'static/css',
        'static/js',
        'templates',
        'models',
        'test_data'
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        except Exception as e:
            logger.error(f"Error creating directory {directory}: {str(e)}")
            raise

def install_requirements():
    """Install required packages."""
    try:
        logger.info("Installing requirements...")
        # Upgrade pip first
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        # Install requirements
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        logger.info("Successfully installed requirements")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing requirements: {e}")
        return False

def verify_cuda():
    """Verify CUDA availability and setup."""
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            device_name = torch.cuda.get_device_name(0)
            cuda_version = torch.version.cuda
            logger.info(f"CUDA is available - Device: {device_name}, CUDA Version: {cuda_version}")
        else:
            logger.warning("CUDA is not available - using CPU (this will be slower)")
        return cuda_available
    except Exception as e:
        logger.warning(f"Error checking CUDA: {str(e)}")
        return False

def verify_models():
    """Verify all required models are present and valid."""
    required_models = [
        "sam_vit_h_4b8939.pth",
        "control_v11p_sd15_inpaint.pth"
    ]
    
    model_dir = "models"
    all_present = True
    
    for model in required_models:
        model_path = os.path.join(model_dir, model)
        if not os.path.exists(model_path):
            logger.error(f"Missing required model: {model}")
            all_present = False
        else:
            logger.info(f"Found model: {model}")
    
    return all_present

def main():
    """Main setup function."""
    logger.info("Starting Virtual Try-On System setup...")
    
    try:
        # Create necessary directories
        create_directories()
        
        # Install requirements
        if not install_requirements():
            logger.error("Failed to install requirements")
            return False
        
        # Check CUDA availability
        verify_cuda()
        
        # Download models
        if not download_models():
            logger.error("Failed to download required models")
            return False
        
        # Verify models
        if not verify_models():
            logger.error("Model verification failed")
            return False
        
        logger.info("\nSetup complete! You can now run the application using:")
        logger.info("python app.py")
        return True
        
    except Exception as e:
        logger.error(f"Setup failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)