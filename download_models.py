import os
import sys
import urllib.request
import logging
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model URLs and paths
MODELS = {
    "SAM": {
        "url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth",
        "path": "models/sam_vit_h_4b8939.pth",
        "size": 2564356163  # ~2.4GB
    },
    "ControlNet": {
        "url": "https://huggingface.co/lllyasviel/control_v11p_sd15_inpaint/resolve/main/diffusion_pytorch_model.bin",
        "path": "models/control_v11p_sd15_inpaint.pth",
        "size": 1419044714  # ~1.3GB
    }
}

class DownloadProgressBar:
    def __init__(self, filename, total_size):
        self.pbar = tqdm(
            total=total_size,
            unit='iB',
            unit_scale=True,
            desc=f'Downloading {filename}'
        )

    def update(self, block_num, block_size, total_size):
        if total_size != -1:
            self.pbar.total = total_size
        self.pbar.update(block_size)

def check_disk_space(required_bytes):
    """Check if there's enough disk space available."""
    try:
        if sys.platform == 'win32':
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p('.'), None, None, ctypes.pointer(free_bytes)
            )
            free_space = free_bytes.value
        else:
            import os
            st = os.statvfs('.')
            free_space = st.f_bavail * st.f_frsize
            
        # Add 1GB buffer
        required_with_buffer = required_bytes + (1024 * 1024 * 1024)
        
        if free_space < required_with_buffer:
            logger.error(f"Not enough disk space. Required: {required_with_buffer/1024/1024/1024:.1f}GB "
                        f"(including buffer), Available: {free_space/1024/1024/1024:.1f}GB")
            return False
        return True
    except Exception as e:
        logger.error(f"Error checking disk space: {str(e)}")
        return False

def download_model(name, url, save_path, expected_size):
    """Download a model file with progress bar."""
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        if os.path.exists(save_path):
            actual_size = os.path.getsize(save_path)
            if actual_size == expected_size:
                logger.info(f"{name} already exists and has correct size")
                return True
            else:
                logger.warning(f"Existing {name} has incorrect size. Redownloading...")
                os.remove(save_path)
        
        logger.info(f"Downloading {name}...")
        progress_bar = DownloadProgressBar(os.path.basename(save_path), expected_size)
        
        urllib.request.urlretrieve(
            url,
            save_path,
            reporthook=progress_bar.update
        )
        progress_bar.pbar.close()
        
        # Verify download
        if os.path.exists(save_path):
            actual_size = os.path.getsize(save_path)
            if actual_size == expected_size:
                logger.info(f"Successfully downloaded {name}")
                return True
            else:
                logger.error(f"Downloaded file size mismatch for {name}")
                os.remove(save_path)
                return False
        else:
            logger.error(f"Failed to download {name}")
            return False
            
    except Exception as e:
        logger.error(f"Error downloading {name}: {str(e)}")
        if os.path.exists(save_path):
            os.remove(save_path)
        return False

def main():
    """Main download function."""
    # Calculate total required space
    total_size = sum(model["size"] for model in MODELS.values())
    
    # Check disk space
    if not check_disk_space(total_size):
        return False
    
    # Download models
    success = True
    for name, info in MODELS.items():
        if not download_model(name, info["url"], info["path"], info["size"]):
            success = False
            break
    
    if success:
        logger.info("\nAll models downloaded successfully!")
        logger.info("You can now run the application using: python app.py")
    else:
        logger.error("\nFailed to download all required models")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\nDownload interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\nUnexpected error: {str(e)}")
        sys.exit(1)