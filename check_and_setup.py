import os
import sys
import subprocess
import urllib.request
from tqdm import tqdm
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SetupChecker:
    def __init__(self):
        self.model_dir = 'models'
        self.required_models = {
            'sam_vit_h_4b8939.pth': 'https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth',
            'control_v11p_sd15_inpaint.pth': 'https://huggingface.co/lllyasviel/control_v11p_sd15_inpaint/resolve/main/diffusion_pytorch_model.bin'
        }
        self.required_dirs = ['models', 'uploads', 'static', 'templates']

    def check_python_version(self):
        """Check Python version."""
        major, minor = sys.version_info[:2]
        logger.info(f"Python version: {major}.{minor}")
        if (major, minor) < (3, 8):
            logger.error("Python 3.8 or higher is required")
            return False
        return True

    def check_pip(self):
        """Check pip installation and version."""
        try:
            import pip
            logger.info(f"pip version: {pip.__version__}")
            return True
        except ImportError:
            logger.error("pip is not installed")
            return False

    def check_cuda(self):
        """Check CUDA availability."""
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            if cuda_available:
                device_name = torch.cuda.get_device_name(0)
                logger.info(f"CUDA is available: {device_name}")
            else:
                logger.warning("CUDA is not available. The application will run on CPU (slower)")
            return True
        except ImportError:
            logger.error("PyTorch is not installed")
            return False

    def check_directories(self):
        """Check and create required directories."""
        for directory in self.required_dirs:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                    logger.info(f"Created directory: {directory}")
                except Exception as e:
                    logger.error(f"Failed to create directory {directory}: {str(e)}")
                    return False
            else:
                logger.info(f"Directory exists: {directory}")
        return True

    def check_disk_space(self):
        """Check available disk space."""
        required_space = 5 * 1024 * 1024 * 1024  # 5GB
        try:
            if sys.platform == 'win32':
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p('.'), None, None, ctypes.pointer(free_bytes)
                )
                free_space = free_bytes.value
            else:
                st = os.statvfs('.')
                free_space = st.f_bavail * st.f_frsize

            free_gb = free_space / (1024**3)
            logger.info(f"Available disk space: {free_gb:.1f}GB")
            
            if free_space < required_space:
                logger.error(f"Insufficient disk space. Required: 5GB, Available: {free_gb:.1f}GB")
                return False
            return True
        except Exception as e:
            logger.error(f"Failed to check disk space: {str(e)}")
            return False

    def download_models(self):
        """Download required models."""
        os.makedirs(self.model_dir, exist_ok=True)
        
        for model_name, url in self.required_models.items():
            model_path = os.path.join(self.model_dir, model_name)
            
            if os.path.exists(model_path):
                logger.info(f"Model already exists: {model_name}")
                continue
                
            try:
                logger.info(f"Downloading {model_name}...")
                response = urllib.request.urlopen(url)
                total_size = int(response.headers.get('Content-Length', 0))
                
                with tqdm(total=total_size, unit='iB', unit_scale=True) as pbar:
                    urllib.request.urlretrieve(
                        url,
                        model_path,
                        reporthook=lambda count, block_size, total_size: pbar.update(block_size)
                    )
                logger.info(f"Successfully downloaded {model_name}")
            except Exception as e:
                logger.error(f"Failed to download {model_name}: {str(e)}")
                return False
        return True

    def install_requirements(self):
        """Install required packages."""
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            logger.info("Successfully installed requirements")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install requirements: {str(e)}")
            return False

    def run_checks(self):
        """Run all checks and setup steps."""
        checks = [
            ('Python Version', self.check_python_version),
            ('pip Installation', self.check_pip),
            ('Disk Space', self.check_disk_space),
            ('Directories', self.check_directories),
            ('Requirements', self.install_requirements),
            ('CUDA', self.check_cuda),
            ('Models', self.download_models)
        ]

        success = True
        print("\n=== Virtual Try-On System Setup Check ===\n")
        
        for name, check in checks:
            print(f"\nChecking {name}...")
            if not check():
                success = False
                print(f"❌ {name} check failed")
            else:
                print(f"✅ {name} check passed")

        if success:
            print("\n✅ All checks passed! You can now run the application:")
            print("   python app.py")
        else:
            print("\n❌ Some checks failed. Please fix the issues and try again.")

        return success

if __name__ == '__main__':
    checker = SetupChecker()
    success = checker.run_checks()
    sys.exit(0 if success else 1)